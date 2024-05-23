from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from database.db import get_session
from utils.twiml import generate_twiml_response

router = APIRouter()

# @router.post("call_status/{user_id}")
# async def handle_call_status(
#     user_id: int,
#     request: Request,
#     session: AsyncSession = Depends(get_session),
#     CallStatus: str = Form(...),
#     CallSid: str = Form(...)
# ):
#     print(f"Handling call status for User ID: {user_id}, CallSid: {CallSid}, CallStatus: {CallStatus}")
#     result = await session.execute(select(User).filter(User.id == user_id))
#     user = result.scalar_one_or_none()

#     if not user:
#         print("No user found for the given ID.")
#         response_message = "User not found. Goodbye!"
#     elif CallStatus in ["no-answer", "failed", "busy", "canceled"]:
#         print(f"Call was not successful: {CallStatus}")
#         await session.delete(user)
#         await session.commit()
#         return Response(content=f"<Response><Say>Call was unsuccessful. status: {CallStatus}</Say><Hangup/></Response>", media_type="application/xml")

#     elif CallStatus == "completed":
#         print("Call completed successfully.")
#         return Response(content="<Response><Say>Call was completed. status: {CallStatus}</Say><Hangup/></Response>", media_type='application/xml')
#     else:
#         print("Unexpected call status received.")
#         return Response(content="<Response><Say>We've received an unexpected status, sorry.</Say><Hangup/></Response>", media_type='application/xml')
#     response_xml = generate_twiml_response(response_message)
#     print(f"Sending TwiML Response: {response_xml}")
#     return Response(content=response_xml, media_type="application/xml")



@router.post("call_status/{user_id}")
async def handle_call_status(
    user_id: int,  # Accept user_id as part of the URL
    request: Request,
    session: AsyncSession = Depends(get_session),
    CallStatus: str = Form(...),
    CallSid: str = Form(...)
):
    # Fetch the user based on the user_id instead of CallSid if user_id is meant to represent a user identifier
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        response_message = "User not found. Goodbye!"
        return Response(content=generate_twiml_response(response_message), media_type="application/xml")

    # Handling based on call status
    if CallStatus in ["no-answer", "failed", "busy", "canceled"]:
        print(f"Call status: {CallStatus}")
        await session.delete(user)
        await session.commit()
        response_message = "We could not verify your phone number as the call was not successful. Goodbye!"
    elif CallStatus == "completed":
        user.call_status = "completed"
        await session.commit()
        response_message = "Please proceed with the verification."
    else:
        response_message = "We received an unexpected status. Please contact support."

    return Response(content=generate_twiml_response(response_message), media_type="application/xml")



@router.get("check_call_status/{user_id}")
async def check_call_status(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"call_status": user.call_status}

