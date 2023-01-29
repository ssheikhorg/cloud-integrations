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


class RoleIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "role-index"
        projection = AllProjection()

    role = UnicodeAttribute(hash_key=True)


class EmailIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "email-index"
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)


class UserModel(BaseModel):
    pk = UnicodeAttribute(hash_key=True, default=lambda: str(uuid4()))
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

    username_index = UsernameIndex()
    role_index = RoleIndex()
    email_index = EmailIndex()