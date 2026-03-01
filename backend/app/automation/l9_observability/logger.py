"""
Layer 9 Observability: Structured Logging.
"""
import logging
import json
import uuid
import time
from typing import Any, Dict

class StructuredLogger:
    """
    Structured JSON Logger that captures correlation IDs and layer traces 
    for AWS CloudWatch ingestion. Enforces Layer 9 Observability.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            
    def _log(self, level: int, msg: str, layer: str, session_id: str, extra: Dict[str, Any] = None):
        if extra is None:
            extra = {}
            
        trace_id = str(uuid.uuid4())
        
        log_entry = {
            "timestamp": time.time(),
            "layer": layer,
            "session_id": session_id,
            "trace_id": trace_id,
            "level": logging.getLevelName(level),
            "message": msg,
            "metrics": extra
        }
        
        # In a real environment, this goes to stdout as JSON for CloudWatch
        self.logger.log(level, json.dumps(log_entry))
        
    def info(self, msg: str, layer: str = "Unknown", session_id: str = "Unknown", **kwargs):
        self._log(logging.INFO, msg, layer, session_id, kwargs)
        
    def error(self, msg: str, layer: str = "Unknown", session_id: str = "Unknown", **kwargs):
        self._log(logging.ERROR, msg, layer, session_id, kwargs)
        
    def warn(self, msg: str, layer: str = "Unknown", session_id: str = "Unknown", **kwargs):
        self._log(logging.WARNING, msg, layer, session_id, kwargs)

# Singleton factory
def get_structured_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)
