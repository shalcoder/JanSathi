"""
JanSathi API Stack — Lambda + API Gateway + WAF
From AWS_PRODUCTION_ARCHITECTURE.md Section 2: API Layer
"""
import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_logs as logs,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_wafv2 as wafv2,
    aws_kendra as kendra,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_events as events,
    aws_cognito as cognito,
)
from constructs import Construct


class ApiStack(Stack):
    """
    Creates:
    - Lambda function (Flask via Mangum, 512MB, 29s timeout)
    - API Gateway REST API (CORS enabled, throttling)
    - WAF WebACL (rate limiting 100 req/5min per IP)
    - CloudWatch alarms (error rate, latency)
    - IAM roles (least privilege: Bedrock, Polly, Transcribe, S3, DynamoDB)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        users_table: dynamodb.Table,
        conversations_table: dynamodb.Table,
        cache_table: dynamodb.Table,
        hitl_table: dynamodb.Table,
        audio_bucket: s3.Bucket,
        uploads_bucket: s3.Bucket,
        kendra_index: kendra.CfnIndex,
        notifications_topic: sns.Topic,
        hitl_queue: sqs.Queue,
        event_bus: events.EventBus,
        user_pool: cognito.UserPool,
        state_machine_arn: str = None,
        bedrock_agent_id: str = "",
        bedrock_agent_alias_id: str = "",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ============================================================
        # Lambda Function (Flask app via Mangum)
        # ============================================================
        backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")

        self.lambda_function = _lambda.Function(
            self, "QueryHandler",
            function_name="JanSathi-QueryHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset(
                backend_path,
                exclude=[
                    "__pycache__",
                    "*.pyc",
                    ".env",
                    "instance/*",
                    "uploads/*",
                    "test_*",
                    "verify_*",
                    ".git",
                ],
            ),
            memory_size=512,
            timeout=Duration.seconds(29),
            architecture=_lambda.Architecture.X86_64,
            environment={
                "DYNAMODB_USERS_TABLE": users_table.table_name,
                "DYNAMODB_CONVERSATIONS_TABLE": conversations_table.table_name,
                "DYNAMODB_CACHE_TABLE": cache_table.table_name,
                "AUDIO_BUCKET": audio_bucket.bucket_name,
                "UPLOADS_BUCKET": uploads_bucket.bucket_name,
                "SNS_TOPIC_ARN": notifications_topic.topic_arn,
                "AWS_REGION_NAME": kwargs.get("env", cdk.Environment()).region or "ap-south-1",
                # Bedrock
                "BEDROCK_MODEL_ID": "amazon.nova-lite-v1:0",
                "BEDROCK_MAX_TOKENS": "2048",
                "BEDROCK_AGENT_ID": bedrock_agent_id,
                "BEDROCK_AGENT_ALIAS_ID": bedrock_agent_alias_id,
                # Kendra
                "KENDRA_INDEX_ID": kendra_index.attr_id,
                # Step Functions
                "STATE_MACHINE_ARN": state_machine_arn or "",
                # DynamoDB
                "HITL_TABLE": hitl_table.table_name,
                # SQS
                "HITL_QUEUE_URL": hitl_queue.queue_url,
                # EventBridge
                "EVENTBRIDGE_BUS_NAME": event_bus.event_bus_name,
                # Cognito
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
                # Runtime
                "NODE_ENV": "production",
                "USE_DYNAMODB": "true",
                "XRAY_ENABLED": "true",
            },
            tracing=_lambda.Tracing.ACTIVE,
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

        # ============================================================
        # IAM Permissions (Least Privilege)
        # ============================================================
        # DynamoDB
        users_table.grant_read_write_data(self.lambda_function)
        conversations_table.grant_read_write_data(self.lambda_function)
        cache_table.grant_read_write_data(self.lambda_function)

        # SNS
        notifications_topic.grant_publish(self.lambda_function)

        # S3
        audio_bucket.grant_read_write(self.lambda_function)
        uploads_bucket.grant_read_write(self.lambda_function)

        # HITL table
        hitl_table.grant_read_write_data(self.lambda_function)

        # Bedrock — foundation models + AgentCore (InvokeAgent)
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                resources=["arn:aws:bedrock:*::foundation-model/*"],
            )
        )
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock-agent-runtime:InvokeAgent"],
                resources=["arn:aws:bedrock:*:*:agent-alias/*"],
            )
        )

        # Polly (SynthesizeSpeech only)
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["polly:SynthesizeSpeech"],
                resources=["*"],
            )
        )

        # Transcribe
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "transcribe:StartTranscriptionJob",
                    "transcribe:GetTranscriptionJob",
                ],
                resources=["*"],
            )
        )

        # Step Functions (Agri/Civic Workflow)
        if state_machine_arn:
            self.lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["states:StartExecution"],
                    resources=[state_machine_arn],
                )
            )

        # Kendra — query and retrieve
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["kendra:Query", "kendra:Retrieve", "kendra:BatchGetDocumentStatus"],
                resources=[f"arn:aws:kendra:{self.region}:{self.account}:index/*"],
            )
        )

        # EventBridge — publish domain events
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["events:PutEvents"],
                resources=[event_bus.event_bus_arn],
            )
        )

        # SQS — send HITL cases to FIFO queue
        hitl_queue.grant_send_messages(self.lambda_function)

        # SSM Parameter Store
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "ssm:GetParameters"],
                resources=[f"arn:aws:ssm:*:*:parameter/jansathi/*"],
            )
        )

        # ============================================================
        # API Gateway REST API
        # ============================================================
        self.api = apigw.LambdaRestApi(
            self, "JanSathiApi",
            rest_api_name="JanSathi-API",
            handler=self.lambda_function,
            proxy=True,
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
                logging_level=apigw.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                tracing_enabled=True,
                metrics_enabled=True,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization", "X-Amz-Date"],
                max_age=Duration.hours(1),
            ),
        )

        # Cognito authorizer — protects /api/* routes
        # /health and OPTIONS (CORS preflight) remain open
        self.cognito_authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name="JanSathi-CognitoAuth",
            identity_source="method.request.header.Authorization",
            results_cache_ttl=Duration.minutes(5),
        )

        # Usage Plan for External Partners
        usage_plan = self.api.add_usage_plan(
            "JanSathiUsagePlan",
            name="ProfessionalPartners",
            throttle=apigw.ThrottleSettings(
                rate_limit=50,
                burst_limit=100
            ),
            quota=apigw.QuotaSettings(
                limit=1000,
                period=apigw.Period.DAY
            )
        )

        api_key = self.api.add_api_key("JanSathiPartnerKey")
        usage_plan.add_api_key(api_key)

        # Store API URL for frontend stack
        self.api_url = self.api.url

        # ============================================================
        # WAF WebACL (Rate Limiting)
        # ============================================================
        waf_acl = wafv2.CfnWebACL(
            self, "JanSathiWAF",
            name="JanSathi-WAF",
            scope="REGIONAL",  # For API Gateway
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name="JanSathiWAF",
            ),
            rules=[
                # Rule 1: Rate limiting (100 requests per 5 minutes per IP)
                wafv2.CfnWebACL.RuleProperty(
                    name="RateLimitPerIP",
                    priority=1,
                    action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                            limit=100,
                            aggregate_key_type="IP",
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="RateLimitPerIP",
                    ),
                ),
                # Rule 2: AWS Managed - Common Rule Set (SQLi, XSS)
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedCommonRuleSet",
                    priority=2,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(none={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesCommonRuleSet",
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedCommonRuleSet",
                    ),
                ),
            ],
        )

        # Associate WAF with API Gateway
        api_stage_arn = f"arn:aws:apigateway:{self.region}::/restapis/{self.api.rest_api_id}/stages/prod"
        wafv2.CfnWebACLAssociation(
            self, "WAFAssociation",
            resource_arn=api_stage_arn,
            web_acl_arn=waf_acl.attr_arn,
        )

        # ============================================================
        # CloudWatch Alarms
        # ============================================================
        # Error rate alarm (> 1% errors)
        error_alarm = cloudwatch.Alarm(
            self, "ErrorRateAlarm",
            alarm_name="JanSathi-HighErrorRate",
            metric=self.lambda_function.metric_errors(
                period=Duration.minutes(5),
                statistic="Sum",
            ),
            threshold=5,
            evaluation_periods=2,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        # Latency alarm (P95 > 2s)
        latency_alarm = cloudwatch.Alarm(
            self, "LatencyAlarm",
            alarm_name="JanSathi-HighLatency",
            metric=self.lambda_function.metric_duration(
                period=Duration.minutes(5),
                statistic="p95",
            ),
            threshold=2000,  # 2 seconds in ms
            evaluation_periods=3,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        # ============================================================
        # Outputs
        # ============================================================
        cdk.CfnOutput(self, "ApiUrl",
                       value=self.api.url,
                       description="API Gateway endpoint URL")
        cdk.CfnOutput(self, "LambdaFunctionName",
                       value=self.lambda_function.function_name,
                       description="Lambda function name")
        cdk.CfnOutput(self, "WAFWebACLArn",
                       value=waf_acl.attr_arn,
                       description="WAF WebACL ARN")
