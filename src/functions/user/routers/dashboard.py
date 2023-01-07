from fastapi import APIRouter, Request, Depends

from ..schemas import ChangePasswordSchema
from ...auth import AuthBearer
from ...utils.response import Response as Rs
from ..cognito import Be3UserDashboard

router = APIRouter(prefix="/user/dashboard", tags=["User-Dashboard"])
m = Be3UserDashboard()


@router.post("/delete/{email}", dependencies=[Depends(AuthBearer())])
async def cognito_delete_user(email: str):
    try:
        signup = m.delete_user(email)
        if signup['success']:
            return Rs.success(signup, "User deleted successfully")
        return Rs.error(signup, "User not deleted")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/sign-out", dependencies=[Depends(AuthBearer())])
async def user_sign_out(request: Request):
    try:
        access_token = request.headers['Authorization'].split(' ')[1]
        response = m.sign_out(access_token)
        return Rs.success(response, "User logged out successfully")
    except Exception as e:
        return Rs.error(e.__str__())


@router.post("/change-password", dependencies=[Depends(AuthBearer())])
async def cognito_change_password(request: Request, body: ChangePasswordSchema):
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
