from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class Bucket(BaseModel):
    bucket_name: str = Field(..., example="my-bucket")
    # optional fields
    default_encryption: Optional[bool] = Field(False, example=False)
    object_locking: Optional[bool] = Field(False, example=False)
    versioning: Optional[bool] = Field(False, example=False)


class AssignRegion(BaseModel):
    email: EmailStr = Field(..., example="example@mail.com")
    region: str = Field(..., example="LDN")


class RemoveRegion(BaseModel):
    email: EmailStr = Field(..., example="example@mail.com")
    region_key: str = Field(..., example="LA")


class StorageUsage(BaseModel):
    email: EmailStr = Field(...)
    date_from: str = Field(..., example="2022-11-01")
    date_to: str = Field(..., example="2022-11-31")


class AccessKey(BaseModel):
    email: EmailStr = Field(..., example="example@mail.com")
    storage_dn: str = Field(..., example="i4v5.ldn.idrivee2-33.com")
    name: str = Field(..., example="my-access-key")
    permission: int = Field(..., example=1)
