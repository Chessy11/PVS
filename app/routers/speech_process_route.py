from fastapi import APIRouter, HTTPException, Request, Depends, Form, Response
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.db import get_session
from models.models import User
from utils.twiml import generate_twiml_response
from utils.ngrok_config import get_ngrok_url


router = APIRouter()

async def get_user_by_call_sid(call_sid: str, session: AsyncSession):
    return await session.execute(select(User).filter(User.call_sid == call_sid)).scalar_one_or_none()


@router.post("process_speech/{attempt}")
async def process_verification(
    attempt: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    RecordingUrl: str = Form(None),
    CallSid: str = Form(...),
    SpeechResult: str = Form(None)
):
    result = await session.execute(select(User).filter(User.call_sid == CallSid))
    user = result.scalar_one_or_none()  

    if not user:
        return Response(content="<Response><Say>User not found.</Say><Hangup/></Response>", media_type="application/xml")

    ngrok_url = get_ngrok_url()
    max_attempts = 2 
    if SpeechResult and SpeechResult.strip().upper() == user.verification_code.upper():
        print(f"Speech Result: {SpeechResult}")
        user.is_verified = True
        await session.commit()
        return Response(content="<Response><Say>Verification successful. Thank you for using TechBurst.</Say><Hangup/></Response>", media_type="application/xml")
    else:
        user.verification_attempts += 1
        await session.commit()
        if user.verification_attempts < max_attempts:
            return Response(content=f"<Response><Say>Verification failed. Please try again.</Say><Redirect method='POST'>{ngrok_url}/twiml/{user.verification_code}</Redirect></Response>", media_type="application/xml")
        else:
            await session.delete(user) 
            await session.commit()
            return Response(content="<Response><Say>Verification failed, no more attempts left. Goodbye!</Say><Hangup/></Response>", media_type="application/xml")