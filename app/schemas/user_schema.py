from pydantic import BaseModel, validator
import phonenumbers
from typing import Optional


class UserCreateSchema(BaseModel):
    username: str
    name: str
    phone_number: str
    password: str
    email: str

    @validator('phone_number')
    def validate_phone_number(cls, v):
        try:
            phone_number_obj = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(phone_number_obj):
                raise ValueError('Invalid phone number')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError('Invalid phone number format')
        return v

class UserUpdate(BaseModel):
    name: str = None
    phone_number: str = None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            try:
                phone_number_obj = phonenumbers.parse(v, None)
                if not phonenumbers.is_valid_number(phone_number_obj):
                    raise ValueError('Invalid phone number')
            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValueError('Invalid phone number format')
        return v

class UserResponseSchema(BaseModel):
    id: int
    username: str
    name: str
    phone_number: str

    class Config:
        form_attributes = True
