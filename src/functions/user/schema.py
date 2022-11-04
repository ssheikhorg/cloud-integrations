from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class AddUserToGroupSchema(BaseModel):
    email: EmailStr
    group_name: str


class GroupEnum(str, Enum):
    admin = "admin"
    retailer = "retailer"
    user = "user"


class SignupSchema(BaseModel):
    """Cognito User signup schema"""
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    role: GroupEnum = GroupEnum.user
    company: Optional[str] = None
    agreement: Optional[bool] = False


class ConfirmSignupSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr
    code: str


class ResendConfirmationCodeSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr


class SignInSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr


class ConfirmForgotPasswordSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr
    password: str
    code: str


class ChangePasswordSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr
    old_password: str
    new_password: str
