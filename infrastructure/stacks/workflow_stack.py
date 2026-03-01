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
        # Step 1: Mock Pass States (for Hackathon Demo)
        # ============================================================
        # In a real app, these would be LambdaInvoke tasks
        
        verify_aadhaar = sfn.Pass(
            self, "AadhaarVerification",
            result=sfn.Result.from_object({"status": "verified", "auth_code": "UID-OK"}),
            result_path="$.aadhaar_result"
        )
        
        check_bank = sfn.Pass(
            self, "CheckBankLink",
            result=sfn.Result.from_object({"status": "active", "bank": "SBI"}),
            result_path="$.bank_result"
        )

        eligibility_audit = sfn.Pass(
            self, "EligibilityAudit",
            result=sfn.Result.from_object({"eligible": True, "score": 95}),
            result_path="$.eligibility_result"
        )

        form_synthesis = sfn.Pass(
            self, "FormSynthesis",
            result=sfn.Result.from_object({"form_id": "FORM-12345", "status": "generated"}),
            result_path="$.form_result"
        )

        final_submission = sfn.Pass(
            self, "FinalSubmission",
            result=sfn.Result.from_object({"application_id": "APP-2024-001", "status": "submitted"}),
            result_path="$.submission_result"
        )

        # ============================================================
        # Chain Definition
        # ============================================================
        definition = verify_aadhaar.next(check_bank).next(eligibility_audit).next(form_synthesis).next(final_submission)

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
