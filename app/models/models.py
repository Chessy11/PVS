from sqlalchemy import Column, Integer, String
from database.db import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String, nullable=False)
    phone_number=Column(String)
    email = Column(String, nullable=False, unique=True)
    call_sid = Column(String, nullable=True)  # Store the Call SID provided by Twilio
    verification_code = Column(String)
    verification_attempts = Column(Integer, default=0)
    is_verified = Column(Integer, default=0)  # 0 is not verified, 1 is verified
    call_status = Column(String, nullable=True)  # Add this line to store the call status




    
    
