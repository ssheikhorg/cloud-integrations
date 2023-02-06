from pynamodb.models import Model
from ..core.config import settings as c


class BaseModel(Model):
    class Meta:
        table_name = f"be3-table-{c.env_state}"
        region = c.aws_default_region
