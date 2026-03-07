import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from app.services.bedrock_service import BedrockService
import time

def run_test():
    with app.app_context():
        bedrock = BedrockService()
        
        query = "What documents do I need for my uploaded PM Awas PDF?"
        context = "The PM Awas Yojana requires Aadhaar, Income Certificate, and a passport-sized photograph."
        language = "hi"
        
        print(f"--- FIRST CALL (EXPECT GENERATING) ---")
        start = time.time()
        res1 = bedrock.generate_response(query, context, language)
        time1 = time.time() - start
        print(f"Time: {time1:.2f}s")
        text1 = res1.get('text', '')[:100].encode('ascii', 'ignore').decode('ascii')
        print(f"Text snippet: {text1}...\n")
        
        print(f"--- SECOND CALL (EXPECT CACHE HIT) ---")
        start = time.time()
        res2 = bedrock.generate_response(query, context, language)
        time2 = time.time() - start
        print(f"Time: {time2:.2f}s")
        text2 = res2.get('text', '')[:100].encode('ascii', 'ignore').decode('ascii')
        print(f"Text snippet: {text2}...\n")

if __name__ == "__main__":
    run_test()
