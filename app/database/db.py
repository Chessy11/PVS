from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# DATABASE_URL =  URL.create(
#     drivername="postgresql+asyncpg",
#     usenmae = os.getenv('DB_USER'),
#     password = os.getenv('DB_PASSWORD'),
#     host = os.getenv("DB_HOST"),
#     port = os.getenv("DB_PORT"),
#     database = os.getenv("DB_NAME")
# )

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/pvs"


engine = create_async_engine(str(DATABASE_URL), connect_args={"ssl": None})

SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
