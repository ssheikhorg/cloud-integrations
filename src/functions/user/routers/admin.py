from fastapi import APIRouter

from ..cognito import Be3UserAdmin
from ..schemas.users import *

from ...utils.response import Response as Rs

router = APIRouter(prefix="/user/admin", tags=["User-Admin"])
m = Be3UserAdmin()


@router.post("/login")
async def cognito_sign_in(body: SignInSchema):
    try:
        tokens = m.sign_in(body.dict())
        if tokens["success"]:
            return Rs.success(tokens)
        return Rs.error(tokens, "Invalid Credentials")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/sign-up")
async def cognito_signup(body: SignupSchema):
    try:
        signup = m.sign_up(body.dict())
        if signup['success']:
            return Rs.created(signup, "User created successfully")
        return Rs.not_created(signup, "User not created")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/confirm-sign-up")
async def cognito_confirm_signup(body: ConfirmSignupSchema):
    try:
        signup = m.confirm_signup(body.dict())
        if signup['success']:
            return Rs.success(signup, "User confirmed successfully")
        return Rs.error(signup, "User not confirmed")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/resend-confirmation-code/{email}")
async def cognito_resend_confirmation_code(email: str):
    try:
        signup = m.resend_confirmation_code(email)
        if signup:
            return Rs.success(signup)
        else:
            return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/forgot-password/{email}")
async def cognito_forgot_password(email: str):
    try:
        signup = m.forgot_password(email)
        if signup:
            return Rs.success(signup)
        else:
            return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/confirm-forgot-password")
async def cognito_confirm_forgot_password(body: ConfirmForgotPasswordSchema):
    try:
        signup = m.confirm_forgot_password(body.dict())
        if signup['success']:
            return Rs.success(signup)
        return Rs.error(signup, "Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())
