from uuid import uuid4

from .base import BaseModel
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, BooleanAttribute, MapAttribute, ListAttribute
)


class ResellerModel(BaseModel):
    email = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute(default="")
    quota = NumberAttribute(default=100)
    created_at = UnicodeAttribute()
    user_enabled = BooleanAttribute()
    assigned_regions = ListAttribute(default=[])
    access_tokens = MapAttribute(default={})  # ak, sk from /create_access_key api


class RegionsModel(BaseModel):
    pk = UnicodeAttribute(hash_key=True, default=lambda: str(uuid4()))
    regions = ListAttribute(of=MapAttribute)
