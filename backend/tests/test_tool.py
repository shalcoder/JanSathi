import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from main import create_app
from agentcore.tools import retrieve_knowledge

def test_tool():
    app = create_app()
    with app.app_context():
        print("Testing retrieve_knowledge tool...")
        result = retrieve_knowledge(query="PM Kisan", scheme_hint="pm_kisan", language="en")
        print("\n--- Result ---")
        import json
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_tool()
