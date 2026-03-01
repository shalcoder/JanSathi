"""
Layer 1 Integration: Standardizing incoming requests across all transports.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class UnifiedEventObject(BaseModel):
    """
    Unified Event Object representing a request from any channel.
    This aligns with Layer 1 of the Agentic Civic Automation Architecture.
    """
    session_id: str = Field(description="Unique session identifier for the workflow")
    channel: str = Field(default="ivr", description="Channel of entry: ivr, whatsapp, web")
    language: str = Field(default="hi", description="Language code: hi, en, ta, kn")
    message: str = Field(default="", description="The transcribed text or raw input message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="ISO-8601 UTC timestamp")
    
    # Context injected by early lookup (e.g. caller DB match)
    user_context: Dict[str, Any] = Field(default_factory=dict, description="Metadata like caller phone, profile")
    
    # Metadata for specific channels
    channel_metadata: Dict[str, Any] = Field(default_factory=dict, description="Channel specific data (DTMF, Confidence)")
    
    # Security/Consent flags
    consent_given: bool = Field(default=False, description="Whether the user explicitly consented")

    def __str__(self):
        return f"[{self.channel.upper()}] {self.session_id} - {self.language}: '{self.message}'"
