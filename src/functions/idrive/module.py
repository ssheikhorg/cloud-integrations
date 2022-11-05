import base64

import httpx

from ..core.configs import settings as c


# base64 encoded string
def get_base64_string(string):
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")


# base64 decoded string
def get_base64_decoded_string(string):
    return base64.b64decode(string).decode("utf-8")


def get_users():
    url = "https://api.idrivee2.com/api/reseller/v1/users"
    # encode token
    token = get_base64_string(c.reseller_api_key)
    headers = {
        "Content-Type": "application/json",
        "token": c.reseller_api_key
    }
    response = httpx.get(url, headers=headers)
    if response.status_code == 200:
        return {"success": True, "body": response.json()}
    return {"success": False, "body": response.json()}


def create_user_api(body):
    try:
        url = "https://api.idrivee2.com/api/reseller/v1/create_user"
        headers = {
            "Content-Type": "application/json",
            "token": c.reseller_api_key
        }
        body["password"] = get_base64_string(body["password"])
        response = httpx.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return {"success": True, "body": response.json()}
        return {"success": False, "body": response.json()}
    except Exception as e:
        return {"success": False, "body": e.__str__()}


def enum_list():
    return {
        "regions": {
            "Oregon": "us-west-2",
            "LosAngeles": "us-west-1",
            "Virginia": "us-east-1",
            "Dallas": "us-east-2",
            "Phoenix": "us-west-3",
            "Chicago": "us-central-1",
            "SanJose": "us-central-2",
            "Miami": "us-south-1",
            "Montreal": "ca-central-1",
            "Ireland": "eu-west-1",
            "London": "eu-west-2",
            "Frankfurt": "eu-central-1",
            "Paris": "eu-west-3"
        },
        "user_types": {
            "admin": "admin",
            "retailer": "retailer",
            "user": "user"
        },
        "quota": {
            "gb_100": "100 GB",
            "gb_200": "200 GB",
            "gb_300": "300 GB",
            "gb_400": "400 GB",
            "gb_500": "500 GB",
            "gb_600": "600 GB",
            "gb_700": "700 GB",
            "gb_800": "800 GB",
            "gb_900": "900 GB",
            "gb_1000": "1000 GB"
        }
    }
