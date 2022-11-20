from fastapi import APIRouter, Request, Depends

from ..auth import AuthBearer
from .cognito import Be3CognitoUser
from .schema import *

from ..utils.response import Response as Rs

routes = APIRouter(prefix="/app-user", tags=["user"])
m = Be3CognitoUser()

'''WITH AUTH'''


@routes.get("/all", dependencies=[Depends(AuthBearer())])
async def get_user():
    try:
        # get token from header
        response = m.get_users()
        return Rs.success(response)
    except Exception as e:
        return Rs.error(e.__str__())


'''WITHOUT AUTH'''


@routes.post("/login")
async def cognito_sign_in(body: SignInSchema):
    try:
        tokens = m.sign_in(body.dict())
        if tokens:
            return Rs.success(tokens)
        return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/sign-up")
async def cognito_signup(body: SignupSchema):
    try:
        signup = m.sign_up(body.dict())
        if signup['success']:
            return Rs.created(signup, "User created successfully")
        return Rs.not_created(signup, "User not created")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/confirm-sign-up")
async def cognito_confirm_signup(body: ConfirmSignupSchema):
    try:
        signup = m.confirm_signup(body.dict())
        if signup['success']:
            return Rs.success(signup, "User confirmed successfully")
        return Rs.error(signup, "User not confirmed")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/sign-out", dependencies=[Depends(AuthBearer())])
async def user_sign_out(request: Request):
    try:
        access_token = request.headers['Authorization'].split(' ')[1]
        response = m.sign_out(access_token)
        return Rs.success(response, "User logged out successfully")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/resend-confirmation-code/{email}")
async def cognito_resend_confirmation_code(email: str):
    try:
        signup = m.resend_confirmation_code(email)
        if signup:
            return Rs.success(signup)
        else:
            return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/delete/{email}")
async def cognito_delete_user(email: str):
    try:
        signup = m.delete_user(email)
        if signup['success']:
            return Rs.success(signup, "User deleted successfully")
        return Rs.error(signup, "User not deleted")
    except Exception as e:
        return Rs.error(e.__str__())


# @router.post("/forgot-password/{email}")
# async def cognito_forgot_password(email: str):
#     try:
#         signup = m.forgot_password(body.dict())
#         if signup:
#             return Rs.success(signup)
#         else:
#             return Rs.error("Something went wrong")
#     except Exception as e:
#         return Rs.error(e.__str__())
#
#
# @router.post("/confirm-forgot-password")
# async def cognito_confirm_forgot_password(body: ConfirmForgotPasswordSchema):
#     try:
#         signup = m.confirm_forgot_password(body.dict())
#         if signup:
#             return Rs.success(signup)
#         else:
#             return Rs.error("Something went wrong")
#     except Exception as e:
#         return Rs.error(e.__str__())
#
#
# @router.post("/change-password")
# async def cognito_change_password(body: ChangePasswordSchema):
#     try:
#         signup = m.change_password(body.dict())
#         if signup:
#             return Rs.success(signup)
#         else:
#             return Rs.error("Something went wrong")
#     except Exception as e:
#         return Rs.error(e.__str__())
