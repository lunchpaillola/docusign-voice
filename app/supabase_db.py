from supabase import create_client
from datetime import datetime, timedelta
import os
from typing import Optional, Dict
from flask import current_app
import uuid

def get_supabase_client():
    """Get Supabase client when needed"""
    supabase_url = current_app.config.get('SUPABASE_URL') or os.getenv('SUPABASE_URL')
    supabase_key = current_app.config.get('SUPABASE_KEY') or os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and Key are required")
        
    return create_client(supabase_url, supabase_key)

def store_oauth_token(
    state: str,
    notion_token: str,
    workspace_id: Optional[str] = None,
    workspace_name: Optional[str] = None
) -> Dict:
    """Store OAuth token in Supabase"""
    supabase = get_supabase_client()
    data = {
        'state': state,
        'notion_token': notion_token,
        'workspace_id': workspace_id,
        'workspace_name': workspace_name,
        'created_at': datetime.utcnow().isoformat()
    }
    return supabase.table('oauth_tokens').insert(data).execute()

def get_oauth_token(state: str) -> Optional[Dict]:
    """Get OAuth token from Supabase"""
    supabase = get_supabase_client()
    response = supabase.table('oauth_tokens')\
        .select('*')\
        .eq('state', state)\
        .execute()
    return response.data[0] if response.data else None

# Only used in these specific OAuth flows:
# 1. When storing Notion token during OAuth
# 2. When storing DocuSign state
# 3. When retrieving tokens during verification

def store_docusign_state(state: str, params: Dict) -> Dict:
    """Store DocuSign state in Supabase"""
    try:
        supabase = get_supabase_client()
        data = {
            'state': state,
            'params': params,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        result = supabase.table('docusign_states').insert(data).execute()
        return result
        
    except Exception as e:
        print(f"Error type: {type(e)}")
        raise

def get_docusign_state(state: str) -> Optional[Dict]:
    """Get DocuSign state from Supabase"""
    response = get_supabase_client().table('docusign_states')\
        .select('*')\
        .eq('state', state)\
        .execute()
    return response.data[0] if response.data else None

def get_oauth_token_by_code(code):
    """
    Get OAuth token using state (code parameter is actually the state).
    Keeping function name for compatibility.
    """
    try:
        supabase = get_supabase_client()
        token_response = supabase.table('oauth_tokens')\
            .select("*")\
            .eq('state', code)\
            .execute()
        
        if not token_response.data:
            print("❌ No token found for state:", code)
            return None
            
        return token_response.data[0]
        
    except Exception as e:
        print("❌ Error getting token:", str(e))
        return None

def update_last_used(state: str):
    """Update the last_used timestamp for an installation"""
    try:
        supabase = get_supabase_client()
        return supabase.table('oauth_tokens')\
            .update({'last_used': datetime.utcnow().isoformat()})\
            .eq('state', state)\
            .execute()
    except Exception as e:
        print(f"Error updating last_used: {str(e)}")

def store_verification_code(phone, code):
    """Store a new verification code"""
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    query = """
    INSERT INTO verification_codes (phone, code, expires_at)
    VALUES (:phone, :code, :expires_at)
    """
    
    current_app.db.execute(query, {
        'phone': phone,
        'code': code,
        'expires_at': expires_at
    })

def verify_code(phone, code):
    """Verify a code and return True if valid"""
    query = """
    SELECT id FROM verification_codes 
    WHERE phone = :phone 
    AND code = :code 
    AND expires_at > NOW() 
    AND verified = FALSE
    """
    
    result = current_app.db.execute(query, {
        'phone': phone,
        'code': code
    }).fetchone()
    
    if result:
        # Mark code as verified
        current_app.db.execute(
            "UPDATE verification_codes SET verified = TRUE WHERE id = :id",
            {'id': result[0]}
        )
        return True
    return False

def create_or_get_user(phone):
    """Get existing user or create new one"""
    query = """
    INSERT INTO users (id, phone)
    VALUES (:id, :phone)
    ON CONFLICT (phone) DO UPDATE
    SET last_login = NOW()
    RETURNING id
    """
    
    user_id = str(uuid.uuid4())
    result = current_app.db.execute(query, {
        'id': user_id,
        'phone': phone
    }).fetchone()
    
    return result[0]

def store_user_session(user_id, refresh_token):
    """Store a new user session"""
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    query = """
    INSERT INTO user_sessions (user_id, refresh_token, expires_at)
    VALUES (:user_id, :refresh_token, :expires_at)
    """
    
    current_app.db.execute(query, {
        'user_id': user_id,
        'refresh_token': refresh_token,
        'expires_at': expires_at
    })

def store_oauth_state(state, data):
    """Store OAuth state"""
    supabase = get_supabase_client()
    return supabase.table('oauth_tokens').insert({
        'state': state,
        'redirect_uri': data['redirect_uri'],
        # Don't try to store docusign_state yet
        'created_at': datetime.utcnow().isoformat()
    }).execute()

def get_oauth_state(state):
    """Get OAuth state"""
    supabase = get_supabase_client()
    response = supabase.table('oauth_tokens')\
        .select('*')\
        .eq('state', state)\
        .execute()
    if not response.data:
        return None
    
    data = response.data[0]
    return {
        'redirect_uri': data.get('redirect_uri'),
        # Return None for docusign_state
        'docusign_state': None
    } 