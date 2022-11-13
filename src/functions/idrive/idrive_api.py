from datetime import datetime

import httpx

from .models import RegionsModel, ResellerModel
from ..config import settings as c
from ..utils.helpers import get_base64_string


class IDriveReseller:
    def __init__(self):
        self.token = c.reseller_api_key
        self.reseller_base_url = c.reseller_base_url
        self.table = c.dynamodb_table_name

    def get_idrive_users(self):
        url = self.reseller_base_url + "/users"
        headers = {"token": self.token}
        response = httpx.get(url, headers=headers)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def create_reseller_user(self, body):
        url = self.reseller_base_url + "/create_user"
        headers = {"token": self.token}
        body["password"] = get_base64_string(body["password"])
        body["email_notification"] = False

        res = httpx.put(url, headers=headers, data=body)

        if res.json()["user_created"]:
            body.pop("email_notification")
            body["pk"] = body.pop("email")
            body["created_at"] = str(datetime.today().replace(microsecond=0))
            body["user_enabled"] = True
            ResellerModel(**body).save()
            return {"success": True, "body": body}
        return {"success": False, "body": res.json()}

    def disable_reseller_user(self, email):
        url = self.reseller_base_url + "/disable_user"
        headers = {"token": self.token}
        res = httpx.post(url, headers=headers, data={"email": email})
        if res.json()["user_disabled"]:
            return {"success": True, "body": res.json()}
        return {"success": False, "body": res.json()}

    def enable_reseller_user(self, email):
        url = self.reseller_base_url + "/enable_user"
        headers = {"token": self.token}
        res = httpx.post(url, headers=headers, data={"email": email})
        if res.json()["user_enabled"]:
            return {"success": True, "body": res.json()}
        return {"success": False, "body": res.json()}

    def remove_reseller_user(self, email):
        url = self.reseller_base_url + "/remove_user"
        headers = {"token": self.token}
        res = httpx.post(url, headers=headers, data={"email": email})
        if res.json()["user_removed"]:
            return {"success": True, "body": res.json()}
        return {"success": False, "body": res.json()}

    def get_reseller_regions_list(self):
        user = RegionsModel.get("regions", "regions")
        if user:
            return {"success": True, "body": user.regions}
        return {"success": False, "body": "No regions found"}

    def assign_reseller_user_region(self, body):
        user = ResellerModel.get(body["email"], "reseller")
        if user:
            url = self.reseller_base_url + "/enable_user_region"
            headers = {"token": self.token}
            data = {"email": body["email"], "region": body["region"]}

            res = httpx.post(url, headers=headers, data=data)
            print(res.json())
            if res.json()["storage_added"]:
                user.region = body["region"]
                user.save()
                return {"success": True, "body": res.json()}
            return {"success": False, "body": res.json()}
        #     if body["region"] in user.region:
        #         return {"success": False, "body": "Region already assigned"}


    def remove_reseller_assigned_region(self, body):
        """body = {"email": email, "storage_dn": email}"""
        url = self.reseller_base_url + "/remove_user_region"
        headers = {"token": self.token}
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def get_storage_usage(self, body):
        url = self.reseller_base_url + "/usage_stats"
        headers = {"token": self.token}
        response = httpx.post(url, headers=headers, data=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}


"""
            "regions": [
                {
                    "region_key": "VA",
                    "region_name": "Virginia",
                    "country": "US",
                    "active": true,
                    "region_code": "us-va"
                },
                {
                    "region_key": "LA",
                    "region_name": "Los Angeles",
                    "country": "US",
                    "active": true,
                    "region_code": "us-la"
                },
                {
                    "region_key": "OR",
                    "region_name": "Oregon",
                    "country": "US",
                    "active": true,
                    "region_code": "us-or"
                },
                {
                    "region_key": "DA",
                    "region_name": "Dallas",
                    "country": "US",
                    "active": true,
                    "region_code": "us-da"
                },
                {
                    "region_key": "PH",
                    "region_name": "Phoenix",
                    "country": "US",
                    "active": true,
                    "region_code": "us-ph"
                },
                {
                    "region_key": "CH",
                    "region_name": "Chicago",
                    "country": "US",
                    "active": true,
                    "region_code": "us-ch"
                },
                {
                    "region_key": "SJ",
                    "region_name": "San Jose",
                    "country": "US",
                    "active": true,
                    "region_code": "us-sj"
                },
                {
                    "region_key": "MI",
                    "region_name": "Miami",
                    "country": "US",
                    "active": true,
                    "region_code": "us-mi"
                },
                {
                    "region_key": "CA",
                    "region_name": "Montreal (Canada)",
                    "country": "CA",
                    "active": true,
                    "region_code": "ca-mtl"
                },
                {
                    "region_key": "IE",
                    "region_name": "Ireland",
                    "country": "IE",
                    "active": true,
                    "region_code": "eu-ie"
                },
                {
                    "region_key": "LDN",
                    "region_name": "London",
                    "country": "GB",
                    "active": true,
                    "region_code": "gb-ldn"
                },
                {
                    "region_key": "FRA",
                    "region_name": "Frankfurt",
                    "country": "DE",
                    "active": true,
                    "region_code": "de-fra"
                },
                {
                    "region_key": "PAR",
                    "region_name": "Paris",
                    "country": "FR",
                    "active": true,
                    "region_code": "fr-par"
                }
            ]
"""