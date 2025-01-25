from flask import Flask
from flask_cors import CORS
from .api.oauth import oauth  # Only import oauth blueprint
from .api.dataio import dataio  # Import from new location
from .api.archive import archive  # Add this import
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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
    
    # Register oauth blueprint only once
    app.register_blueprint(oauth, url_prefix='/oauth')  # This makes routes start with /oauth
    app.register_blueprint(dataio, url_prefix='/api/dataio')  # Add this line
    app.register_blueprint(archive, url_prefix='/api')  # Add this line
    
    return app 