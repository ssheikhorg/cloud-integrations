from typing import Any, Optional
from fastapi import APIRouter, Depends, Request

from .schemas import ResellerUser, StorageUsage, AccessKeySchema, AssignRegionSchema, RemoveRegionSchema, BucketSchema
from .idrive_api import idrive
from ...services.auth import AuthBearer

""" Admin API """
admin_router = APIRouter(prefix="/idrive", tags=["idrive-admin"])


@admin_router.get("/user", dependencies=[Depends(AuthBearer())])
async def get_idrive_users(request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.get_idrive_user(_token.split(" ")[1])


@admin_router.post("/create", dependencies=[Depends(AuthBearer())])
async def create_reseller(body: ResellerUser, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.create_reseller_user(_token.split(" ")[1], body.dict())


@admin_router.post("/disable/{email}", dependencies=[Depends(AuthBearer())])
async def disable_user(email: str, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.disable_reseller_user(email, _token.split(" ")[1])


@admin_router.post("/enable/{email}", dependencies=[Depends(AuthBearer())])
async def enable_user(email: str, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.enable_reseller_user(email, _token.split(" ")[1])


@admin_router.delete("/delete/{email}", dependencies=[Depends(AuthBearer())])
async def delete_user(email: str, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.remove_reseller_user(email, _token.split(" ")[1])


""" Reseller API """
reseller_router = APIRouter(prefix="/idrive", tags=["idrive-reseller"])


@reseller_router.get("/regions", dependencies=[Depends(AuthBearer())])
async def get_regions(request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.get_reseller_regions(_token.split(" ")[1])


@reseller_router.post("/assign-region", dependencies=[Depends(AuthBearer())])
async def get_assign_region(body: AssignRegionSchema, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.assign_reseller_user_region(_token.split(" ")[1], body.dict())


@reseller_router.post("/remove-region", dependencies=[Depends(AuthBearer())])
async def get_remove_region(body: RemoveRegionSchema, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.remove_reseller_assigned_region(_token.split(" ")[1], body.dict())


@reseller_router.post("/storage-usage", dependencies=[Depends(AuthBearer())])
async def get_reseller_storage_usage(body: StorageUsage) -> Any:
    return await idrive.get_storage_usage(body.dict())


@reseller_router.post("/create-access-key", dependencies=[Depends(AuthBearer())])
async def get_create_access_key(body: AccessKeySchema, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.create_access_key(_token.split(" ")[1], body.dict())


@reseller_router.delete("/remove-access-key", dependencies=[Depends(AuthBearer())])
async def get_delete_access_key(request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.remove_access_key(_token.split(" ")[1])

""" Operations API """
operations_router = APIRouter(prefix="/idrive", tags=["idrive-operations"])


@operations_router.post("/create-bucket", dependencies=[Depends(AuthBearer())])
async def create_bucket(body: BucketSchema, request: Request) -> Any:
    _token = request.headers.get("Authorization")
    if _token:
        return await idrive.create_bucket(_token.split(" ")[1], body.dict())
