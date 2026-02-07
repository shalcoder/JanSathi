import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Production configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///jansathi.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # API Rate Limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"

    @staticmethod
    def validate():
        """Ensure critical env vars are set in production."""
        if os.environ.get('NODE_ENV') == 'production':
            required = ['SECRET_KEY', 'DATABASE_URL', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
            for var in required:
                if not os.environ.get(var):
                    raise RuntimeError(f"Missing required environment variable: {var}")
