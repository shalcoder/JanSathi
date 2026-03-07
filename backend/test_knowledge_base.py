"""
Test Script for Bedrock Knowledge Base with Caching
===================================================
Demonstrates PDF upload and intelligent query caching.

Usage:
    python test_knowledge_base.py
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/kb"


def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_health_check():
    """Test Knowledge Base service health."""
    print_section("1. Health Check")
    
    response = requests.get(f"{API_BASE}/health")
    data = response.json()
    
    print(f"Status: {data.get('status')}")
    print(f"KB ID: {data.get('kb_id')}")
    print(f"Cache Enabled: {data.get('cache_enabled')}")
    print(f"Working: {data.get('working')}")
    
    return data.get('working', False)


def test_upload_pdf():
    """Test PDF upload to Knowledge Base."""
    print_section("2. Upload PDF Document")
    
    # Create a sample PDF (you should replace this with actual PDF)
    print("Note: Replace with actual PDF file path")
    print("Example: pdf_path = 'path/to/your/scheme_document.pdf'")
    
    # Uncomment and modify when you have a real PDF
    # pdf_path = "test_scheme.pdf"
    # if not Path(pdf_path).exists():
    #     print(f"Error: {pdf_path} not found")
    #     return None
    
    # with open(pdf_path, 'rb') as f:
    #     files = {'file': f}
    #     data = {
    #         'user_id': 'test_user',
    #         'document_type': 'scheme_info'
    #     }
    #     response = requests.post(f"{API_BASE}/upload", files=files, data=data)
    
    # result = response.json()
    # print(f"Document ID: {result.get('document_id')}")
    # print(f"S3 URI: {result.get('s3_uri')}")
    # print(f"Status: {result.get('status')}")
    # print(f"Message: {result.get('message')}")
    
    # return result.get('document_id')
    
    print("Skipping upload test (no PDF provided)")
    return None


def test_query_without_cache():
    """Test query to Knowledge Base (cache miss)."""
    print_section("3. Query Knowledge Base (First Time - Cache Miss)")
    
    query_data = {
        "question": "What is PM-KISAN scheme?",
        "language": "en",
        "user_context": {
            "occupation": "farmer",
            "location_state": "UP"
        },
        "max_results": 3
    }
    
    print(f"Question: {query_data['question']}")
    print(f"Language: {query_data['language']}")
    print("\nQuerying...")
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/query", json=query_data)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Response received in {elapsed:.2f}s")
        print(f"Cached: {result.get('cached', False)}")
        print(f"Cost Saved: ${result.get('cost_saved', 0):.2f}")
        print(f"\nAnswer Preview:")
        print(result.get('answer', 'No answer')[:200] + "...")
        print(f"\nSources Found: {len(result.get('sources', []))}")
        
        for i, source in enumerate(result.get('sources', [])[:2], 1):
            print(f"\n  Source {i}:")
            print(f"    Score: {source.get('score', 0):.2f}")
            print(f"    Text: {source.get('text', '')[:100]}...")
        
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None


def test_query_with_cache():
    """Test same query again (cache hit)."""
    print_section("4. Query Again (Cache Hit)")
    
    query_data = {
        "question": "What is PM-KISAN scheme?",
        "language": "en",
        "max_results": 3
    }
    
    print(f"Question: {query_data['question']}")
    print("Querying (should hit cache)...")
    
    start_time = time.time()
    response = requests.post(f"{API_BASE}/query", json=query_data)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Response received in {elapsed:.2f}s")
        print(f"Cached: {result.get('cached', False)} {'✅' if result.get('cached') else '❌'}")
        print(f"Cost Saved: ${result.get('cost_saved', 0):.2f}")
        
        if result.get('cached'):
            print(f"Cache Age: {result.get('cache_age_hours', 0):.1f} hours")
            print("\n🎉 Cache working! Query served from cache (Cost: $0.00)")
        else:
            print("\n⚠️ Cache miss - this might be expected if cache is disabled")
        
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None


def test_cache_stats():
    """Get cache statistics."""
    print_section("5. Cache Statistics")
    
    response = requests.get(f"{API_BASE}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        
        print(f"Total Cached Queries: {stats.get('total_cached_queries', 0)}")
        print(f"Cached Last 24h: {stats.get('cached_last_24h', 0)}")
        print(f"Cache TTL: {stats.get('cache_ttl_hours', 0)} hours")
        print(f"Estimated Cost Saved: ${stats.get('estimated_cost_saved', 0):.2f}")
        print(f"Cache Enabled: {stats.get('cache_enabled', False)}")
        
        print("\nLanguage Distribution:")
        for lang, count in stats.get('language_distribution', {}).items():
            print(f"  {lang}: {count} queries")
        
        return stats
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def test_multilingual_query():
    """Test query in Hindi."""
    print_section("6. Multilingual Query (Hindi)")
    
    query_data = {
        "question": "PM-KISAN योजना क्या है?",
        "language": "hi",
        "max_results": 3
    }
    
    print(f"Question: {query_data['question']}")
    print(f"Language: {query_data['language']}")
    print("\nQuerying...")
    
    response = requests.post(f"{API_BASE}/query", json=query_data)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Response received")
        print(f"Cached: {result.get('cached', False)}")
        print(f"\nAnswer Preview (Hindi):")
        print(result.get('answer', 'No answer')[:200] + "...")
        
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None


def test_cache_invalidation():
    """Test cache invalidation."""
    print_section("7. Cache Invalidation")
    
    print("Invalidating specific query...")
    
    response = requests.delete(
        f"{API_BASE}/cache",
        params={
            'query': 'what is pm-kisan scheme?',
            'language': 'en'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Deleted: {result.get('deleted', 0)} entries")
        print(f"Status: {result.get('status')}")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("  Bedrock Knowledge Base - Test Suite")
    print("="*60)
    
    try:
        # Test 1: Health Check
        is_working = test_health_check()
        
        if not is_working:
            print("\n⚠️ Knowledge Base service not available")
            print("Make sure:")
            print("  1. AWS credentials are configured")
            print("  2. BEDROCK_KB_ID is set in .env")
            print("  3. Backend server is running")
            return
        
        # Test 2: Upload PDF (optional)
        # doc_id = test_upload_pdf()
        
        # Test 3: Query without cache
        test_query_without_cache()
        
        # Small delay to ensure cache is written
        time.sleep(1)
        
        # Test 4: Query with cache
        test_query_with_cache()
        
        # Test 5: Cache stats
        test_cache_stats()
        
        # Test 6: Multilingual
        test_multilingual_query()
        
        # Test 7: Cache invalidation
        test_cache_invalidation()
        
        # Final stats
        print_section("Final Statistics")
        test_cache_stats()
        
        print("\n" + "="*60)
        print("  ✅ All Tests Completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to backend server")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    run_all_tests()
