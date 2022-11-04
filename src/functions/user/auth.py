from typing import Any

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer

from .module import CognitoUser


class AuthBearer(HTTPBearer):
    def __init__(self):
        super().__init__()
        self.client = CognitoUser()

    async def __call__(self, request: Request) -> Any:
        try:
            access_token = request.headers['Authorization'].split(' ')[1]
            return self.client.get_user_info(access_token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Unauthorized")
