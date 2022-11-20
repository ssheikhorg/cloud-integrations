from fastapi import APIRouter

from ...utils.response import Response as Rs
from ..schema import reseller as s
from ..idrive_api import IDriveReseller

router = APIRouter(prefix="/idrive-reseller", tags=["idrive-reseller"])
r = IDriveReseller()


@router.get("/regions")
async def get_regions():
    try:
        regions = r.get_reseller_regions_list()
        if regions["success"]:
            return Rs.success(regions, "Regions fetched successfully")
        return Rs.error(regions, "Failed to fetch regions")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/storage-usage")
async def get_reseller_storage_usage(body: s.StorageUsage):
    try:
        response = r.get_storage_usage(body.dict())
        if response["success"]:
            return Rs.success(response, "Storage usage fetched successfully")
        return Rs.error(response, "Failed to fetch storage usage")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/assign-region")
async def get_assign_region(body: s.AssignRegion):
    try:
        regions = await r.assign_reseller_user_region(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Assign region fetched successfully")
        return Rs.error(regions, "Failed to fetch assign region")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/remove-region")
async def get_remove_region(body: s.RemoveRegion):
    try:
        regions = r.remove_reseller_assigned_region(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Remove region fetched successfully")
        return Rs.error(regions, "Failed to fetch remove region")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/create-access-key")
async def get_create_access_key(body: s.AccessKey):
    try:
        regions = r.create_access_key(body.dict())
        if regions["success"]:
            return Rs.success(regions, "Create access key fetched successfully")
        return Rs.error(regions, "Failed to fetch create access key")
    except Exception as e:
        return Rs.server_error(e.__str__())


@router.post("/remove-access-key/{email}")
async def get_delete_access_key(email: str):
    try:
        regions = r.remove_access_key(email)
        if regions["success"]:
            return Rs.success(regions, "Delete access key fetched successfully")
        return Rs.error(regions, "Failed to fetch delete access key")
    except Exception as e:
        return Rs.server_error(e.__str__())
