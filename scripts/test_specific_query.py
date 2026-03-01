#!/usr/bin/env python3
"""
Test specific JanSathi queries
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_pm_kisan():
    """Test PM Kisan query"""
    print("🔍 Testing PM Kisan query...")
    
    payload = {
        "text_query": "PM Kisan scheme benefits",
        "language": "en",
        "userId": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Query: {result.get('query')}")
        print(f"✅ Answer: {result.get('answer', {}).get('text')}")
        
        if result.get('answer', {}).get('audio'):
            print(f"🎵 Audio: {result['answer']['audio']}")
        
        if result.get('structured_sources'):
            print(f"📋 Sources: {len(result['structured_sources'])} found")
            for source in result['structured_sources']:
                print(f"   - {source.get('title')}: {source.get('benefit')}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_pm_kisan()