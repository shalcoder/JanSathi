"""
agentcore/deploy.py — JanSathi Bedrock AgentCore Deployment Script
===================================================================
Run this script to deploy the JanSathi agent to Bedrock AgentCore.

Prerequisites:
  1. AWS credentials configured (aws configure or IAM role)
  2. AmazonBedrockFullAccess policy on your IAM user/role
  3. Bedrock AgentCore enabled in your AWS region (us-east-1 recommended)
  4. AGENTCORE_ROLE_ARN environment variable set

Usage:
  cd e:\\JanSathi\\backend
  python -m agentcore.deploy

  # Or from the backend directory:
  python agentcore/deploy.py
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def deploy():
    print("=" * 60)
    print("JanSathi — AWS-Native Bedrock AgentCore Deployment")
    print("=" * 60)
    print()
    print("Architecture being deployed:")
    print("  Citizen → API Gateway → Lambda (Flask) → Bedrock AgentCore")
    print("            → Action Group Lambda (tools.py)")
    print("              → classify_intent   → Nova Micro / Comprehend")
    print("              → retrieve_knowledge → Kendra")
    print("              → validate_eligibility → DynamoDB rules engine")
    print("              → compute_risk_score")
    print("              → create_benefit_receipt → S3")
    print("              → send_sms_notification → SNS")
    print("              → enqueue_hitl_case → SQS / DynamoDB")
    print()

    # ── Pre-flight checks ──────────────────────────────────────────────────────
    region = os.getenv("AWS_REGION", "us-east-1")
    role_arn = os.getenv("AGENTCORE_ROLE_ARN", "")
    lambda_arn = os.getenv("ACTION_GROUP_LAMBDA_ARN", "")

    print(f"Region     : {region}")
    print(f"Agent Role : {role_arn or '❌ NOT SET'}")
    print(f"Tools Lambda: {lambda_arn or '⚠️  NOT SET — action group will be skipped'}")

    if not role_arn:
        print("\n❌ ERROR: AGENTCORE_ROLE_ARN is required.")
        print("  1. IAM → Roles → Create Role → Trusted entity: bedrock.amazonaws.com")
        print("  2. Attach: AmazonBedrockFullAccess, AWSLambdaRole")
        print("  3. Set: AGENTCORE_ROLE_ARN=arn:aws:iam::ACCOUNT:role/ROLE_NAME")
        sys.exit(1)

    # ── Import deployment modules ─────────────────────────────────────────────
    try:
        from agentcore.agent import get_or_create_agent, create_agent_alias, save_agent_config, create_action_group
    except ImportError:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agentcore.agent import get_or_create_agent, create_agent_alias, save_agent_config, create_action_group

    # ── Step 1: Create/get agent ───────────────────────────────────────────────
    print("\n[1/4] Creating/verifying Bedrock Agent...")
    agent_info = get_or_create_agent(region=region, role_arn=role_arn)
    agent_id = agent_info["agent_id"]
    status = agent_info["status"]
    print(f"  ✅ Agent ID: {agent_id} ({status})")

    # ── Step 2: Register Action Group (tools Lambda) ───────────────────────────
    if lambda_arn:
        print("\n[2/4] Registering Action Group (JanSathiTools → Lambda)...")
        ag_info = create_action_group(agent_id=agent_id, lambda_arn=lambda_arn, region=region)
        print(f"  ✅ Action Group ID: {ag_info['action_group_id']}")
        print(f"     Tools Lambda   : {lambda_arn}")
    else:
        print("\n[2/4] ⚠️  Skipping Action Group — ACTION_GROUP_LAMBDA_ARN not set.")
        print("        Deploy agentcore/tools.py as a Lambda first, then re-run with:")
        print("        ACTION_GROUP_LAMBDA_ARN=arn:aws:lambda:... python -m agentcore.deploy")

    # ── Step 3: Create production alias (auto-prepares agent first) ────────────
    print("\n[3/4] Creating production alias...")
    alias_info = create_agent_alias(agent_id=agent_id, alias_name="prod", region=region)
    alias_id = alias_info["alias_id"]
    print(f"  ✅ Alias ID: {alias_id}")

    # ── Step 4: Save config ───────────────────────────────────────────────────
    print("\n[4/4] Saving deployment config...")
    config_path = save_agent_config(agent_id, alias_id)

    print(f"\n✅ Deployment complete!")
    print(f"   Config: {config_path}")
    print(f"\nAdd to backend/.env:")
    print(f"  BEDROCK_AGENT_ID={agent_id}")
    print(f"  BEDROCK_AGENT_ALIAS_ID={alias_id}")
    print(f"  USE_AGENTCORE=true")
    if lambda_arn:
        print(f"  ACTION_GROUP_LAMBDA_ARN={lambda_arn}")
    else:
        print(f"  ACTION_GROUP_LAMBDA_ARN=<deploy tools.py Lambda and set this>")



if __name__ == "__main__":
    deploy()
