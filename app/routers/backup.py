

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import get_session
from app.models.models import User
from google.cloud import speech
from twilio.rest import Client
from google.oauth2 import service_account
from json import JSONDecodeError
import requests

import os

router = APIRouter()

# Initialize Twilio client
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(twilio_account_sid, twilio_auth_token)



def transcribe_local_audio(file_path):
    client = speech.SpeechClient()

    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Correct for PCM 16-bit
        sample_rate_hertz=8000,  # Match the file's sample rate
        language_code="ka-GE",
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")
        return result.alternatives[0].transcript
    return None


async def get_user_by_call_sid(call_sid: str, session: AsyncSession):
    result = await session.execute(select(User).filter(User.call_sid == call_sid))
    user = result.scalars().first()
    return user



@router.post("process_speech")
async def handle_call_status(request: Request, session: AsyncSession = Depends(get_session)):
    data = await request.json()
    call_sid = data.get('CallSid')
    
    if not call_sid:
        return {"message": "CallSid is required"}, 400

    local_file_path = os.path.join('/home/OffPower/Downloads', 'test_recording.wav')  # Assuming the file is located here
    transcript = transcribe_local_audio(local_file_path)
    
    if not transcript:
        return {"message": "Failed to transcribe the recording"}, 500
    
    user = await get_user_by_call_sid(call_sid, session)
    if user and transcript.lower().strip() == user.name.lower().strip():
        user.is_verified = True
        await session.commit()
        return {"message": "User verified successfully."}
    
    return {"message": "Verification failed, name does not match.", "transcript": transcript}

