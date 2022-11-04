from pydantic import BaseModel, Field
from enum import Enum, auto
from typing import Optional


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
    gb_100 = 102400
    gb_200 = 204800
    gb_300 = 307200
    gb_400 = 409600
    gb_500 = 512000
    gb_600 = 614400
    gb_700 = 716800
    gb_800 = 819200
    gb_900 = 921600
    gb_1000 = 1024000


class ResellerUser(BaseModel):
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="123456")
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    quota: QuotaEnum = Field(..., example="102400")


class Bucket(BaseModel):
    bucket_name: str = Field(..., example="my-bucket")
    region: RegionEnum = Field(..., example="London")
    # optional fields
    default_encryption: Optional[bool] = Field(False, example=False)
    object_locking: Optional[bool] = Field(False, example=False)
    versioning: Optional[bool] = Field(False, example=False)
