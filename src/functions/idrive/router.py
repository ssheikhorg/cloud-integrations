from fastapi import APIRouter

from . import schema as s
from .models import idrive_reseller_create
from .idrive_api import IDriveReseller
from ..utils.response import Response as Rs

routes = APIRouter(prefix="/idrive/reseller", tags=["idrive"])
m = IDriveReseller()


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
            context = await idrive_reseller_create(data)
            if context:
                return Rs.success(context, "User created successfully")
            return Rs.error(context, "Failed to save user")
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


@routes.post("/storage-usage")
async def get_reseller_storage_usage(body: s.StorageUsage):
    try:
        response = m.get_storage_usage(body.dict())
        if response["success"]:
            return Rs.success(response, "Storage usage fetched successfully")
        return Rs.error(response, "Failed to fetch storage usage")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.get("/regions/{role}/{email}")
async def get_regions(role: str, email: str):
    try:
        regions = m.get_reseller_regions_list(role, email)
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
