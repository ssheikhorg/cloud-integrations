from datetime import datetime

import httpx

from .models import RegionsModel, ResellerModel
from ..config import settings as c
from ..utils.helpers import get_base64_string
from ..database import DynamoDBCRUD


class IDriveAPI:
    def __init__(self):
        self.token = c.reseller_api_key
        self.reseller_base_url = c.reseller_base_url
        self.table = c.dynamodb_table_name
        self.timeout = httpx.Timeout(60.0, connect=60.0)

    def get_idrive_users(self):
        url = self.reseller_base_url + "/users"
        headers = {"token": self.token}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200:
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}

    def create_reseller_user(self, body):
        url = self.reseller_base_url + "/create_user"
        headers = {"token": self.token}
        body["password"] = get_base64_string(body["password"])
        body["email_notification"] = False

        with httpx.Client(timeout=self.timeout) as client:
            res = client.put(url, headers=headers, data=body)
            if res.json()["user_created"]:
                body.pop("email_notification")
                body["pk"] = body.pop("email")
                body["created_at"] = str(datetime.today().replace(microsecond=0))
                body["user_enabled"] = True
                # save user to dynamodb
                DynamoDBCRUD(ResellerModel).create(**body)
                return {"success": True, "body": body}
            return {"success": False, "body": res.json()}

    def enable_reseller_user(self, email):
        url = self.reseller_base_url + "/enable_user"
        headers = {"token": self.token}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, data={"email": email})
            if res.json()["user_enabled"]:
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}

    def disable_reseller_user(self, email):
        url = self.reseller_base_url + "/disable_user"
        headers = {"token": self.token}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, data={"email": email})
            if res.json()["user_disabled"]:
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}

    def remove_reseller_user(self, email):
        url = self.reseller_base_url + "/remove_user"
        headers = {"token": self.token}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, data={"email": email})
            if res.json()["user_removed"]:
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}


class IDriveReseller(IDriveAPI):

    def get_reseller_regions_list(self):
        user = RegionsModel.get("regions", "regions")
        if user:
            return {"success": True, "body": user.regions}
        return {"success": False, "body": "No regions found"}

    def assign_reseller_user_region(self, body):
        try:
            url = self.reseller_base_url + "/enable_user_region"
            headers = {"token": self.token}
            payload = {"email": body["email"], "region": body["region"]}

            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, data=payload)
                data = res.json()
                if data["storage_added"]:
                    update = {"assigned_regions": {
                        "region": body["region"],
                        "storage_dn": data["storage_dn"],
                        "assigned_at": str(datetime.today().replace(microsecond=0)),
                    }}
                    # update user and append assigned region
                    DynamoDBCRUD(ResellerModel).update(body["email"], "reseller", update, arr=True)
                    return {"success": True, "body": update["assigned_regions"]}

            return {"success": True, "body": "Region assigned successfully"}
        except Exception as e:
            return {"success": False, "body": e.__str__()}

    def remove_reseller_assigned_region(self, body):
        user = ResellerModel.get(body["email"], "reseller")
        if user:

            url = self.reseller_base_url + "/remove_user_region"
            headers = {"token": self.token}

            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, data=body, timeout=60)
                if res.json()["removed"]:
                    return {"success": True, "body": res.json()}
                return {"success": False, "body": res.json()}

    def get_storage_usage(self, body):
        url = self.reseller_base_url + "/usage_stats"
        headers = {"token": self.token}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, data=body)
            if res.status_code == 200:
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}

    def create_access_key(self, body):
        url = self.reseller_base_url + "/create_access_key"
        headers = {"token": self.token}
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, data=body)
            if res.json()["created"]:
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}

    def remove_access_key(self, email):
        user = ResellerModel.get(email, "reseller")
        url = self.reseller_base_url + "/remove_access_key"

        if "access_key" in user:
            headers = {"token": self.token}
            data = {
                "email": email,
                "access_key": user["access_key"],
                "storage_dn": user["storage_dn"],
            }
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, data=data)
                if res.json()["removed"]:
                    return {"success": True, "body": res.json()}
                return {"success": False, "body": res.json()}
