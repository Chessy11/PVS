from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.models.models import User
from app.schemas.user_schema import UserCreateSchema
from twilio.rest import Client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



async def create_user(session: AsyncSession, user: UserCreateSchema):
    new_user = User(
        username=user.username,
        name=user.name,
        phone_number=user.phone_number,
        email=user.email, 
        password=pwd_context.hash(user.password), 
        is_verified=user.is_verified,)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


