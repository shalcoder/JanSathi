#!/usr/bin/env python3
"""
JanSathi CDK App — Production Infrastructure
Deploys: API Gateway + Lambda + WAF + DynamoDB + S3 + CloudFront
"""
import aws_cdk as cdk
from stacks.data_stack import DataStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack

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
# Stack 2: API Layer (Lambda + API Gateway + WAF)
# ============================================================
api_stack = ApiStack(
    app, "JanSathi-API",
    conversations_table=data_stack.conversations_table,
    cache_table=data_stack.cache_table,
    audio_bucket=data_stack.audio_bucket,
    uploads_bucket=data_stack.uploads_bucket,
    env=env,
)
api_stack.add_dependency(data_stack)

# ============================================================
# Stack 3: Frontend (S3 + CloudFront)
# ============================================================
frontend_stack = FrontendStack(
    app, "JanSathi-Frontend",
    api_url=api_stack.api_url,
    env=env,
)
frontend_stack.add_dependency(api_stack)

# Tags for cost tracking
for stack in [data_stack, api_stack, frontend_stack]:
    cdk.Tags.of(stack).add("Project", "JanSathi")
    cdk.Tags.of(stack).add("Environment", "Production")
    cdk.Tags.of(stack).add("CostCenter", "Hackathon")

app.synth()
