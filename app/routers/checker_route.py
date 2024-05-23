from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import User
from database.db import get_session

router = APIRouter()

@router.get("check_verification/{user_id}")
async def check_verification(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"is_verified": user.is_verified, "verification_attempts": user.verification_attempts}
