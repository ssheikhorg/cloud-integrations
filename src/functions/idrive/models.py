from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute, BooleanAttribute,
    MapAttribute, ListAttribute, BinaryAttribute, JSONAttribute
)
from ..config import settings as c


class ResellerModel(Model):
    class Meta:
        table_name = c.dynamodb_table_name
        region = c.aws_default_region

    pk = UnicodeAttribute(hash_key=True)  # email
    sk = UnicodeAttribute(range_key=True, default="reseller")  # sk
    password = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute(null=True)
    quota = NumberAttribute(default=100)
    created_at = UnicodeAttribute()
    user_enabled = BooleanAttribute()
    region = ListAttribute(of=MapAttribute, null=True)


class RegionsModel(Model):
    class Meta:
        table_name = c.dynamodb_table_name
        region = c.aws_default_region

    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)
    regions = ListAttribute(of=MapAttribute)
