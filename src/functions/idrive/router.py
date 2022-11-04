from fastapi import APIRouter

from .schema import Bucket, ResellerUser
from .module import (create_user_api, enum_list, get_users)
from ..utils.response import Response as Rs

routes = APIRouter(prefix="/idrive", tags=["idrive"])


@routes.get("/users")
async def get_idrive_users():
    try:
        response = get_users()
        if response["success"]:
            return Rs.success(response, "Users fetched successfully")
        return Rs.error(response, "Failed to fetch users")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/add-user")
async def add_user(body: ResellerUser):
    try:
        user = create_user_api(body.dict())
        if user["success"]:
            return Rs.success(user, "User created successfully")
        return Rs.error(user, "Failed to create user")
    except Exception as e:
        return Rs.server_error(data=e.__str__())


@routes.get("/enums")
async def get_enums():
    enum = enum_list()
    if enum:
        return Rs.success(enum, "Enums fetched successfully")
    return Rs.not_found("Failed to fetch enums")
