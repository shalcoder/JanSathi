"""
Smart RAG Service with Learning Pipeline
=========================================

This service implements an intelligent RAG pipeline that:
1. Searches Kendra for existing answers (verified government data)
2. If confidence is low, generates answer using Bedrock
3. Stores new Q&A pairs back to S3 for Kendra to index
4. Implements caching, telemetry, and personalization

Flow:
User Query → Kendra Search → High Confidence? → Return Answer
                          ↓ Low Confidence
                    Bedrock Generate → Store to S3 → Sync Kendra → Return Answer
"""

import os
import json
import boto3
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from botocore.exceptions import ClientError

class SmartRAGService:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.kendra_index_id = os.getenv('KENDRA_INDEX_ID', 'mock-index')
        self.s3_bucket = os.getenv('S3_BUCKET_NAME', 'jansathi-knowledge-base-1772952106')
        self.learning_folder = 'learned-qa'  # Folder in S3 for new Q&A pairs
        
        # Confidence thresholds
        self.HIGH_CONFIDENCE = 0.75  # Use Kendra answer directly
        self.LOW_CONFIDENCE = 0.40   # Generate new answer with Bedrock
        
        # Initialize AWS clients
        try:
            self.kendra = boto3.client('kendra', region_name=self.region)
            self.s3 = boto3.client('s3', region_name=self.region)
            self.working = True
        except Exception as e:
            print(f"SmartRAG Init Error: {e}")
            self.working = False
            self.kendra = None
            self.s3 = None
        
        # In-memory cache for recent queries (session-level)
        self.query_cache = {}  # query_hash -> (answer, timestamp, confidence)
        self.cache_ttl = 3600  # 1 hour
        
        # Telemetry
        self.stats = {
            'kendra_hits': 0,
            'bedrock_generates': 0,
            'cache_hits': 0,
            'learned_qa_stored': 0,
        }
    
    def query(self, user_query: str, language: str = 'en', 
              user_profile: Optional[Dict] = None, 
              session_id: Optional[str] = None) -> Dict:
        """
        Main entry point for smart RAG query.
        
        Returns:
            {
                'answer': str,
                'confidence': float,
                'source': 'kendra' | 'bedrock' | 'cache',
                'sources': List[Dict],
                'learned': bool,  # True if this was a new answer stored to Kendra
                'telemetry': Dict
            }
        """
        start_time = time.time()
        
        # 1. Check cache first
        cache_result = self._check_cache(user_query)
        if cache_result:
            self.stats['cache_hits'] += 1
            return {
                'answer': cache_result['answer'],
                'confidence': cache_result['confidence'],
                'source': 'cache',
                'sources': cache_result.get('sources', []),
                'learned': False,
                'telemetry': {
                    'latency_ms': (time.time() - start_time) * 1000,
                    'cache_hit': True,
                }
            }
        
        # 2. Search Kendra for existing answer
        kendra_result = self._search_kendra(user_query, language)
        
        # 3. Evaluate confidence
        if kendra_result['confidence'] >= self.HIGH_CONFIDENCE:
            # High confidence - use Kendra answer
            self.stats['kendra_hits'] += 1
            answer = self._format_kendra_answer(kendra_result)
            
            # Cache it
            self._cache_answer(user_query, answer, kendra_result['confidence'], kendra_result['sources'])
            
            return {
                'answer': answer,
                'confidence': kendra_result['confidence'],
                'source': 'kendra',
                'sources': kendra_result['sources'],
                'learned': False,
                'telemetry': {
                    'latency_ms': (time.time() - start_time) * 1000,
                    'kendra_confidence': kendra_result['confidence'],
                    'num_sources': len(kendra_result['sources']),
                }
            }
        
        # 4. Low confidence - generate with Bedrock
        bedrock_result = self._generate_with_bedrock(
            user_query, 
            language, 
            kendra_context=kendra_result.get('raw_text', ''),
            user_profile=user_profile,
            session_id=session_id
        )
        
        if bedrock_result['success']:
            self.stats['bedrock_generates'] += 1
            answer = bedrock_result['answer']
            
            # 5. Store new Q&A to S3 for Kendra to learn
            learned = self._store_learned_qa(
                user_query, 
                answer, 
                language, 
                session_id,
                kendra_context=kendra_result.get('raw_text', '')
            )
            
            if learned:
                self.stats['learned_qa_stored'] += 1
            
            # Cache it
            self._cache_answer(user_query, answer, bedrock_result['confidence'], [])
            
            return {
                'answer': answer,
                'confidence': bedrock_result['confidence'],
                'source': 'bedrock',
                'sources': bedrock_result.get('sources', []),
                'learned': learned,
                'telemetry': {
                    'latency_ms': (time.time() - start_time) * 1000,
                    'kendra_confidence': kendra_result['confidence'],
                    'bedrock_used': True,
                    'stored_to_s3': learned,
                }
            }
        
        # 6. Fallback - return best available answer
        fallback_answer = kendra_result.get('raw_text', '') or "I don't have enough information to answer that question accurately. Please visit https://myscheme.gov.in for official information."
        
        return {
            'answer': fallback_answer,
            'confidence': kendra_result['confidence'],
            'source': 'fallback',
            'sources': kendra_result['sources'],
            'learned': False,
            'telemetry': {
                'latency_ms': (time.time() - start_time) * 1000,
                'fallback_used': True,
            }
        }
    
    def _search_kendra(self, query: str, language: str) -> Dict:
        """
        Search Kendra index for relevant documents.
        
        Returns:
            {
                'confidence': float,
                'raw_text': str,
                'sources': List[Dict],
            }
        """
        if not self.working or not self.kendra or self.kendra_index_id == 'mock-index':
            return {'confidence': 0.0, 'raw_text': '', 'sources': []}
        
        try:
            response = self.kendra.retrieve(
                IndexId=self.kendra_index_id,
                QueryText=query,
                PageSize=5
            )
            
            items = response.get('ResultItems', [])
            
            if not items:
                return {'confidence': 0.0, 'raw_text': '', 'sources': []}
            
            # Calculate confidence based on top result score
            top_score = items[0].get('ScoreAttributes', {}).get('ScoreConfidence', 'LOW')
            confidence_map = {
                'VERY_HIGH': 0.95,
                'HIGH': 0.85,
                'MEDIUM': 0.65,
                'LOW': 0.35,
            }
            confidence = confidence_map.get(top_score, 0.35)
            
            # Aggregate text from top results
            raw_text = '\n\n'.join([
                item.get('Content', '') 
                for item in items[:3]  # Top 3 results
                if item.get('Content')
            ])
            
            # Extract sources
            sources = []
            for item in items[:3]:
                sources.append({
                    'title': item.get('DocumentTitle', 'Government Document'),
                    'uri': item.get('DocumentURI', ''),
                    'excerpt': item.get('Content', '')[:200] + '...',
                    'confidence': top_score,
                })
            
            return {
                'confidence': confidence,
                'raw_text': raw_text,
                'sources': sources,
            }
            
        except Exception as e:
            print(f"Kendra Search Error: {e}")
            return {'confidence': 0.0, 'raw_text': '', 'sources': []}
    
    def _generate_with_bedrock(self, query: str, language: str, 
                               kendra_context: str = '', 
                               user_profile: Optional[Dict] = None,
                               session_id: Optional[str] = None) -> Dict:
        """
        Generate answer using Bedrock when Kendra confidence is low.
        """
        try:
            from app.services.bedrock_service import BedrockService
            
            bedrock = BedrockService()
            
            if not bedrock.working:
                return {'success': False, 'answer': '', 'confidence': 0.0}
            
            # Build enhanced context
            context_parts = []
            
            if kendra_context:
                context_parts.append(f"PARTIAL INFORMATION FROM KENDRA:\n{kendra_context[:500]}")
            
            if user_profile:
                state = user_profile.get('state', '')
                occupation = user_profile.get('occupation', '')
                if state or occupation:
                    context_parts.append(f"USER CONTEXT: State={state}, Occupation={occupation}")
            
            context_parts.append(
                "INSTRUCTIONS: Provide accurate information about Indian government schemes. "
                "If you're not certain, recommend visiting official portals like myscheme.gov.in or india.gov.in."
            )
            
            full_context = '\n\n'.join(context_parts)
            
            # Generate response
            result = bedrock.generate_response(
                query=query,
                context_text=full_context,
                language=language,
                intent="INFORMATION",
                session_id=session_id
            )
            
            return {
                'success': True,
                'answer': result.get('text', ''),
                'confidence': result.get('explainability', {}).get('confidence', 0.75),
                'sources': [{
                    'title': 'AI Generated Response',
                    'uri': 'https://myscheme.gov.in',
                    'excerpt': 'Generated using AWS Bedrock with available context',
                    'confidence': 'AI_GENERATED',
                }]
            }
            
        except Exception as e:
            print(f"Bedrock Generation Error: {e}")
            return {'success': False, 'answer': '', 'confidence': 0.0}
    
    def _store_learned_qa(self, question: str, answer: str, language: str, 
                          session_id: Optional[str], kendra_context: str = '') -> bool:
        """
        Store new Q&A pair to S3 so Kendra can index it in next sync.
        
        Creates a structured document with metadata for better retrieval.
        """
        if not self.working or not self.s3:
            return False
        
        try:
            # Generate unique ID for this Q&A
            qa_id = hashlib.md5(question.encode()).hexdigest()[:12]
            timestamp = datetime.utcnow().isoformat()
            
            # Create structured document
            document = {
                'id': qa_id,
                'type': 'learned_qa',
                'question': question,
                'answer': answer,
                'language': language,
                'session_id': session_id or 'unknown',
                'timestamp': timestamp,
                'source': 'bedrock_generated',
                'kendra_context_available': bool(kendra_context),
                'metadata': {
                    'created_by': 'JanSathi Smart RAG',
                    'version': '1.0',
                    'confidence': 'ai_generated',
                }
            }
            
            # Create searchable text content
            content = f"""
# Question: {question}

## Answer:
{answer}

## Metadata:
- Language: {language}
- Generated: {timestamp}
- Session: {session_id or 'N/A'}
- Source: AI Generated with Bedrock
- Type: Learned Q&A Pair

## Context Used:
{kendra_context[:300] if kendra_context else 'No prior context available'}

---
This document was automatically generated by JanSathi's learning pipeline.
For official information, please visit https://myscheme.gov.in
"""
            
            # Store to S3
            key = f"{self.learning_folder}/{qa_id}_{timestamp.replace(':', '-')}.txt"
            
            self.s3.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain; charset=utf-8',
                Metadata={
                    'qa-id': qa_id,
                    'language': language,
                    'type': 'learned_qa',
                    'timestamp': timestamp,
                }
            )
            
            print(f"✅ Stored learned Q&A to S3: {key}")
            return True
            
        except Exception as e:
            print(f"Error storing learned Q&A: {e}")
            return False
    
    def _format_kendra_answer(self, kendra_result: Dict) -> str:
        """Format Kendra results into a clean answer."""
        raw_text = kendra_result.get('raw_text', '')
        sources = kendra_result.get('sources', [])
        
        if not raw_text:
            return "No information found."
        
        # Clean up text
        answer = raw_text.strip()
        
        # Add source attribution
        if sources:
            source_urls = [s['uri'] for s in sources if s.get('uri')]
            if source_urls:
                answer += f"\n\n📚 Sources: {', '.join(source_urls[:2])}"
        
        return answer
    
    def _check_cache(self, query: str) -> Optional[Dict]:
        """Check if query is in cache and not expired."""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        
        if query_hash in self.query_cache:
            cached = self.query_cache[query_hash]
            age = time.time() - cached['timestamp']
            
            if age < self.cache_ttl:
                return cached
            else:
                # Expired - remove from cache
                del self.query_cache[query_hash]
        
        return None
    
    def _cache_answer(self, query: str, answer: str, confidence: float, sources: List[Dict]):
        """Cache answer for future queries."""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        
        self.query_cache[query_hash] = {
            'answer': answer,
            'confidence': confidence,
            'sources': sources,
            'timestamp': time.time(),
        }
        
        # Limit cache size
        if len(self.query_cache) > 100:
            # Remove oldest entry
            oldest = min(self.query_cache.items(), key=lambda x: x[1]['timestamp'])
            del self.query_cache[oldest[0]]
    
    def trigger_kendra_sync(self) -> bool:
        """
        Trigger Kendra data source sync to index new learned Q&A pairs.
        
        Note: This should be called periodically (e.g., every hour) or after
        a batch of new Q&A pairs have been stored.
        """
        if not self.working or not self.kendra:
            return False
        
        try:
            # Get data source ID for S3 bucket
            # You'll need to configure this based on your Kendra setup
            data_source_id = os.getenv('KENDRA_DATA_SOURCE_ID', '')
            
            if not data_source_id:
                print("⚠️  KENDRA_DATA_SOURCE_ID not configured. Sync skipped.")
                return False
            
            response = self.kendra.start_data_source_sync_job(
                Id=data_source_id,
                IndexId=self.kendra_index_id
            )
            
            execution_id = response.get('ExecutionId')
            print(f"✅ Kendra sync triggered: {execution_id}")
            return True
            
        except Exception as e:
            print(f"Error triggering Kendra sync: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get telemetry statistics."""
        return {
            **self.stats,
            'cache_size': len(self.query_cache),
            'cache_ttl_seconds': self.cache_ttl,
        }
