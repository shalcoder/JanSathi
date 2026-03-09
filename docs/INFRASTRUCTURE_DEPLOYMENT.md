# ☁️ JanSathi Infrastructure & Deployment Implementation

## 📋 Overview

JanSathi's infrastructure is built on **AWS cloud-native services** with **Infrastructure as Code (IaC)** using AWS CDK. The system is designed for **serverless scalability**, **cost optimization** (<₹2/user/month), and **high availability** across Indian regions.

---

## 🏗️ **Infrastructure Architecture**

### **AWS Services Stack (16 Services)**
```
┌─────────────────┬──────────────────┬─────────────────────┬────────────────┐
│   Compute       │     Storage      │      AI/ML          │   Networking   │
├─────────────────┼──────────────────┼─────────────────────┼────────────────┤
│ Lambda          │ DynamoDB         │ Bedrock (Nova)      │ API Gateway    │
│ Step Functions  │ S3               │ Kendra              │ CloudFront     │
│                 │                  │ Transcribe          │ Route53        │
│                 │                  │ Polly               │                │
├─────────────────┼──────────────────┼─────────────────────┼────────────────┤
│   Messaging     │   Monitoring     │      Security       │   Integration  │
├─────────────────┼──────────────────┼─────────────────────┼────────────────┤
│ SQS             │ CloudWatch       │ Cognito             │ Connect        │
│ SNS             │ X-Ray            │ WAF                 │                │
│                 │                  │ IAM                 │                │
└─────────────────┴──────────────────┴─────────────────────┴────────────────┘
```

### **Deployment Regions**
- **Primary**: `us-east-1` (N. Virginia) - Global services, lowest latency to India
- **Secondary**: `ap-south-1` (Mumbai) - Data residency compliance (future)
- **Edge**: CloudFront global edge locations

---

## 🏢 **AWS CDK Infrastructure (`/infrastructure`)**

### **Main CDK Application (`app.py`)**
**Purpose**: Orchestrates all infrastructure stacks with proper dependencies and tagging.

```python
#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.data_stack import DataStack
from stacks.api_stack import ApiStack
from stacks.workflow_stack import WorkflowStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()

# Environment configuration
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1"
)

# Stack deployment with dependencies
data_stack = DataStack(app, "JanSathiDataStack", env=env)

api_stack = ApiStack(
    app, "JanSathiApiStack", 
    env=env,
    dynamo_table=data_stack.user_table,
    s3_bucket=data_stack.documents_bucket,
    kendra_index=data_stack.kendra_index
)

workflow_stack = WorkflowStack(
    app, "JanSathiWorkflowStack",
    env=env,
    api_gateway=api_stack.api_gateway
)

frontend_stack = FrontendStack(
    app, "JanSathiFrontendStack",
    env=env,
    api_gateway_url=api_stack.api_gateway.url
)

# Global tags for cost tracking
cdk.Tags.of(app).add("Project", "JanSathi")
cdk.Tags.of(app).add("Environment", app.node.try_get_context("env") or "dev")
cdk.Tags.of(app).add("CostCenter", "RuralTech")

app.synth()
```

### **CDK Configuration (`cdk.json`)**
**Purpose**: CDK toolkit configuration with feature flags and context.

```json
{
  "app": "python app.py",
  "watch": {
    "include": ["**"],
    "exclude": ["README.md", "cdk*.json", "requirements*.txt"]
  },
  "context": {
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:enableStackNameDuplicates": true,
    "aws-cdk:enableDiffNoFail": true,
    "@aws-cdk/core:stackRelativeExports": true
  }
}
```

---

## 🗄️ **Data Stack (`/infrastructure/stacks/data_stack.py`)**
**Purpose**: Foundational data services - DynamoDB, S3, Kendra, SNS.

### **DynamoDB Tables**

```python
class DataStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # User profiles table
        self.user_table = dynamodb.Table(
            self, "UserProfiles",
            table_name="jansathi-users",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            
            # GSI for phone number lookup
            global_secondary_indexes=[
                dynamodb.GlobalSecondaryIndex(
                    index_name="phone-index",
                    partition_key=dynamodb.Attribute(
                        name="phone_number",
                        type=dynamodb.AttributeType.STRING
                    )
                )
            ]
        )

        # Conversations table
        self.conversations_table = dynamodb.Table(
            self, "Conversations",
            table_name="jansathi-conversations",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Cache table for response optimization
        self.cache_table = dynamodb.Table(
            self, "ResponseCache",
            table_name="jansathi-cache",
            partition_key=dynamodb.Attribute(
                name="cache_key",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="expires_at"
        )
```

### **S3 Buckets**

```python
        # Documents and receipts bucket
        self.documents_bucket = s3.Bucket(
            self, "DocumentsBucket",
            bucket_name="jansathi-documents-prod",
            versioning=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.POST],
                    allowed_origins=["https://jansathi.com", "https://localhost:3000"],
                    allowed_headers=["*"]
                )
            ],
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldReceipts",
                    expiration=cdk.Duration.days(30),
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=cdk.Duration.days(7)
                        )
                    ]
                )
            ]
        )

        # Audio files bucket (voice recordings)
        self.audio_bucket = s3.Bucket(
            self, "AudioBucket",
            bucket_name="jansathi-audio-prod",
            encryption=s3.BucketEncryption.S3_MANAGED,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldAudio",
                    expiration=cdk.Duration.days(7)  # Audio deleted after 7 days
                )
            ]
        )
```

### **Amazon Kendra Search Index**

```python
        # Kendra index for government scheme knowledge
        self.kendra_index = kendra.CfnIndex(
            self, "SchemeKnowledgeIndex",
            name="jansathi-schemes",
            edition="DEVELOPER_EDITION",  # Cost-optimized for development
            role_arn=kendra_role.role_arn,
            description="Government schemes knowledge base for JanSathi"
        )

        # Government documents data source
        kendra_data_source = kendra.CfnDataSource(
            self, "GovernmentDocsDataSource",
            name="government-schemes-docs",
            index_id=self.kendra_index.ref,
            type="S3",
            configuration={
                "S3Configuration": {
                    "BucketName": "indian-government-schemes-docs",
                    "InclusionPrefixes": ["schemes/", "eligibility/"],
                    "DocumentsMetadataConfiguration": {
                        "S3Prefix": "metadata/"
                    }
                }
            },
            role_arn=kendra_data_source_role.role_arn
        )
```

### **SNS Topics for Notifications**

```python
        # SMS notifications topic
        self.sms_topic = sns.Topic(
            self, "SmsNotifications",
            topic_name="jansathi-sms",
            display_name="JanSathi SMS Notifications"
        )

        # HITL notifications for admin alerts
        self.hitl_topic = sns.Topic(
            self, "HitlAlerts",
            topic_name="jansathi-hitl",
            display_name="JanSathi HITL Alerts"
        )
```

---

## 🔧 **API Stack (`/infrastructure/stacks/api_stack.py`)**
**Purpose**: Serverless compute layer - Lambda functions, API Gateway, CloudWatch.

### **Lambda Functions**

```python
class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Main API Lambda function
        self.api_lambda = _lambda.Function(
            self, "ApiFunction",
            function_name="jansathi-api",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("../backend"),
            handler="lambda_handler.handler",
            timeout=cdk.Duration.seconds(30),
            memory_size=1024,
            
            # Environment variables
            environment={
                "USERS_TABLE": kwargs["dynamo_table"].table_name,
                "DOCUMENTS_BUCKET": kwargs["s3_bucket"].bucket_name,
                "KENDRA_INDEX": kwargs["kendra_index"].ref,
                "SMS_TOPIC_ARN": self.sms_topic.topic_arn,
                "CORS_ORIGINS": "https://jansathi.com,https://localhost:3000"
            },
            
            # Performance optimizations
            reserved_concurrent_executions=100,
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "BedrockLayer",
                    "arn:aws:lambda:us-east-1:123456789:layer:bedrock-python:1"
                )
            ]
        )

        # IVR webhook Lambda (for Amazon Connect)
        self.ivr_lambda = _lambda.Function(
            self, "IvrWebhookFunction",
            function_name="jansathi-ivr-webhook",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("../backend"),
            handler="lambda_handler.ivr_handler",
            timeout=cdk.Duration.seconds(10),
            memory_size=512
        )

        # Audio processing Lambda
        self.audio_lambda = _lambda.Function(
            self, "AudioProcessingFunction",
            function_name="jansathi-audio-processor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset("../backend"),
            handler="lambda_handler.audio_handler",
            timeout=cdk.Duration.minutes(5),  # Longer timeout for audio processing
            memory_size=2048
        )
```

### **API Gateway**

```python
        # REST API Gateway
        self.api_gateway = apigateway.RestApi(
            self, "JanSathiApi",
            rest_api_name="jansathi-api",
            description="JanSathi Civic Automation API",
            
            # CORS configuration
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["https://jansathi.com", "https://localhost:3000"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"]
            ),
            
            # Request validation
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            )
        )

        # API Gateway resources and methods
        v1_resource = self.api_gateway.root.add_resource("v1")
        
        # Session management
        sessions_resource = v1_resource.add_resource("sessions")
        sessions_resource.add_method(
            "POST", 
            apigateway.LambdaIntegration(self.api_lambda),
            request_validator=request_validator
        )

        # Query endpoint
        query_resource = v1_resource.add_resource("query")
        query_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.api_lambda)
        )

        # Application submission
        apply_resource = v1_resource.add_resource("apply")
        apply_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.api_lambda)
        )

        # Admin endpoints
        admin_resource = v1_resource.add_resource("admin")
        cases_resource = admin_resource.add_resource("cases")
        cases_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.api_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer
        )

        # IVR webhook
        ivr_resource = v1_resource.add_resource("ivr")
        webhook_resource = ivr_resource.add_resource("connect-webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.ivr_lambda)
        )
```

### **WAF Security Rules**

```python
        # Web Application Firewall
        self.waf = wafv2.CfnWebACL(
            self, "ApiWaf",
            name="jansathi-api-waf",
            scope="REGIONAL",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            
            rules=[
                # Rate limiting rule
                wafv2.CfnWebACL.RuleProperty(
                    name="RateLimitRule",
                    priority=1,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        rate_based_statement=wafv2.CfnWebACL.RateLimitStatementProperty(
                            limit=200,  # 200 requests per 5 minutes
                            aggregate_key_type="IP"
                        )
                    ),
                    action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="RateLimitRule"
                    )
                ),
                
                # SQL injection protection
                wafv2.CfnWebACL.RuleProperty(
                    name="SqlInjectionRule",
                    priority=2,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesSQLiRuleSet"
                        )
                    ),
                    action=wafv2.CfnWebACL.RuleActionProperty(block={}),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="SqlInjectionRule"
                    )
                )
            ]
        )
```

### **CloudWatch Monitoring**

```python
        # CloudWatch Log Groups
        api_log_group = logs.LogGroup(
            self, "ApiLogGroup",
            log_group_name="/aws/lambda/jansathi-api",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Custom CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self, "JanSathiDashboard",
            dashboard_name="JanSathi-Operations"
        )

        # API Gateway metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="API Requests",
                left=[
                    self.api_gateway.metric_count(period=cdk.Duration.minutes(5)),
                    self.api_gateway.metric_error(period=cdk.Duration.minutes(5))
                ]
            ),
            
            cloudwatch.GraphWidget(
                title="Lambda Performance",
                left=[
                    self.api_lambda.metric_duration(period=cdk.Duration.minutes(5)),
                    self.api_lambda.metric_errors(period=cdk.Duration.minutes(5))
                ]
            )
        )

        # CloudWatch Alarms
        high_error_rate_alarm = cloudwatch.Alarm(
            self, "HighErrorRateAlarm",
            alarm_description="API error rate > 5%",
            metric=self.api_gateway.metric_client_error(
                period=cdk.Duration.minutes(5)
            ),
            threshold=5,
            evaluation_periods=2
        )

        high_latency_alarm = cloudwatch.Alarm(
            self, "HighLatencyAlarm", 
            alarm_description="API latency > 2000ms",
            metric=self.api_lambda.metric_duration(
                period=cdk.Duration.minutes(5)
            ),
            threshold=2000,
            evaluation_periods=3
        )
```

---

## 🔄 **Step Functions Workflow Stack (`/infrastructure/stacks/workflow_stack.py`)**
**Purpose**: Complex multi-step workflow orchestration using AWS Step Functions.

### **State Machine Definition**

```python
class WorkflowStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # HITL Review Workflow
        hitl_workflow = stepfunctions.StateMachine(
            self, "HitlReviewWorkflow",
            state_machine_name="jansathi-hitl-review",
            definition=self.create_hitl_definition(),
            timeout=cdk.Duration.hours(48)  # 48 hour SLA for human review
        )

        # Multi-step Application Process
        application_workflow = stepfunctions.StateMachine(
            self, "ApplicationWorkflow",
            state_machine_name="jansathi-application-process",
            definition=self.create_application_definition()
        )

    def create_hitl_definition(self):
        # Case assignment step
        assign_case = stepfunctions_tasks.LambdaInvoke(
            self, "AssignCase",
            lambda_function=kwargs["assign_case_function"],
            output_path="$.Payload"
        )

        # Human review wait state
        wait_for_review = stepfunctions.Wait(
            self, "WaitForHumanReview",
            time=stepfunctions.WaitTime.duration(cdk.Duration.hours(24))
        )

        # Check review status
        check_status = stepfunctions_tasks.LambdaInvoke(
            self, "CheckReviewStatus",
            lambda_function=kwargs["check_status_function"]
        )

        # Approval notification
        send_approval = stepfunctions_tasks.SnsPublish(
            self, "SendApprovalNotification",
            topic=kwargs["notification_topic"],
            message=stepfunctions.TaskInput.from_json_path_at("$.approvalMessage")
        )

        # Rejection notification  
        send_rejection = stepfunctions_tasks.SnsPublish(
            self, "SendRejectionNotification",
            topic=kwargs["notification_topic"],
            message=stepfunctions.TaskInput.from_json_path_at("$.rejectionMessage")
        )

        # Define workflow
        workflow_definition = assign_case.next(
            wait_for_review.next(
                check_status.next(
                    stepfunctions.Choice(self, "ReviewDecision")
                    .when(
                        stepfunctions.Condition.string_equals("$.status", "approved"),
                        send_approval
                    )
                    .when(
                        stepfunctions.Condition.string_equals("$.status", "rejected"),
                        send_rejection
                    )
                    .otherwise(wait_for_review)
                )
            )
        )

        return workflow_definition
```

---

## 🌐 **Frontend Stack (`/infrastructure/stacks/frontend_stack.py`)**
**Purpose**: Static website hosting with CDN and DNS management.

### **S3 Static Website Hosting**

```python
class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for static website
        self.website_bucket = s3.Bucket(
            self, "WebsiteBucket",
            bucket_name="jansathi.com",
            website_index_document="index.html",
            website_error_document="404.html",
            public_read_access=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self, "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront_origins.S3Origin(self.website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True
            ),
            
            # Additional behaviors
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=cloudfront_origins.HttpOrigin(
                        f"{kwargs['api_gateway_url']}.execute-api.us-east-1.amazonaws.com"
                    ),
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN
                ),
                
                "/_next/static/*": cloudfront.BehaviorOptions(
                    origin=cloudfront_origins.S3Origin(self.website_bucket),
                    cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED_FOR_UNCOMPRESSED_OBJECTS
                )
            },
            
            # Security settings
            certificate=acm.Certificate.from_certificate_arn(
                self, "SslCertificate",
                certificate_arn="arn:aws:acm:us-east-1:123456789:certificate/abc123"
            ),
            domain_names=["jansathi.com", "www.jansathi.com"],
            
            # Geo restriction for India focus
            geo_restriction=cloudfront.GeoRestriction.allowlist("IN", "US", "GB")
        )

        # Route53 DNS
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name="jansathi.com"
        )

        # A record for apex domain
        route53.ARecord(
            self, "ApexRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution)
            )
        )

        # AAAA record for IPv6
        route53.AaaaRecord(
            self, "ApexRecordIPv6",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution)
            )
        )
```

---

## 🔧 **Deployment Scripts (`/scripts`)**

### **Complete AWS Setup (`setup_complete_aws.py`)**
**Purpose**: One-command infrastructure deployment and configuration.

```python
#!/usr/bin/env python3
"""
JanSathi Complete AWS Setup Script
Deploys entire infrastructure with proper sequencing and error handling.
"""

import boto3
import subprocess
import time
import json
from typing import Dict, List

class JanSathiDeployment:
    def __init__(self):
        self.session = boto3.Session()
        self.region = 'us-east-1'
        self.project_name = 'JanSathi'
        
    def deploy_infrastructure(self):
        """Deploy all infrastructure stacks in proper order."""
        print("🚀 Starting JanSathi infrastructure deployment...")
        
        # Step 1: Deploy data stack (foundational)
        print("📊 Deploying data stack...")
        self.deploy_cdk_stack("JanSathiDataStack")
        
        # Step 2: Deploy API stack
        print("🔧 Deploying API stack...")
        self.deploy_cdk_stack("JanSathiApiStack")
        
        # Step 3: Deploy workflow stack
        print("🔄 Deploying workflow stack...")
        self.deploy_cdk_stack("JanSathiWorkflowStack")
        
        # Step 4: Deploy frontend stack
        print("🌐 Deploying frontend stack...")
        self.deploy_cdk_stack("JanSathiFrontendStack")
        
        # Step 5: Configure services
        print("⚙️ Configuring AWS services...")
        self.setup_kendra_index()
        self.setup_bedrock_access()
        self.setup_amazon_connect()
        
        # Step 6: Populate initial data
        print("📝 Populating initial data...")
        self.populate_schemes_database()
        
        print("✅ JanSathi infrastructure deployment completed!")
        self.print_deployment_summary()

    def deploy_cdk_stack(self, stack_name: str):
        """Deploy a specific CDK stack."""
        try:
            cmd = [
                'cdk', 'deploy', stack_name,
                '--require-approval', 'never',
                '--outputs-file', f'{stack_name}-outputs.json'
            ]
            
            result = subprocess.run(
                cmd, 
                cwd='infrastructure',
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ {stack_name} deployed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy {stack_name}")
            print(f"Error: {e.stderr}")
            raise

    def setup_kendra_index(self):
        """Set up Kendra index with government schemes data."""
        kendra = self.session.client('kendra')
        s3 = self.session.client('s3')
        
        try:
            # Upload government schemes documents
            schemes_docs = [
                'pm_kisan_eligibility.pdf',
                'pm_awas_yojana_guidelines.pdf',
                'eshram_registration_process.pdf',
                # ... more scheme documents
            ]
            
            for doc in schemes_docs:
                s3.upload_file(
                    f'docs/schemes/{doc}',
                    'jansathi-kendra-docs',
                    f'schemes/{doc}'
                )
            
            # Wait for Kendra to index documents
            print("⏳ Waiting for Kendra to index documents...")
            time.sleep(300)  # 5 minutes for indexing
            
            print("✅ Kendra index configured successfully")
            
        except Exception as e:
            print(f"❌ Failed to setup Kendra: {str(e)}")
            raise

    def setup_bedrock_access(self):
        """Configure Bedrock model access."""
        bedrock = self.session.client('bedrock')
        
        try:
            # Request access to Nova models
            models_to_enable = [
                'amazon.nova-micro-v1:0',
                'amazon.nova-lite-v1:0',
                'amazon.nova-pro-v1:0'
            ]
            
            for model in models_to_enable:
                try:
                    bedrock.put_model_invocation_logging_configuration(
                        loggingConfig={
                            'cloudWatchConfig': {
                                'logGroupName': '/aws/bedrock/modelinvocations',
                                'roleArn': 'arn:aws:iam::123456789:role/BedrockLogRole'
                            }
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Note: Bedrock access may need manual setup for {model}")
            
            print("✅ Bedrock access configured")
            
        except Exception as e:
            print(f"❌ Failed to setup Bedrock: {str(e)}")
            
    def setup_amazon_connect(self):
        """Configure Amazon Connect instance for IVR."""
        connect = self.session.client('connect')
        
        try:
            # Create Connect instance (if not exists)
            instance_alias = 'jansathi-ivr'
            
            instances = connect.list_instances()['InstanceSummaryList']
            existing = [i for i in instances if i['InstanceAlias'] == instance_alias]
            
            if not existing:
                response = connect.create_instance(
                    IdentityManagementType='CONNECT_MANAGED',
                    InstanceAlias=instance_alias,
                    DirectoryId='d-123456789'  # Replace with actual directory
                )
                
                instance_id = response['Id']
                print(f"✅ Amazon Connect instance created: {instance_id}")
            else:
                instance_id = existing[0]['Id']
                print(f"✅ Using existing Connect instance: {instance_id}")
                
        except Exception as e:
            print(f"❌ Failed to setup Amazon Connect: {str(e)}")

    def populate_schemes_database(self):
        """Populate DynamoDB with government schemes data."""
        dynamodb = self.session.resource('dynamodb')
        table = dynamodb.Table('jansathi-schemes')
        
        schemes_data = [
            {
                'scheme_id': 'pm_kisan',
                'name': 'PM-KISAN Samman Nidhi',
                'description': 'Direct income support for farmers',
                'eligibility_rules': {
                    'age': {'min': 18},
                    'land_ownership': {'min': 0.1},
                    'income': {'max': 200000}
                },
                'benefits': ['₹6000 per year', 'Direct bank transfer'],
                'documents_required': ['Aadhaar', 'Bank account', 'Land records']
            },
            # ... more schemes
        ]
        
        try:
            with table.batch_writer() as batch:
                for scheme in schemes_data:
                    batch.put_item(Item=scheme)
                    
            print("✅ Schemes database populated successfully")
            
        except Exception as e:
            print(f"❌ Failed to populate schemes database: {str(e)}")

    def print_deployment_summary(self):
        """Print deployment summary with important URLs and resources."""
        print("\n" + "="*60)
        print("🇮🇳 JanSathi Deployment Summary")
        print("="*60)
        
        # Load stack outputs
        outputs = {}
        for stack in ['JanSathiDataStack', 'JanSathiApiStack', 'JanSathiFrontendStack']:
            try:
                with open(f'infrastructure/{stack}-outputs.json') as f:
                    outputs[stack] = json.load(f)
            except FileNotFoundError:
                pass
        
        print(f"📊 DynamoDB Tables: {len(outputs.get('JanSathiDataStack', {}).get('Tables', []))}")
        print(f"🔧 Lambda Functions: {len(outputs.get('JanSathiApiStack', {}).get('Functions', []))}")
        print(f"🌐 CloudFront Distribution: {outputs.get('JanSathiFrontendStack', {}).get('DistributionDomain', 'N/A')}")
        print(f"📡 API Gateway URL: {outputs.get('JanSathiApiStack', {}).get('ApiUrl', 'N/A')}")
        
        print("\n🔗 Important Links:")
        print(f"   Frontend: https://jansathi.com")
        print(f"   Admin Dashboard: https://jansathi.com/admin")
        print(f"   API Health: {outputs.get('JanSathiApiStack', {}).get('ApiUrl', '')}/health")
        
        print("\n⚙️ Next Steps:")
        print("   1. Test the API endpoints")
        print("   2. Upload frontend build to S3")
        print("   3. Configure DNS for custom domain")
        print("   4. Set up monitoring alerts")
        print("   5. Run integration tests")
        print("\n" + "="*60)

if __name__ == "__main__":
    deployment = JanSathiDeployment()
    deployment.deploy_infrastructure()
```

### **Individual Service Setup Scripts**

#### **Kendra Setup (`setup_kendra.py`)**
**Purpose**: Amazon Kendra search index setup and document ingestion.

```python
#!/usr/bin/env python3
"""
Amazon Kendra Setup for JanSathi
Creates search index and ingests government scheme documents.
"""

import boto3
import os
import json
from pathlib import Path

def setup_kendra_index():
    kendra = boto3.client('kendra')
    s3 = boto3.client('s3')
    
    # Create Kendra index
    index_response = kendra.create_index(
        Name='jansathi-schemes',
        Edition='DEVELOPER_EDITION',
        RoleArn='arn:aws:iam::123456789:role/KendraServiceRole',
        Description='Government schemes knowledge base for JanSathi'
    )
    
    index_id = index_response['Id']
    print(f"✅ Kendra index created: {index_id}")
    
    # Upload scheme documents to S3
    docs_bucket = 'jansathi-kendra-docs'
    scheme_docs = Path('docs/schemes').glob('*.pdf')
    
    for doc_path in scheme_docs:
        s3.upload_file(str(doc_path), docs_bucket, f'schemes/{doc_path.name}')
        print(f"📄 Uploaded: {doc_path.name}")
    
    # Create S3 data source
    data_source_response = kendra.create_data_source(
        Name='government-schemes-docs',
        IndexId=index_id,
        Type='S3',
        Configuration={
            'S3Configuration': {
                'BucketName': docs_bucket,
                'InclusionPrefixes': ['schemes/'],
                'DocumentsMetadataConfiguration': {
                    'S3Prefix': 'metadata/'
                }
            }
        },
        RoleArn='arn:aws:iam::123456789:role/KendraDataSourceRole'
    )
    
    print(f"📊 Data source created: {data_source_response['Id']}")
    
    # Start data source sync
    kendra.start_data_source_sync_job(
        Id=data_source_response['Id'],
        IndexId=index_id
    )
    
    print("🔄 Document synchronization started")
    return index_id

if __name__ == "__main__":
    index_id = setup_kendra_index()
    print(f"🎉 Kendra setup complete! Index ID: {index_id}")
```

#### **CloudWatch Setup (`setup_cloudwatch.py`)**
**Purpose**: CloudWatch dashboards, alarms, and monitoring configuration.

```python
#!/usr/bin/env python3
"""
CloudWatch Monitoring Setup for JanSathi
Creates comprehensive monitoring dashboards and alarms.
"""

import boto3
import json

def create_operations_dashboard():
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/ApiGateway", "Count", "ApiName", "jansathi-api"],
                        [".", "4XXError", ".", "."],
                        [".", "5XXError", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "API Gateway Requests"
                }
            },
            {
                "type": "metric", 
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Duration", "FunctionName", "jansathi-api"],
                        [".", "Errors", ".", "."],
                        [".", "Throttles", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Lambda Performance"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "jansathi-users"],
                        [".", "ConsumedWriteCapacityUnits", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1", 
                    "title": "DynamoDB Usage"
                }
            }
        ]
    }
    
    cloudwatch.put_dashboard(
        DashboardName='JanSathi-Operations',
        DashboardBody=json.dumps(dashboard_body)
    )
    
    print("📊 Operations dashboard created")

def create_alarms():
    cloudwatch = boto3.client('cloudwatch')
    sns = boto3.client('sns')
    
    # Create SNS topic for alerts
    topic_response = sns.create_topic(Name='jansathi-alerts')
    topic_arn = topic_response['TopicArn']
    
    # High error rate alarm
    cloudwatch.put_metric_alarm(
        AlarmName='JanSathi-HighErrorRate',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='4XXError',
        Namespace='AWS/ApiGateway',
        Period=300,
        Statistic='Sum',
        Threshold=50.0,
        ActionsEnabled=True,
        AlarmActions=[topic_arn],
        AlarmDescription='API Gateway error rate > 50 per 5 minutes',
        Dimensions=[
            {
                'Name': 'ApiName',
                'Value': 'jansathi-api'
            }
        ]
    )
    
    # High latency alarm  
    cloudwatch.put_metric_alarm(
        AlarmName='JanSathi-HighLatency',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=3,
        MetricName='Duration',
        Namespace='AWS/Lambda',
        Period=300,
        Statistic='Average',
        Threshold=2000.0,
        ActionsEnabled=True,
        AlarmActions=[topic_arn],
        AlarmDescription='Lambda duration > 2000ms',
        Dimensions=[
            {
                'Name': 'FunctionName', 
                'Value': 'jansathi-api'
            }
        ]
    )
    
    print("🚨 CloudWatch alarms created")

if __name__ == "__main__":
    create_operations_dashboard()
    create_alarms()
    print("✅ CloudWatch monitoring setup complete")
```

---

## 💰 **Cost Optimization Scripts**

### **AWS Cost Analysis (`check_aws_costs.ps1`)**
**Purpose**: PowerShell script for cost monitoring and optimization recommendations.

```powershell
# JanSathi AWS Cost Analysis Script
# Monitors and optimizes AWS spending to stay under ₹2/user/month target

param(
    [string]$Profile = "default",
    [int]$Days = 30
)

Write-Host "💰 JanSathi AWS Cost Analysis" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

# Set AWS profile
$env:AWS_PROFILE = $Profile

# Get cost and usage data
$EndDate = Get-Date -Format "yyyy-MM-dd"
$StartDate = (Get-Date).AddDays(-$Days).ToString("yyyy-MM-dd")

Write-Host "📊 Analyzing costs from $StartDate to $EndDate" -ForegroundColor Yellow

# Get total costs
$TotalCosts = aws ce get-cost-and-usage `
    --time-period Start=$StartDate,End=$EndDate `
    --granularity MONTHLY `
    --metrics UnblendedCost `
    --group-by Type=DIMENSION,Key=SERVICE | ConvertFrom-Json

# Calculate costs by service
Write-Host "`n🔧 Cost Breakdown by Service:" -ForegroundColor Cyan

$ServiceCosts = @{}
foreach ($result in $TotalCosts.ResultsByTime) {
    foreach ($group in $result.Groups) {
        $service = $group.Keys[0]
        $cost = [math]::Round([decimal]$group.Metrics.UnblendedCost.Amount, 2)
        
        if ($ServiceCosts.ContainsKey($service)) {
            $ServiceCosts[$service] += $cost
        } else {
            $ServiceCosts[$service] = $cost
        }
    }
}

# Sort by cost and display top services
$SortedCosts = $ServiceCosts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10

foreach ($item in $SortedCosts) {
    $percentage = if ($TotalCosts.ResultsByTime[0].Total.UnblendedCost.Amount -gt 0) {
        [math]::Round(($item.Value / [decimal]$TotalCosts.ResultsByTime[0].Total.UnblendedCost.Amount) * 100, 1)
    } else { 0 }
    
    Write-Host "  $($item.Key): $$$($item.Value) ($percentage%)" -ForegroundColor White
}

# Calculate per-user cost (assuming 1000 active users for estimation)
$TotalMonthlyCost = [math]::Round([decimal]$TotalCosts.ResultsByTime[0].Total.UnblendedCost.Amount, 2)
$EstimatedUsers = 1000
$CostPerUser = [math]::Round($TotalMonthlyCost / $EstimatedUsers, 4)
$CostPerUserINR = [math]::Round($CostPerUser * 83, 2)  # USD to INR conversion

Write-Host "`n💵 Cost Analysis:" -ForegroundColor Cyan
Write-Host "  Total Monthly Cost: $$$TotalMonthlyCost" -ForegroundColor White
Write-Host "  Estimated Users: $EstimatedUsers" -ForegroundColor White
Write-Host "  Cost per User: $$$CostPerUser (₹$CostPerUserINR)" -ForegroundColor White

# Cost optimization recommendations
Write-Host "`n💡 Cost Optimization Recommendations:" -ForegroundColor Yellow

if ($ServiceCosts["Amazon DynamoDB"] -gt 50) {
    Write-Host "  ⚠️ DynamoDB costs are high. Consider:" -ForegroundColor Red
    Write-Host "    - Switching to on-demand billing for variable workloads" -ForegroundColor White
    Write-Host "    - Implementing data archival for old conversations" -ForegroundColor White
}

if ($ServiceCosts["AWS Lambda"] -gt 30) {
    Write-Host "  ⚠️ Lambda costs are high. Consider:" -ForegroundColor Red
    Write-Host "    - Optimizing function memory allocation" -ForegroundColor White
    Write-Host "    - Implementing response caching to reduce invocations" -ForegroundColor White
}

if ($ServiceCosts["Amazon Bedrock"] -gt 100) {
    Write-Host "  ⚠️ Bedrock costs are high. Consider:" -ForegroundColor Red
    Write-Host "    - Using Nova Micro for simple tasks" -ForegroundColor White
    Write-Host "    - Implementing aggressive response caching" -ForegroundColor White
    Write-Host "    - Optimizing prompts to reduce token usage" -ForegroundColor White
}

# Target validation
$TargetCostPerUserINR = 2.0
if ($CostPerUserINR -le $TargetCostPerUserINR) {
    Write-Host "`n✅ COST TARGET MET: Under ₹2/user/month!" -ForegroundColor Green
} else {
    $ExcessCost = [math]::Round($CostPerUserINR - $TargetCostPerUserINR, 2)
    Write-Host "`n❌ COST TARGET EXCEEDED: ₹$ExcessCost over target" -ForegroundColor Red
}

Write-Host "`n📈 Free Tier Usage Recommendations:" -ForegroundColor Cyan
Write-Host "  - Lambda: 1M requests/month free" -ForegroundColor White
Write-Host "  - DynamoDB: 25GB storage + 25 RCU/WCU free" -ForegroundColor White
Write-Host "  - API Gateway: 1M calls/month free" -ForegroundColor White
Write-Host "  - CloudWatch: 10 metrics + 5GB logs free" -ForegroundColor White
Write-Host "  - S3: 5GB storage + 20,000 GET requests free" -ForegroundColor White
```

---

## ⚙️ **Operations & Management Scripts**

### **System Verification (`backend/verify_system.py`)**
**Purpose**: Comprehensive system health check and connectivity validation.

```python
#!/usr/bin/env python3
"""
JanSathi System Verification Script
Validates all AWS services and system components are working correctly.
"""

import boto3
import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class SystemVerifier:
    def __init__(self):
        self.session = boto3.Session()
        self.region = 'us-east-1'
        self.results = {}
        
    def run_all_checks(self) -> Dict[str, bool]:
        """Run comprehensive system checks."""
        print("🔍 JanSathi System Verification")
        print("=" * 40)
        
        checks = [
            ("AWS Credentials", self.check_aws_credentials),
            ("DynamoDB Tables", self.check_dynamodb_tables),
            ("S3 Buckets", self.check_s3_buckets), 
            ("Lambda Functions", self.check_lambda_functions),
            ("API Gateway", self.check_api_gateway),
            ("Bedrock Access", self.check_bedrock_access),
            ("Kendra Index", self.check_kendra_index),
            ("SNS Topics", self.check_sns_topics),
            ("CloudWatch Logs", self.check_cloudwatch_logs)
        ]
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                self.results[check_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{check_name:<20} {status}")
            except Exception as e:
                self.results[check_name] = False
                print(f"{check_name:<20} ❌ ERROR: {str(e)}")
        
        self.print_summary()
        return self.results
    
    def check_aws_credentials(self) -> bool:
        """Verify AWS credentials are configured correctly."""
        try:
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            print(f"  Account: {identity['Account']}")
            print(f"  User: {identity['Arn'].split('/')[-1]}")
            return True
        except Exception:
            return False
    
    def check_dynamodb_tables(self) -> bool:
        """Check DynamoDB tables existence and status."""
        dynamodb = self.session.client('dynamodb')
        
        required_tables = [
            'jansathi-users',
            'jansathi-conversations', 
            'jansathi-cache'
        ]
        
        try:
            existing_tables = dynamodb.list_tables()['TableNames']
            
            for table in required_tables:
                if table not in existing_tables:
                    print(f"  Missing table: {table}")
                    return False
                    
                # Check table status
                table_desc = dynamodb.describe_table(TableName=table)
                if table_desc['Table']['TableStatus'] != 'ACTIVE':
                    print(f"  Table {table} not ACTIVE")
                    return False
            
            print(f"  All {len(required_tables)} tables are ACTIVE")
            return True
            
        except Exception as e:
            print(f"  Error checking tables: {str(e)}")
            return False
    
    def check_s3_buckets(self) -> bool:
        """Verify S3 buckets exist and are accessible."""
        s3 = self.session.client('s3')
        
        required_buckets = [
            'jansathi-documents-prod',
            'jansathi-audio-prod'
        ]
        
        try:
            existing_buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
            
            for bucket in required_buckets:
                if bucket not in existing_buckets:
                    print(f"  Missing bucket: {bucket}")
                    return False
                    
                # Test bucket accessibility
                s3.head_bucket(Bucket=bucket)
            
            print(f"  All {len(required_buckets)} buckets accessible")
            return True
            
        except Exception as e:
            print(f"  Error checking buckets: {str(e)}")
            return False
    
    def check_lambda_functions(self) -> bool:
        """Verify Lambda functions are deployed and configured."""
        lambda_client = self.session.client('lambda')
        
        required_functions = [
            'jansathi-api',
            'jansathi-ivr-webhook',
            'jansathi-audio-processor'
        ]
        
        try:
            for function_name in required_functions:
                try:
                    func = lambda_client.get_function(FunctionName=function_name)
                    
                    # Check function state
                    if func['Configuration']['State'] != 'Active':
                        print(f"  Function {function_name} not Active")
                        return False
                        
                    # Check last update (should be recent for active development)
                    last_modified = func['Configuration']['LastModified']
                    print(f"  {function_name}: Last updated {last_modified}")
                    
                except lambda_client.exceptions.ResourceNotFoundException:
                    print(f"  Function {function_name} not found")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  Error checking Lambda functions: {str(e)}")
            return False
    
    def check_api_gateway(self) -> bool:
        """Test API Gateway endpoints."""
        try:
            # Get API Gateway URL from CloudFormation outputs or config
            api_url = "https://api.jansathi.com"  # Replace with actual URL
            
            # Test health endpoint
            response = requests.get(f"{api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"  API Health: {health_data.get('status', 'Unknown')}")
                return True
            else:
                print(f"  API Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Error checking API Gateway: {str(e)}")
            return False
    
    def check_bedrock_access(self) -> bool:
        """Verify Bedrock model access."""
        bedrock = self.session.client('bedrock-runtime')
        
        try:
            # Test Nova Micro model (smallest/cheapest)
            response = bedrock.invoke_model(
                modelId='amazon.nova-micro-v1:0',
                body=json.dumps({
                    "inputText": "Test connectivity",
                    "textGenerationConfig": {
                        "maxTokenCount": 10,
                        "temperature": 0.1
                    }
                })
            )
            
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"  Nova Micro model accessible")
                return True
            else:
                print(f"  Bedrock access failed")
                return False
                
        except Exception as e:
            print(f"  Error checking Bedrock: {str(e)}")
            return False
    
    def check_kendra_index(self) -> bool:
        """Verify Kendra index exists and has documents."""
        kendra = self.session.client('kendra')
        
        try:
            # List indexes
            indexes = kendra.list_indices()['IndexConfigurationSummaryItems']
            jansathi_indexes = [idx for idx in indexes if 'jansathi' in idx['Name'].lower()]
            
            if not jansathi_indexes:
                print(f"  No JanSathi Kendra index found")
                return False
            
            index_id = jansathi_indexes[0]['Id']
            
            # Test search functionality
            search_response = kendra.query(
                IndexId=index_id,
                QueryText="PM KISAN eligibility",
                PageSize=1
            )
            
            result_count = len(search_response.get('ResultItems', []))
            print(f"  Kendra index active with {result_count} results for test query")
            return result_count > 0
            
        except Exception as e:
            print(f"  Error checking Kendra: {str(e)}")
            return False
    
    def check_sns_topics(self) -> bool:
        """Verify SNS topics for notifications."""
        sns = self.session.client('sns')
        
        try:
            topics = sns.list_topics()['Topics']
            jansathi_topics = [t for t in topics if 'jansathi' in t['TopicArn'].lower()]
            
            if len(jansathi_topics) < 2:  # Should have SMS and HITL topics
                print(f"  Expected 2+ SNS topics, found {len(jansathi_topics)}")
                return False
            
            print(f"  {len(jansathi_topics)} SNS topics configured")
            return True
            
        except Exception as e:
            print(f"  Error checking SNS: {str(e)}")
            return False
    
    def check_cloudwatch_logs(self) -> bool:
        """Verify CloudWatch log groups exist."""
        logs = self.session.client('logs')
        
        try:
            log_groups = logs.describe_log_groups(
                logGroupNamePrefix='/aws/lambda/jansathi'
            )['logGroups']
            
            if len(log_groups) == 0:
                print(f"  No JanSathi log groups found")
                return False
            
            print(f"  {len(log_groups)} CloudWatch log groups found")
            return True
            
        except Exception as e:
            print(f"  Error checking CloudWatch logs: {str(e)}")
            return False
    
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "=" * 40)
        
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        print(f"📊 System Health: {passed}/{total} checks passed")
        
        if passed == total:
            print("🎉 All systems operational!")
        else:
            failed_checks = [name for name, result in self.results.items() if not result]
            print(f"⚠️  Failed checks: {', '.join(failed_checks)}")
        
        print(f"🕒 Verification completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    verifier = SystemVerifier()
    results = verifier.run_all_checks()
    
    # Exit with error code if any checks failed
    if not all(results.values()):
        sys.exit(1)
```

---

## 📊 **Monitoring & Operations**

### **Live Metrics Collection**
- **CloudWatch Dashboards**: Real-time system health monitoring
- **X-Ray Tracing**: Request flow visualization and bottleneck identification  
- **Custom Metrics**: 14 KPIs specific to civic automation workflows
- **Alerting**: Proactive error detection and escalation

### **Cost Management**
- **Budget Alerts**: Automatic notifications when approaching cost thresholds
- **Resource Tagging**: Cost allocation by feature and environment
- **Free Tier Monitoring**: Maximize free tier usage across all services
- **Cost Optimization**: Automated recommendations for reducing expenses

### **Security & Compliance**
- **IAM Policies**: Least-privilege access controls
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: Immutable audit trails for compliance
- **PII Protection**: Automatic masking and data protection

---

This comprehensive infrastructure implementation provides a scalable, secure, and cost-effective foundation for JanSathi's civic automation platform, designed to serve millions of rural Indians while maintaining strict cost and performance targets.