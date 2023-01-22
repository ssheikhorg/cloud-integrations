from fastapi import APIRouter, Request, Depends

from ..role_checker import RoleChecker
from ..schemas import users, roles
from src.functions.services.auth import AuthBearer
from ...core.database import Dynamo
from ...models.users import UserModel
from ...utils.response import Response as Rs
from ..cognito import Be3UserDashboard

router = APIRouter(prefix="/user/dashboard", tags=["User-Dashboard"])
m = Be3UserDashboard()
db = Dynamo(UserModel)


# @router.get("/users", dependencies=[Depends(AuthBearer())])
# async def get_users(user: roles.AuthUser = Depends(RoleChecker([roles.Role.ADMIN]))):
@router.get("/users")
async def get_users():
    """get all users from dynamo if the role matches"""
    try:
        user_list = db.query(pk="users", index="users_index")
        return Rs.success(user_list)
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/delete/{email}", dependencies=[Depends(AuthBearer())])
async def cognito_delete_user(email: str):
    try:
        signup = m.delete_user(email)
        if signup['success']:
            return Rs.success(signup, "User deleted successfully")
        return Rs.error(signup, "User not deleted")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/sign-out/{email}", dependencies=[Depends(AuthBearer())])
async def user_sign_out(email: str, request: Request):
    try:
        access_token = request.headers['Authorization'].split(' ')[1]
        response = m.sign_out(access_token, email)
        return Rs.success(response, "User logged out successfully")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/change-password", dependencies=[Depends(AuthBearer())])
async def cognito_change_password(request: Request, body: users.ChangePasswordSchema):
    try:
        data = body.dict()
        data["access_token"] = request.headers['Authorization'].split(' ')[1]
        signup = m.change_password(data)
        if signup:
            return Rs.success(signup)
        return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())


@router.get("/get-user/{email}", dependencies=[Depends(AuthBearer())])
async def cognito_get_user(email: str):
    try:
        signup = m.get_user_by_email(email)
        if signup:
            return Rs.success(signup)
        return Rs.error("Something went wrong")
    except Exception as e:
        return Rs.error(e.__str__())
