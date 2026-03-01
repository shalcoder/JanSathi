import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.core.utils import setup_logging
from app.core.config import Config
from app.core.middleware import register_middleware

# Setup Logging Early
setup_logging()

# Detect deployment mode
USE_DYNAMODB = os.getenv("USE_DYNAMODB", "false").lower() == "true"


def create_app():
    # Validate critical env vars if in production
    Config.validate()
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Security: CORS - Allow all origins for deployment testing
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
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
        from flask_migrate import Migrate
        db.init_app(app)
        Migrate(app, db)

    # Rate Limiting (memory storage for Lambda, file for local)
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[Config.RATELIMIT_DEFAULT],
        storage_uri="memory://" if USE_DYNAMODB else Config.RATELIMIT_STORAGE_URL,
    )
    # Expose limiter on app so blueprints can reference it
    app.limiter = limiter

    # Register correlation-ID + lifecycle logging middleware
    register_middleware(app)

    # Register Agent Blueprint (New Architectural Layer)
    from app.agent import agent_bp
    app.register_blueprint(agent_bp, url_prefix='/agent')

    # Register API Blueprints
    from app.api.v1_routes import v1 as v1_bp
    from app.api.profile_routes import profile_bp
    
    app.register_blueprint(v1_bp)
    app.register_blueprint(profile_bp)


    # Create SQLite tables only in local dev mode
    if not USE_DYNAMODB:
        with app.app_context():
            from app.models.models import db
            db.create_all()

    return app


# Create app for both local and production
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('NODE_ENV') != 'production'))
