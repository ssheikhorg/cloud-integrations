from datetime import datetime
from typing import Any, Optional

from httpx import Timeout, AsyncClient
import boto3

from ...models.idrive import IDriveUserModel  # type: ignore
from ...core.config import settings as c  # type: ignore
from ...services.helpers import get_base64_string  # type: ignore
from ...core.database import DynamoDB  # type: ignore
from ...utils.response import HttpResponse as Rs  # type: ignore
from ..user.cognito import cognito  # type: ignore

db = DynamoDB(IDriveUserModel)


def httpx_timeout(timeout: float = 60.0, connect: float = 60.0) -> Timeout:
    return Timeout(timeout=timeout, connect=connect)


async def _httpx_request(method: str, url: str, headers: Optional[dict] = None, data: Optional[dict] = None) -> Any:
    if not headers:
        headers = {"Content-Type": "application/json", "Accept": "application/json",
                   "token": c.reseller_api_key}
    async with AsyncClient(timeout=httpx_timeout()) as client:
        if method == "GET":
            return await client.get(url, headers=headers)
        elif method == "POST":
            return await client.post(url, headers=headers, data=data)
        elif method == "PUT":
            return await client.put(url, headers=headers, data=data)
        elif method == "DELETE":
            return await client.delete(url, headers=headers)
        else:
            return None


class API:
    def __init__(self) -> None:
        self.base_url = c.reseller_base_url

    async def get_idrive_users(self) -> Any:
        try:
            url = self.base_url + "/users"
            res = await _httpx_request("GET", url)
            if res.status_code == 200:
                return Rs.success(res.json(), "Users fetched successfully")
            return Rs.bad_request(msg="Failed to fetch users")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def create_reseller_user(self, token: str, body: dict) -> Any:
        try:
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]

            url = self.base_url + "/create_user"
            body["password"] = get_base64_string(body["password"])
            body["email_notification"] = False
            res = await _httpx_request("PUT", url, data=body)
            res_json = res.json()
            if res.status_code == 200:
                # if res.json()["user_created"]:
                body.pop("email_notification")
                body["pk"] = pk
                body["created_at"] = str(datetime.today().replace(microsecond=0))
                body["user_enabled"] = True
                # save user to dynamodb
                await db.create(**body)
                return Rs.success(res_json, "User created successfully")
            return Rs.bad_request(res_json, "Failed to create user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def enable_reseller_user(self, token: str) -> Any:
        try:
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            # get user from dynamodb
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            url = self.base_url + "/enable_user"
            res = await _httpx_request("POST", url, data={"email": user["email"]})
            if res.status_code == 200:
                # update user in dynamodb
                user["user_enabled"] = True
                await db.update(user)
                return Rs.success(res.json(), "User enabled successfully")
            return Rs.bad_request(msg="Failed to enable user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def disable_reseller_user(self, token: str) -> Any:
        try:
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            # get user from dynamodb
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            url = self.base_url + "/disable_user"
            res = await _httpx_request("POST", url, data={"email": user["email"]})
            res_json = res.json()
            if res.status_code == 200:
                # update user in dynamodb
                user["user_enabled"] = False
                await db.update(user)
                return Rs.success(res_json, "User disabled successfully")
            return Rs.bad_request(res_json, "Failed to disable user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_reseller_user(self, token: str) -> Any:
        try:
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            # get user from dynamodb
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            url = self.base_url + "/remove_user"
            res = await _httpx_request("POST", url, data={"email": user["email"]})
            if res.status_code == 200:
                # delete user from dynamodb
                await db.delete(pk, "idrive")
                return Rs.success(res.json(), "User removed successfully")
            return Rs.bad_request(msg="Failed to remove user")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Reseller(API):

    async def get_reseller_regions(self, token: str) -> Any:
        try:
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            if len(user["available_regions"]) > 0:
                return Rs.success(user["available_regions"], "Regions fetched successfully")
            else:
                url = self.base_url + "/regions"
                res = await _httpx_request("GET", url)
                res_json = res.json()
                if res.status_code == 200:
                    # save regions to dynamodb
                    user["available_regions"] = res_json
                    await db.update(user)
                    return Rs.success(res_json, "Regions fetched successfully")
                return Rs.bad_request(res_json, "Failed to fetch regions")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_reseller_user(self, token: str) -> Any:
        try:
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")
            return Rs.success(user, "User fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def assign_reseller_user_region(self, token: str, region: str) -> Any:
        try:
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            if region in [r["region"] for r in item["assigned_regions"]]:
                return Rs.bad_request(msg="Region already assigned")

            url = self.base_url + "/enable_user_region"
            body = {"email": item["email"], "region": region}
            res = await _httpx_request("POST", url, data=body)
            res_json = res.json()
            if res.status_code == 200:
                # update user and append assigned region
                to_update = {"region": body["region"], "storage_dn": res_json["storage_dn"],
                             "assigned_at": str(datetime.today().replace(microsecond=0))}

                item["assigned_regions"].append(to_update)
                await db.update(item)
                return Rs.success(res_json, "Region assigned successfully")
            return Rs.bad_request(res_json, "Failed to assign region")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_reseller_assigned_region(self, token: str, region_key: str) -> Any:
        try:
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")
            url = self.base_url + "/remove_user_region"
            body = {"email": item["email"], "region": region_key}
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                for item in item["assigned_regions"]:
                    if item["region"] == body["region"]:
                        item["assigned_regions"].remove(item)
                        # save changes to dynamodb
                        await db.update(item)
                        return Rs.success(res.json(), "Region removed successfully")
                return Rs.bad_request(msg="Failed to remove region")
            return Rs.bad_request(msg="Failed to remove region")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_storage_usage(self, body: dict) -> Any:
        try:
            url = self.base_url + "/usage_stats"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                return Rs.success(res.json(), "Storage usage fetched successfully")
            return Rs.bad_request(msg="Failed to fetch storage usage")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def create_access_key(self, token: str, body: dict) -> Any:
        try:
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            url = self.base_url + "/create_access_key"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                kwargs = {"access_key": res.json()["access_key"], "storage_dn": res.json()["storage_dn"],
                          "created_at": str(datetime.today().replace(microsecond=0))}
                item["access_keys"].append(kwargs)
                await db.update(item)
                return Rs.success(res.json(), "Access key created successfully")
            return Rs.bad_request(msg="Failed to create access key")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_access_key(self, token: str) -> Any:
        try:
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            url = self.base_url + "/remove_access_key"
            if "access_key" in item:
                data = {
                    "email": item["email"],
                    "access_key": item["access_key"],
                    "storage_dn": item["storage_dn"],
                }
                res = await _httpx_request("POST", url, data=data)

                if res.status_code == 200:
                    item["access_key"] = None
                    item["storage_dn"] = None
                    await db.update(item)
                    return Rs.success(res.json(), "Access key removed successfully")
                return Rs.bad_request(msg="Failed to remove access key")
            return Rs.not_found(msg="Access key not found")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Operations:
    """create idrive bucket"""

    async def create_bucket(self, body: dict) -> Any:
        try:
            endpoint = "https://api.idrive.com/v1/bucket/create"
            client = boto3.client("s3", endpoint_url=endpoint)
            res = client.create_bucket(Bucket=body["bucket_name"])
            return Rs.success(res, "Bucket created successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())


class IdriveFactory(Reseller, Operations):
    """Idrive factory class"""


idrive = IdriveFactory()
