from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter

from . import schema as s
from .module import IDriveReseller, enum_list
from .models import ResellerModel
from ..utils.response import Response as Rs

routes = APIRouter(prefix="/idrive/reseller", tags=["idrive"])
m = IDriveReseller()


# from ..core.configs import settings as c
# import boto3
# dynamo = boto3.resource('dynamodb', region_name=c.aws_default_region,
#                         aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
# table = dynamo.Table("be3cloud-table")


@routes.get("/users")
async def get_idrive_users():
    try:
        response = m.get_idrive_users()
        if response["success"]:
            return Rs.success(response, "Users fetched successfully")
        return Rs.error(response, "Failed to fetch users")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/create")
async def create_reseller(body: s.ResellerUser):
    try:
        data = body.dict()
        user = m.create_reseller_user(data)
        if user["success"]:
            data["pk"] = data.pop("email")
            data["sk"] = data.pop("first_name")
            data["reseller_id"] = str(uuid4())
            data["created_at"] = datetime.today()
            data["user_enabled"] = True

            ResellerModel(**data).save()
            return Rs.success(data, "User created successfully")
        return Rs.error(user, "Failed to create user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.put("/disable/{email}")
async def disable_user(email: str):
    try:
        user = m.disable_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User disabled successfully")
        return Rs.error(user, "Failed to disable user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.put("/enable/{email}")
async def enable_user(email: str):
    try:
        user = m.enable_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User enabled successfully")
        return Rs.error(user, "Failed to enable user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.put("/delete/{email}")
async def delete_user(email: str):
    try:
        user = m.remove_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User removed successfully")
        return Rs.error(user, "Failed to remove user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.get("/regions")
async def get_regions():
    try:
        regions = m.get_reseller_regions_list()
        if regions["success"]:
            return Rs.success(regions, "Regions fetched successfully")
        return Rs.error(regions, "Failed to fetch regions")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/assign-region")
async def get_assign_region(body: s.EnableRegion):
    try:
        regions = m.enable_reseller_user_region(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Assign region fetched successfully")
        return Rs.error(regions, "Failed to fetch assign region")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/remove-region")
async def get_remove_region(body: s.EnableRegion):
    try:
        regions = m.remove_reseller_assigned_region(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Remove region fetched successfully")
        return Rs.error(regions, "Failed to fetch remove region")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.get("/enums")
async def get_enums():
    enum = enum_list()
    if enum:
        return Rs.success(enum, "Enums fetched successfully")
    return Rs.not_found("Failed to fetch enums")
