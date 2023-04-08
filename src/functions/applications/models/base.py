from pynamodb.models import Model

from ...core.config import settings as c


class BaseModel(Model):
    class Meta:
        table_name = f"{c.env_state}-be3-table"
        region = c.aws_default_region
