"""
JanSathi Workflow Stack — AWS Step Functions
Handles multi-step civic workflows (Verification -> Eligibility -> Submission)
"""
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_lambda as _lambda,
)
from constructs import Construct

class WorkflowStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ============================================================
        # Step 1: Lambda Task Definitions
        # ============================================================
        
        verify_aadhaar_fn = _lambda.Function(
            self, "AadhaarVerifyFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.verification_tasks.aadhaar_verify",
            code=_lambda.Code.from_asset("backend"),
            timeout=cdk.Duration.seconds(15)
        )

        check_bank_fn = _lambda.Function(
            self, "BankVerifyFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.verification_tasks.bank_verify",
            code=_lambda.Code.from_asset("backend"),
            timeout=cdk.Duration.seconds(15)
        )

        eligibility_audit_fn = _lambda.Function(
            self, "EligibilityAuditFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.engine_tasks.evaluate_eligibility",
            code=_lambda.Code.from_asset("backend"),
            timeout=cdk.Duration.seconds(15)
        )

        artifact_gen_fn = _lambda.Function(
            self, "ArtifactGenFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.tasks.engine_tasks.generate_artifact",
            code=_lambda.Code.from_asset("backend"),
            timeout=cdk.Duration.seconds(30)
        )

        # ============================================================
        # Step 2: Step Function Tasks
        # ============================================================
        
        aadhaar_task = tasks.LambdaInvoke(
            self, "AadhaarVerificationTask",
            lambda_function=verify_aadhaar_fn,
            result_path="$.aadhaar_result"
        )
        
        bank_task = tasks.LambdaInvoke(
            self, "CheckBankLinkTask",
            lambda_function=check_bank_fn,
            result_path="$.bank_result"
        )

        audit_task = tasks.LambdaInvoke(
            self, "EligibilityAuditTask",
            lambda_function=eligibility_audit_fn,
            result_path="$.eligibility_result"
        )

        artifact_task = tasks.LambdaInvoke(
            self, "GenerateArtifactTask",
            lambda_function=artifact_gen_fn,
            result_path="$.artifact_result"
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
            definition=definition,
            timeout=cdk.Duration.minutes(5),
            tracing_enabled=True
        )

        # ============================================================
        # Outputs
        # ============================================================
        cdk.CfnOutput(self, "StateMachineArn",
                       value=self.state_machine.state_machine_arn,
                       description="Step Functions State Machine ARN")
