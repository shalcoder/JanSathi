import logging
import time
import functools
import json

# Configure Structured Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def setup_logging():
    """Ensure logging is configured for Lambda."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def log_event(event_type, details):
    """Log an event in JSON format for easy CloudWatch parsing."""
    entry = {
        "event": event_type,
        "details": details,
        "timestamp": time.time()
    }
    logger.info(json.dumps(entry))

def normalize_query(query):
    """
    Normalizes the user query into a clean internal format.
    - Trims whitespace
    - Converts to lowercase (optional, depending on downstream needs, but good for caching)
    """
    if not query:
        return ""
    cleaned = query.strip()
    return cleaned

def retry_aws(max_retries=3, backoff_factor=1):
    """
    Decorator for retrying AWS SDK calls on specific exceptions.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Check for throttling or timeouts in string representation
                    msg = str(e).lower()
                    if 'throttling' in msg or 'timeout' in msg or 'rate exceeded' in msg:
                        tries += 1
                        wait_time = backoff_factor * (2 ** (tries - 1))
                        logger.warning(f"Retry {tries}/{max_retries} for {func.__name__} after {wait_time}s due to: {e}")
                        time.sleep(wait_time)
                    else:
                        raise e
            return func(*args, **kwargs) # Last attempt
        return wrapper
    return decorator
