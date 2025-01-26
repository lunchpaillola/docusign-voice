import os
from vapi import AsyncVapi
import random
import logging

logger = logging.getLogger(__name__)

# Debug environment variables
logger.info("VAPI Client Initialization:")
api_key = os.getenv('VAPI_API_KEY')
phone_number = os.getenv('VAPI_PHONE_NUMBER')

# Safer logging that checks for None
logger.info(f"VAPI_API_KEY: {'✅ Set' if api_key else '❌ Not Set'}")
if api_key:
    logger.info(f"VAPI_API_KEY (truncated): {api_key[:10]}...")
logger.info(f"VAPI_PHONE_NUMBER: {phone_number}")

if not api_key:
    raise ValueError("❌ VAPI_API_KEY not found in environment variables!")

# Initialize with token
vapi_client = AsyncVapi(
    token=api_key
)

async def create_verification_assistant(verification_code):
    """Create a verification assistant with a specific code"""
    return await vapi_client.assistants.create(
        name=f"Phone Verification {verification_code}",
        model={
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are a phone verification assistant. Your only job is to verify the code {verification_code}.

                    Follow these exact steps:
                    1. Listen for the user to say numbers
                    2. Compare their numbers to {verification_code}
                    3. If they say exactly {verification_code}:
                       - Say "This call is verified. Thank you and have a great day."
                       - End call
                    4. If they say different numbers:
                       - Say "Incorrect code. Let me repeat it: {verification_code}"
                       - Give one more try
                       - If second attempt wrong:
                         - Say "This call is not verified. Thank you and have a great day."
                         - End call
                    5. If no clear numbers heard:
                       - Say "I need you to say the numbers {verification_code}"
                       - If still no numbers:
                         - Say "This call is not verified. Thank you and have a great day."
                         - End call

                    Only use these exact ending phrases:
                    - "This call is verified. Thank you and have a great day."
                    - "This call is not verified. Thank you and have a great day."
                    """
                }
            ]
        },
        first_message=f"""Hi, this is Jennifer from DocuVoice. I'm calling to verify your phone number for a DocuSign contract. 
        Your verification code is: {verification_code}.
        Please repeat this code back to me.""",
        first_message_mode="assistant-speaks-first",
        silence_timeout_seconds=30,
        max_duration_seconds=300,
        end_call_phrases=[
            "This call is verified. Thank you and have a great day.",
            "This call is not verified. Thank you and have a great day."
        ],
        artifact_plan={
            "recording_enabled": True,
            "transcript_plan": {
                "enabled": True
            }
        }
    ) 