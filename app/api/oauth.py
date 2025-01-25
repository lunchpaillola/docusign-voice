from flask import Blueprint, request, jsonify, render_template, current_app, redirect
from ..utils.errors import AuthError
from ..utils.oauth_utils import exchange_notion_code
from ..supabase_db import (
    store_oauth_token, 
    store_docusign_state, 
    get_docusign_state, 
    get_oauth_token_by_code
)
from urllib.parse import urlencode
import jwt
from datetime import datetime, timedelta
import uuid

oauth = Blueprint('oauth', __name__)

@oauth.route('/authorize')
def oauth_authorize():
    """
    Initial endpoint hit by DocuSign Extension.
    Stores DocuSign state and redirects to Notion for authorization.
    
    Flow:
    1. DocuSign Extension calls this endpoint
    2. We store their state and redirect_uri
    3. Redirect user to Notion authorization page
    """
    # Store DocuSign callback information for later
    state = request.args.get('state')
    store_docusign_state(state, {
        'redirect_uri': request.args.get('redirect_uri'),
        'state': state
    })
    
    # Prepare Notion OAuth parameters
    notion_params = {
        'client_id': current_app.config.get('OAUTH_CLIENT_ID'),
        'response_type': 'code',
        'owner': 'user',
        'redirect_uri': current_app.config.get('NOTION_REDIRECT_URI'),
        'state': state  # Pass through DocuSign state to maintain session
    }
    
    # Redirect to Notion's authorization page
    return redirect(f"https://api.notion.com/v1/oauth/authorize?{urlencode(notion_params)}")

@oauth.route('/notion/callback')
def notion_callback():
    """
    Handles Notion's OAuth callback after user authorizes the integration.
    
    Flow:
    1. User approves Notion access, Notion redirects here
    2. Exchange authorization code for Notion access token
    3. Store the token in Supabase
    4. Redirect back to DocuSign with our authorization code
    """
    # Validate state and get stored DocuSign parameters
    state = request.args.get('state')
    stored_state = get_docusign_state(state)
    if not stored_state:
        raise AuthError("Invalid state")
    
    # Exchange Notion code for access token
    code = request.args.get('code')
    if not code:
        raise AuthError("No authorization code received from Notion")
    
    token_data = exchange_notion_code(code)
    
    # Store Notion access token and workspace info
    store_oauth_token(
        state=state,
        notion_token=token_data['access_token'],
        workspace_id=token_data.get('workspace_id'),
        workspace_name=token_data.get('workspace_name')
    )
    
    # No need to generate auth code, just use state
    return redirect(
        f"{stored_state['params']['redirect_uri']}?code={state}&state={state}"
    )

@oauth.route('/token', methods=['POST'])
def oauth_token():
    """
    Handles token exchange and refresh requests from DocuSign.
    
    Two flows:
    1. New installation (authorization_code):
       - DocuSign sends code from callback
       - We verify state and return Notion token
       - If no token found, return error so user can authorize Notion
    
    2. Existing installation (refresh_token):
       - DocuSign sends refresh token
       - We decode and return the Notion token
    """
    grant_type = request.form.get('grant_type')
    
    if grant_type == 'authorization_code':
        code = request.form.get('code')
        token_data = get_oauth_token_by_code(code)
        
        if not token_data:
            # This is a new installation that needs Notion auth
            print("🔄 New installation - Notion authorization required")
            raise AuthError("Please authorize Notion access first")
            
        print(f"✅ Found existing installation for workspace: {token_data.get('workspace_name')}")
        
        # Create refresh token that encodes the Notion token
        refresh_token = jwt.encode(
            {
                'notion_token': token_data.get('notion_token'),
                'exp': datetime.utcnow() + timedelta(days=365)
            },
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
            
        return jsonify({
            'access_token': token_data.get('notion_token'),
            'token_type': 'Bearer',
            'refresh_token': refresh_token,
            'expires_in': 3600,
            'workspace_id': token_data.get('workspace_id'),
            'workspace_name': token_data.get('workspace_name')
        })
    
    elif grant_type == 'refresh_token':
        # Handle refresh token flow
        refresh_token = request.form.get('refresh_token')
        if not refresh_token:
            raise AuthError("Missing refresh token")
            
        try:
            # Decode refresh token to get original Notion token
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            return jsonify({
                'access_token': payload['notion_token'],
                'token_type': 'Bearer',
                'refresh_token': refresh_token,  # Return same refresh token
                'expires_in': 3600  # Required by DocuSign
            })
            
        except jwt.InvalidTokenError:
            raise AuthError("Invalid refresh token")
    
    raise AuthError("Invalid grant type") 