#!/usr/bin/env python3
"""
Demo: Smart RAG Learning Pipeline
Shows how the system learns from queries and improves over time
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.smart_rag_service import SmartRAGService

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def demo_learning_pipeline():
    print_header("🚀 JanSathi Smart RAG Learning Pipeline Demo")
    
    smart_rag = SmartRAGService()
    
    # Demo query
    query = "What are the eligibility criteria for PM Kisan scheme?"
    
    print("📝 Demo Query:")
    print(f"   '{query}'\n")
    
    # First query - will search Kendra, then generate with Bedrock
    print_header("🔍 FIRST QUERY - Learning Phase")
    print("⏳ Searching Kendra for existing answer...")
    
    start = time.time()
    result1 = smart_rag.query(
        user_query=query,
        language="en",
        session_id="demo-1"
    )
    latency1 = time.time() - start
    
    print(f"\n✅ Result:")
    print(f"   Source: {result1['source']}")
    print(f"   Confidence: {result1['confidence']:.2f}")
    print(f"   Learned: {result1.get('learned', False)}")
    print(f"   Latency: {latency1*1000:.0f}ms")
    
    if result1.get('learned'):
        print(f"\n💡 NEW KNOWLEDGE ACQUIRED!")
        print(f"   This answer has been stored to S3 for future queries.")
        print(f"   After Kendra sync, it will be instantly retrievable.")
    
    # Second query - should hit cache
    print_header("⚡ SECOND QUERY - Cache Hit")
    print("⏳ Checking cache...")
    
    start = time.time()
    result2 = smart_rag.query(
        user_query=query,
        language="en",
        session_id="demo-2"
    )
    latency2 = time.time() - start
    
    print(f"\n✅ Result:")
    print(f"   Source: {result2['source']}")
    print(f"   Confidence: {result2['confidence']:.2f}")
    print(f"   Latency: {latency2*1000:.0f}ms")
    
    speedup = latency1 / latency2 if latency2 > 0 else 0
    print(f"\n🚀 PERFORMANCE IMPROVEMENT:")
    print(f"   First query: {latency1*1000:.0f}ms")
    print(f"   Second query: {latency2*1000:.0f}ms")
    print(f"   Speedup: {speedup:.1f}x faster!")
    
    # Show stats
    print_header("📊 System Statistics")
    stats = smart_rag.get_stats()
    
    print(f"   Kendra Hits: {stats['kendra_hits']}")
    print(f"   Bedrock Generates: {stats['bedrock_generates']}")
    print(f"   Cache Hits: {stats['cache_hits']}")
    print(f"   Learned Q&A Stored: {stats['learned_qa_stored']}")
    print(f"   Cache Size: {stats['cache_size']}")
    
    # Show learning impact
    print_header("🎯 Learning Impact")
    
    total_queries = stats['kendra_hits'] + stats['bedrock_generates'] + stats['cache_hits']
    if total_queries > 0:
        cache_rate = (stats['cache_hits'] / total_queries) * 100
        print(f"   Total Queries: {total_queries}")
        print(f"   Cache Hit Rate: {cache_rate:.1f}%")
        print(f"   Knowledge Base Growth: +{stats['learned_qa_stored']} documents")
    
    print(f"\n   💰 Cost Savings:")
    print(f"      - Bedrock calls avoided: {stats['cache_hits']}")
    print(f"      - Estimated savings: ${stats['cache_hits'] * 0.003:.2f}")
    
    print_header("✅ Demo Complete!")
    
    print("🎓 Key Takeaways:")
    print("   1. First query searches Kendra, then generates with Bedrock")
    print("   2. Answer is automatically stored to S3 for future use")
    print("   3. Second query hits cache - 10-100x faster!")
    print("   4. After Kendra sync, answer becomes part of verified knowledge")
    print("   5. System learns and improves with every interaction")
    
    print("\n🚀 This is how JanSathi becomes smarter every day!")
    print("   Every citizen query helps the next citizen get faster answers.\n")

if __name__ == "__main__":
    demo_learning_pipeline()
