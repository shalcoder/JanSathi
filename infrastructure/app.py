#!/usr/bin/env python3
"""
JanSathi CDK App — Production Infrastructure
Deploys: API Gateway + Lambda + WAF + DynamoDB + S3 + CloudFront
"""
import aws_cdk as cdk
from stacks.data_stack import DataStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack
from stacks.workflow_stack import WorkflowStack

app = cdk.App()

# Environment (Mumbai region for India-focused app)
env = cdk.Environment(
    region=app.node.try_get_context("region") or "us-east-1"
)

# ============================================================
# Stack 1: Data Layer (DynamoDB + S3)
# ============================================================
data_stack = DataStack(app, "JanSathi-Data", env=env)

# ============================================================
# Stack 2: Workflow Layer (Step Functions)
# ============================================================
workflow_stack = WorkflowStack(app, "JanSathi-Workflow", env=env)

# ============================================================
# Stack 3: API Layer (Lambda + API Gateway + WAF)
# ============================================================
api_stack = ApiStack(
    app, "JanSathi-API",
    users_table=data_stack.users_table,
    conversations_table=data_stack.conversations_table,
    cache_table=data_stack.cache_table,
    audio_bucket=data_stack.audio_bucket,
    uploads_bucket=data_stack.uploads_bucket,
    kendra_index=data_stack.kendra_index,
    notifications_topic=data_stack.notifications_topic,
    state_machine_arn=workflow_stack.state_machine.state_machine_arn, # Pass SFN ARN
    env=env,
)
api_stack.add_dependency(data_stack)
api_stack.add_dependency(workflow_stack)

# ============================================================
# Stack 4: Frontend (S3 + CloudFront)
# ============================================================
frontend_stack = FrontendStack(
    app, "JanSathi-Frontend",
    api_url=api_stack.api_url,
    env=env,
)
frontend_stack.add_dependency(api_stack)

# Tags for cost tracking
for stack in [data_stack, workflow_stack, api_stack, frontend_stack]:
    cdk.Tags.of(stack).add("Project", "JanSathi")
    cdk.Tags.of(stack).add("Environment", "Production")
    cdk.Tags.of(stack).add("CostCenter", "Hackathon")

app.synth()
