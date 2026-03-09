import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from main import create_app
from agentcore.invoke import invoke_agentcore

def test_connection():
    app = create_app()
    with app.app_context():
        agent_id = os.getenv("BEDROCK_AGENT_ID")
        agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID")
        use_agentcore = os.getenv("USE_AGENTCORE")
        
        print(f"DEBUG: BEDROCK_AGENT_ID={agent_id}")
        print(f"DEBUG: BEDROCK_AGENT_ALIAS_ID={agent_alias_id}")
        print(f"DEBUG: USE_AGENTCORE={use_agentcore}")
        
        if not agent_id:
            print("ERROR: BEDROCK_AGENT_ID not set")
            return

        print("\nAttempting to invoke AgentCore with App Context...")
        try:
            result = invoke_agentcore(
                user_message="Tell me about PM Kisan scheme.",
                session_id="test-session-789",
                language="en",
                channel="web"
            )
            print("\n--- Response ---")
            print(result.get("response"))
            print("\n--- Mode ---")
            print(result.get("mode"))
            print("\n--- Citations ---")
            citations = result.get("citations", [])
            print(f"Count: {len(citations)}")
            for c in citations:
                print(f" - {c.get('text')[:100]}...")

            print("\n--- Error (if any) ---")
            print(result.get("error"))
        except Exception as e:
            print(f"\nFATAL ERROR: {e}")

if __name__ == "__main__":
    test_connection()
