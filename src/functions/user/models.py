from ..models.users import UserModel
from ..core.database import DynamoDB
from ..utils.response import Response as Rs

db = DynamoDB(UserModel)


async def get_user_by_id(_id):
    try:
        if len(_id) == 36:
            user = list(await db.get(_id))
        elif "@" in _id:
            user = await db.query(pk=_id, index_name="email_index")
        else:
            user = await db.query(pk=_id, index_name="username_index")
        if user:
            return {"success": True, "body": user[0]}
        return {"success": False, "msg": "User not found"}
    except Exception as e:
        return Rs.server_error(e.__str__())


async def get_all_user(limit, offset):
    try:
        users = await db.scan()
        for x in users:
            x["access_tokens"] = x["access_tokens"].attribute_values
        return Rs.success(data=users)
        # return await db.scan(limit, offset)
    except Exception as e:
        return Rs.server_error(e.__str__())
