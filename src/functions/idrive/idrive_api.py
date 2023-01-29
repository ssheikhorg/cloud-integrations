from datetime import datetime

from httpx import Timeout, AsyncClient

from ..models.idrive import RegionsModel, ResellerModel
from ..core.config import settings as c
from ..services.helpers import get_base64_string
from ..core.database import DynamoDB
from ..utils.response import Response as Rs
from ..user.cognito import cognito

db_reseller = DynamoDB(ResellerModel)
db_regions = DynamoDB(RegionsModel)


def httpx_timeout(timeout=60.0, connect=60.0):
    return Timeout(timeout=timeout, connect=connect)


async def _httpx_request(method: str, url: str, headers=None, data=None):
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


class IDriveAPI:
    def __init__(self):
        self.base_url = c.reseller_base_url

    async def get_idrive_users(self):
        try:
            url = self.base_url + "/users"
            res = await _httpx_request("GET", url)
            if res.status_code == 200:
                return Rs.success(res.json(), "Users fetched successfully")
            return Rs.error(res.json(), "Failed to fetch users")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def create_reseller_user(self, body):
        try:
            url = self.base_url + "/create_user"
            body["password"] = get_base64_string(body["password"])
            body["email_notification"] = False
            res = await _httpx_request("PUT", url, data=body)
            if res.status_code == 200:
                # if res.json()["user_created"]:
                body.pop("email_notification")
                body["pk"] = body.pop("email")
                body["created_at"] = str(datetime.today().replace(microsecond=0))
                body["user_enabled"] = True
                # save user to dynamodb
                await db_reseller.create(**body)
                return Rs.success(res.json(), "User created successfully")
            return Rs.error(res.json(), "Failed to create user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def enable_reseller_user(self, email):
        try:
            url = self.base_url + "/enable_user"
            res = await _httpx_request("POST", url, data={"email": email})
            if res.status_code == 200:
                # if res.json()["user_enabled"]:
                return Rs.success(res.json(), "User enabled successfully")
            return Rs.error(res.json(), "Failed to enable user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def disable_reseller_user(self, email):
        try:
            url = self.base_url + "/disable_user"
            res = await _httpx_request("POST", url, data={"email": email})
            if res.status_code == 200:
                # if res.json()["user_disabled"]:
                return Rs.success(res.json(), "User disabled successfully")
            return Rs.error(res.json(), "Failed to disable user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_reseller_user(self, email):
        try:
            url = self.base_url + "/remove_user"
            res = await _httpx_request("POST", url, data={"email": email})
            if res.status_code == 200:
                # if res.json()["user_removed"]:
                return Rs.success(res.json(), "User removed successfully")
            return Rs.error(res.json(), "Failed to remove user")
        except Exception as e:
            return Rs.server_error(e.__str__())


class IDriveReseller(IDriveAPI):

    async def get_reseller_regions(self, _token) -> dict:
        user = cognito.get_user_info(_token)
        email = user["UserAttributes"][3]["Value"]
        try:
            user = db_regions.get(email)
            if user:
                return Rs.success(user, "Regions fetched successfully")
            else:
                url = self.base_url + "/regions"
                res = await _httpx_request("GET", url)
                if res.status_code == 200:
                    items = res.json()
                    items["email"] = email
                    # save regions to dynamodb
                    await db_regions.create(**items)
                    return Rs.success(items, "Regions fetched successfully")
                return Rs.error(res.json(), "Failed to fetch regions")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_reseller_user(self, email):
        try:
            user = await db_reseller.query(email)
            if user:
                return Rs.success(user[0], "User fetched successfully")
            return Rs.error("Failed to fetch user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def assign_reseller_user_region(self, body):
        try:
            url = self.base_url + "/enable_user_region"
            payload = {"email": body["email"], "region": body["region"]}

            res = await _httpx_request("POST", url, data=payload)
            if res.status_code == 200:
                # if data["storage_added"]:
                # update user and append assigned region
                update_kw = {"region": body["region"], "storage_dn": res.json()["storage_dn"],
                             "assigned_at": str(datetime.today().replace(microsecond=0))}

                item = await db_reseller.query(body["email"])
                item[0]["assigned_regions"].append(update_kw)
                await db_reseller.update(item[0])
                return Rs.success(res.json(), "Region assigned successfully")
            return Rs.error(res.json(), "Failed to assign region")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_reseller_assigned_region(self, body):
        try:
            url = self.base_url + "/remove_user_region"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                # if res.json()["removed"]:
                items = await db_reseller.query(body["email"])
                for item in items[0]["assigned_regions"]:
                    if item["region"] == body["region"]:
                        items[0]["assigned_regions"].remove(item)
                        # save changes to dynamodb
                        await db_reseller.update(items[0])
                        return Rs.success(res.json(), "Region removed successfully")
                return Rs.error("Failed to remove region")
            return Rs.error(res.json(), "Failed to remove region")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_storage_usage(self, body):
        try:
            url = self.base_url + "/usage_stats"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                return Rs.success(res.json(), "Storage usage fetched successfully")
            return Rs.error(res.json(), "Failed to fetch storage usage")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def create_access_key(self, body):
        try:
            url = self.base_url + "/create_access_key"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                # if res.json()["created"]:
                kwargs = {"access_key": res.json()["access_key"], "storage_dn": res.json()["storage_dn"],
                          "created_at": str(datetime.today().replace(microsecond=0))}
                item = await db_reseller.get(body["email"])
                item["access_keys"].append(kwargs)
                await db_reseller.update(item)
                return Rs.success(res.json(), "Access key created successfully")
            return Rs.error(res.json(), "Failed to create access key")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_access_key(self, email):
        try:
            item = await db_reseller.get(email)
            url = self.base_url + "/remove_access_key"

            if "access_key" in item:
                data = {
                    "email": email,
                    "access_key": item["access_key"],
                    "storage_dn": item["storage_dn"],
                }
                res = await _httpx_request("POST", url, data=data)

                if res.status_code == 200:
                    item["access_key"] = None
                    item["storage_dn"] = None
                    await db_reseller.update(item)
                    return Rs.success(res.json(), "Access key removed successfully")
                return Rs.error(res.json(), "Failed to remove access key")
            return Rs.error("Access key not found")
        except Exception as e:
            return Rs.server_error(e.__str__())


idrive = IDriveReseller()
