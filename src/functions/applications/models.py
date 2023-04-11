from datetime import datetime

from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.attributes import (
    UnicodeAttribute, BooleanAttribute, MapAttribute, NumberAttribute, ListAttribute
)
from pynamodb.models import Model

from ..core.config import settings as c
from .user.schemas import Role


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


class ResellerUserModel(MapAttribute):
    created_at = UnicodeAttribute(null=True)
    user_enabled = BooleanAttribute(default=False)
    assigned_regions: ListAttribute = ListAttribute(default=[])
    access_tokens: MapAttribute = MapAttribute(default={})  # ak, sk from /create_access_key api
    available_regions: ListAttribute = ListAttribute(of=MapAttribute, default=[])  # regions from /regions api
    reseller_access_key: ListAttribute = ListAttribute(of=MapAttribute, default=[])
    buckets: ListAttribute = ListAttribute(of=MapAttribute, default=[])


class UserModel(Model):
    class Meta:
        table_name = f"{c.env_state}-be3-table"
        region = c.aws_default_region

    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True, default="user")
    username = UnicodeAttribute()
    email = UnicodeAttribute()
    password = UnicodeAttribute()
    email_verified = BooleanAttribute(null=True, default=False)
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute(null=True)
    role = UnicodeAttribute(default=Role.USER)
    phone_number = UnicodeAttribute(null=True)
    created_at = UnicodeAttribute(default=lambda: str(datetime.today().replace(microsecond=0)))
    updated_at = UnicodeAttribute(default=lambda: str(datetime.today().replace(microsecond=0)))
    company = UnicodeAttribute(null=True)
    agreement = BooleanAttribute(null=True)
    access_tokens: MapAttribute = MapAttribute(default={})
    quota = NumberAttribute(default=100)
    activity_log = ListAttribute(of=MapAttribute, default=[])
    reseller = ResellerUserModel(null=True, default={})

    username_index = UsernameIndex()
    role_index = RoleIndex()
    email_index = EmailIndex()
