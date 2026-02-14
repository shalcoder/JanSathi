"""
Application Configuration — SSM Parameter Store pattern with .env fallback.
"""

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# SECRET RETRIEVAL (SSM Parameter Store → .env fallback)
# ============================================================

_ssm_client = None

def get_secret(param_name: str, default: str = None) -> str:
    """
    Retrieve secret from AWS SSM Parameter Store (FREE tier).
    Falls back to environment variables for local development.
    
    Args:
        param_name: SSM parameter name (e.g., '/jansathi/prod/secret-key')
                    or environment variable name (e.g., 'SECRET_KEY')
        default: Default value if not found
        
    Returns:
        Secret value string
    """
    global _ssm_client
    
    # First, try environment variable (local dev)
    env_value = os.environ.get(param_name, None)
    if env_value:
        return env_value
    
    # In production, try SSM Parameter Store
    if os.environ.get('NODE_ENV') == 'production':
        try:
            if _ssm_client is None:
                _ssm_client = boto3.client('ssm', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
            response = _ssm_client.get_parameter(
                Name=param_name,
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except Exception as e:
            print(f"SSM Parameter Store fallback for '{param_name}': {e}")
    
    return default


# ============================================================
# APPLICATION CONFIG
# ============================================================

class Config:
    """Production configuration with SSM Parameter Store support."""
    
    # Flask Core
    SECRET_KEY = get_secret('SECRET_KEY', 'dev-secret-key-123')
    
    # Database
    SQLALCHEMY_DATABASE_URI = get_secret('DATABASE_URL', 'sqlite:///jansathi.db')
    DATABASE_URL = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AWS
    AWS_REGION = get_secret('AWS_REGION', 'us-east-1')
    
    # CORS
    ALLOWED_ORIGINS = get_secret('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Rate Limiting (Free Tier safe)
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Cache Configuration
    CACHE_TTL_SECONDS = int(get_secret('CACHE_TTL_SECONDS', '3600'))
    
    # Query Limits
    MAX_QUERY_LENGTH = int(get_secret('MAX_QUERY_LENGTH', '500'))
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {'hi', 'en', 'kn', 'ta', 'te', 'bn', 'mr', 'gu', 'ml', 'pa', 'or'}
    
    # Bedrock Settings
    BEDROCK_MODEL_ID = get_secret('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
    BEDROCK_MAX_TOKENS = int(get_secret('BEDROCK_MAX_TOKENS', '300'))

    @staticmethod
    def validate():
        """Ensure critical env vars are set in production."""
        if os.environ.get('NODE_ENV') == 'production':
            required = ['SECRET_KEY', 'DATABASE_URL', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
            for var in required:
                if not os.environ.get(var):
                    raise RuntimeError(f"Missing required environment variable: {var}")
