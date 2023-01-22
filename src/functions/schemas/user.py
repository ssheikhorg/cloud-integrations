from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ResellerUser(BaseModel):
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="123456")
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    quota: int = Field(..., example=100)
