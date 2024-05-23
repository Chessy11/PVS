from pydantic import BaseModel

class CreatePaymentSchema(BaseModel):
    amount: float