from fastapi import APIRouter, Request, Depends

from ..models import get_all_user, get_user_by_id
from ..role_checker import RoleChecker
from ..schemas import users, roles
from ...services.auth import AuthBearer
from ...core.database import DynamoDB
from ...models.users import UserModel
from ..cognito import Be3UserDashboard

router = APIRouter(prefix="/dashboard", tags=["User-Dashboard"])
m = Be3UserDashboard()
db = DynamoDB(UserModel)


@router.get("/users", dependencies=[Depends(AuthBearer())])
async def get_users(limit: int = 10, offset: int = 0,
                    _=Depends(RoleChecker([roles.Role.USER]))):
    """get all users from dynamo if the role matches"""
    return await get_all_user(limit, offset)


@router.get("/get-user-details", dependencies=[Depends(AuthBearer())])
async def cognito_get_user(request: Request):
    """get user by id or email or username"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await m.get_user_details(_token)


@router.delete("/delete", dependencies=[Depends(AuthBearer())])
async def cognito_delete_user(request: Request):
    """delete user by email"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await m.delete_user(_token)


@router.post("/sign-out/{email}", dependencies=[Depends(AuthBearer())])
async def user_sign_out(email: str, request: Request):
    """sign out user by email"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await m.sign_out(_token, email)


@router.post("/change-password", dependencies=[Depends(AuthBearer())])
async def cognito_change_password(request: Request, body: users.ChangePasswordSchema):
    """change password"""
    _token = request.headers['Authorization'].split(' ')[1]
    return await m.change_password(_token, body.dict())
