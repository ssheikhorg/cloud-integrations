from typing import Any
from fastapi import APIRouter, Depends, Request, File, UploadFile

from .schemas import (
    StorageUsage, AccessKeySchema, ObjectRemoveSchema,
    AssignRegionSchema, RemoveRegionSchema, BucketSchema
)
from .idrive_api import idrive
from .utils import get_idrive_user_details
from ...services.auth import AuthBearer
from ..user.schemas import EmailSchema

""" Admin API """
admin_router = APIRouter(
    prefix="/idrive", tags=["idrive-admin"], dependencies=[Depends(AuthBearer())]
)


@admin_router.get("/reseller-details")
async def get_idrive_reseller_details(pk: str) -> Any:
    return await get_idrive_user_details(pk)


@admin_router.post("/disable")
async def disable_user(request: Request) -> Any:
    return await idrive.disable_reseller_user(request)


@admin_router.post("/enable")
async def enable_user(request: Request) -> Any:
    return await idrive.enable_reseller_user(request)


""" Reseller API """
reseller_router = APIRouter(
    prefix="/idrive", tags=["idrive-reseller"], dependencies=[Depends(AuthBearer())]
)


@reseller_router.get("/regions")
async def get_regions(request: Request) -> Any:
    return await idrive.get_reseller_regions(request)


@reseller_router.post("/assign-region")
async def get_assign_region(body: AssignRegionSchema, request: Request) -> Any:
    return await idrive.assign_reseller_user_region(body.dict(), request)


@reseller_router.post("/remove-region")
async def get_remove_region(body: RemoveRegionSchema, request: Request) -> Any:
    return await idrive.remove_reseller_assigned_region(body.dict(), request)


@reseller_router.post("/storage-usage")
async def get_reseller_storage_usage(body: StorageUsage) -> Any:
    return await idrive.get_storage_usage(body.dict())


@reseller_router.post("/create-access-key")
async def get_create_access_key(body: AccessKeySchema, request: Request) -> Any:
    return await idrive.create_access_key(body.dict(), request)


@reseller_router.delete("/remove-access-key")
async def get_delete_access_key(storage_dn: str, request: Request) -> Any:
    return await idrive.remove_access_key(storage_dn, request)


""" Operations API """
# make operations router file upload compatible
operations_router = APIRouter(
    prefix="/idrive", tags=["idrive-operations"], dependencies=[Depends(AuthBearer())]
)


@operations_router.post("/create-bucket")
async def create_bucket(body: BucketSchema, request: Request) -> Any:
    return await idrive.create_bucket(body.dict(), request)


@operations_router.delete("/remove-bucket")
async def delete_bucket(storage_dn: str, request: Request) -> Any:
    return await idrive.delete_bucket(storage_dn, request)


@operations_router.get("/list-buckets")
async def get_bucket_list(request: Request) -> Any:
    return await idrive.get_bucket_list(request)


@operations_router.post("/upload-object")
async def upload_object(storage_dn: str, request: Request, files: list[UploadFile] = File(...)) -> Any:
    return await idrive.upload_object(storage_dn, request, files)


@operations_router.get("/list-objects")
async def get_object_list(request: Request) -> Any:
    return await idrive.get_object_list(request)


@operations_router.post("/remove-object")
async def delete_object(body: ObjectRemoveSchema, request: Request) -> Any:
    return await idrive.delete_object(body.dict(), request)
