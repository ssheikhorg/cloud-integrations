from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ResellerUser(BaseModel):
    email: str = Field(..., example="example@gmail.com")
    password: str = Field(..., example="123456")
    first_name: str = Field(..., example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    quota: int = Field(..., example=100)


class Bucket(BaseModel):
    bucket_name: str = Field(..., example="my-bucket")
    # optional fields
    default_encryption: Optional[bool] = Field(False, example=False)
    object_locking: Optional[bool] = Field(False, example=False)
    versioning: Optional[bool] = Field(False, example=False)


class StorageUsage(BaseModel):
    email: EmailStr = Field(...)
    date_from: str = Field(..., example="2022-11-01")
    date_to: str = Field(..., example="2022-11-31")


class AccessKey(BaseModel):
    email: EmailStr = Field(..., description="Email of the reseller")
    storage_dn: str = Field(..., description="Storage DN of the reseller")
    name: str = Field(..., description="Name of the access key")
    permission: int = Field(..., description="Permission of the access key")
