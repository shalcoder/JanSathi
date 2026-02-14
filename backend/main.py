import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.core.utils import setup_logging
from app.api.routes import bp as api_bp
from app.core.config import Config

# Setup Logging Early
setup_logging()

# Detect deployment mode
USE_DYNAMODB = os.getenv("USE_DYNAMODB", "false").lower() == "true"


def create_app():
    # Validate critical env vars if in production
    Config.validate()
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Security: CORS
    CORS(app, resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}})
    
    # Talisman only in non-Lambda mode (API Gateway handles HTTPS)
    if not USE_DYNAMODB:
        try:
            from flask_talisman import Talisman
            Talisman(app, content_security_policy=None)
        except ImportError:
            pass

    # Database: SQLite only for local dev
    if not USE_DYNAMODB:
        from app.models.models import db
        db.init_app(app)

    # Rate Limiting (memory storage for Lambda, file for local)
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[Config.RATELIMIT_DEFAULT],
        storage_uri="memory://" if USE_DYNAMODB else Config.RATELIMIT_STORAGE_URL,
    )

    # Register Blueprints
    app.register_blueprint(api_bp)

    # Create SQLite tables only in local dev mode
    if not USE_DYNAMODB:
        with app.app_context():
            from app.models.models import db
            db.create_all()

    return app


# Only create app at module level for local dev (Lambda uses lambda_handler.py)
if not USE_DYNAMODB:
    app = create_app()

if __name__ == '__main__':
    if USE_DYNAMODB:
        app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('NODE_ENV') != 'production'))
