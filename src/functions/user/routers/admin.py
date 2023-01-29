from fastapi import APIRouter

from ..cognito import Be3UserAdmin
from ..schemas.users import *
from ...core.database import DynamoDB
from ...models.users import UserModel

router = APIRouter(prefix="/admin", tags=["User-Admin"])
m = Be3UserAdmin()
db = DynamoDB(UserModel)


@router.post("/sign-up")
async def cognito_signup(body: SignupSchema):
    return await m.sign_up(body.dict())


@router.post("/login")
async def cognito_sign_in(body: SignInSchema):
    return await m.sign_in(body.dict())


@router.post("/confirm-sign-up")
async def cognito_confirm_signup(body: ConfirmSignupSchema):
    return await m.confirm_signup(body.dict())


@router.post("/resend-confirmation-code/{email}")
async def cognito_resend_confirmation_code(email: str):
    return await m.resend_confirmation_code(email)


@router.post("/forgot-password/{email}")
async def cognito_forgot_password(email: str):
    return await m.forgot_password(email)


@router.post("/confirm-forgot-password")
async def cognito_confirm_forgot_password(body: ConfirmForgotPasswordSchema):
    return await m.confirm_forgot_password(body.dict())
