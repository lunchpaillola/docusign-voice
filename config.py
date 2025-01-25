import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Environment
    NODE_ENV = os.getenv('NODE_ENV', 'development')
    PORT = int(os.getenv('PORT', 3000))
    
    # OAuth
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    AUTHORIZATION_CODE = os.getenv('AUTHORIZATION_CODE')
    
    # Redirect URIs
    NOTION_REDIRECT_URI = os.getenv('NOTION_REDIRECT_URI')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Add these to your existing Config class
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False 