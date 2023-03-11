from datetime import datetime
from typing import Any, Optional

from httpx import Timeout, AsyncClient
import boto3

from ...models.idrive import IDriveUserModel
from ...core.config import settings as c
from ...services.helpers import get_base64_string, get_base64_decoded_string
from ...core.database import DynamoDB
from ...utils.response import HttpResponse as Rs
from ..user.cognito import cognito

db = DynamoDB(IDriveUserModel)


def httpx_timeout(timeout: float = 60.0, connect: float = 60.0) -> Timeout:
    return Timeout(timeout=timeout, connect=connect)


async def _httpx_request(
        method: str,
        url: str, headers: Optional[dict] = None,
        data: Optional[dict] = None) -> Any:
    if not headers:
        headers = {"Accept": "application/json", "token": c.reseller_api_key}

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

    async def get_idrive_user(self, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")
            return Rs.success(user, "User found")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def create_reseller_user(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            url = self.base_url + "/create_user"
            body["password"] = get_base64_string(body["password"])
            body["email_notification"] = False
            res = await _httpx_request("PUT", url, data=body)
            if res.status_code == 200:
                body.pop("email_notification")
                body["pk"] = pk
                body["created_at"] = str(datetime.today().replace(microsecond=0))
                body["user_enabled"] = True
                # save user to dynamodb
                await db.create(body)
                return Rs.success(res.json(), "User created successfully")
            return Rs.bad_request(res.json(), "Failed to create user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def enable_reseller_user(self, email: str, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            # get user from dynamodb
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            url = self.base_url + "/enable_user"
            res = await _httpx_request("POST", url, data={"email": email})
            if res.status_code == 200:
                # update user in dynamodb
                user["user_enabled"] = True
                await db.update(user)
                return Rs.success(res.json(), "User enabled successfully")
            return Rs.bad_request(msg="Failed to enable user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def disable_reseller_user(self, email: str, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            # get user from dynamodb
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            url = self.base_url + "/disable_user"
            res = await _httpx_request("POST", url, data={"email": email})
            if res.status_code == 200:
                # update user in dynamodb
                user["user_enabled"] = False
                await db.update(user)
                return Rs.success(msg="User disabled successfully")
            return Rs.bad_request(res.json(), "Failed to disable user")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_reseller_user(self, email: str, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            # get user pk from cognito
            details = cognito.get_user_info(token)
            pk = details["UserAttributes"][0]["Value"]
            # get user from dynamodb
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")
            url = self.base_url + "/remove_user"
            res = await _httpx_request("POST", url, data={"email": email})
            if res.status_code == 200:
                # delete user from dynamodb
                await db.delete(pk, "idrive")
                return Rs.success(res.json(), "User removed successfully")
            return Rs.bad_request(msg="Failed to remove user")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Reseller(API):

    async def get_reseller_regions(self, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            user = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")

            if len(user.get("available_regions", [])) > 0:
                return Rs.success(user["available_regions"], "Regions fetched successfully")
            else:
                url = self.base_url + "/regions"
                res = await _httpx_request("GET", url)
                res_json = res.json()
                if res.status_code == 200:
                    # save regions to dynamodb
                    user["available_regions"] = res_json["regions"]
                    await db.update(user)
                    return Rs.success(user["available_regions"], "Regions fetched successfully")
                return Rs.bad_request(res_json, "Failed to fetch regions")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def assign_reseller_user_region(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            region = body.get("region_key")
            email = body.get("email")
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")
            if region in [r["region"] for r in item["assigned_regions"]]:
                return Rs.conflict(msg="Region already assigned")

            url = self.base_url + "/enable_user_region"
            body = {"email": email, "region": region}
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

    async def remove_reseller_assigned_region(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            email = body.get("email")
            storage_dn = body.get("storage_dn")
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            user = await db.get(pk, "idrive")
            url = self.base_url + "/remove_user_region"
            body = {"email": email, "storage_dn": storage_dn}

            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                for item in user["assigned_regions"]:
                    if item["storage_dn"] == storage_dn:
                        user["assigned_regions"].remove(item)
                        # save changes to dynamodb
                        await db.update(user)
                        return Rs.success("res.json()", "Region removed successfully")
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

    async def create_access_key(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            body["permissions"] = 2
            url = self.base_url + "/create_access_key"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code == 200:
                result = res.json()
                update_item = {
                    **result["data"],
                    "storage_dn": body["storage_dn"],
                    "email": body["email"],
                    "created_at": str(datetime.today().replace(microsecond=0))
                }
                item["reseller_access_key"].append(update_item)
                await db.update(item)
                return Rs.success(msg="Access key created successfully")
            return Rs.bad_request(data=res.json(), msg="Failed to create access key")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_access_key(self, storage_dn: str, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            url = self.base_url + "/remove_access_key"
            for data in item["reseller_access_key"]:
                if data["storage_dn"] == storage_dn:
                    # remove access key from idrive
                    payload = {
                        "access_key": data["access_key"],
                        "email": data["email"],
                        "storage_dn": data["storage_dn"]
                    }
                    res = await _httpx_request("POST", url, data=payload)
                    if res.status_code == 200:
                        # remove access key from dynamodb
                        item["reseller_access_key"].remove(data)
                        await db.update(item)
                        return Rs.success(res.json(), "Access key removed successfully")
                    return Rs.bad_request(msg="Failed to remove access key")
            return Rs.not_found(msg="Access key not found")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Operations:
    """create idrive bucket"""

    @staticmethod
    async def create_bucket(body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            for data in item["reseller_access_key"]:
                if data["storage_dn"] == body["storage_dn"]:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            client = boto3.client("s3", endpoint_url=f"https://{body['storage_dn']}",
                                  aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            result = client.create_bucket(Bucket=body["bucket_name"])
            if body["versioning"]:
                client.put_bucket_versioning(
                    Bucket=body["bucket_name"],
                    VersioningConfiguration={"Status": "Enabled"}
                )
            if body["default_encryption"]:
                client.put_bucket_encryption(
                    Bucket=body["bucket_name"],
                    ServerSideEncryptionConfiguration={
                        "Rules": [
                            {
                                "ApplyServerSideEncryptionByDefault": {
                                    "SSEAlgorithm": "AES256"
                                }
                            }
                        ]
                    }
                )
            if result["ResponseMetadata"]["HTTPStatusCode"] == 200:
                # update user and append assigned region
                to_update = {"bucket_name": body["bucket_name"], "storage_dn": body["storage_dn"],
                             "created_at": str(datetime.today().replace(microsecond=0))}

                item["buckets"].append(to_update)
                await db.update(item)
                return Rs.success(result, "Bucket created successfully")
            return Rs.bad_request(msg="Failed to create bucket")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def delete_bucket(storage_dn: str, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            for data in item["reseller_access_key"]:
                if data["storage_dn"] == storage_dn:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            for bucket in item["buckets"]:
                if bucket["storage_dn"] == storage_dn:
                    client = boto3.client("s3", endpoint_url=f"https://{storage_dn}",
                                          aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    result = client.delete_bucket(Bucket=bucket["bucket_name"])
                    if result["ResponseMetadata"]["HTTPStatusCode"] == 204:
                        item["buckets"].remove(bucket)
                        await db.update(item)
                        return Rs.success(msg="Bucket deleted successfully")
                    return Rs.bad_request(msg="Failed to delete bucket")
            return Rs.not_found(msg="Bucket not found")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def get_bucket_list(request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")
            return Rs.success(item["buckets"], "Buckets fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def upload_object(storage_dn: str, request: Any, files: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            for data in item["reseller_access_key"]:
                if data["storage_dn"] == storage_dn:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            for bucket in item["buckets"]:
                if bucket["storage_dn"] == storage_dn:
                    client = boto3.resource("s3", endpoint_url=f"https://{storage_dn}",
                                            aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    for x in files:
                        name = x.filename
                        file = x.file.read()
                        size = round(len(file) / 1024 / 1024, 2)
                        content_type = x.content_type
                        client.Bucket(bucket["bucket_name"]).put_object(Key=name, Body=file)
                        # push file name to dynamodb
                        to_update = {
                            "name": name,
                            "created_at": str(datetime.today().replace(microsecond=0)),
                            "size": size,
                            "url": f"https://{bucket['bucket_name']}.{storage_dn}/{name}",
                            "content_type": content_type
                        }
                        # add an array of files to bucket
                        bucket["files"] = []
                        bucket["files"].append(to_update)
                        await db.update(item)
                        return Rs.success(data=to_update, msg="File uploaded successfully")
                return Rs.not_found(msg="Bucket not found")
            return Rs.not_found(msg="Bucket not found")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def get_object_list(request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")
            for x in item["buckets"]:
                if "files" not in x:
                    x["files"] = []
                return Rs.success(x["files"], "Files fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def delete_object(body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "idrive")

            for data in item["reseller_access_key"]:
                if data["storage_dn"] == body["storage_dn"]:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            for bucket in item["buckets"]:
                if bucket["storage_dn"] == body["storage_dn"]:
                    for file in bucket["files"]:
                        if file["name"] == body["object_name"]:
                            client = boto3.client("s3", endpoint_url=f"https://{bucket['storage_dn']}",
                                                  aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                            result = client.delete_object(Bucket=body["bucket_name"], Key=body["object_name"])
                            if result["ResponseMetadata"]["HTTPStatusCode"] == 204:
                                bucket["files"].remove(file)
                                await db.update(item)
                                return Rs.success(msg="File deleted successfully")
                            return Rs.bad_request(msg="Failed to delete file")
                    return Rs.not_found(msg="File not found")
            return Rs.not_found(msg="Bucket not found")
        except Exception as e:
            return Rs.server_error(e.__str__())


class IdriveFactory(Reseller, Operations):
    """Idrive factory class"""


idrive = IdriveFactory()
