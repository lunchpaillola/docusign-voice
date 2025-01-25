import jwt
import uuid
from datetime import datetime, timedelta
from flask import current_app
from .errors import AuthError

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return str(uuid.uuid4().int)[:6]

def generate_access_token(user_id):
    """Generate JWT access token"""
    payload = {
        'type': 'access_token',
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def generate_refresh_token(user_id):
    """Generate JWT refresh token"""
    payload = {
        'type': 'refresh_token',
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(days=30),
        'jti': str(uuid.uuid4())
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify a JWT token"""
    try:
        return jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")

def refresh_token(refresh_token):
    """Handle token refresh"""
    try:
        payload = verify_token(refresh_token)
        
        if payload['type'] != 'refresh_token':
            raise AuthError("Invalid token type")
            
        return {
            'access_token': generate_access_token(payload['sub']),
            'refresh_token': generate_refresh_token(payload['sub']),
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
    except jwt.InvalidTokenError:
        raise AuthError("Invalid refresh token") 