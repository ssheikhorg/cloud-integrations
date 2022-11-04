from fastapi import APIRouter, Request, Depends

from .auth import AuthBearer
from .module import CognitoUser
from .schema import *

from ..utils.response import Response as Rs

routes = APIRouter(prefix="/user", tags=["user"])
users = CognitoUser()

'''WITH AUTH'''


@routes.get("/all", dependencies=[Depends(AuthBearer())])
async def get_user():
    try:
        # get token from header
        response = users.get_users()
        return Rs.success(response)
    except Exception as e:
        return Rs.error(e.__str__())


'''WITHOUT AUTH'''


@routes.post("/login")
async def cognito_sign_in(body: SignInSchema):
    try:
        tokens = users.sign_in(body.dict())
        if tokens:
            return Rs.success(tokens)
        return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/sign-up")
async def cognito_signup(body: SignupSchema):
    try:
        signup = users.sign_up(body.dict())
        if signup['success']:
            return Rs.created(signup, "User created successfully")
        return Rs.not_created(signup, "User not created")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/sign-out", dependencies=[Depends(AuthBearer())])
async def user_sign_out(request: Request):
    try:
        access_token = request.headers['Authorization'].split(' ')[1]
        response = users.sign_out(access_token)
        return Rs.success(response, "User logged out successfully")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/confirm-sign-up")
async def cognito_confirm_signup(body: ConfirmSignupSchema):
    try:
        signup = users.confirm_signup(body.dict())
        if signup:
            return Rs.success(signup)
        else:
            return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@routes.post("/resend-confirmation-code")
async def cognito_resend_confirmation_code(body: ResendConfirmationCodeSchema):
    try:
        signup = users.resend_confirmation_code(body.dict())
        if signup:
            return Rs.success(signup)
        else:
            return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())

# @router.post("/forgot-password")
# async def cognito_forgot_password(body: ForgotPasswordSchema):
#     try:
#         signup = users.forgot_password(body.dict())
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
#         signup = users.confirm_forgot_password(body.dict())
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
#         signup = users.change_password(body.dict())
#         if signup:
#             return Rs.success(signup)
#         else:
#             return Rs.error("Something went wrong")
#     except Exception as e:
#         return Rs.error(e.__str__())
