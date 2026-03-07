"""
agentcore/invoke.py — Bedrock AgentCore Invocation Wrapper
==========================================================
Wraps the Bedrock Agent invoke_agent API for use by the Flask routes.
Handles multi-turn sessions via session_id continuity.

Used when USE_AGENTCORE=true in .env (production mode).
When USE_AGENTCORE=false, the Flask API uses the local LangGraph supervisor directly.
"""
import os
import json
import logging
import uuid

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# ── AgentCore Configuration ────────────────────────────────────────────────────
AGENT_ID = os.getenv("BEDROCK_AGENT_ID", "")
AGENT_ALIAS_ID = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")  # Default test alias


from agentcore.tools import dispatch_tool

def invoke_agentcore(
    user_message: str,
    session_id: str = None,
    language: str = "hi",
    channel: str = "web",
    slots: dict = None,
    consent_given: bool = True,
    asr_confidence: float = 1.0,
    **kwargs
) -> dict:
    """
    Invoke the JanSathi Bedrock AgentCore agent.
    Handles 'Return Control' by dispatching local tools.
    """
    if not AGENT_ID:
        logger.error("[AgentCore] BEDROCK_AGENT_ID not set. Use local LangGraph mode.")
        return {
            "response": "AgentCore not configured. Please set BEDROCK_AGENT_ID in .env",
            "error": "AGENT_ID_MISSING",
        }

    session_id = session_id or str(uuid.uuid4())
    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client("bedrock-agent-runtime", region_name=region)

    # Initial input state
    input_text = user_message
    session_state = {
        "sessionAttributes": {
            "language": language,
            "channel": channel,
        }
    }
    if slots:
        session_state["sessionAttributes"]["slots"] = json.dumps(slots)

    response_text = ""
    citations = []
    
    # We use a loop because Return Control can happen multiple times in one turn
    # (e.g. Agent calls intent, then calls RAG after getting intent)
    while True:
        try:
            # Prepare invoke arguments
            kwargs = {
                "agentId": AGENT_ID,
                "agentAliasId": AGENT_ALIAS_ID,
                "sessionId": session_id,
                "sessionState": session_state,
                "enableTrace": os.getenv("AGENTCORE_TRACE", "false").lower() == "true",
            }
            if input_text:
                kwargs["inputText"] = input_text
                # After first call, we don't send inputText anymore if we are returning control results
                input_text = None

            response = client.invoke_agent(**kwargs)

            # Process the event stream
            return_control = None
            
            for event in response.get("completion", []):
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        response_text += chunk["bytes"].decode("utf-8")
                    if "attribution" in chunk:
                        for citation in chunk["attribution"].get("citations", []):
                            ref = citation.get("generatedResponsePart", {}).get("textResponsePart", {})
                            citations.append({
                                "text": ref.get("text", ""),
                                "sources": [
                                    r.get("location", {}).get("s3Location", {}).get("uri", "")
                                    for r in citation.get("retrievedReferences", [])
                                ],
                            })
                
                elif "returnControl" in event:
                    return_control = event["returnControl"]

            # If agent requested tool execution (Return Control)
            if return_control:
                invocation_id = return_control["invocationId"]
                tool_results = []
                
                for call in return_control.get("invocationInputs", []):
                    if "functionInvocationInput" in call:
                        func = call["functionInvocationInput"]
                        tool_name = func["function"]
                        params = func.get("parameters", [])
                        
                        # Convert Bedrock params list to dict for our dispatch_tool
                        param_dict = {p["name"]: p["value"] for p in params}
                        param_dict["session_id"] = session_id 
                        
                        logger.info(f"[AgentCore] Dispatching tool: {tool_name}")
                        result = dispatch_tool(tool_name, param_dict)
                        
                        # Correct Bedrock schema for Function Result
                        tool_results.append({
                            "functionResult": {
                                "actionGroup": func["actionGroup"],
                                "function": tool_name,
                                "responseBody": {
                                    "TEXT": {
                                        "body": json.dumps(result)
                                    }
                                }
                            }
                        })

                # Prepare session_state for the next iteration with tool results
                session_state["invocationId"] = invocation_id
                session_state["returnControlInvocationResults"] = tool_results
                # Loop back to send results
                continue
            
            # If no returnControl, the turn is finished
            break

        except ClientError as e:
            code = e.response["Error"]["Code"]
            logger.error(f"[AgentCore] ClientError ({code}): {e}")
            return {
                "response": "⚠️ AgentCore request failed. Please try again.",
                "error": str(e),
                "session_id": session_id,
            }
        except Exception as e:
            logger.error(f"[AgentCore] Unexpected error: {e}")
            return {
                "response": "⚠️ Service error. Please visit india.gov.in",
                "error": str(e),
                "session_id": session_id,
            }

    logger.info(
        f"[AgentCore] session={session_id} "
        f"response_len={len(response_text)} citations={len(citations)}"
    )

    return {
        "response": response_text.strip(),
        "session_id": session_id,
        "citations": citations,
        "mode": "agentcore",
    }
