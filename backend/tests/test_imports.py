
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.getcwd())

print("Testing HITLService import...")
from app.services.hitl_service import HITLService
print("Done.")

print("Testing NotifyService import...")
from app.services.notify_service import NotifyService
print("Done.")

print("Testing IVRService import...")
from app.services.ivr_service import IVRService
print("Done.")

print("Testing RagService import...")
from app.services.rag_service import RagService
print("Done.")

print("Testing SchemeFeedService import...")
from app.services.scheme_feed_service import SchemeFeedService
print("Done SchemeFeedService.")

print("Testing CivicInfraService import...")
from app.services.civic_infra_service import CivicInfraService
print("Done CivicInfraService.")

print("Testing process_user_input import...")
from app.core.execution import process_user_input
print("Done.")

print("Testing models import...")
from app.models.models import db
print("Done.")

print("Testing session_manager import...")
from agentic_engine.session_manager import SessionManager
print("Done.")
