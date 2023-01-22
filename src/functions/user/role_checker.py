from fastapi import HTTPException, Depends

from ..models.users import UserModel
from ..services.auth import get_current_user
from ..utils.response import Response as Rs
from .schemas.roles import AuthUser


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: AuthUser = Depends(get_current_user)) -> dict:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=Rs.forbidden(msg="You don't have permission to access this resource"))
        return user.dict()
