import httpx

from ..config import settings as c
from ..utils.helpers import get_base64_string


class IDriveReseller:
    def __init__(self):
        self.token = c.reseller_api_key
        self.reseller_base_url = c.reseller_base_url

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

        response = httpx.put(url, headers=headers, json=body)

        if response.status_code == 200:
            body.pop("email_notification")
            return {"success": True, "body": body}
        return {"success": False, "body": response.json()}

    def disable_reseller_user(self, email):
        url = self.reseller_base_url + "/disable_user"
        headers = {"token": self.token}
        res = httpx.put(url, headers=headers, json={"email": email})
        response = res.json()
        if response["user_disabled"]:
            return {"success": True, "body": response}
        return {"success": False, "body": response.json()}


    def enable_reseller_user(self, email):
        url = self.reseller_base_url + "/enable_user"
        headers = {"token": self.token}
        body = {"email": email}
        res = httpx.put(url, headers=headers, json=body)
        response = res.json()
        if response["user_enabled"]:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def remove_reseller_user(self, email):
        url = self.reseller_base_url + "/delete_user"
        headers = {"token": self.token}
        body = {"email": email}
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def get_reseller_regions_list(self):
        url = self.reseller_base_url + "/regions"
        headers = {"token": self.token}
        response = httpx.get(url, headers=headers)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def enable_reseller_user_region(self, body):
        """body = {"email": email, "region": region}"""
        url = self.reseller_base_url + "/enable_user_region"
        headers = {"token": self.token}
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def remove_reseller_assigned_region(self, body):
        """body = {"email": email, "storage_dn": email}"""
        url = self.reseller_base_url + "/remove_user_region"
        headers = {"token": self.token}
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}


'''
    def create_reseller_access_key(self, body):
        """body = email, storage_dn, name, permission"""
        url = self.reseller_base_url + "/create_access_key"
        headers = {"token": self.token}
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}

    def remove_reseller_access_key(self, body):
        """body = email, storage_dn, access_key"""
        url = self.reseller_base_url + "/delete_access_key"
        headers = {"token": self.token}
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}
'''


def enum_list():
    return {
        "regions": {"Oregon": "us-west-2", "LosAngeles": "us-west-1", "Virginia": "us-east-1", "Dallas": "us-east-2",
                    "Phoenix": "us-west-3", "Chicago": "us-central-1", "SanJose": "us-central-2", "Miami": "us-south-1",
                    "Montreal": "ca-central-1", "Ireland": "eu-west-1", "London": "eu-west-2",
                    "Frankfurt": "eu-central-1",
                    "Paris": "eu-west-3"}, "user_types": {"admin": "admin", "retailer": "retailer", "user": "user"},
        "quota": {"100 GB": "100", "200 GB": "200", "300 GB": "300", "400 GB": "400", "500 GB": "500", "600 GB": "600",
                  "700 GB": "700", "800 GB": "800", "900 GB": "900", "1000 GB": "1000"}}
