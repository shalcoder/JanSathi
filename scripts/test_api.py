#!/usr/bin/env python3
"""
Test JanSathi API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_query():
    """Test query endpoint"""
    print("\n🔍 Testing /query endpoint...")
    try:
        payload = {
            "text_query": "What is PM Kisan scheme?",
            "language": "en",
            "userId": "test_user"
        }
        
        response = requests.post(
            f"{BASE_URL}/query", 
            json=payload,
            timeout=30
        )
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query: {result.get('query', 'N/A')}")
            print(f"✅ Answer: {result.get('answer', {}).get('text', 'N/A')[:100]}...")
            
            if result.get('answer', {}).get('audio'):
                print(f"✅ Audio URL: {result['answer']['audio']}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_schemes():
    """Test schemes endpoint"""
    print("\n🔍 Testing /schemes endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/schemes", timeout=10)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            schemes = response.json()
            print(f"✅ Found {len(schemes)} schemes")
            
            if schemes:
                print(f"✅ Sample scheme: {schemes[0].get('title', 'N/A')}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Schemes test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 JanSathi API Test Suite")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Query Processing", test_query),
        ("Schemes Retrieval", test_schemes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! JanSathi API is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the backend logs.")

if __name__ == "__main__":
    main()