"""
Layer 2 Ingestion: Ingestion and Normalization Data Structures.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class StructuredInput(BaseModel):
    """
    Structured Input representing the normalized, verified intention of a UnifiedEventObject.
    This aligns with Layer 2 of the Agentic Civic Automation Architecture.
    """
    intent_candidate: str = Field(description="The initially detected intent classification")
    slots_detected: Dict[str, Any] = Field(default_factory=dict, description="Extracted entity key-value pairs")
    confidence: float = Field(default=1.0, description="Overall confidence of ingestion (ASR * Intent)")
    is_pii_masked: bool = Field(default=False, description="Whether PII was detected and masked")
    
    # Normalized message output
    clean_message: str = Field(description="The normalized user text")
    
    # Carried over or enhanced context
    user_context: Dict[str, Any] = Field(default_factory=dict)
