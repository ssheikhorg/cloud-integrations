from typing import Any
from fastapi import APIRouter, Request, Depends

from .role_checker import RoleChecker
from ...services.auth import AuthBearer

from .cognito import cognito
from .schemas import (Role, SignupSchema, ConfirmSignupSchema,
                      SignInSchema, ConfirmForgotPasswordSchema,
                      ChangePasswordSchema, EmailSchema, UpdateUserSchema
                      )

user_router = APIRouter(prefix="/admin", tags=["User-Admin"])


@user_router.post("/sign-up")
async def cognito_signup(body: SignupSchema) -> Any:
    return await cognito.sign_up(body.dict())


@user_router.post("/login")
async def cognito_sign_in(body: SignInSchema) -> Any:
    return await cognito.sign_in(body.dict())


@user_router.post("/confirm-sign-up")
async def cognito_confirm_signup(body: ConfirmSignupSchema) -> Any:
    return await cognito.confirm_signup(body.dict())


@user_router.post("/resend-confirmation-code")
async def cognito_resend_confirmation_code(body: EmailSchema) -> Any:
    return await cognito.resend_confirmation_code(body.email)


@user_router.post("/forgot-password")
async def cognito_forgot_password(body: EmailSchema) -> Any:
    return await cognito.forgot_password(body.email)


@user_router.post("/confirm-forgot-password")
async def cognito_confirm_forgot_password(body: ConfirmForgotPasswordSchema) -> Any:
    return await cognito.confirm_forgot_password(body.dict())


"""DASHBOARD ROUTES"""
dashboard_router = APIRouter(
    prefix="/dashboard", tags=["User-Dashboard"], dependencies=[Depends(AuthBearer())]
)


@dashboard_router.get("/users")
async def get_users(limit: int = 10, offset: int = 0, _: bool = Depends(RoleChecker([Role.ADMIN]))) -> Any:
    """get all users from dynamo if the role matches"""
    return await cognito.get_all_users(limit, offset)


@dashboard_router.get("/get-user-details")
async def cognito_get_user(request: Request) -> Any:
    """get user by id or email or username"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.get_user_details(_token)


@dashboard_router.get("/logs")
async def get_logs(pk: str, limit: int = 10, offset: int = 0) -> Any:
    """get all logs from dynamo if the role matches"""
    return await cognito.get_all_logs(pk, limit, offset)


@dashboard_router.put("/update")
async def cognito_update_user(body: UpdateUserSchema) -> Any:
    """update user by email"""
    return await cognito.update_user(body.dict())


@dashboard_router.delete("/delete")
async def cognito_delete_user(pk: str) -> Any:
    """delete user by email"""
    return await cognito.delete_user(pk)


@dashboard_router.post("/sign-out")
async def user_sign_out(request: Request) -> Any:
    """sign out user by email"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.sign_out(_token)


@dashboard_router.post("/change-password")
async def cognito_change_password(request: Request, body: ChangePasswordSchema) -> Any:
    """change password"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await cognito.change_password(_token, body.dict())
