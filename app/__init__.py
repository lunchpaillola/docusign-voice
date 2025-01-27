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
from .api.dataio import dataio
from .api.archive import archive

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {  # Allow all routes
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Load config
    app.config.from_object('config.Config')
    
    # Set Flask secret key for sessions
    app.secret_key = os.getenv('JWT_SECRET_KEY')
    
    # Load config from environment
    app.config.update(
        AUTHORIZATION_CODE=os.getenv('AUTHORIZATION_CODE'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
        OAUTH_CLIENT_ID=os.getenv('OAUTH_CLIENT_ID'),
        OAUTH_CLIENT_SECRET=os.getenv('OAUTH_CLIENT_SECRET'),
        NOTION_REDIRECT_URI=os.getenv('NOTION_REDIRECT_URI'),
        SUPABASE_URL=os.getenv('SUPABASE_URL'),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY')
    )
    
    # Register blueprints with correct prefixes
    app.register_blueprint(oauth, url_prefix='/oauth')
    app.register_blueprint(verify, url_prefix='/api')
    app.register_blueprint(dataio, url_prefix='/api/dataio')
    app.register_blueprint(archive, url_prefix='/api')
    
    return app 