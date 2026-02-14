import logging
import time
import functools
import json
import hashlib
import typing
from uuid import uuid4
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


def log_event(event_type: str, details: typing.Optional[typing.Dict[str, typing.Any]] = None):
    """
    Log a structured event for CloudWatch Logs Insights.
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
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_event('function_timing', {
                'function': func.__name__,
                'latency_ms': float(f"{elapsed_ms:.2f}"),
                'status': 'success'
            })
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_event('function_timing', {
                'function': func.__name__,
                'latency_ms': float(f"{elapsed_ms:.2f}"),
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

# ============================================================
# AWS X-RAY SIMULATION (Distributed Tracing)
# ============================================================

def xray_traced(segment_name: str):
    """
    Decorator to simulate AWS X-Ray subsegments for distributed tracing.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t_obj = uuid4()
            hex_id = str(t_obj.hex)
            trace_id = f"1-{hex(int(time.time()))[2:]}-{hex_id[:24]}"
            start = time.perf_counter()
            log_event('xray_segment_start', {
                'trace_id': trace_id,
                'segment': segment_name,
                'function': func.__name__
            })
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start) * 1000
                log_event('xray_segment_end', {
                    'trace_id': trace_id,
                    'segment': segment_name,
                    'latency_ms': float(f"{elapsed:.2f}"),
                    'status': 'OK'
                })
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start) * 1000
                log_event('xray_segment_end', {
                    'trace_id': trace_id,
                    'segment': segment_name,
                    'latency_ms': float(f"{elapsed:.2f}"),
                    'status': 'Fault',
                    'error': str(e)
                })
                raise
        return wrapper
    return decorator


# ============================================================
# AI QUALITY & DRIFT MONITORING
# ============================================================

class QualityMonitor:
    """
    Tracks AI response quality and flags drift from performance baselines.
    Baseline Accuracy Target: 90%
    """
    
    @staticmethod
    def log_prediction(query: str, confidence: float, provenance: str):
        """Log metadata for SageMaker Model Monitor and QuickSight."""
        log_event('ai_quality_metric', {
            'query_hash': hashlib.md5(query.encode()).hexdigest(),
            'confidence': confidence,
            'provenance': provenance,
            'is_low_confidence': confidence < 0.6,
            'baseline_drift': confidence < 0.9
        })
        
        if confidence < 0.6:
            logger.warning(f"Low confidence AI response detected [{confidence}]. Flagging for human audit.")

