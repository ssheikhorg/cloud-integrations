from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status as s


class Response(JSONResponse):
    def __init__(self, data=None, msg=None, status_code: int = s.HTTP_200_OK):
        super().__init__(
            content=jsonable_encoder({
                "data": data if data else [],
                "msg": msg if msg else "Success",
                "status_code": status_code,
            }), status_code=s.HTTP_200_OK if status_code == s.HTTP_201_CREATED else status_code
        )

    @classmethod
    def success(cls, data=None, msg=None, status_code: int = s.HTTP_200_OK):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def confict(cls, data=None, msg=None, status_code: int = s.HTTP_409_CONFLICT):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def created(cls, data=None, msg=None, status_code: int = s.HTTP_201_CREATED):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def not_created(cls, data=None, msg=None, status_code: int = s.HTTP_202_ACCEPTED):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def error(cls, data=None, msg=None, status_code: int = s.HTTP_400_BAD_REQUEST):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def validation_error(cls, data=None, msg=None, status_code: int = s.HTTP_422_UNPROCESSABLE_ENTITY):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def not_found(cls, data=None, msg=None, status_code: int = s.HTTP_404_NOT_FOUND):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def server_error(cls, data=None, msg=None, status_code: int = s.HTTP_500_INTERNAL_SERVER_ERROR):
        return cls(data=data, msg=msg if msg else "Server Error", status_code=status_code)

    @classmethod
    def unauthorized(cls, data=None, msg=None, status_code: int = s.HTTP_401_UNAUTHORIZED):
        return cls(data=data, msg=msg, status_code=status_code)

    @classmethod
    def forbidden(cls, data=None, msg=None, status_code: int = s.HTTP_403_FORBIDDEN):
        return cls(data=data, msg=msg, status_code=status_code)
