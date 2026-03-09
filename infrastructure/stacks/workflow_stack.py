"""
JanSathi Workflow Stack — AWS Step Functions + EventBridge trigger
Handles multi-step civic workflows (Verification -> Eligibility -> Submission)
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
)
from constructs import Construct


class WorkflowStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        hitl_table: dynamodb.Table = None,
        event_bus: events.EventBus = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Common env for task Lambdas
        task_env = {
            "HITL_TABLE":          hitl_table.table_name if hitl_table else "JanSathi-HITL-Cases",
            "AWS_REGION":          self.region,
            "DYNAMODB_SESSIONS_TABLE": "JanSathi-Sessions",
        }

        # ============================================================
        # Step 1: Lambda Task Definitions
        # ============================================================

        verify_aadhaar_fn = _lambda.Function(
            self, "AadhaarVerifyFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.verification_tasks.aadhaar_verify",
            code=_lambda.Code.from_asset("backend"),
            timeout=Duration.seconds(15),
            environment=task_env,
            tracing=_lambda.Tracing.ACTIVE,
        )

        check_bank_fn = _lambda.Function(
            self, "BankVerifyFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.verification_tasks.bank_verify",
            code=_lambda.Code.from_asset("backend"),
            timeout=Duration.seconds(15),
            environment=task_env,
            tracing=_lambda.Tracing.ACTIVE,
        )

        eligibility_audit_fn = _lambda.Function(
            self, "EligibilityAuditFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.engine_tasks.evaluate_eligibility",
            code=_lambda.Code.from_asset("backend"),
            timeout=Duration.seconds(15),
            environment={
                **task_env,
                "S3_UPLOADS_BUCKET": "jansathi-uploads",
            },
            tracing=_lambda.Tracing.ACTIVE,
        )

        artifact_gen_fn = _lambda.Function(
            self, "ArtifactGenFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.engine_tasks.generate_artifact",
            code=_lambda.Code.from_asset("backend"),
            timeout=Duration.seconds(30),
            environment={
                **task_env,
                "S3_UPLOADS_BUCKET": "jansathi-uploads",
            },
            tracing=_lambda.Tracing.ACTIVE,
        )

        # Grant DynamoDB access to task Lambdas
        if hitl_table:
            hitl_table.grant_read_write_data(verify_aadhaar_fn)
            hitl_table.grant_read_write_data(check_bank_fn)
            hitl_table.grant_read_write_data(eligibility_audit_fn)
            hitl_table.grant_read_write_data(artifact_gen_fn)

        # S3 access for artifact_gen
        artifact_gen_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject", "s3:GetObject"],
                resources=["arn:aws:s3:::jansathi-uploads/*"],
            )
        )

        # ============================================================
        # Step 2: Step Function Tasks (payload passthrough — no result_path)
        # ============================================================

        aadhaar_task = tasks.LambdaInvoke(
            self, "AadhaarVerificationTask",
            lambda_function=verify_aadhaar_fn,
            output_path="$.Payload",
        )

        bank_task = tasks.LambdaInvoke(
            self, "CheckBankLinkTask",
            lambda_function=check_bank_fn,
            output_path="$.Payload",
        )

        audit_task = tasks.LambdaInvoke(
            self, "EligibilityAuditTask",
            lambda_function=eligibility_audit_fn,
            output_path="$.Payload",
        )

        artifact_task = tasks.LambdaInvoke(
            self, "GenerateArtifactTask",
            lambda_function=artifact_gen_fn,
            output_path="$.Payload",
        )

        # ============================================================
        # Chain Definition
        # ============================================================
        definition = aadhaar_task.next(bank_task).next(audit_task).next(artifact_task)

        # ============================================================
        # State Machine
        # ============================================================
        self.state_machine = sfn.StateMachine(
            self, "JanSathiWorkflow",
            state_machine_name="JanSathi-ApplicationWorkflow",
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            timeout=Duration.minutes(5),
            tracing_enabled=True,
        )

        # ============================================================
        # EventBridge Rule: ApplicationSubmitted → StartExecution
        # ============================================================
        if event_bus:
            rule = events.Rule(
                self, "ApplicationSubmittedRule",
                rule_name="JanSathi-ApplicationSubmitted",
                event_bus=event_bus,
                description="Trigger Step Functions when citizen submits benefit application",
                event_pattern=events.EventPattern(
                    source=["in.gov.jansathi"],
                    detail_type=["ApplicationSubmitted"],
                ),
            )
            rule.add_target(
                targets.SfnStateMachine(
                    self.state_machine,
                    input=events.RuleTargetInput.from_event_path("$.detail"),
                    role=iam.Role(
                        self, "EventBridgeSfnRole",
                        assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
                        inline_policies={
                            "StartExecution": iam.PolicyDocument(
                                statements=[
                                    iam.PolicyStatement(
                                        actions=["states:StartExecution"],
                                        resources=[self.state_machine.state_machine_arn],
                                    )
                                ]
                            )
                        },
                    ),
                )
            )

        # ============================================================
        # Outputs
        # ============================================================
        cdk.CfnOutput(self, "StateMachineArn",
                       value=self.state_machine.state_machine_arn,
                       description="Step Functions State Machine ARN")
