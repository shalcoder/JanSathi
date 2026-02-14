"""
Security Utilities — PII anonymization, content moderation, response sanitization.
Production-grade security layer for JanSathi.
"""

import re
import hashlib
import hmac
import os

# ============================================================
# PII ANONYMIZATION
# ============================================================

# Salt for HMAC (use environment variable in production)
_PII_SALT = os.getenv('PII_SALT', 'jansathi-default-salt-change-in-prod').encode('utf-8')

# PII detection patterns
AADHAAR_PATTERN = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+91[\s-]?)?[6-9]\d{9}\b')
PAN_PATTERN = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
BANK_ACCOUNT_PATTERN = re.compile(r'\b\d{9,18}\b')  # Bank account numbers


def anonymize_aadhaar(aadhaar: str) -> str:
    """
    Hash Aadhaar number with HMAC-SHA256 for safe storage.
    
    Args:
        aadhaar: Raw Aadhaar number (12 digits)
        
    Returns:
        Hashed token like 'AADHAAR_a1b2c3d4e5f6'
    """
    clean = re.sub(r'\s', '', aadhaar)
    hashed = hmac.new(_PII_SALT, clean.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"AADHAAR_{hashed[:16]}"


def anonymize_phone(phone: str) -> str:
    """Mask phone number, keeping last 4 digits."""
    clean = re.sub(r'[\s\-+]', '', phone)
    if len(clean) >= 4:
        return f"PHONE_XXXX{clean[-4:]}"
    return "PHONE_MASKED"


def strip_pii_from_text(text: str) -> str:
    """
    Remove PII from text before logging or storing.
    Replaces Aadhaar, phone, PAN, email, and bank account numbers.
    
    Args:
        text: Input text potentially containing PII
        
    Returns:
        Text with PII replaced by masked tokens
    """
    if not text:
        return text
    
    # Replace Aadhaar numbers
    text = AADHAAR_PATTERN.sub('[AADHAAR_MASKED]', text)
    
    # Replace phone numbers  
    text = PHONE_PATTERN.sub('[PHONE_MASKED]', text)
    
    # Replace PAN numbers
    text = PAN_PATTERN.sub('[PAN_MASKED]', text)
    
    # Replace email addresses
    text = EMAIL_PATTERN.sub('[EMAIL_MASKED]', text)
    
    return text


# ============================================================
# CONTENT MODERATION
# ============================================================

# Toxic/harmful keywords (basic filter — use AWS Comprehend for production)
TOXIC_KEYWORDS = {
    'hack', 'exploit', 'steal', 'fraud', 'scam', 'fake',
    'illegal', 'abuse', 'violence', 'threat', 'bomb',
    'weapon', 'drug', 'narcotic', 'terror'
}

SENSITIVE_TOPICS = {
    'religion', 'caste', 'political party', 'election manipulation',
    'vote buying', 'bribery'
}


def moderate_content(text: str) -> dict:
    """
    Basic content moderation check.
    
    Returns:
        dict with 'is_safe' (bool), 'flags' (list of flagged items),
        'confidence' (float 0-1)
    """
    if not text:
        return {'is_safe': True, 'flags': [], 'confidence': 1.0}
    
    text_lower = text.lower()
    flags = []
    
    # Check toxic keywords
    for keyword in TOXIC_KEYWORDS:
        if keyword in text_lower:
            flags.append(f'toxic:{keyword}')
    
    # Check sensitive topics
    for topic in SENSITIVE_TOPICS:
        if topic in text_lower:
            flags.append(f'sensitive:{topic}')
    
    is_safe = len(flags) == 0
    confidence = 1.0 if is_safe else max(0.3, 1.0 - (len(flags) * 0.15))
    
    return {
        'is_safe': is_safe,
        'flags': flags,
        'confidence': confidence
    }


def sanitize_ai_response(response: str) -> str:
    """
    Sanitize AI response before sending to user.
    - Strip any accidentally leaked PII
    - Remove internal system markers
    - Clean formatting
    
    Args:
        response: Raw AI-generated response
        
    Returns:
        Cleaned response safe for display
    """
    if not response:
        return response
    
    # Strip PII
    response = strip_pii_from_text(response)
    
    # Remove any system/internal markers that LLM might output
    system_markers = [
        r'\[SYSTEM\].*?\[/SYSTEM\]',
        r'\[INTERNAL\].*?\[/INTERNAL\]',
        r'<system>.*?</system>',
        r'Human:.*?(?=\n|$)',
        r'Assistant:',
    ]
    
    for marker in system_markers:
        response = re.sub(marker, '', response, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up excessive newlines
    response = re.sub(r'\n{3,}', '\n\n', response)
    
    return response.strip()
