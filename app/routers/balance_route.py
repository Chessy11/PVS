from fastapi import APIRouter, HTTPException
from twilio.rest import Client
import os
from dotenv import load_dotenv
import json

router = APIRouter()

# Load environment variables from .env file
load_dotenv()

# Initialize the Twilio client with your account SID and auth token
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(twilio_account_sid, twilio_auth_token)

if twilio_account_sid:
    print(f"TWWWWWW SID: {twilio_account_sid}")
else:
    print("Can't access the credentials")
print(f"TWWWWWW TOKEN: {twilio_auth_token}")

@router.get("twilio_balance")
async def get_twilio_balance():
    try:
        balance_resource_url = f'https://api.twilio.com/2010-04-01/Accounts/{twilio_client.username}/Balance.json'
        response = twilio_client.request('GET', balance_resource_url)
        balance_info = json.loads(response.content)
        balance = float(balance_info['balance'])
        currency = balance_info['currency']
        return {"balance": balance, "currency": currency}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
