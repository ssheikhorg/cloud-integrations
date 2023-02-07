from fastapi import APIRouter, Depends, Request

from .schemas import ResellerUser, StorageUsage, AccessKey
from .idrive_api import idrive
from ...services.auth import AuthBearer

admin_router = APIRouter(prefix="/idrive", tags=["idrive-admin"])


@admin_router.get("/users", dependencies=[Depends(AuthBearer())])
async def get_idrive_users():
    return await idrive.get_idrive_users()


@admin_router.post("/create", dependencies=[Depends(AuthBearer())])
async def create_reseller(body: ResellerUser, request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.create_reseller_user(_token, body.dict())


@admin_router.post("/disable", dependencies=[Depends(AuthBearer())])
async def disable_user(request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.disable_reseller_user(_token)


@admin_router.post("/enable", dependencies=[Depends(AuthBearer())])
async def enable_user(request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.enable_reseller_user(_token)


@admin_router.delete("/delete", dependencies=[Depends(AuthBearer())])
async def delete_user(request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.remove_reseller_user(_token)


""" Reseller API """
reseller_router = APIRouter(prefix="/idrive", tags=["idrive-reseller"])


@reseller_router.get("/regions", dependencies=[Depends(AuthBearer())])
async def get_regions(request: Request):
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.get_reseller_regions(_token)


@reseller_router.get("reseller-details", dependencies=[Depends(AuthBearer())])
async def get_reseller(request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.get_reseller_user(_token)


@reseller_router.post("/storage-usage", dependencies=[Depends(AuthBearer())])
async def get_reseller_storage_usage(body: StorageUsage):
    return await idrive.get_storage_usage(body.dict())


@reseller_router.post("/assign-region/{region}", dependencies=[Depends(AuthBearer())])
async def get_assign_region(region: str, request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.assign_reseller_user_region(_token, region)


@reseller_router.post("/remove-region/{region}", dependencies=[Depends(AuthBearer())])
async def get_remove_region(region: str, request: Request) -> dict:
    # region example: "LA"
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.remove_reseller_assigned_region(_token, region)


@reseller_router.post("/create-access-key", dependencies=[Depends(AuthBearer())])
async def get_create_access_key(body: AccessKey, request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.create_access_key(_token, body.dict())


@reseller_router.delete("/remove-access-key", dependencies=[Depends(AuthBearer())])
async def get_delete_access_key(request: Request) -> dict:
    _token = request.headers.get("Authorization").split(" ")[1]
    return await idrive.remove_access_key(_token)
