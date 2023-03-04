from .base import BaseModel

from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, BooleanAttribute, MapAttribute, ListAttribute
)


class IDriveUserModel(BaseModel):
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True, default="idrive")
    email = UnicodeAttribute(null=True)
    password = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute(default="")
    quota = NumberAttribute(default=100)
    created_at = UnicodeAttribute()
    user_enabled = BooleanAttribute()
    assigned_regions: ListAttribute = ListAttribute(default=[])
    access_tokens: MapAttribute = MapAttribute(default={})  # ak, sk from /create_access_key api
    available_regions: ListAttribute = ListAttribute(of=MapAttribute, default=[])  # regions from /regions api
