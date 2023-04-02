from typing import Optional
from pydantic import BaseModel, EmailStr, Field, SecretStr
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    RETAILER = "retailer"
    USER = "user"


class AuthUser(BaseModel):
    pk: str
    role: Role = Role.USER

    class Config:
        orm_mode = True


class SignupSchema(BaseModel):
    """Cognito User signup schemas"""
    email: EmailStr = Field(..., description="Email address of the user")
    username: str = Field(..., description="Username of the user",
                          min_length=5, max_length=20)
    password: SecretStr = Field(..., description="Password of the user",
                                min_length=8, max_length=15)
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    role: Role = Field(Role.USER, description="Role of the user")
    company: Optional[str] = Field(None, description="Company name")
    agreement: Optional[bool] = Field(default=False, description="Agreement")
    quota: int = Field(default=100, description="Quota of the user")

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None
        }


class UpdateUserSchema(BaseModel):
    pk: str
    first_name: str
    last_name: str


class ConfirmSignupSchema(BaseModel):
    """Cognito User signup schemas"""
    username: str
    code: str


class SignInSchema(BaseModel):
    """Cognito User signup schemas"""
    username: str
    password: SecretStr


class ConfirmForgotPasswordSchema(BaseModel):
    """Cognito User signup schemas"""
    email: EmailStr = Field(..., description="Email address of the user")
    password: SecretStr = Field(..., description="Password of the user")
    code: str = Field(..., description="Confirmation code")


class ChangePasswordSchema(BaseModel):
    """Cognito User signup schemas"""
    old_password: SecretStr = Field(..., description="Old password of the user")
    new_password: SecretStr = Field(..., description="New password of the user")


class EmailSchema(BaseModel):
    """Cognito User signup schemas"""
    email: EmailStr = Field(..., description="Email address of the user")
