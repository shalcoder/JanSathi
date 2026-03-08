#!/usr/bin/env python3
"""
Test Smart RAG Service directly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.smart_rag_service import SmartRAGService

def test_smart_rag():
    print("="*60)
    print("Testing Smart RAG Service")
    print("="*60)
    print()
    
    smart_rag = SmartRAGService()
    
    # Test queries
    queries = [
        ("What is PM Kisan scheme?", "en"),
        ("Tell me about Ayushman Bharat eligibility", "en"),
        ("How do I apply for PM Awas Yojana?", "en"),
        ("What are the benefits of MUDRA loan?", "en"),
    ]
    
    for i, (query, lang) in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print(f"{'='*60}")
        
        result = smart_rag.query(
            user_query=query,
            language=lang,
            session_id=f"test-{i}"
        )
        
        print(f"\n✅ Source: {result['source']}")
        print(f"✅ Confidence: {result['confidence']:.2f}")
        print(f"✅ Learned: {result.get('learned', False)}")
        print(f"\n📝 Answer:")
        print(result['answer'][:500])
        
        if result.get('sources'):
            print(f"\n📚 Sources:")
            for src in result['sources'][:2]:
                print(f"  - {src.get('title', 'N/A')}")
                print(f"    {src.get('uri', 'N/A')}")
        
        print(f"\n⏱️  Latency: {result['telemetry'].get('latency_ms', 0):.2f}ms")
    
    # Print stats
    print(f"\n{'='*60}")
    print("Smart RAG Statistics")
    print(f"{'='*60}")
    stats = smart_rag.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_smart_rag()
