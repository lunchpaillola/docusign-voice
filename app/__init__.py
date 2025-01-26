from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables first, before any other imports
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'
load_dotenv(env_path)

# Now import routes after environment is loaded
from .api.verify import verify
from .api.oauth import oauth

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(verify, url_prefix='/api')
    app.register_blueprint(oauth, url_prefix='/api')
    
    return app 