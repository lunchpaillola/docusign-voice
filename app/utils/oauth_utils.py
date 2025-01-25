import requests
import base64
import jwt
import uuid
from datetime import datetime, timedelta
from flask import current_app
from .errors import AuthError

def exchange_notion_code(code):
    """Exchange authorization code for Notion access token"""
    token_url = "https://api.notion.com/v1/oauth/token"
    
    auth = base64.b64encode(
        f"{current_app.config['OAUTH_CLIENT_ID']}:{current_app.config['OAUTH_CLIENT_SECRET']}".encode()
    ).decode()
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['NOTION_REDIRECT_URI']
    }
    
    response = requests.post(token_url, json=data, headers=headers)
    if not response.ok:
        raise AuthError(f"Failed to exchange Notion code for token: {response.text}")
        
    return response.json()

def generate_access_token():
    """Generate JWT access token"""
    payload = {
        'type': 'access_token',
        'sub': str(uuid.uuid4()),
        'email': f"{uuid.uuid4()}@test.com",
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def generate_refresh_token():
    """Generate JWT refresh token"""
    payload = {
        'type': 'refresh_token',
        'jti': str(uuid.uuid4())
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def refresh_token(refresh_token):
    """Handle token refresh"""
    try:
        payload = jwt.decode(
            refresh_token, 
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        if payload['type'] != 'refresh_token':
            raise AuthError("Invalid token type")
            
        return {
            'access_token': generate_access_token(),
            'refresh_token': generate_refresh_token(),
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
    except jwt.InvalidTokenError:
        raise AuthError("Invalid refresh token") 