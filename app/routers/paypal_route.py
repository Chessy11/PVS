from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import paypalrestsdk
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

paypalrestsdk.configure({
    "mode": "sandbox",  # or "live" for production
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

class CreateOrderRequest(BaseModel):
    amount: float

class CaptureOrderRequest(BaseModel):
    orderID: str

@router.post("create-paypal-order")
async def create_paypal_order(request: CreateOrderRequest):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": f"{request.amount:.2f}",
                "currency": "USD"
            },
            "description": "Payment transaction description."
        }],
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/payment/cancel"
        }
    })

    if payment.create():
        return {"orderID": payment.id}
    else:
        raise HTTPException(status_code=500, detail=payment.error)


@router.post("capture-paypal-order")
async def capture_paypal_order(request: CaptureOrderRequest):
    payment = paypalrestsdk.Payment.find(request.orderID)
    if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
        return {"status": "COMPLETED"}
    else:
        raise HTTPException(status_code=500, detail=payment.error)
