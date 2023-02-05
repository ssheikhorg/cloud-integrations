import json
from typing import Any

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from passlib.hash import bcrypt
from jose import jwt, JWTError

from ..applications.user.cognito import Be3UserDashboard
from ..core.config import settings as c
from ..utils.response import Response as Rs

cognito = Be3UserDashboard()


class AuthBearer(HTTPBearer):
    def __init__(self):
        super().__init__()

    async def __call__(self, request: Request) -> Any:
        try:
            access_token = request.headers['Authorization'].split(' ')[1]
            return cognito.get_user_info(access_token)
        except Exception as e:
            raise HTTPException(status_code=401, detail={
                "msg": "Unauthorized",
                "error": str(e)
            })


def get_current_user_role(request: Request) -> list:
    _token = request.headers['Authorization'].split(' ')[1]
    return AuthService.verify_token(_token)['cognito:groups']


class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a stored password against one provided by user"""
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password for storing."""
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> Any:
        exception = HTTPException(
            status_code=401,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        from urllib.request import urlopen
        try:
            up_keys_url = f"https://cognito-idp.{c.aws_default_region}.amazonaws.com/{c.up_id}/.well-known/jwks.json"

            response = urlopen(up_keys_url)
            keys = json.loads(response.read())['keys']
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in keys:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=["RS256"],
                        audience=c.up_id,
                        issuer=f"https://cognito-idp.{c.aws_default_region}.amazonaws.com/{c.up_id}"
                    )
                    return payload
                except JWTError:
                    raise exception
        except Exception as e:
            raise exception from e
