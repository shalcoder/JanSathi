#!/usr/bin/env python3
"""
Setup script to deploy Kendra infrastructure and populate with initial government schemes.
Run this after deploying the CDK stack to populate Kendra with base knowledge.
"""

import boto3
import json
import os
import sys
from pathlib import Path

# Add backend to path for importing services
sys.path.append(str(Path(__file__).parent.parent / "backend"))
from app.services.rag_service import RagService

def populate_kendra_with_schemes():
    """Populate Kendra index with the base government schemes."""
    
    # Initialize RAG service (will use local schemes as source)
    rag_service = RagService()
    
    if not rag_service.use_kendra:
        print("❌ Kendra not configured. Please set KENDRA_INDEX_ID environment variable.")
        return False
    
    print(f"📋 Populating Kendra index: {rag_service.kendra_index_id}")
    
    # Get all schemes from local knowledge base
    schemes = rag_service.schemes
    
    success_count = 0
    for scheme in schemes:
        title = scheme['title']
        content = f"""
{scheme['title']}

{scheme['text']}

Benefits: {scheme['benefit']}
Ministry: {scheme['ministry']}
Category: {scheme['category']}
Keywords: {', '.join(scheme['keywords'])}
Official Link: {scheme['link']}
"""
        
        metadata = {
            'scheme_id': scheme['id'],
            'ministry': scheme['ministry'],
            'category': scheme['category'],
            'benefit': scheme['benefit']
        }
        
        print(f"📄 Indexing: {title}")
        success = rag_service._index_document_to_kendra(title, content, metadata)
        
        if success:
            success_count += 1
            print(f"✅ Successfully indexed: {title}")
        else:
            print(f"❌ Failed to index: {title}")
    
    print(f"\n🎉 Indexing complete: {success_count}/{len(schemes)} schemes indexed successfully")
    return success_count == len(schemes)

def test_kendra_search():
    """Test Kendra search functionality."""
    print("\n🔍 Testing Kendra search...")
    
    rag_service = RagService()
    
    if not rag_service.use_kendra:
        print("❌ Kendra not available for testing")
        return False
    
    test_queries = [
        "PM Kisan scheme for farmers",
        "Health insurance Ayushman Bharat",
        "Housing scheme for poor families",
        "Loan for small business"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: {query}")
        results = rag_service._kendra_search(query, top_k=2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} (Score: {result['score']:.2f})")
                print(f"     {result['text'][:100]}...")
        else:
            print("  No results found")
    
    return True

def main():
    """Main setup function."""
    print("🚀 JanSathi Kendra Setup")
    print("=" * 50)
    
    # Check environment
    kendra_index_id = os.getenv('KENDRA_INDEX_ID')
    if not kendra_index_id or kendra_index_id == 'mock-index':
        print("❌ Please set KENDRA_INDEX_ID environment variable with your deployed Kendra index ID")
        print("   You can get this from the CDK stack outputs after deployment")
        return 1
    
    # Populate Kendra
    if populate_kendra_with_schemes():
        print("\n✅ Kendra population successful!")
        
        # Wait a bit for indexing to complete
        print("⏳ Waiting 30 seconds for indexing to complete...")
        import time
        time.sleep(30)
        
        # Test search
        test_kendra_search()
        
        print("\n🎉 Kendra setup complete! You can now use Kendra-powered search.")
        return 0
    else:
        print("\n❌ Kendra population failed!")
        return 1

if __name__ == "__main__":
    exit(main())