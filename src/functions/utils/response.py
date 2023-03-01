"""Helper functions for the bot."""
from __future__ import annotations
from typing import Any, TypeVar, Union, Generic

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette import status as s

S = TypeVar("S", covariant=True)
T = TypeVar("T", covariant=True)
U = TypeVar("U", bound="HttpResponse")


class HttpResponse(Generic[S, T], JSONResponse):
    def __init__(
            self, data: Union[S, Any] = None, msg: Union[T, str] = None, status_code: int = s.HTTP_200_OK
    ) -> None:
        super().__init__(
            {
                "statusCode": status_code,
                "data": jsonable_encoder(data) if data else [],
                "msg": msg if msg else "Success",
            },
            status_code=s.HTTP_200_OK if status_code == s.HTTP_201_CREATED else status_code,
            headers={"Content-Type": "application/json"},
        )

    @classmethod
    def success(cls, data: Any = None, msg: str = "Success") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg)

    @classmethod
    def not_found(cls, data: Any = None, msg: str = "Not found") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_200_OK)

    @classmethod
    def conflict(cls, data: Any = None, msg: str = "Conflict") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_409_CONFLICT)

    @classmethod
    def created(cls, data: Any = None, msg: str = "Created") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_201_CREATED)

    @classmethod
    def not_created(cls, data: Any = None, msg: str = "Not created") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_400_BAD_REQUEST)

    @classmethod
    def modified(cls, data: Any = None, msg: str = "Modified") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg)

    @classmethod
    def deleted(cls, data: Any = None, msg: str = "Deleted") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg)

    @classmethod
    def bad_request(cls, data: Any = None, msg: str = "Bad request") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_400_BAD_REQUEST)

    @classmethod
    def unauthorized(cls, data: Any = None, msg: str = "Unauthorized") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_401_UNAUTHORIZED)

    @classmethod
    def server_error(cls, data: Any = None, msg: str = "Something went wrong") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def not_acceptable(cls, data: Any = None, msg: str = "Not acceptable") -> Union[U, JSONResponse]:
        return cls(data=data, msg=msg, status_code=s.HTTP_406_NOT_ACCEPTABLE)


class UnicornExceptionError(Generic[T], Exception):
    def __init__(self, code: int, errmsg: T, data: Any = None) -> None:
        self.code = code
        self.errmsg = errmsg
        self.data = data or {}

# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# from fastapi import status as s
#
#
# class Response(JSONResponse):
#     def __init__(self, data=None, msg=None, status_code: int = s.HTTP_200_OK):
#         super().__init__(
#             content=jsonable_encoder({
#                 "data": data if data else [],
#                 "msg": msg if msg else "Success",
#                 "status_code": status_code,
#             }), status_code=s.HTTP_200_OK if status_code == s.HTTP_201_CREATED else status_code
#         )
#
#     @classmethod
#     def success(cls, data=None, msg=None, status_code: int = s.HTTP_200_OK):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def confict(cls, data=None, msg=None, status_code: int = s.HTTP_409_CONFLICT):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def created(cls, data=None, msg=None, status_code: int = s.HTTP_201_CREATED):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def not_created(cls, data=None, msg=None, status_code: int = s.HTTP_202_ACCEPTED):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def error(cls, data=None, msg=None, status_code: int = s.HTTP_400_BAD_REQUEST):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def validation_error(cls, data=None, msg=None, status_code: int = s.HTTP_422_UNPROCESSABLE_ENTITY):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def not_found(cls, data=None, msg=None, status_code: int = s.HTTP_404_NOT_FOUND):
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def server_error(cls, data=None, msg: str =None, status_code: int = s.HTTP_500_INTERNAL_SERVER_ERROR) -> None:
#         return cls(data=data, msg=msg if msg else "Server Error", status_code=status_code)
#
#     @classmethod
#     def unauthorized(cls, data=None, msg=None, status_code: int = s.HTTP_401_UNAUTHORIZED) -> None:
#         return cls(data=data, msg=msg, status_code=status_code)
#
#     @classmethod
#     def forbidden(cls, data=None, msg=None, status_code: int = s.HTTP_403_FORBIDDEN) -> None:
#         return cls(data=data, msg=msg, status_code=status_code)
#
#
# class UnicornException(Exception):
#     def __init__(self, code, errmsg, data=None) -> None:
#         self.code = code
#         self.errmsg = errmsg
#         self.data = data or {}
