from fastapi import HTTPException, Depends

from ...services.auth import get_current_user_role
from .schemas import AuthUser


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, users: AuthUser = Depends(get_current_user_role)) -> dict:
        for user in users:
            if user not in self.allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this resource",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return {"success": True}
