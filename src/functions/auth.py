from typing import Any

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer

from .user.cognito import Be3UserDashboard


class AuthBearer(HTTPBearer):
    def __init__(self):
        super().__init__()
        self.client = Be3UserDashboard()

    async def __call__(self, request: Request) -> Any:
        access_token = request.headers['Authorization'].split(' ')[1]
        res = self.client.get_user_info(access_token)
        if res['success']:
            return res['body']
        raise HTTPException(status_code=401, detail=res["msg"])
