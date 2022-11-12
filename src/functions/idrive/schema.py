from pydantic import BaseModel, Field, EmailStr
from enum import Enum, auto
from typing import Optional

from ..user.schema import RoleEnum


class RegionEnum(str, Enum):
    Oregon = "us-west-2"
    LosAngeles = "us-west-1"
    Virginia = "us-east-1"
    Dallas = "us-east-2"
    Phoenix = "us-west-3"
    Chicago = "us-central-1"
    SanJose = "us-central-2"
    Miami = "us-south-1"
    Montreal = "ca-central-1"
    Ireland = "eu-west-1"
    London = "eu-west-2"
    Frankfurt = "eu-central-1"
    Paris = "eu-west-3"


class QuotaEnum(str, Enum):
    GB100 = "100"
    GB200 = "200"
    GB300 = "300"
    GB400 = "400"
    GB500 = "500"
    GB600 = "600"
    GB700 = "700"
    GB800 = "800"
    GB900 = "900"
    GB1000 = "1000"


class ResellerUser(BaseModel):
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="123456")
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    quota: QuotaEnum = Field(..., example="100")


class Bucket(BaseModel):
    bucket_name: str = Field(..., example="my-bucket")
    region: RegionEnum = Field(..., example="London")
    # optional fields
    default_encryption: Optional[bool] = Field(False, example=False)
    object_locking: Optional[bool] = Field(False, example=False)
    versioning: Optional[bool] = Field(False, example=False)


class EnableRegion(BaseModel):
    email: EmailStr = Field(...)
    # storage_dn: str = Field(..., example="
