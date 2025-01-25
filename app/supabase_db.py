from supabase import create_client
from datetime import datetime, timedelta
import os
from typing import Optional, Dict
from flask import current_app

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