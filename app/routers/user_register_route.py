from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from database.db import get_session
from schemas.user_schema import UserCreateSchema, UserResponseSchema
from utils.code_generator import generate_verification_code
from utils.phone_number_normalizer import normalize_phone_number
from utils.ngrok_config import get_ngrok_url
from twilio.rest import Client

import os
import re

router = APIRouter()




print("Loading environment variables...")
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(twilio_account_sid, twilio_auth_token)
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')



print("TWILIO_ACCOUNT_SID:", twilio_account_sid)
print("TWILIO_AUTH_TOKEN:", twilio_auth_token)
print("TWILIO_PHONE_NUMBER:", twilio_phone_number)
print("TWILIO_CLIENT", twilio_client)


@router.post("register", response_model=UserResponseSchema)
async def create_user(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    normalized_phone = normalize_phone_number(user.phone_number)
    result = await session.execute(select(User).filter(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    if not re.search(r'\d', user.password) or not re.search(r'[!@#$%^&*()_+=-]', user.password):
        raise HTTPException(status_code=400, detail="Password must include at least one number and one symbol from !@#$%^&*()_+=-")

    verification_code = generate_verification_code()

    new_user = User(
        username=user.username,
        name=user.name,
        phone_number=normalized_phone,
        email=user.email,
        password=user.password,
        verification_code=verification_code,  # Set the code here
        is_verified=False 
    )
    session.add(new_user)
    await session.commit()

    ngrok_url = get_ngrok_url()
    try:
        call = twilio_client.calls.create(
            to=new_user.phone_number,
            from_=twilio_phone_number,
            url=f"{ngrok_url}/twiml/{verification_code}",
            status_callback=f"{ngrok_url}/call_status/{new_user.id}",
            status_callback_event=["completed", "no-answer", "failed", "busy", "canceled"]
        )
        new_user.call_sid = call.sid
        await session.commit()
    except Exception as e:
        await session.delete(new_user)
        await session.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return {"id": new_user.id, "username": new_user.username, "name": new_user.name, "phone_number": new_user.phone_number, "email": new_user.email}


    
    
