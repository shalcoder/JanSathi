"""
Input Validation & Prompt Injection Defense.

Blocks common prompt injection patterns, enforces length limits,
sanitizes HTML/script tags, and validates language codes.
"""

import re
import html

# ============================================================
# CONFIGURATION
# ============================================================

MAX_QUERY_LENGTH = 500
SUPPORTED_LANGUAGES = {'hi', 'en', 'kn', 'ta', 'te', 'bn', 'mr', 'gu', 'ml', 'pa', 'or'}

# Prompt injection patterns (case-insensitive)
BLOCKED_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions',
    r'ignore\s+the\s+above',
    r'disregard\s+(all\s+)?previous',
    r'system:\s*you\s+are',
    r'you\s+are\s+now\s+a',
    r'new\s+instructions:',
    r'override\s+instructions',
    r'forget\s+(all\s+)?previous',
    r'pretend\s+you\s+are',
    r'act\s+as\s+if',
    r'jailbreak',
    r'DAN\s+mode',
    r'developer\s+mode',
    r'<script\b',
    r'javascript:',
    r'UNION\s+SELECT',
    r'DROP\s+TABLE',
    r'INSERT\s+INTO',
    r'DELETE\s+FROM',
    r';\s*--',
    r'eval\s*\(',
    r'exec\s*\(',
]

# Compile patterns for performance
_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

class ValidationError(Exception):
    """Raised when input fails validation."""
    def __init__(self, message: str, error_code: str = 'VALIDATION_ERROR'):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class PromptInjectionError(ValidationError):
    """Raised when prompt injection is detected."""
    def __init__(self, message: str = "Potentially harmful input detected."):
        super().__init__(message, error_code='PROMPT_INJECTION')


def validate_query(query: str) -> str:
    """
    Validate and sanitize a user query.
    
    1. Check for empty input
    2. Enforce length limits
    3. Sanitize HTML entities
    4. Block prompt injection patterns
    5. Strip excessive whitespace
    
    Args:
        query: Raw user input string
        
    Returns:
        Cleaned, validated query string
        
    Raises:
        ValidationError: If query is empty or too long
        PromptInjectionError: If injection pattern detected
    """
    if not query or not query.strip():
        raise ValidationError("Query cannot be empty.", 'EMPTY_QUERY')
    
    # Strip and truncate
    cleaned = query.strip()
    
    if len(cleaned) > MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Query too long ({len(cleaned)} chars). Maximum is {MAX_QUERY_LENGTH}.",
            'QUERY_TOO_LONG'
        )
    
    # Sanitize HTML
    cleaned = sanitize_input(cleaned)
    
    # Check for prompt injection
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(cleaned):
            raise PromptInjectionError()
    
    # Normalize whitespace (collapse multiple spaces)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def sanitize_input(text: str) -> str:
    """
    Strip HTML tags and decode entities.
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text with HTML removed
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    return text


def validate_language(language: str) -> str:
    """
    Validate language code against supported languages.
    
    Args:
        language: ISO language code
        
    Returns:
        Validated language code (defaults to 'hi' if invalid)
    """
    if not language:
        return 'hi'
    
    lang = str(language).strip().lower()[:5]
    
    if lang not in SUPPORTED_LANGUAGES:
        return 'hi'  # Default to Hindi
    
    return lang


def validate_user_id(user_id: str) -> str:
    """
    Validate and sanitize user ID.
    
    Args:
        user_id: User identifier string
        
    Returns:
        Sanitized user ID
    """
    if not user_id:
        return 'anonymous'
    
    # Allow only alphanumeric, hyphens, underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_\-]', '', user_id)
    
    if not cleaned:
        return 'anonymous'
    
    return str(cleaned)[:100]  # Max 100 chars
