import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

from app.core.utils import setup_logging
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
    
    # Security: CORS - Allow all origins for deployment testing
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Database: SQLite only for local dev
    if not USE_DYNAMODB:
        from app.models.models import db
        try:
            from flask_migrate import Migrate
            db.init_app(app)
            Migrate(app, db)
        except ImportError:
            db.init_app(app)

    # Register Blueprints
    from app.api.routes import bp as api_bp
    app.register_blueprint(api_bp)
    
    # Register Agent Blueprint (New Architectural Layer) - Optional
    try:
        from app.agent import agent_bp
        app.register_blueprint(agent_bp, url_prefix='/agent')
    except ImportError:
        pass

    # Register v1 unified API blueprint (frontend integration layer) - Optional
    try:
        from app.api.v1_routes import v1 as v1_bp
        app.register_blueprint(v1_bp)
    except ImportError:
        pass

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
