from flask import Blueprint, request, jsonify, current_app
from ..utils.errors import AuthError
import base64
import os
import json
import requests
from string import Template
from datetime import datetime

# Get DocuSign URL base from environment
DOCUSIGN_URL_BASE = os.getenv('DOCUSIGN_URL_BASE', 'apps-d.docusign.com')

archive = Blueprint('archive', __name__)

@archive.route('/archive', methods=['POST'])
def archive_files():
    """
    Handle DocuSign file archive requests
    
    Expected request:
    {
        "files": [{
            "name": "Agreement {{test-var-1}} about {{test-var-2}}",
            "content": "SSBhZ3JlZSE=",  # Base64 encoded file
            "contentType": "bytes",
            "path": "Folder1/Folder2/",
            "pathTemplateValues": ["1", "Contract negotiation"]
        }]
    }
    """
    try:
        print("\n=== Archive Request ===")
        print("Headers:", dict(request.headers))
        data = request.get_json()
        print("Request Data:", json.dumps(data, indent=2))
        
        if not data or 'files' not in data:
            return jsonify({
                "message": "No files provided"
            }), 400
            
        # Get Notion token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "No authorization token provided"}), 401
        notion_token = auth_header.split(' ')[1]
        
        # Get or create database
        database_id = get_default_database(notion_token)
        if not database_id:
            return jsonify({"message": "Could not find or create database"}), 500
            
        # Process each file
        processed_files = []
        failed_files = []
        for file in data['files']:
            # Replace template variables in filename
            filename = file['name']
            if 'pathTemplateValues' in file:
                for i, value in enumerate(file['pathTemplateValues']):
                    filename = filename.replace(f"{{{{Get Signatures.envelopeId}}}}", value) if i == 0 else filename
            
            print(f"\n=== Creating Page ===")
            print(f"Processed Filename: {filename}")
            
            # Create page first
            page_data = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Title": {
                        "title": [{"type": "text", "text": {"content": filename}}]
                    },
                    "Contract Status": {
                        "select": {"name": "Archived"}
                    },
                    "Archive Date": {
                        "date": {"start": datetime.now().isoformat()}
                    },
                    "Document Type": {
                        "select": {"name": "Agreement"}
                    },
                    "File Name": {
                        "rich_text": [{"type": "text", "text": {"content": filename}}]
                    },
                    "File Path": {
                        "rich_text": [{"type": "text", "text": {"content": file.get('path', '')}}]
                    },
                    "Department": {
                        "rich_text": [{"type": "text", "text": {"content": ""}}]
                    },
                    "File URL": {
                        "url": f"https://{DOCUSIGN_URL_BASE}/send/documents/details/{file.get('path', '')}"
                    }
                }
            }

            # Create the page
            headers = {
                'Authorization': f'Bearer {notion_token}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.notion.com/v1/pages',
                headers=headers,
                json=page_data
            )

            if response.status_code == 200:
                processed_files.append(filename)
                print(f"✅ Created page for {filename}")
            else:
                print(f"❌ Failed to create page: {response.text}")
                failed_files.append(filename)
                continue
        
        # Return appropriate response based on success/failure
        if not processed_files and failed_files:
            return jsonify({
                "message": f"Failed to upload {len(failed_files)} file(s)",
                "failed": failed_files
            }), 500
        elif failed_files:
            return jsonify({
                "message": f"Partially successful: {len(processed_files)} uploaded, {len(failed_files)} failed",
                "failed": failed_files
            }), 207
            
        return jsonify({
            "message": f"{len(processed_files)} file{'s' if len(processed_files) != 1 else ''} successfully uploaded"
        }), 200
            
    except Exception as e:
        print(f"❌ Archive Error: {str(e)}")
        return jsonify({
            "message": f"Something went wrong: {str(e)}"
        }), 500

def get_default_database(notion_token):
    """Get or create DocuSign Contract Archive database"""
    headers = {
        'Authorization': f'Bearer {notion_token}',
        'Notion-Version': '2022-06-28'
    }
    
    # Search for "DocuSign Contract Archive" database
    response = requests.post(
        'https://api.notion.com/v1/search',
        headers=headers,
        json={
            "query": "DocuSign Contract Archive",
            "filter": {
                "value": "database",
                "property": "object"
            }
        }
    )
    
    databases = response.json().get('results', [])
    if databases:
        print("✅ Found existing DocuSign Contract Archive database")
        return databases[0]['id']
    
    # Create database if not found
    print("🔄 Creating new DocuSign Contract Archive database...")
    response = requests.post(
        'https://api.notion.com/v1/databases',
        headers=headers,
        json={
            "title": [{"type": "text", "text": {"content": "DocuSign Contract Archive"}}],
            "properties": {
                "Title": {"type": "title", "title": {}},
                "Contract Status": {"type": "select", "select": {
                    "options": [
                        {"name": "Archived", "color": "green"}
                    ]
                }},
                "Archive Date": {"type": "date", "date": {}},
                "Completion Date": {"type": "date", "date": {}},
                "Document Type": {"type": "select", "select": {
                    "options": [
                        {"name": "Agreement", "color": "blue"}
                    ]
                }},
                "Envelope ID": {"type": "rich_text", "rich_text": {}},
                "Signers": {"type": "rich_text", "rich_text": {}},
                "File URL": {"type": "url", "url": {}},
                "File Name": {"type": "rich_text", "rich_text": {}},
                "File Path": {"type": "rich_text", "rich_text": {}},
                "Department": {"type": "rich_text", "rich_text": {}},
                "Notes": {"type": "rich_text", "rich_text": {}},
                "Tags": {"type": "rich_text", "rich_text": {}}
            }
        }
    )
    
    if response.status_code == 200:
        print("✅ Created new DocuSign Contract Archive database")
        return response.json()['id']
    else:
        print("❌ Failed to create database:", response.text)
        return None 