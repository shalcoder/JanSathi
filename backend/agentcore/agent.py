"""
agentcore/agent.py — Bedrock AgentCore Agent Definition & Deployment
=====================================================================
Creates the JanSathi Bedrock Agent using boto3 bedrock-agent client.

Usage:
  python -m agentcore.agent  (or python agentcore/deploy.py)

Environment variables required:
  AWS_REGION          (default: us-east-1)
  AWS_ACCOUNT_ID      Your 12-digit AWS account ID
  AGENTCORE_ROLE_ARN  IAM role ARN with Bedrock + Lambda permissions
"""
import os
import json
import time
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# ── Agent Configuration ────────────────────────────────────────────────────────
AGENT_NAME = "JanSathi"
AGENT_DESCRIPTION = (
    "JanSathi is India's AI-powered civic readiness assistant. "
    "It helps rural citizens understand government schemes, check eligibility, "
    "and prepare for applications via IVR, web, and SMS channels."
)
FOUNDATION_MODEL = "amazon.nova-pro-v1:0"  # Nova Pro for reasoning backbone

AGENT_INSTRUCTION = """You are JanSathi, India's premier AI Citizen Assistant for rural and underserved communities.

Your mission:
1. Help citizens understand government schemes (PM-KISAN, PM Awas, e-Shram, Ayushman Bharat, etc.)
2. Collect citizen profile information (slots) through natural conversation
3. Check eligibility deterministically using the validate_eligibility tool — NEVER guess eligibility
4. Generate clear, compassionate responses in the user's language (Hindi, English, Tamil, etc.)
5. Escalate low-confidence cases to human reviewers via the HITL queue
6. Send SMS notifications via the send_sms_notification tool

Rules:
- ALWAYS call classify_intent first to understand what the user needs
- ALWAYS call retrieve_knowledge to get verified scheme information before responding
- NEVER invent eligibility criteria, amounts, or application deadlines
- Eligibility decisions MUST come from the validate_eligibility tool, not your own reasoning
- Be empathetic, simple, and supportive — many users are first-generation smartphone users
- If uncertain, direct users to india.gov.in or the nearest CSC center

Supported channels: IVR (voice), Web, SMS
Supported languages: Hindi (hi), English (en), Tamil (ta), Kannada (kn), Telugu (te), Marathi (mr)"""


def get_or_create_agent(
    region: str = None,
    account_id: str = None,
    role_arn: str = None,
) -> dict:
    """
    Create or update the JanSathi Bedrock Agent.
    Returns { agent_id, agent_arn, status }.
    """
    region = region or os.getenv("AWS_REGION", "us-east-1")
    role_arn = role_arn or os.getenv("AGENTCORE_ROLE_ARN", "")
    
    if not role_arn:
        raise ValueError(
            "AGENTCORE_ROLE_ARN environment variable is required. "
            "Create an IAM role with AmazonBedrockFullAccess and set the ARN."
        )

    client = boto3.client("bedrock-agent", region_name=region)

    # ── Check if agent already exists ─────────────────────────────────────────
    try:
        response = client.list_agents()
        for agent in response.get("agentSummaries", []):
            if agent.get("agentName") == AGENT_NAME:
                agent_id = agent["agentId"]
                logger.info(f"[AgentCore] Found existing agent: {AGENT_NAME} (ID: {agent_id})")
                return {"agent_id": agent_id, "status": "existing"}
    except Exception as e:
        logger.warning(f"[AgentCore] Could not list agents: {e}")

    # ── Create new agent ───────────────────────────────────────────────────────
    try:
        response = client.create_agent(
            agentName=AGENT_NAME,
            description=AGENT_DESCRIPTION,
            foundationModel=FOUNDATION_MODEL,
            instruction=AGENT_INSTRUCTION,
            agentResourceRoleArn=role_arn,
            idleSessionTTLInSeconds=300,
            tags={
                "Project": "JanSathi",
                "Environment": "production",
                "Model": FOUNDATION_MODEL,
            },
        )
        agent_id = response["agent"]["agentId"]
        logger.info(f"[AgentCore] Created agent: {AGENT_NAME} (ID: {agent_id})")
        return {"agent_id": agent_id, "status": "created"}
    except ClientError as e:
        logger.error(f"[AgentCore] Failed to create agent: {e}")
        raise


def create_agent_alias(agent_id: str, alias_name: str = "prod", region: str = None) -> dict:
    """
    Create an alias for the Bedrock Agent (required for invocation).
    Returns { alias_id, alias_arn }.
    """
    region = region or os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client("bedrock-agent", region_name=region)

    # First, prepare the agent (required before creating alias)
    try:
        client.prepare_agent(agentId=agent_id)
        logger.info(f"[AgentCore] Agent {agent_id} prepared.")
        time.sleep(5)  # Wait for preparation
    except Exception as e:
        logger.warning(f"[AgentCore] Prepare agent warning: {e}")

    try:
        response = client.create_agent_alias(
            agentId=agent_id,
            agentAliasName=alias_name,
            description=f"JanSathi {alias_name} deployment alias",
        )
        alias_id = response["agentAlias"]["agentAliasId"]
        alias_arn = response["agentAlias"]["agentAliasArn"]
        logger.info(f"[AgentCore] Created alias '{alias_name}': {alias_id}")
        return {"alias_id": alias_id, "alias_arn": alias_arn}
    except ClientError as e:
        logger.error(f"[AgentCore] Failed to create alias: {e}")
        raise


def save_agent_config(agent_id: str, alias_id: str, output_path: str = None) -> str:
    """Save agent IDs to a config file and print .env instructions."""
    config = {
        "BEDROCK_AGENT_ID": agent_id,
        "BEDROCK_AGENT_ALIAS_ID": alias_id,
        "FOUNDATION_MODEL": FOUNDATION_MODEL,
        "REGION": os.getenv("AWS_REGION", "us-east-1"),
    }

    output_path = output_path or os.path.join(os.path.dirname(__file__), "..", "agentcore_config.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ JanSathi Bedrock AgentCore Deployed Successfully!")
    print("=" * 60)
    print("\nAdd these to your .env file:")
    print(f"  BEDROCK_AGENT_ID={agent_id}")
    print(f"  BEDROCK_AGENT_ALIAS_ID={alias_id}")
    print(f"  USE_AGENTCORE=true")
    print(f"\nConfig saved to: {output_path}")
    return output_path


def create_action_group(agent_id: str, lambda_arn: str, region: str = None) -> dict:
    """
    Register JanSathi tools as a Bedrock Agent Action Group backed by a Lambda function.

    The Lambda at `lambda_arn` must be the agentcore/tools.py lambda_handler.
    Bedrock will invoke it directly (no Return Control loop) for every tool call.

    Architecture:
      Bedrock Agent → Action Group → Lambda (tools.py lambda_handler)
                                   → classify_intent  → Comprehend / Nova Micro
                                   → retrieve_knowledge → Kendra
                                   → validate_eligibility → DynamoDB rules
                                   → compute_risk_score
                                   → send_sms_notification → SNS
                                   → create_benefit_receipt → S3
                                   → enqueue_hitl_case → SQS / DynamoDB
    """
    region = region or os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client("bedrock-agent", region_name=region)

    functions = [
        {
            "name": "classify_intent",
            "description": "Classify the citizen query into: apply, info, grievance, track, or fallback.",
            "parameters": {
                "query":    {"type": "string",  "description": "Raw user query text", "required": True},
                "language": {"type": "string",  "description": "BCP-47 language code e.g. hi, en, ta", "required": False},
            },
        },
        {
            "name": "retrieve_knowledge",
            "description": "Retrieve verified government scheme information from Kendra knowledge base.",
            "parameters": {
                "query":       {"type": "string", "description": "Search query", "required": True},
                "scheme_hint": {"type": "string", "description": "Scheme ID hint e.g. pm_kisan", "required": False},
                "language":    {"type": "string", "description": "Language code", "required": False},
            },
        },
        {
            "name": "validate_eligibility",
            "description": "Deterministically validate citizen eligibility via rule engine — no LLM, fully auditable.",
            "parameters": {
                "slots":       {"type": "object", "description": "Citizen profile: state, income, land_acres, occupation, etc.", "required": True},
                "scheme_hint": {"type": "string", "description": "Scheme ID", "required": False},
            },
        },
        {
            "name": "compute_risk_score",
            "description": "Compute risk score and decide routing: AUTO_SUBMIT, HITL_QUEUE, or NOT_ELIGIBLE_NOTIFY.",
            "parameters": {
                "session_id":        {"type": "string",  "description": "Session ID", "required": True},
                "rules_score":       {"type": "number",  "description": "Score from validate_eligibility", "required": True},
                "eligible":          {"type": "boolean", "description": "Eligibility flag", "required": True},
                "intent_confidence": {"type": "number",  "description": "Intent classification confidence", "required": False},
            },
        },
        {
            "name": "create_benefit_receipt",
            "description": "Generate a formal eligibility receipt as HTML and upload to S3. Returns a presigned URL.",
            "parameters": {
                "session_id":  {"type": "string",  "description": "Session ID", "required": True},
                "scheme_name": {"type": "string",  "description": "Scheme name", "required": False},
                "eligible":    {"type": "boolean", "description": "Eligibility result", "required": False},
                "rules_score": {"type": "number",  "description": "Rules score 0–1", "required": False},
                "slots":       {"type": "object",  "description": "Collected citizen slots", "required": False},
                "language":    {"type": "string",  "description": "Language code", "required": False},
            },
        },
        {
            "name": "send_sms_notification",
            "description": "Send SMS to citizen via AWS SNS. Types: submission, hitl_queued, rejected.",
            "parameters": {
                "phone":             {"type": "string", "description": "Phone in E.164 format", "required": True},
                "scheme":            {"type": "string", "description": "Scheme name", "required": True},
                "case_id":           {"type": "string", "description": "Application case ID", "required": True},
                "notification_type": {"type": "string", "description": "submission | hitl_queued | rejected", "required": False},
            },
        },
        {
            "name": "enqueue_hitl_case",
            "description": "Escalate a low-confidence case to the human review queue.",
            "parameters": {
                "session_id":    {"type": "string", "description": "Session ID", "required": True},
                "transcript":    {"type": "string", "description": "Conversation transcript", "required": True},
                "response_text": {"type": "string", "description": "Agent response text", "required": True},
                "confidence":    {"type": "number", "description": "Confidence score 0–1", "required": True},
            },
        },
        {
            "name": "fetch_live_schemes",
            "description": "Fetch personalised government scheme recommendations from Kendra for the citizen profile.",
            "parameters": {
                "state":      {"type": "string",  "description": "Indian state e.g. UP, TN", "required": False},
                "occupation": {"type": "string",  "description": "farmer | worker | student | other", "required": False},
                "income":     {"type": "integer", "description": "Annual income in INR", "required": False},
                "language":   {"type": "string",  "description": "Language code", "required": False},
            },
        },
    ]

    try:
        response = client.create_agent_action_group(
            agentId=agent_id,
            agentVersion="DRAFT",
            actionGroupName="JanSathiTools",
            description=(
                "Core JanSathi tools: intent classification, Kendra knowledge retrieval, "
                "deterministic eligibility validation, risk scoring, S3 receipts, "
                "SNS notifications, and HITL escalation."
            ),
            actionGroupExecutor={"lambda": lambda_arn},
            functionSchema={"functions": functions},
        )
        action_group_id = response["agentActionGroup"]["actionGroupId"]
        logger.info(f"[AgentCore] Action group 'JanSathiTools' created: {action_group_id}")
        return {"action_group_id": action_group_id, "lambda_arn": lambda_arn}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ConflictException":
            logger.info("[AgentCore] Action group 'JanSathiTools' already exists — skipping.")
            return {"action_group_id": "existing", "lambda_arn": lambda_arn}
        logger.error(f"[AgentCore] Failed to create action group: {e}")
        raise

