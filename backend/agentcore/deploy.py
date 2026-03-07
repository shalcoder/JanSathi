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
    print("🚀 JanSathi Bedrock AgentCore Deployment")
    print("=" * 60)

    # ── Pre-flight checks ──────────────────────────────────────────────────────
    region = os.getenv("AWS_REGION", "us-east-1")
    role_arn = os.getenv("AGENTCORE_ROLE_ARN", "")

    print(f"\nRegion : {region}")
    print(f"Role   : {role_arn or '❌ NOT SET'}")

    if not role_arn:
        print("\n❌ ERROR: AGENTCORE_ROLE_ARN is required.")
        print("Steps to create the role:")
        print("  1. Go to AWS Console → IAM → Roles → Create Role")
        print("  2. Trusted entity: bedrock.amazonaws.com")
        print("  3. Attach policy: AmazonBedrockFullAccess")
        print("  4. Set env: AGENTCORE_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT:role/ROLE_NAME")
        sys.exit(1)

    # ── Import deployment modules ─────────────────────────────────────────────
    try:
        from agentcore.agent import get_or_create_agent, create_agent_alias, save_agent_config
    except ImportError:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agentcore.agent import get_or_create_agent, create_agent_alias, save_agent_config

    # ── Step 1: Create/get agent ───────────────────────────────────────────────
    print("\n[1/3] Creating/verifying Bedrock Agent...")
    agent_info = get_or_create_agent(region=region, role_arn=role_arn)
    agent_id = agent_info["agent_id"]
    status = agent_info["status"]
    print(f"  ✅ Agent ID: {agent_id} ({status})")

    # ── Step 2: Create production alias ───────────────────────────────────────
    print("\n[2/3] Creating production alias...")
    alias_info = create_agent_alias(agent_id=agent_id, alias_name="prod", region=region)
    alias_id = alias_info["alias_id"]
    print(f"  ✅ Alias ID: {alias_id}")

    # ── Step 3: Save config ───────────────────────────────────────────────────
    print("\n[3/3] Saving deployment config...")
    config_path = save_agent_config(agent_id, alias_id)

    print(f"\n✅ Deployment complete!")
    print(f"   Config: {config_path}")
    print(f"\nNext steps:")
    print(f"  1. Add BEDROCK_AGENT_ID={agent_id} to backend/.env")
    print(f"  2. Add BEDROCK_AGENT_ALIAS_ID={alias_id} to backend/.env")
    print(f"  3. Add USE_AGENTCORE=true to backend/.env")
    print(f"  4. Restart the backend server")


if __name__ == "__main__":
    deploy()
