from flask import Blueprint, request, jsonify
import logging
import json
from ..utils.vapi_client import create_verification_assistant, wait_for_call_completion
import random
from datetime import datetime, timedelta

verify = Blueprint('verify', __name__)
logger = logging.getLogger(__name__)

# Simple in-memory store for recent calls
recent_calls = {}

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
    phone = None  # Initialize phone variable for error handling
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
            }), 200
            
        # Format phone number
        phone = data['phoneNumber']  # Now phone is defined in the main scope
        region = data.get('region', '1')
        clean_phone = ''.join(filter(str.isdigit, phone))
        formatted_phone = f"+{region}{clean_phone}"
        logger.info(f"Formatting phone: {phone} with region {region} -> {formatted_phone}")
        
        if not clean_phone:
            return jsonify({
                "verified": False,
                "verifyFailureReason": "Invalid phone number format"
            }), 200
        
        # Check if we've called this number recently (within last 30 seconds)
        if phone in recent_calls:
            last_call_time = recent_calls[phone]
            if datetime.now() - last_call_time < timedelta(seconds=30):
                return jsonify({
                    "verified": False,
                    "verifyFailureReason": "Please wait before trying again"
                }), 200

        # Store this call attempt
        recent_calls[phone] = datetime.now()

        # Generate verification code
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        logger.info(f"Generated verification code {verification_code}")
        
        # Create assistant and initiate call
        call = await create_verification_assistant(verification_code, formatted_phone)
        logger.info(f"Call initiated with ID: {call.get('id')}")
        
        # Wait for completion and check result
        result = await wait_for_call_completion(call.get('id'))
        
        # Log transcript
        logger.info("\n=== Call Transcript ===")
        for message in result.get('messages', []):
            logger.info(f"{message.get('role', 'unknown')}: {message.get('content', '')}")
        
        # Check verification status from analysis summary
        analysis = result.get('analysis', {}).get('summary')
        logger.info(f"Call Analysis: {analysis}")
        
        # If analysis is a string, try to parse it as JSON
        if isinstance(analysis, str):
            try:
                analysis_data = json.loads(analysis)
                verified = analysis_data.get('verified', False)
                verification_reason = analysis_data.get('reason', 'No analysis available')
            except json.JSONDecodeError:
                verified = False
                verification_reason = "Could not parse analysis result"
        else:
            verified = analysis.get('verified', False) if analysis else False
            verification_reason = analysis.get('reason', 'No analysis available') if analysis else 'No analysis available'

        # Clean up after verification attempt
        if phone in recent_calls:
            del recent_calls[phone]

        if verified:
            logger.info(f"✅ Phone {formatted_phone} verified with code {verification_code}")
            return jsonify({
                "verified": True,
                "reason": verification_reason,
                "transcript": result.get('messages', [])
            }), 200
        else:
            logger.info(f"❌ Phone {formatted_phone} verification failed: {verification_reason}")
            return jsonify({
                "verified": False,
                "verifyFailureReason": verification_reason,
                "transcript": result.get('messages', [])
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Verification Error: {str(e)}")
        # Clean up on error (phone is now defined)
        if phone and phone in recent_calls:
            del recent_calls[phone]
        return jsonify({
            "verified": False,
            "verifyFailureReason": f"Verification service error: {str(e)}"
        }), 200 