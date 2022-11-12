from datetime import datetime
from uuid import uuid4

from .dynamo import ResellerModel


async def idrive_reseller_create(body):
    body["pk"] = body.pop("email")
    body["sk"] = body.pop("quota")
    # body["reseller_id"] = str(uuid4())
    # remove miliseconds from datetime
    body["created_at"] = str(datetime.today().replace(microsecond=0))
    body["user_enabled"] = True
    print("body: ", body)
    user = ResellerModel(**body)
    user.save()
    return body
