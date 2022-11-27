from typing import Optional
from pydantic import BaseModel, EmailStr, Field, SecretStr


class AddUserToGroupSchema(BaseModel):
    email: EmailStr = Field(..., description="Email of the user")
    group_name: str = Field(..., description="Group name")


class SignupSchema(BaseModel):
    """Cognito User signup schema"""
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    email: EmailStr = Field(..., description="Email address of the user")
    password: SecretStr = Field(..., description="Password of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    role: str = Field(default="user", description="User role")  # Enum `admin` `retailer` `user`
    company: Optional[str] = Field(None, description="Company name")
    agreement: Optional[bool] = Field(default=False, description="Agreement")

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None
        }


class ConfirmSignupSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr = Field(..., description="Email address of the user")
    code: str = Field(..., description="Confirmation code")


class SignInSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr = Field(..., description="Email address of the user")
    password: SecretStr = Field(..., description="Password of the user")


class ConfirmForgotPasswordSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr = Field(..., description="Email address of the user")
    password: SecretStr = Field(..., description="Password of the user")
    code: str = Field(..., description="Confirmation code")


class ChangePasswordSchema(BaseModel):
    """Cognito User signup schema"""
    email: EmailStr = Field(..., description="Email address of the user")
    old_password: SecretStr = Field(..., description="Old password of the user")
    new_password: SecretStr = Field(..., description="New password of the user")
