#!/usr/bin/env python3
"""
JanSathi CDK App — Production Infrastructure
Deploys: MessagingStack → DataStack → WorkflowStack → ApiStack → FrontendStack

Stack dependency order:
  MessagingStack  (SQS + EventBridge + Cognito)
  DataStack       (DynamoDB + S3 + Kendra + SNS)
  WorkflowStack   (Step Functions + task Lambdas + EventBridge rule)
  ApiStack        (Lambda + API Gateway + WAF + X-Ray)
  FrontendStack   (S3 + CloudFront)
"""
import os
import aws_cdk as cdk
from stacks.data_stack import DataStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack
from stacks.workflow_stack import WorkflowStack
from stacks.messaging_stack import MessagingStack

app = cdk.App()

# Environment (default us-east-1; override via --context region=ap-south-1)
env = cdk.Environment(
    region=app.node.try_get_context("region") or "us-east-1",
    account=app.node.try_get_context("account") or os.getenv("CDK_DEFAULT_ACCOUNT"),
)

# Bedrock agent IDs (pass in via context or env for security)
bedrock_agent_id       = app.node.try_get_context("bedrockAgentId")       or os.getenv("BEDROCK_AGENT_ID",       "")
bedrock_agent_alias_id = app.node.try_get_context("bedrockAgentAliasId")  or os.getenv("BEDROCK_AGENT_ALIAS_ID",  "")

# ============================================================
# Stack 1: Messaging (SQS FIFO + EventBridge + Cognito)
# ============================================================
messaging_stack = MessagingStack(app, "JanSathi-Messaging", env=env)

# ============================================================
# Stack 2: Data Layer (DynamoDB + S3 + Kendra + SNS)
# ============================================================
data_stack = DataStack(app, "JanSathi-Data", env=env)
data_stack.add_dependency(messaging_stack)

# ============================================================
# Stack 3: Workflow Layer (Step Functions + EventBridge rule)
# ============================================================
workflow_stack = WorkflowStack(
    app, "JanSathi-Workflow",
    hitl_table=data_stack.hitl_table,
    event_bus=messaging_stack.event_bus,
    env=env,
)
workflow_stack.add_dependency(data_stack)
workflow_stack.add_dependency(messaging_stack)

# ============================================================
# Stack 4: API Layer (Lambda + API Gateway + WAF + X-Ray)
# ============================================================
api_stack = ApiStack(
    app, "JanSathi-API",
    users_table=data_stack.users_table,
    conversations_table=data_stack.conversations_table,
    cache_table=data_stack.cache_table,
    hitl_table=data_stack.hitl_table,
    audio_bucket=data_stack.audio_bucket,
    uploads_bucket=data_stack.uploads_bucket,
    kendra_index=data_stack.kendra_index,
    notifications_topic=data_stack.notifications_topic,
    hitl_queue=messaging_stack.hitl_queue,
    event_bus=messaging_stack.event_bus,
    user_pool=messaging_stack.user_pool,
    state_machine_arn=workflow_stack.state_machine.state_machine_arn,
    bedrock_agent_id=bedrock_agent_id,
    bedrock_agent_alias_id=bedrock_agent_alias_id,
    env=env,
)
api_stack.add_dependency(data_stack)
api_stack.add_dependency(workflow_stack)
api_stack.add_dependency(messaging_stack)

# ============================================================
# Stack 5: Frontend (S3 + CloudFront)
# ============================================================
frontend_stack = FrontendStack(
    app, "JanSathi-Frontend",
    api_url=api_stack.api_url,
    env=env,
)
frontend_stack.add_dependency(api_stack)

# Cost-tracking tags
for stack in [messaging_stack, data_stack, workflow_stack, api_stack, frontend_stack]:
    cdk.Tags.of(stack).add("Project",     "JanSathi")
    cdk.Tags.of(stack).add("Environment", "Production")
    cdk.Tags.of(stack).add("CostCenter",  "Hackathon")

app.synth()

