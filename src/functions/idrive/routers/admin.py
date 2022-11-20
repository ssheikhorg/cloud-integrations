from fastapi import APIRouter

from ..schema import user as s
from ..idrive_api import IDriveAPI, IDriveReseller
from ...utils.response import Response as Rs

router = APIRouter(prefix="/idrive-admin", tags=["idrive-user"])
m = IDriveAPI()


@router.get("/users")
async def get_idrive_users():
    try:
        response = m.get_idrive_users()
        if response["success"]:
            return Rs.success(response, "Users fetched successfully")
        return Rs.error(response, "Failed to fetch users")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/create")
async def create_reseller(body: s.ResellerUser):
    try:
        user = m.create_reseller_user(body.dict())
        if user["success"]:
            return Rs.success(user, "User created successfully")
        return Rs.error(user, "Failed to create user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/disable/{email}")
async def disable_user(email: str):
    try:
        user = m.disable_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User disabled successfully")
        return Rs.error(user, "Failed to disable user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/enable/{email}")
async def enable_user(email: str):
    try:
        user = m.enable_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User enabled successfully")
        return Rs.error(user, "Failed to enable user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/delete/{email}")
async def delete_user(email: str):
    try:
        user = m.remove_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User removed successfully")
        return Rs.error(user, "Failed to remove user")
    except Exception as e:
        return Rs.server_error(e.__str__())
