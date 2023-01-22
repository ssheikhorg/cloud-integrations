from typing import Any

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import ValidationError
from passlib.hash import bcrypt
from jose import jwt, JWTError

from ..user.cognito import Be3UserDashboard
from ..core.config import settings as c

cognito = Be3UserDashboard()


class AuthBearer(HTTPBearer):
    def __init__(self):
        super().__init__()

    async def __call__(self, request: Request) -> Any:
        access_token = request.headers['Authorization'].split(' ')[1]
        res = cognito.get_user_info(access_token)
        if res['success']:
            return res['body']
        raise HTTPException(status_code=401, detail={
            "success": False,
            "msg": "Invalid access token",
            "data": res['msg']
        })


class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a stored password against one provided by user"""
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(self, password: str) -> str:
        """Hash a password for storing."""
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> Any:
        exception = HTTPException(
            status_code=401,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            res = cognito.get_user_info(token)
            if res['success']:
                # decode cognito token
                payload = jwt.decode(token, c.up_client_id, algorithms=['RS256'])
                if payload['token_use'] != 'access':
                    raise exception

                user_data = {
                    'pk': payload['sub'],
                    'role': payload['cognito:groups'],
                }
                return user_data
        except JWTError:
            raise exception from None


def get_current_user(token: str = Depends(AuthBearer())) -> dict:
    return AuthService.verify_token(token)
