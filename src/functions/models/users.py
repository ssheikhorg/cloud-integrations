from datetime import datetime

from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.attributes import (
    UnicodeAttribute, BooleanAttribute, MapAttribute
)
from uuid import uuid4
from ..user.schemas.roles import Role
from .base import BaseModel


class UsernameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "username-index"
        projection = AllProjection()

    username = UnicodeAttribute(hash_key=True)


class UsersIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "sk-index"
        projection = AllProjection()

    sk = UnicodeAttribute(hash_key=True)


class RoleIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "role-index"
        projection = AllProjection()

    role = UnicodeAttribute(hash_key=True)


class UserModel(BaseModel):
    pk = UnicodeAttribute(hash_key=True, default=lambda: str(uuid4()))
    sk = UnicodeAttribute(range_key=True, default="user")
    username = UnicodeAttribute()
    email = UnicodeAttribute(null=True)
    password = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute(null=True)
    role = UnicodeAttribute(default=Role.USER)
    phone_number = UnicodeAttribute(null=True)
    created_at = UnicodeAttribute(default=lambda: str(datetime.today().replace(microsecond=0)))
    user_confirmed = BooleanAttribute(default=False)
    company = UnicodeAttribute(null=True)
    agreement = BooleanAttribute(null=True)
    access_tokens = MapAttribute(default={})

    # email_index = EmailIndex()
    username_index = UsernameIndex()
    user_index = UsersIndex()
    role_index = RoleIndex()

# class EmailIndex(GlobalSecondaryIndex):
#     class Meta:
#         index_name = "email-index"
#         projection = AllProjection()
#
#     email = UnicodeAttribute(hash_key=True)
#     sk = UnicodeAttribute(range_key=True, default="user")
