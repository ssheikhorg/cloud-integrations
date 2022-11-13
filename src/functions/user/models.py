from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute, BooleanAttribute,
    MapAttribute, ListAttribute, BinaryAttribute, JSONAttribute
)
from ..config import settings as c


class CognitoModel(Model):
    class Meta:
        table_name = c.dynamodb_table_name
        region = c.aws_default_region

    pk = UnicodeAttribute(hash_key=True)  # email
    sk = UnicodeAttribute(range_key=True, default="cognito") # sk
    password = UnicodeAttribute()
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute(null=True)
    role = UnicodeAttribute()
    phone_number = UnicodeAttribute(null=True)
    created_at = UnicodeAttribute()
    user_id = UnicodeAttribute(null=True)
    user_confirmed = BooleanAttribute()
    company = UnicodeAttribute(null=True)
    agreement = BooleanAttribute(null=True)
    tokens = MapAttribute(null=True)
