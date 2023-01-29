from fastapi import APIRouter, Depends, Request

from .schemas import user as s, reseller as r
from .idrive_api import idrive
from ..services.auth import AuthBearer

admin_router = APIRouter(prefix="/idrive", tags=["idrive-admin"])


@admin_router.get("/users")
async def get_idrive_users():
    return await idrive.get_idrive_users()


@admin_router.post("/create")
async def create_reseller(body: s.ResellerUser):
    return await idrive.create_reseller_user(body.dict())


@admin_router.post("/disable/{email}")
async def disable_user(email: str):
    return await idrive.disable_reseller_user(email)


@admin_router.post("/enable/{email}")
async def enable_user(email: str):
    return await idrive.enable_reseller_user(email)


@admin_router.post("/delete/{email}")
async def delete_user(email: str):
    return await idrive.remove_reseller_user(email)


""" Reseller API """
reseller_router = APIRouter(prefix="/idrive", tags=["idrive-reseller"])


@reseller_router.get("/regions-list", dependencies=[Depends(AuthBearer())])
async def get_regions(request: Request):
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.get_reseller_regions(_token)


@reseller_router.get("reseller-details/{email}")
async def get_reseller(email: str):
    return await idrive.get_reseller_user(email)


@reseller_router.post("/storage-usage")
async def get_reseller_storage_usage(body: r.StorageUsage):
    return await idrive.get_storage_usage(body.dict())


@reseller_router.post("/assign-region")
async def get_assign_region(body: r.AssignRegion):
    return await idrive.assign_reseller_user_region(body.dict())


@reseller_router.post("/remove-region")
async def get_remove_region(body: r.RemoveRegion):
    return await idrive.remove_reseller_assigned_region(body.dict())


@reseller_router.post("/create-access-key")
async def get_create_access_key(body: r.AccessKey):
    return await idrive.create_access_key(body.dict())


@reseller_router.post("/remove-access-key/{email}")
async def get_delete_access_key(email: str):
    return await idrive.remove_access_key(email)
