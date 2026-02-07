import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from app.models.models import db
from app.core.utils import setup_logging
from app.api.routes import bp as api_bp
from app.core.config import Config

# Setup Logging Early
setup_logging()

def create_app():
    # Validate critical env vars if in production
    Config.validate()
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Security: CORS and Talisman
    CORS(app, resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}})
    Talisman(app, content_security_policy=None) # CSP managed by frontend if needed

    db.init_app(app)

    # Rate Limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[Config.RATELIMIT_DEFAULT],
        storage_uri=Config.RATELIMIT_STORAGE_URL,
    )

    # Register Blueprints
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('NODE_ENV') != 'production'))
