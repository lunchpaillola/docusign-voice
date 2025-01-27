import os
import httpx
import logging
import asyncio

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

VAPI_BASE_URL = "https://api.vapi.ai"

async def create_verification_assistant(verification_code, formatted_phone):
    """Create a verification assistant and initiate call using direct API calls"""
    async with httpx.AsyncClient() as client:
        # Create assistant first
        assistant_response = await client.post(
            f"{VAPI_BASE_URL}/assistant",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "name": f"Phone Verification {verification_code}",
                "model": {
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
                               - Set result: VERIFIED
                               - End call
                            4. If they say different numbers:
                               - Say "Incorrect code. Let me repeat it: {verification_code}"
                               - Give one more try
                               - If second attempt wrong:
                                 - Say "This call is not verified. Thank you and have a great day."
                                 - Set result: NOT_VERIFIED
                                 - End call
                            5. If no clear numbers heard:
                               - Say "I need you to say the numbers {verification_code}"
                               - If still no numbers:
                                 - Say "This call is not verified. Thank you and have a great day."
                                 - Set result: NOT_VERIFIED
                                 - End call

                            Always end your response with either:
                            RESULT: VERIFIED
                            or
                            RESULT: NOT_VERIFIED"""
                        }
                    ]
                },
                "firstMessage": f"Hi, this is Jennifer from DocuVoice. I'm calling to verify your phone number for a DocuSign contract. Your verification code is: {verification_code}. Please repeat this code back to me.",
                "firstMessageMode": "assistant-speaks-first",
                "silenceTimeoutSeconds": 30,
                "maxDurationSeconds": 300,
                "endCallPhrases": [
                    "This call is verified. Thank you and have a great day.",
                    "This call is not verified. Thank you and have a great day."
                ],
                "analysisPlan": {
                    "summaryPlan": {
                        "enabled": True,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""Analyze if the verification code {verification_code} was correctly provided.
                                Return a JSON object with:
                                - verified: boolean
                                - reason: string explaining the verification result
                                """
                            }
                        ]
                    }
                }
            }
        )
        assistant_response.raise_for_status()
        assistant = assistant_response.json()

        # Create call using the assistant ID
        call_response = await client.post(
            f"{VAPI_BASE_URL}/call",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "name": f"DocuSign Verification {verification_code}",
                "assistantId": assistant.get('id'),
                "phoneNumberId": os.getenv('VAPI_PHONE_NUMBER_ID'),
                "customer": {
                    "number": formatted_phone,
                    "numberE164CheckEnabled": True
                }
            }
        )
        call_response.raise_for_status()
        return call_response.json()

async def wait_for_call_completion(call_id):
    """Poll call status until completion"""
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"{VAPI_BASE_URL}/call/{call_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            call_data = response.json()
            
            # Log status and messages for debugging
            logger.info(f"Call status: {call_data.get('status')}")
            if 'messages' in call_data:
                logger.info("Current messages:")
                for msg in call_data.get('messages', []):
                    logger.info(f"{msg.get('role')}: {msg.get('content')}")
            
            if call_data.get('status') == 'ended':
                return call_data
                
            await asyncio.sleep(2)  # Poll every 2 seconds 