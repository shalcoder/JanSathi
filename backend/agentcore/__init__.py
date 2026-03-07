"""
JanSathi Bedrock AgentCore Deployment Package
=============================================
Deploys the JanSathi LangGraph multi-agent system to Amazon Bedrock AgentCore.

Files:
  - __init__.py     : Package init
  - tools.py        : Tool definitions (action groups) for AgentCore
  - agent.py        : Agent creation + alias deployment via boto3
  - invoke.py       : Invocation wrapper (used by Flask API)
  - deploy.py       : CLI script to deploy/update the AgentCore agent
"""
