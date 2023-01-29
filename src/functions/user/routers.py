from fastapi import APIRouter, Request, Depends

from ..services.models import get_all_user
from .role_checker import RoleChecker
from ..services.auth import AuthBearer

from .cognito import cognito
from .schemas.users import *
from .schemas.roles import Role, AuthUser
from ..core.database import DynamoDB
from ..models.users import UserModel

user_router = APIRouter(prefix="/admin", tags=["User-Admin"])
db = DynamoDB(UserModel)


@user_router.post("/sign-up")
async def cognito_signup(body: SignupSchema):
    return await cognito.sign_up(body.dict())


@user_router.post("/login")
async def cognito_sign_in(body: SignInSchema):
    return await cognito.sign_in(body.dict())


@user_router.post("/confirm-sign-up")
async def cognito_confirm_signup(body: ConfirmSignupSchema):
    return await cognito.confirm_signup(body.dict())


@user_router.post("/resend-confirmation-code/{email}")
async def cognito_resend_confirmation_code(email: str):
    return await cognito.resend_confirmation_code(email)


@user_router.post("/forgot-password/{email}")
async def cognito_forgot_password(email: str):
    return await cognito.forgot_password(email)


@user_router.post("/confirm-forgot-password")
async def cognito_confirm_forgot_password(body: ConfirmForgotPasswordSchema):
    return await cognito.confirm_forgot_password(body.dict())


"""DASHBOARD ROUTES"""
dashboard_router = APIRouter(prefix="/dashboard", tags=["User-Dashboard"])


@dashboard_router.get("/users", dependencies=[Depends(AuthBearer())])
async def get_users(limit: int = 10, offset: int = 0,
                    _: AuthUser = Depends(RoleChecker([Role.ADMIN]))):
    """get all users from dynamo if the role matches"""
    return await get_all_user(limit, offset)


@dashboard_router.get("/get-user-details", dependencies=[Depends(AuthBearer())])
async def cognito_get_user(request: Request):
    """get user by id or email or username"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.get_user_details(_token)


@dashboard_router.delete("/delete", dependencies=[Depends(AuthBearer())])
async def cognito_delete_user(request: Request):
    """delete user by email"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.delete_user(_token)


@dashboard_router.post("/sign-out", dependencies=[Depends(AuthBearer())])
async def user_sign_out(request: Request):
    """sign out user by email"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.sign_out(_token)


@dashboard_router.post("/change-password", dependencies=[Depends(AuthBearer())])
async def cognito_change_password(request: Request, body: ChangePasswordSchema):
    """change password"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.change_password(_token, body.dict())
