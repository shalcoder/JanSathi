
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from flask import Flask
from app.services.transcribe_service import TranscribeService
from app.services.bedrock_service import BedrockService
from app.services.rag_service import RagService
from app.services.polly_service import PollyService
from app.services.workflow_service import WorkflowService
from app.services.agent_service import AgentService
from app.services.fl_service import FederatedLearningService
from app.services.ivr_service import IVRService
from app.services.whatsapp_service import WhatsAppService

print("Starting Service Initialization Check...")

try:
    print("Initializing TranscribeService...")
    transcribe_service = TranscribeService()
    print("TranscribeService: OK")
except Exception as e:
    print(f"TranscribeService FAILED: {e}")

try:
    print("Initializing BedrockService...")
    bedrock_service = BedrockService()
    print("BedrockService: OK")
except Exception as e:
    print(f"BedrockService FAILED: {e}")

try:
    print("Initializing RagService...")
    rag_service = RagService()
    print("RagService: OK")
except Exception as e:
    print(f"RagService FAILED: {e}")

try:
    print("Initializing PollyService...")
    polly_service = PollyService()
    print("PollyService: OK")
except Exception as e:
    print(f"PollyService FAILED: {e}")

try:
    print("Initializing WorkflowService...")
    workflow_service = WorkflowService()
    print("WorkflowService: OK")
except Exception as e:
    print(f"WorkflowService FAILED: {e}")

try:
    print("Initializing IVRService...")
    ivr_service = IVRService()
    print("IVRService: OK")
except Exception as e:
    print(f"IVRService FAILED: {e}")

try:
    print("Initializing WhatsAppService...")
    whatsapp_service = WhatsAppService()
    print("WhatsAppService: OK")
except Exception as e:
    print(f"WhatsAppService FAILED: {e}")

try:
    print("Initializing AgentService...")
    # Mock services if they failed
    if 'bedrock_service' not in locals(): bedrock_service = None
    if 'rag_service' not in locals(): rag_service = None
    if 'polly_service' not in locals(): polly_service = None
    
    agent_service = AgentService(bedrock_service, rag_service, polly_service)
    print("AgentService: OK")
except Exception as e:
    print(f"AgentService FAILED: {e}")

try:
    print("Initializing FederatedLearningService...")
    fl_service = FederatedLearningService(min_clients=2)
    print("FederatedLearningService: OK")
except Exception as e:
    print(f"FederatedLearningService FAILED: {e}")

print("Check Complete.")
