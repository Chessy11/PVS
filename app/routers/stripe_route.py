from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Set your secret key: remember to switch to your live secret key in production
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

print(f"STRIPE API KEY: {stripe.api_key}")

class CreatePaymentIntent(BaseModel):
    amount: float = Field(..., gt=0.50, description="The amount in dollars, must be greater than $0.50")

@router.post("create-payment-intent")
async def create_payment_intent(data: CreatePaymentIntent):
    try:
        # Convert amount from dollars to cents
        amount_in_cents = int(data.amount * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='usd',
        )
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Make sure to replace 'usd' with the appropriate currency if needed

@router.post("webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print('PaymentIntent was successful!')
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event['type']))

    return {"status": "success"}
