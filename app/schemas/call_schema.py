from pydantic import BaseModel, validator
import phonenumbers
from typing import Optional


class CallDetailSchema(BaseModel):
    call_sid: str
    recording_sid: str
    recording_url: str

    class Config:
        form_attributes = True

    
    
    

    
    
    