from fastapi import HTTPException, Depends
from typing import Optional

from ...services.auth import get_current_user_role
from .schemas import AuthUser


class RoleChecker:
    def __init__(self, allowed_roles: list) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, users: AuthUser = Depends(get_current_user_role)) -> Optional[bool]:
        for user in users:
            if user not in self.allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this resource",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return True
        return None
   