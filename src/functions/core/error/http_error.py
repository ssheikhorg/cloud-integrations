from starlette.responses import JSONResponse
from fastapi import HTTPException, Request

from ...utils.response import UnicornExceptionError


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        {"statusCode": exc.status_code, "msg": "Something went wrong", "data": exc.detail}, status_code=exc.status_code
    )


async def unicorn_exception_handler(_: Request, exc: UnicornExceptionError) -> JSONResponse:
    return JSONResponse({"statusCode": exc.code, "msg": exc.errmsg, "data": exc.data})
