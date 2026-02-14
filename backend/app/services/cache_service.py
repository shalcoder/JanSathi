"""
Response Cache Service — DynamoDB-style caching using SQLite (Free Tier).
Caches Bedrock AI responses with TTL to reduce API costs by ~80%.
"""

import hashlib
import json
import time
import threading
from datetime import datetime
from app.models.models import db

class CacheEntry(db.Model):
    """SQLAlchemy model for cached AI responses."""
    __tablename__ = 'response_cache'
    
    cache_key = db.Column(db.String(64), primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(10), default='hi')
    response = db.Column(db.Text, nullable=False)
    sources_json = db.Column(db.Text, nullable=True)  # JSON string of source cards
    ttl = db.Column(db.Integer, nullable=False)  # Unix timestamp for expiry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hit_count = db.Column(db.Integer, default=0)


class ResponseCache:
    """
    Application-level response cache.
    
    Uses SQLite (same DB as app) for zero-cost caching.
    Mimics DynamoDB TTL pattern: entries auto-expire after TTL.
    
    Usage:
        cache = ResponseCache(ttl_seconds=3600)
        
        # Check cache first
        cached = cache.get(query, language)
        if cached:
            return cached['response']
        
        # On miss, call Bedrock then cache
        response = bedrock.generate(...)
        cache.set(query, language, response, sources)
    """
    
    def __init__(self, ttl_seconds=3600):
        self.ttl_seconds = ttl_seconds
        self._cleanup_lock = threading.Lock()
    
    def _cache_key(self, query: str, language: str) -> str:
        """Generate deterministic cache key using SHA-256."""
        normalized = f"{query.lower().strip()}:{language.lower()}"
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def get(self, query: str, language: str = 'hi') -> dict | None:
        """
        Retrieve cached response if exists and not expired.
        
        Returns:
            dict with 'response', 'sources', 'cached_at' or None if miss.
        """
        cache_key = self._cache_key(query, language)
        now = int(time.time())
        
        try:
            entry = CacheEntry.query.get(cache_key)
            
            if entry and entry.ttl > now:
                # Cache HIT — increment hit counter
                entry.hit_count += 1
                db.session.commit()
                
                sources = []
                if entry.sources_json:
                    try:
                        sources = json.loads(entry.sources_json)
                    except json.JSONDecodeError:
                        pass
                
                return {
                    'response': entry.response,
                    'sources': sources,
                    'cached_at': entry.created_at.isoformat() if entry.created_at else None,
                    'hit_count': entry.hit_count
                }
            
            # Expired entry — delete it
            if entry:
                db.session.delete(entry)
                db.session.commit()
                
        except Exception as e:
            print(f"Cache GET error: {e}")
        
        return None  # Cache MISS
    
    def set(self, query: str, language: str, response: str, sources: list = None):
        """
        Cache a Bedrock response with TTL.
        
        Args:
            query: Original user query
            language: Response language code
            response: AI-generated response text
            sources: Optional list of source dicts for scheme cards
        """
        cache_key = self._cache_key(query, language)
        ttl_timestamp = int(time.time()) + self.ttl_seconds
        
        try:
            sources_json = json.dumps(sources) if sources else None
            
            # Upsert: delete existing then insert
            existing = CacheEntry.query.get(cache_key)
            if existing:
                db.session.delete(existing)
                db.session.flush()
            
            entry = CacheEntry(
                cache_key=cache_key,
                query=query[:200],
                language=language,
                response=response,
                sources_json=sources_json,
                ttl=ttl_timestamp,
                hit_count=0
            )
            db.session.add(entry)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Cache SET error: {e}")
    
    def cleanup_expired(self):
        """Remove expired entries (background task)."""
        with self._cleanup_lock:
            try:
                now = int(time.time())
                expired = CacheEntry.query.filter(CacheEntry.ttl < now).all()
                for entry in expired:
                    db.session.delete(entry)
                db.session.commit()
                return len(expired)
            except Exception as e:
                db.session.rollback()
                print(f"Cache cleanup error: {e}")
                return 0
    
    def stats(self) -> dict:
        """Return cache statistics."""
        try:
            total = CacheEntry.query.count()
            now = int(time.time())
            active = CacheEntry.query.filter(CacheEntry.ttl > now).count()
            total_hits = db.session.query(
                db.func.sum(CacheEntry.hit_count)
            ).scalar() or 0
            
            return {
                'total_entries': total,
                'active_entries': active,
                'expired_entries': total - active,
                'total_hits': total_hits,
                'ttl_seconds': self.ttl_seconds
            }
        except Exception as e:
            return {'error': str(e)}
