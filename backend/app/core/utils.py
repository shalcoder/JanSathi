"""
Structured Logging & Utility Functions.
CloudWatch-compatible JSON logging with latency tracking.
"""

import logging
import time
import functools
import json
from datetime import datetime

# ============================================================
# STRUCTURED JSON LOGGING (CloudWatch-compatible)
# ============================================================

class JSONFormatter(logging.Formatter):
    """Format log records as JSON for CloudWatch Logs Insights."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        return json.dumps(log_entry, default=str)


# Configure root logger
logger = logging.getLogger('jansathi')
logger.setLevel(logging.INFO)


def setup_logging():
    """Configure structured JSON logging for the application."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    
    # Also configure the root logger for Flask 
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(h.formatter, JSONFormatter) for h in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        root.addHandler(handler)


def log_event(event_type: str, details: dict = None):
    """
    Log a structured event for CloudWatch Logs Insights.
    
    Usage:
        log_event('bedrock_query', {
            'user_id': 'user123',
            'query': 'PM Kisan scheme',
            'latency_ms': 450,
            'cache_hit': False,
            'tokens_used': 1200
        })
    
    CloudWatch Insights query:
        fields @timestamp, event, details.latency_ms
        | filter event = 'bedrock_query'
        | stats avg(details.latency_ms) as avg_latency by details.cache_hit
    """
    entry = {
        'event': event_type,
        'details': details or {},
        'timestamp': time.time()
    }
    logger.info(json.dumps(entry, default=str))


# ============================================================
# QUERY NORMALIZATION
# ============================================================

def normalize_query(query: str) -> str:
    """
    Normalize user query for caching and search.
    - Trims whitespace
    - Collapses multiple spaces
    """
    if not query:
        return ""
    cleaned = query.strip()
    # Collapse multiple spaces
    import re
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


# ============================================================
# LATENCY TRACKING DECORATOR
# ============================================================

def timed(func):
    """
    Decorator to measure and log function execution time.
    
    Usage:
        @timed
        def my_endpoint():
            ...
    
    Logs:
        {"event": "function_timing", "function": "my_endpoint", "latency_ms": 123.45}
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_event('function_timing', {
                'function': func.__name__,
                'latency_ms': round(elapsed_ms, 2),
                'status': 'success'
            })
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_event('function_timing', {
                'function': func.__name__,
                'latency_ms': round(elapsed_ms, 2),
                'status': 'error',
                'error': str(e)
            })
            raise
    return wrapper


# ============================================================
# AWS RETRY DECORATOR
# ============================================================

def retry_aws(max_retries=3, backoff_factor=1):
    """
    Decorator for retrying AWS SDK calls on throttling/timeout exceptions.
    Uses exponential backoff.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    msg = str(e).lower()
                    if 'throttling' in msg or 'timeout' in msg or 'rate exceeded' in msg:
                        tries += 1
                        wait_time = backoff_factor * (2 ** (tries - 1))
                        log_event('aws_retry', {
                            'function': func.__name__,
                            'attempt': tries,
                            'max_retries': max_retries,
                            'wait_seconds': wait_time,
                            'error': str(e)
                        })
                        time.sleep(wait_time)
                    else:
                        raise e
            return func(*args, **kwargs)  # Last attempt
        return wrapper
    return decorator
