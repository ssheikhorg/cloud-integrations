from fastapi import APIRouter

from . import schema as s
from .idrive_api import IDriveReseller
from ..utils.response import Response as Rs

routes = APIRouter(prefix="/idrive/reseller", tags=["idrive"])
m = IDriveReseller()


# """RESELLER USER APIs"""
@routes.get("/regions")
async def get_regions():
    try:
        regions = m.get_reseller_regions_list()
        if regions["success"]:
            return Rs.success(regions, "Regions fetched successfully")
        return Rs.error(regions, "Failed to fetch regions")
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


@routes.post("/assign-region")
async def get_assign_region(body: s.AssignRegion):
    try:
        regions = m.assign_reseller_user_region(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Assign region fetched successfully")
        return Rs.error(regions, "Failed to fetch assign region")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/remove-region")
async def get_remove_region(body: s.AssignRegion):
    try:
        regions = m.remove_reseller_assigned_region(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Remove region fetched successfully")
        return Rs.error(regions, "Failed to fetch remove region")
    except Exception as e:
        return Rs.server_error(e.__str__())


# """Admin APIs"""
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
        user = m.create_reseller_user(body.dict())
        if user["success"]:
            return Rs.success(user, "User created successfully")
        return Rs.error(user, "Failed to create user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/disable/{email}")
async def disable_user(email: str):
    try:
        user = m.disable_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User disabled successfully")
        return Rs.error(user, "Failed to disable user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/enable/{email}")
async def enable_user(email: str):
    try:
        user = m.enable_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User enabled successfully")
        return Rs.error(user, "Failed to enable user")
    except Exception as e:
        return Rs.server_error(e.__str__())


@routes.post("/delete/{email}")
async def delete_user(email: str):
    try:
        user = m.remove_reseller_user(email)
        if user["success"]:
            return Rs.success(user, "User removed successfully")
        return Rs.error(user, "Failed to remove user")
    except Exception as e:
        return Rs.server_error(e.__str__())