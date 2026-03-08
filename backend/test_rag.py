import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentcore.tools import retrieve_knowledge
from main import create_app

app = create_app()

with app.app_context():
    from app.services.rag_service import RagService
    rag = RagService()
    rag.set_app_context(app.app_context())
    
    print("SCHEMES LOADED:", [s['title'] for s in rag.schemes])
    
    results = rag._hybrid_search("PM-KISAN", threshold=0.0)
    print("SCORES:", [(d['title'], s) for d, s in results])
