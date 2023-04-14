from datetime import datetime
from typing import Any
from fastapi import status as st
import boto3

from ..models import UserModel
from ...core.config import settings as c
from ...core.database import DynamoDB
from ...utils.response import HttpResponse as Rs
from .utils import _httpx_request
from ..user.cognito import cognito

db = DynamoDB(UserModel)


class API:
    def __init__(self) -> None:
        self.base_url = c.reseller_base_url

    async def enable_reseller_user(self, email: str) -> Any:
        try:
            # get user from dynamodb
            users = await db.query(pk=email, index_name="email_index")
            user = users[0]
            if not user:
                return Rs.not_found(msg="User not found")

            user["reseller"] = user["reseller"].attribute_values
            url = self.base_url + "/enable_user"
            res = await _httpx_request("POST", url, data={"email": user["email"]})

            if res.status_code != st.HTTP_200_OK:
                return Rs.bad_request(msg="Failed to enable user")

            # update user in dynamodb
            user["reseller"]["user_enabled"] = True
            # update in activity_log
            user["activity_log"].append({
                "action": "Reseller user enabled",
                "time": str(datetime.today().replace(microsecond=0)),
            })
            await db.update(user)
            return Rs.success(msg="User enabled successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def disable_reseller_user(self, email: str) -> Any:
        try:
            # get user from dynamodb
            users = await db.query(pk=email, index_name="email_index")
            user = users[0]
            if not user:
                return Rs.not_found(msg="User not found")

            user["reseller"] = user["reseller"].attribute_values
            url = self.base_url + "/disable_user"
            res = await _httpx_request("POST", url, data={"email": user["email"]})
            if res.status_code != st.HTTP_200_OK:
                return Rs.bad_request(msg="Failed to disable user")
            # update user in dynamodb
            user["reseller"]["user_enabled"] = False
            # update in activity_log
            user["activity_log"].append({
                "action": "Reseller user disabled",
                "time": str(datetime.today().replace(microsecond=0)),
            })
            await db.update(user)
            return Rs.success(msg="User disabled successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Reseller(API):

    async def get_reseller_regions(self, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            user = await db.get(pk, "user")
            if not user:
                return Rs.not_found(msg="User not found")

            user["reseller"] = user["reseller"].attribute_values
            if len(user["reseller"].get("available_regions", [])) > 0:
                return Rs.success(user["reseller"]["available_regions"], "Regions fetched successfully")
            else:
                url = self.base_url + "/regions"
                res = await _httpx_request("GET", url)
                res_json = res.json()
                if res.status_code != st.HTTP_200_OK:
                    return Rs.bad_request(res_json, "Failed to fetch regions")
                # save regions to dynamodb
                user["reseller"]["available_regions"] = res_json["regions"]
                # update in activity_log
                user["activity_log"].append({
                    "action": "Reseller regions fetched",
                    "time": str(datetime.today().replace(microsecond=0)),
                })
                await db.update(user)
                return Rs.success(res_json["regions"], "Regions fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def assign_reseller_user_region(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            region = body.get("region_key")
            email = body.get("email")
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            if region in [r["region"] for r in item["reseller"]["assigned_regions"]]:
                return Rs.conflict(msg="Region already assigned")

            url = self.base_url + "/enable_user_region"
            body = {"email": email, "region": region}
            res = await _httpx_request("POST", url, data=body)
            res_json = res.json()

            if res.status_code != st.HTTP_200_OK:
                return Rs.bad_request(res_json, "Failed to assign region")

            # update user and append assigned region
            to_update = {"region": body["region"], "storage_dn": res_json["storage_dn"],
                         "assigned_at": str(datetime.today().replace(microsecond=0))}
            item["reseller"]["assigned_regions"].append(to_update)
            # update in activity_log
            item["activity_log"].append({
                "action": "Reseller region assigned",
                "time": str(datetime.today().replace(microsecond=0)),
            })
            await db.update(item)
            return Rs.success(res_json, "Region assigned successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def get_reseller_details(pk: str) -> Any:
        try:
            item = await db.get(pk, "user")
            if not item:
                return Rs.not_found(msg="User not found")
            item["reseller"] = item["reseller"].attribute_values
            return Rs.success(item["reseller"], "Reseller details fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_reseller_assigned_region(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            email = body.get("email")
            storage_dn = body.get("storage_dn")
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            user = await db.get(pk, "user")
            user["reseller"] = user["reseller"].attribute_values

            url = self.base_url + "/remove_user_region"
            body = {"email": email, "storage_dn": storage_dn}

            res = await _httpx_request("POST", url, data=body)
            if res.status_code != st.HTTP_200_OK:
                return Rs.bad_request(msg="Failed to remove region")

            for item in user["reseller"]["assigned_regions"]:
                if item["storage_dn"] == storage_dn:
                    user["reseller"]["assigned_regions"].remove(item)
                    # update in activity_log
                    user["activity_log"].append({
                        "action": "Reseller region removed",
                        "time": str(datetime.today().replace(microsecond=0)),
                    })
                    # save changes to dynamodb
                    await db.update(user)
                    return Rs.success("res.json()", "Region removed successfully")
            return Rs.not_found(msg="Region not found")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_storage_usage(self, body: dict) -> Any:
        try:
            url = self.base_url + "/usage_stats"
            res = await _httpx_request("POST", url, data=body)

            if res.status_code != st.HTTP_200_OK:
                return Rs.bad_request(msg="Failed to fetch storage usage")

            return Rs.success(res.json(), "Storage usage fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def create_access_key(self, body: dict, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            body["permissions"] = 2
            url = self.base_url + "/create_access_key"
            res = await _httpx_request("POST", url, data=body)
            if res.status_code != st.HTTP_200_OK:
                return Rs.bad_request(data=res.json(), msg="Failed to create access key")
            result = res.json()
            update_item = {
                **result["data"],
                "storage_dn": body["storage_dn"],
                "email": body["email"],
                "created_at": str(datetime.today().replace(microsecond=0))
            }
            item["reseller"]["reseller_access_key"].append(update_item)
            # update in activity_log
            item["activity_log"].append({
                "action": "Reseller access key created",
                "time": str(datetime.today().replace(microsecond=0)),
            })
            await db.update(item)
            return Rs.success(msg="Access key created successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def remove_access_key(self, storage_dn: str, request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            url = self.base_url + "/remove_access_key"
            for data in item["reseller"]["reseller_access_key"]:
                if data["storage_dn"] == storage_dn:
                    # remove access key from idrive
                    payload = {
                        "access_key": data["access_key"],
                        "email": data["email"],
                        "storage_dn": data["storage_dn"]
                    }
                    res = await _httpx_request("POST", url, data=payload)
                    if res.status_code == st.HTTP_200_OK:
                        # remove access key from dynamodb
                        item["reseller"]["reseller_access_key"].remove(data)
                        # update in activity_log
                        item["activity_log"].append({
                            "action": "Reseller access key removed",
                            "time": str(datetime.today().replace(microsecond=0)),
                        })
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
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            for data in item["reseller"]["reseller_access_key"]:
                if data["storage_dn"] == body["storage_dn"]:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            client = boto3.client("s3", endpoint_url=f"https://{body['storage_dn']}",
                                  aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            if body["versioning"]:
                client.put_bucket_versioning(
                    Bucket=body["bucket_name"],
                    VersioningConfiguration={"Status": "Enabled"}
                )
            if body["default_encryption"]:
                client.put_bucket_encryption(
                    Bucket=body["bucket_name"],
                    ServerSideEncryptionConfiguration={
                        "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
                    }
                )
            result = client.create_bucket(Bucket=body["bucket_name"])
            if result["ResponseMetadata"]["HTTPStatusCode"] == 200:
                # update user and append assigned region
                to_update = {"bucket_name": body["bucket_name"], "storage_dn": body["storage_dn"],
                             "created_at": str(datetime.today().replace(microsecond=0))}

                item["reseller"]["buckets"].append(to_update)
                # update in activity_log
                item["activity_log"].append({
                    "action": "Reseller bucket created",
                    "time": str(datetime.today().replace(microsecond=0)),
                })
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
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            for data in item["reseller"]["reseller_access_key"]:
                if data["storage_dn"] == storage_dn:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            for bucket in item["reseller"]["buckets"]:
                if bucket["storage_dn"] == storage_dn:
                    client = boto3.client("s3", endpoint_url=f"https://{storage_dn}",
                                          aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    result = client.delete_bucket(Bucket=bucket["bucket_name"])
                    if result["ResponseMetadata"]["HTTPStatusCode"] == 204:
                        item["reseller"]["buckets"].remove(bucket)
                        # update in activity_log
                        item["activity_log"].append({
                            "action": "Reseller bucket deleted",
                            "time": str(datetime.today().replace(microsecond=0)),
                        })
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
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values
            return Rs.success(item["reseller"]["buckets"], "Buckets fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def upload_object(request: Any, body: dict, files: Any) -> Any:
        try:
            storage_dn = body["storage_dn"]
            bucket_name = body["bucket_name"]
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            for data in item["reseller"]["reseller_access_key"]:
                if data["storage_dn"] == storage_dn:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            for bucket in item["reseller"]["buckets"]:
                if bucket["storage_dn"] == storage_dn and bucket["bucket_name"] == bucket_name:
                    client = boto3.resource("s3", endpoint_url=f"https://{storage_dn}",
                                            aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                    for x in files:
                        name = x.filename
                        file = x.file.read()
                        size = round(len(file) / 1024, 2)
                        content_type = x.content_type
                        client.Bucket(bucket["bucket_name"]).put_object(Key=name, Body=file)
                        # push file name to dynamodb
                        to_update = {
                            "name": name,
                            "created_at": str(datetime.today().replace(microsecond=0)),
                            "size": f"{size} KB" if size < 1024 else f"{round(size / 1024, 2)} MB",
                            "url": f"https://{bucket_name}.{storage_dn}/{name}",
                            "content_type": content_type
                        }
                        # add an array of files to bucket
                        if "files" not in bucket:
                            bucket["files"] = []
                        bucket["files"].append(to_update)
                        # update in activity_log
                        item["activity_log"].append({
                            "action": "Reseller file uploaded",
                            "time": str(datetime.today().replace(microsecond=0)),
                        })
                        await db.update(item)
                        return Rs.success(data=to_update, msg="File uploaded successfully")
            return Rs.not_found(msg="Bucket not found")
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def get_object_list(request: Any) -> Any:
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            user_info = cognito.get_user_info(token)
            pk = user_info["UserAttributes"][0]["Value"]
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            for x in item["reseller"]["buckets"]:
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
            item = await db.get(pk, "user")
            item["reseller"] = item["reseller"].attribute_values

            for data in item["reseller"]["reseller_access_key"]:
                if data["storage_dn"] == body["storage_dn"]:
                    access_key = data["access_key"]
                    secret_key = data["secret_key"]
                    break
            else:
                return Rs.not_found(msg="Access key not found")

            for bucket in item["reseller"]["buckets"]:
                if bucket["storage_dn"] == body["storage_dn"]:
                    for file in bucket["files"]:
                        if file["name"] == body["object_name"]:
                            client = boto3.client("s3", endpoint_url=f"https://{bucket['storage_dn']}",
                                                  aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                            result = client.delete_object(Bucket=body["bucket_name"], Key=body["object_name"])
                            if result["ResponseMetadata"]["HTTPStatusCode"] == 204:
                                bucket["files"].remove(file)
                                # update in activity_log
                                item["activity_log"].append({
                                    "action": "Reseller file deleted",
                                    "time": str(datetime.today().replace(microsecond=0)),
                                })
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
