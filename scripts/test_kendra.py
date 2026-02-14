#!/usr/bin/env python3
"""
Test script to verify Kendra integration is working properly.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def test_kendra_integration():
    """Test Kendra integration."""
    print("🧪 Testing Kendra Integration")
    print("=" * 40)
    
    # Test environment
    kendra_index_id = os.getenv('KENDRA_INDEX_ID')
    print(f"📋 Kendra Index ID: {kendra_index_id}")
    
    if not kendra_index_id or kendra_index_id == 'mock-index':
        print("❌ Kendra not configured - using mock mode")
        return False
    
    # Test RAG service initialization
    try:
        from app.services.rag_service import RagService
        rag_service = RagService()
        
        print(f"✅ RAG Service initialized")
        print(f"🔍 Using Kendra: {rag_service.use_kendra}")
        
        if not rag_service.use_kendra:
            print("❌ Kendra not available in RAG service")
            return False
        
        # Test search
        print("\n🔎 Testing search functionality...")
        test_queries = [
            "farmer support scheme",
            "health insurance for families",
            "small business loan"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            try:
                results = rag_service.retrieve(query)
                if results:
                    print(f"✅ Found {len(results)} results")
                    for i, result in enumerate(results[:2], 1):
                        preview = result[:100] + "..." if len(result) > 100 else result
                        print(f"   {i}. {preview}")
                else:
                    print("⚠️  No results found")
            except Exception as e:
                print(f"❌ Search failed: {e}")
                return False
        
        print("\n🎉 Kendra integration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ RAG Service initialization failed: {e}")
        return False

def main():
    """Main test function."""
    if test_kendra_integration():
        print("\n✅ All tests passed! Kendra is working properly.")
        return 0
    else:
        print("\n❌ Tests failed! Please check your Kendra setup.")
        return 1

if __name__ == "__main__":
    exit(main())