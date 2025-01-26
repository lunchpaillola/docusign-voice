from flask import Blueprint, request, jsonify, current_app
from ..utils.errors import AuthError
import logging
import json
from ..utils.vapi_client import vapi_client, create_verification_assistant
import asyncio
import os
import random

verify = Blueprint('verify', __name__)
logger = logging.getLogger(__name__)

@verify.route('/verifyPhone', methods=['POST'])
async def verify_phone():
    """
    Handle DocuSign phone verification requests
    
    Expected request:
    {
        "phoneNumber": "1234567890",
        "region": "1"
    }
    
    Response:
    {
        "verified": true/false,
        "verifyFailureReason": "reason" (optional)
    }
    """
    try:
        logger.info("\n=== Phone Verification Request ===")
        logger.info(f"Headers: {dict(request.headers)}")
        data = request.get_json()
        logger.info(f"Request Data: {json.dumps(data, indent=2)}")
        
        # Validate request data
        if not data or 'phoneNumber' not in data:
            return jsonify({
                "verified": False,
                "verifyFailureReason": "Missing phone number"
            }), 200  # Note: Always return 200 as per contract
            
        phone = data['phoneNumber']
        region = data.get('region', '1')  # Default to US/Canada
        
        # Format phone number with region code
        # Remove any non-digit characters from phone number
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Format with + and region code
        formatted_phone = f"+{region}{clean_phone}"
        logger.info(f"Formatting phone: {phone} with region {region} -> {formatted_phone}")
        
        # Validate phone format
        if not clean_phone:
            return jsonify({
                "verified": False,
                "verifyFailureReason": "Invalid phone number format"
            }), 200
        
        # Generate random 4-digit verification code
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        logger.info(f"Generated verification code {verification_code}")
        
        # Create assistant with this specific code
        assistant = await create_verification_assistant(verification_code)
        
        try:
            # Make outbound call with proper configuration
            call = await vapi_client.calls.create(
                assistant=assistant,
                to_number=formatted_phone,
                from_number=os.getenv('VAPI_PHONE_NUMBER'),
                type="outboundPhoneCall",
                phone_call_transport="pstn",  # Use standard phone network
                name=f"DocuSign Verification {verification_code}",
                recordingEnabled=True,
                transcriptEnabled=True
            )
            
            logger.info(f"Call initiated with ID: {call.id}")
            
            # Wait for call completion
            result = await call.wait_for_completion()
            
            # Log the transcript
            logger.info("\n=== Call Transcript ===")
            for message in result.get('messages', []):
                role = message.get('role', 'unknown')
                content = message.get('content', '')
                logger.info(f"{role}: {content}")
            
            # Check last assistant message for verification status
            verified = any(
                "This call is verified" in msg.get('content', '')
                for msg in result.get('messages', [])
                if msg.get('role') == 'assistant'
            )
            
            if verified:
                logger.info(f"✅ Phone {formatted_phone} verified with code {verification_code}")
                return jsonify({
                    "verified": True,
                    "transcript": result.get('messages', [])
                }), 200
            else:
                logger.info(f"❌ Phone {formatted_phone} verification failed")
                return jsonify({
                    "verified": False,
                    "verifyFailureReason": "Failed to verify code",
                    "transcript": result.get('messages', [])
                }), 200
                
        except Exception as e:
            logger.error(f"❌ Call failed: {str(e)}")
            return jsonify({
                "verified": False,
                "verifyFailureReason": f"Call failed: {str(e)}"
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Verification Error: {str(e)}")
        return jsonify({
            "verified": False,
            "verifyFailureReason": f"Verification service error: {str(e)}"
        }), 200 