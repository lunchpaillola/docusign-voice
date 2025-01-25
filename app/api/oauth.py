from flask import Blueprint, request, jsonify, render_template, current_app, redirect, url_for
from ..utils.errors import AuthError
from ..utils.oauth_utils import generate_access_token, generate_refresh_token, verify_token
from ..supabase_db import store_oauth_state, get_oauth_state
import jwt
from datetime import datetime, timedelta
import uuid
import base64
import logging
from flask_cors import cross_origin

oauth = Blueprint('oauth', __name__)
logger = logging.getLogger(__name__)

def verify_client_credentials():
    """Verify the client credentials from Authorization header"""
    auth_header = request.headers.get('Authorization')
    logger.info(f"Verifying client credentials. Auth header present: {bool(auth_header)}")
    
    if not auth_header or not auth_header.startswith('Basic '):
        logger.error("Missing or invalid Authorization header format")
        raise AuthError("Missing or invalid Authorization header")
    
    try:
        # Decode base64 credentials
        encoded_credentials = auth_header.split(' ')[1]
        decoded = base64.b64decode(encoded_credentials).decode('utf-8')
        client_id, client_secret = decoded.split(':')
        
        logger.info(f"Attempting to verify client_id: {client_id[:8]}...")
        
        # Verify against configured credentials
        if (client_id != current_app.config['OAUTH_CLIENT_ID'] or 
            client_secret != current_app.config['OAUTH_CLIENT_SECRET']):
            logger.error("Invalid client credentials provided")
            raise AuthError("Invalid client credentials")
            
        logger.info("Client credentials verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying credentials: {str(e)}")
        raise AuthError("Invalid client credentials format")

@oauth.route('/authorize')
def oauth_authorize():
    """Initial authorization endpoint - show consent button"""
    logger.info("\n=== OAuth Authorize Request ===")
    redirect_uri = request.args.get('redirect_uri')
    state = request.args.get('state')
    
    if not redirect_uri:
        raise AuthError("Missing redirect_uri")
        
    # Use authorization code from config like reference implementation
    code = current_app.config['AUTHORIZATION_CODE']
    
    # Render consent page with variables for redirect
    return render_template('consent.html', 
        redirectUri=redirect_uri,
        code=code,
        state=state
    )

@oauth.route('/verify')
def consent_page():
    """Show authorization consent page"""
    state = request.args.get('state')
    logger.info(f"Consent page requested with state: {state}")
    
    if not state:
        logger.error("Missing state parameter")
        raise AuthError("Missing state parameter")
    
    return render_template('verify.html', state=state)

@oauth.route('/verify/submit', methods=['POST'])
def submit_consent():
    """Handle authorization consent submission"""
    logger.info("\n=== Submit Consent Request ===")
    logger.info(f"Full Request URL: {request.url}")
    logger.info(f"Base URL: {request.base_url}")
    logger.info(f"Host URL: {request.host_url}")
    
    state = request.form.get('state')
    logger.info("\n=== Consent Submission START ===")
    logger.info(f"Our state from form: {state}")
    logger.info(f"Request form data: {dict(request.form)}")
    
    stored_state = get_oauth_state(state)
    logger.info(f"Full stored state object: {stored_state}")
    
    if not stored_state:
        logger.error(f"Invalid state: {state}")
        raise AuthError("Invalid state")
    
    if 'redirect_uri' not in stored_state:
        logger.error(f"Missing redirect_uri in stored state: {stored_state}")
        raise AuthError("Invalid state data")
    
    # Get DocuSign's original state
    docusign_state = stored_state.get('docusign_state')
    
    # Build callback URL
    callback_url = f"{stored_state['redirect_uri']}?code={state}&state={docusign_state if docusign_state else state}"
    
    logger.info("\n=== Callback Details ===")
    logger.info(f"DocuSign's original state: {docusign_state}")
    logger.info(f"State we're sending back: {state}")
    logger.info(f"Full callback URL: {callback_url}")
    logger.info(f"Our token endpoint that DocuSign should call: {url_for('oauth.oauth_token', _external=True, _scheme='https')}")
    
    try:
        # Add response logging
        logger.info("\n=== Creating Redirect Response ===")
        response = redirect(callback_url)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        logger.info("=== About to Return Redirect ===")
        
        # Try to force flush the logs
        import sys
        sys.stdout.flush()
        
        return response
    except Exception as e:
        logger.error(f"\n=== Redirect Error ===")
        logger.error(f"Failed to redirect: {str(e)}")
        raise

@oauth.route('/token', methods=['POST'])
def oauth_token():
    """Handle token exchange - similar to reference generateAuthToken"""
    logger.info("\n=== Token Request ===")
    
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    
    if grant_type == 'authorization_code':
        if code != current_app.config['AUTHORIZATION_CODE']:
            raise AuthError("Invalid authorization code")
            
        # Generate tokens like reference implementation
        access_token = jwt.encode({
            'type': 'access_token',
            'sub': str(uuid.uuid4()),
            'email': f"{uuid.uuid4()}@test.com",
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, current_app.config['JWT_SECRET_KEY'])
        
        refresh_token = jwt.encode({
            'type': 'refresh_token'
        }, current_app.config['JWT_SECRET_KEY'])
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token
        })
        
    elif grant_type == 'refresh_token':
        refresh_token = request.form.get('refresh_token')
        try:
            payload = jwt.decode(
                refresh_token, 
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            if payload['type'] != 'refresh_token':
                raise AuthError("Invalid token type")
                
            # Generate new access token
            access_token = jwt.encode({
                'type': 'access_token',
                'sub': str(uuid.uuid4()),
                'email': f"{uuid.uuid4()}@test.com",
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, current_app.config['JWT_SECRET_KEY'])
            
            return jsonify({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': refresh_token
            })
            
        except jwt.InvalidTokenError:
            raise AuthError("Invalid refresh token")
            
    raise AuthError("Invalid grant type")

@oauth.route('/test-callback')
def test_callback():
    """Test endpoint to verify redirects are working"""
    logger.info("\n=== Test Callback Hit ===")
    logger.info(f"Query params: {dict(request.args)}")
    return jsonify({
        "message": "Callback received",
        "params": dict(request.args)
    })

@oauth.route('/callback')
def oauth_callback():
    """Handle DocuSign's OAuth callback"""
    logger.info("\n=== OAuth Callback Hit ===")
    logger.info(f"Query params: {dict(request.args)}")
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        raise AuthError("Missing code or state")
    
    # Process the callback
    stored_state = get_oauth_state(state)
    if not stored_state:
        raise AuthError("Invalid state")
    
    # Return success response
    return jsonify({
        "message": "Authorization successful",
        "code": code,
        "state": state
    })

@oauth.route('/debug/state/<state>')
def debug_state(state):
    """Debug endpoint to check stored state"""
    stored = get_oauth_state(state)
    return jsonify({
        "stored_state": stored,
        "exists": bool(stored)
    }) 