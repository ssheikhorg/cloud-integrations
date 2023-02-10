from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from mangum import Mangum
from typing import Callable

from .utils.response import Response as Rs, UnicornException
from .applications.user.routers import user_router, dashboard_router
from .applications.idrive.routers import admin_router, reseller_router
from .core.error import http_error, validation_error


def user_routers(app_: FastAPI) -> None:
    # include user routers
    app_.include_router(user_router)
    app_.include_router(dashboard_router)


def idrive_routers(app_: FastAPI) -> None:
    # include idrive routers
    app_.include_router(admin_router)
    app_.include_router(reseller_router)


def init_exception_handlers(app_: FastAPI) -> None:
    app_.add_exception_handler(HTTPException, http_error.http_error_handler)
    app_.add_exception_handler(UnicornException, http_error.unicorn_exception_handler)
    app_.add_exception_handler(RequestValidationError, validation_error.http422_error_handler)
    app_.add_exception_handler(RequestValidationError, validation_error.request_validation_exception_handler)
    app_.add_exception_handler(TypeError, validation_error.type_error_exception_handler)


def init_middleware() -> list:
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]


def create_app(_routes: Callable) -> FastAPI:
    app_ = FastAPI(
        title="Be3 Cloud APIs", description="Be3 Cloud APIs Documentation",
        version="0.1.0", docs_url="/", openapi_url=None, redoc_url=None,
        middleware=init_middleware(),
    )

    """add routers"""
    _routes(app_)

    """add exception handlers"""
    init_exception_handlers(app_)

    return app_


user_app = create_app(user_routers)
idrive_app = create_app(idrive_routers)


def handler_user(event, context):
    if not event.get('requestContext'):
        return None
    mangum = Mangum(user_app, api_gateway_base_path='/user')
    return mangum(event, context)


def handler_idrive(event, context):
    if not event.get('requestContext'):
        return None
    mangum = Mangum(idrive_app, api_gateway_base_path='/idrive')
    return mangum(event, context)
