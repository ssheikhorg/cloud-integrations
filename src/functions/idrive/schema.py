from pydantic import BaseModel, Field, EmailStr
from enum import Enum, auto
from typing import Optional

from ..user.schema import RoleEnum


# Oregon = "us-west-2"
# LosAngeles = "us-west-1"
# Virginia = "us-east-1"
# Dallas = "us-east-2"
# Phoenix = "us-west-3"
# Chicago = "us-central-1"
# SanJose = "us-central-2"
# Miami = "us-south-1"
# Montreal = "ca-central-1"
# Ireland = "eu-west-1"
# London = "eu-west-2"
# Frankfurt = "eu-central-1"
# Paris = "eu-west-3"

class RegionEnum(str, Enum):
    LosAngeles = "LA"
    Virginia = "VA"
    Oregon = "OR"
    Dallas = "DA"
    Phoenix = "PH"
    Chicago = "CH"
    SanJose = "SJ"
    Miami = "MI"
    Montreal = "CA"
    Ireland = "IE"
    London = "LDN"
    Frankfurt = "FRA"
    Paris = "PAR"


class ResellerUser(BaseModel):
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="123456")
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    quota: int = Field(..., example=100)


class Bucket(BaseModel):
    bucket_name: str = Field(..., example="my-bucket")
    # region: RegionEnum = Field(..., example="London")
    # optional fields
    default_encryption: Optional[bool] = Field(False, example=False)
    object_locking: Optional[bool] = Field(False, example=False)
    versioning: Optional[bool] = Field(False, example=False)


class AssignRegion(BaseModel):
    email: EmailStr = Field(..., example="example@mail.com")
    region: RegionEnum = Field(..., example="LDN")


class RemoveRegion(BaseModel):
    email: EmailStr = Field(..., example="example@mail.com")
    storage_dn: str = Field(..., example="i4v5.ldn.idrivee2-33.com")


class StorageUsage(BaseModel):
    email: EmailStr = Field(...)
    date_from: str = Field(..., example="2022-11-01")
    date_to: str = Field(..., example="2022-11-31")
