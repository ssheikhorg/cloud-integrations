from pynamodb.models import Model
from ..core.config import settings as c


class BaseModel(Model):
    class Meta:
        table_name = c.dynamodb_table_name
        region = c.aws_default_region
