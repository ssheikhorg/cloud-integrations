from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    ADMIN = "admin"
    RETAILER = "retailer"
    USER = "user"


class AuthUser(BaseModel):
    pk: str
    role: Role = Role.USER

    class Config:
        orm_mode = True
