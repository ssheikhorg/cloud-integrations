from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# class ResellerUser(BaseModel):
#     email: str = Field(..., example="example@gmail.com")
#     password: str = Field(..., example="123456")
#     first_name: str = Field(..., example="John")
#     last_name: Optional[str] = Field(None, example="Doe")
#     quota: int = Field(..., example=100)


class BucketSchema(BaseModel):
    bucket_name: str
    storage_dn: str
    default_encryption: Optional[bool] = Field(default=False)
    versioning: Optional[bool] = Field(default=False)
    # object_locking: Optional[bool] = Field(default=False)


class UploadObjectSchema(BaseModel):
    bucket_name: str
    storage_dn: str


class StorageUsage(BaseModel):
    email: EmailStr = Field(...)
    date_from: str = Field(..., example="2023-11-31")
    date_to: str = Field(..., example="2023-11-31")


class AccessKeySchema(BaseModel):
    email: EmailStr
    storage_dn: str
    name: str


class AssignRegionSchema(BaseModel):
    email: EmailStr
    region_key: str


class RemoveRegionSchema(BaseModel):
    email: EmailStr
    storage_dn: str


class ObjectRemoveSchema(BaseModel):
    bucket_name: str
    object_name: str
    storage_dn: str
