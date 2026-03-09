"""
messaging_stack.py — JanSathi Messaging Infrastructure (CDK)
=============================================================
Provisions:
  - SQS FIFO queue:   jansathi-hitl.fifo         (HITL case queue)
  - SQS DLQ:         jansathi-hitl-dlq.fifo       (after 3 failures)
  - EventBridge bus: jansathi-events              (domain event bus)
  - Cognito:         JanSathi-UserPool            (citizen + officer auth)

This stack is a dependency of ApiStack and WorkflowStack.
Outputs are passed as constructor params to ApiStack.
"""

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_sqs as sqs,
    aws_events as events,
    aws_cognito as cognito,
    aws_iam as iam,
)
from constructs import Construct


class MessagingStack(Stack):
    """
    SQS FIFO + EventBridge + Cognito resources, kept separate to
    avoid circular dependency between DataStack and ApiStack.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ============================================================
        # SQS — HITL Dead-Letter Queue (FIFO)
        # ============================================================
        self.hitl_dlq = sqs.Queue(
            self, "HitlDlq",
            queue_name="jansathi-hitl-dlq.fifo",
            fifo=True,
            content_based_deduplication=True,
            removal_policy=RemovalPolicy.RETAIN,
            retention_period=Duration.days(14),
            encryption=sqs.QueueEncryption.SQS_MANAGED,
        )

        # ============================================================
        # SQS — HITL FIFO Queue (main)
        # ============================================================
        self.hitl_queue = sqs.Queue(
            self, "HitlQueue",
            queue_name="jansathi-hitl.fifo",
            fifo=True,
            content_based_deduplication=True,
            removal_policy=RemovalPolicy.RETAIN,
            visibility_timeout=Duration.seconds(300),   # 5 min; match Lambda timeout
            retention_period=Duration.days(7),
            encryption=sqs.QueueEncryption.SQS_MANAGED,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.hitl_dlq,
            ),
        )

        # ============================================================
        # EventBridge — Custom Event Bus
        # ============================================================
        self.event_bus = events.EventBus(
            self, "JanSathiEventBus",
            event_bus_name="jansathi-events",
        )

        # Allow any account principal to publish (tightened to Lambda role via IAM)
        self.event_bus.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowAccountPublish",
                principals=[iam.AccountRootPrincipal()],
                actions=["events:PutEvents"],
                resources=[self.event_bus.event_bus_arn],
            )
        )

        # ============================================================
        # Cognito — User Pool (citizen + officer authentication)
        # ============================================================
        self.user_pool = cognito.UserPool(
            self, "JanSathiUserPool",
            user_pool_name="JanSathi-UserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                phone=True,
            ),
            auto_verify=cognito.AutoVerifiedAttrs(
                email=True,
                phone=True,
            ),
            standard_attributes=cognito.StandardAttributes(
                phone_number=cognito.StandardAttribute(required=False, mutable=True),
                email=cognito.StandardAttribute(required=False, mutable=True),
                given_name=cognito.StandardAttribute(required=False, mutable=True),
                family_name=cognito.StandardAttribute(required=False, mutable=True),
            ),
            custom_attributes={
                "preferred_language": cognito.StringAttribute(mutable=True),
                "aadhaar_linked":     cognito.BooleanAttribute(mutable=True),
                "role":               cognito.StringAttribute(mutable=True),  # "citizen" | "officer"
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_AND_PHONE_WITHOUT_MFA,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # App client — used by Next.js frontend (no client secret for SPA)
        self.user_pool_client = self.user_pool.add_client(
            "WebAppClient",
            user_pool_client_name="JanSathi-WebClient",
            auth_flows=cognito.AuthFlow(
                user_srp=True,
                user_password=True,
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=["http://localhost:3000/auth/callback"],
                logout_urls=["http://localhost:3000/"],
            ),
            prevent_user_existence_errors=True,
            generate_secret=False,
        )

        # Identity pool — grants temporary AWS credentials to citizens
        # (for direct S3 document upload via pre-signed URLs)
        self.identity_pool = cognito.CfnIdentityPool(
            self, "JanSathiIdentityPool",
            identity_pool_name="JanSathi_IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=self.user_pool.user_pool_provider_name,
                    server_side_token_check=True,
                )
            ],
        )

        # IAM roles for authenticated identity pool users
        authenticated_role = iam.Role(
            self, "AuthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )

        # Allow authenticated users to upload to their own S3 prefix only
        # (limited to uploads/${cognito-identity.amazonaws.com:sub}/* path)
        authenticated_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject", "s3:GetObject"],
                resources=[
                    f"arn:aws:s3:::jansathi-uploads/uploads/"
                    "${{cognito-identity.amazonaws.com:sub}}/*"
                ],
            )
        )

        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoles",
            identity_pool_id=self.identity_pool.ref,
            roles={"authenticated": authenticated_role.role_arn},
        )

        # ============================================================
        # Outputs
        # ============================================================
        cdk.CfnOutput(self, "HitlQueueUrl",
                       value=self.hitl_queue.queue_url,
                       description="SQS FIFO queue URL for HITL cases")
        cdk.CfnOutput(self, "HitlQueueArn",
                       value=self.hitl_queue.queue_arn,
                       description="SQS FIFO queue ARN for HITL cases")
        cdk.CfnOutput(self, "EventBusName",
                       value=self.event_bus.event_bus_name,
                       description="EventBridge custom bus name")
        cdk.CfnOutput(self, "EventBusArn",
                       value=self.event_bus.event_bus_arn,
                       description="EventBridge custom bus ARN")
        cdk.CfnOutput(self, "UserPoolId",
                       value=self.user_pool.user_pool_id,
                       description="Cognito User Pool ID")
        cdk.CfnOutput(self, "UserPoolClientId",
                       value=self.user_pool_client.user_pool_client_id,
                       description="Cognito App Client ID (frontend)")
        cdk.CfnOutput(self, "IdentityPoolId",
                       value=self.identity_pool.ref,
                       description="Cognito Identity Pool ID")
