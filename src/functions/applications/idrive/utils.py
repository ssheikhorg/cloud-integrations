from datetime import datetime
from typing import Any, Optional
from httpx import Timeout, AsyncClient

from ...services.helpers import get_base64_string
from ...models.idrive import IDriveUserModel
from ...core.config import settings as c
from ...core.database import DynamoDB
from ...utils.response import HttpResponse as Rs

db = DynamoDB(IDriveUserModel)


def httpx_timeout(timeout: float = 60.0, connect: float = 60.0) -> Timeout:
    return Timeout(timeout=timeout, connect=connect)


async def _httpx_request(method: str,
                         url: str, headers: Optional[dict] = None,
                         data: Optional[dict] = None
                         ) -> Any:
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


async def create_idrive_reseller_user(data: dict) -> Any:
    try:
        body = {
            "email": data["email"],
            "password": data["password"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "quota": data["quota"]
        }
        url = c.reseller_base_url + "/create_user"
        body["password"] = get_base64_string(body["password"])
        body["email_notification"] = False
        res = await _httpx_request("PUT", url, data=body)
        if res.status_code == 200:
            body.pop("email_notification")
            body["pk"] = data["pk"]
            body["created_at"] = str(datetime.today().replace(microsecond=0))
            body["user_enabled"] = True
            # save user to dynamodb
            await db.create(body)
            return Rs.success(res.json(), "User created successfully")
        return Rs.bad_request(res.json(), "Failed to create user")
    except Exception as e:
        return Rs.server_error(e.__str__())


async def remove_reseller_user(pk: str) -> Any:
    try:
        # get user from dynamodb
        user = await db.get(pk, "idrive")
        if not user:
            return Rs.not_found(msg="User not found")
        url = c.reseller_base_url + "/remove_user"
        res = await _httpx_request("POST", url, data={"email": user["email"]})
        if res.status_code == 200:
            # delete user from dynamodb
            await db.delete(pk, "idrive")
            return Rs.success(msg="User removed successfully")
        return Rs.bad_request(msg="Failed to remove user")
    except Exception as e:
        return Rs.server_error(e.__str__())


async def get_idrive_user_details(pk: str, cognito: bool = False) -> Any:
    try:
        user = await db.get(pk, "idrive")
        if cognito:
            return user
        if not user:
            return Rs.not_found(msg="User not found")
        return Rs.success(user, "User found")
    except Exception as e:
        return Rs.server_error(e.__str__())
