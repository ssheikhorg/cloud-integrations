from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

from ..utils.response import Response as Rs
from .user.routers import user_router, dashboard_router
from .idrive.routers import admin_router, reseller_router


def create_app() -> FastAPI:
    be3_app = FastAPI(docs_url="/", title="Be3 Cloud Serverless Backend",
                      version="0.0.1")
    be3_app.add_middleware(CORSMiddleware, allow_origins=["*"],
                           allow_methods=["*"], allow_headers=["*"])

    # include user routers
    be3_app.include_router(user_router)
    be3_app.include_router(dashboard_router)

    # include idrive routers
    be3_app.include_router(admin_router)
    be3_app.include_router(reseller_router)

    return be3_app


app = create_app()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return Rs.error(exc.errors())


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return Rs.error(exc.detail)


def handler(event, context):
    print("event: ", event)
    if not event.get('requestContext'):
        return None
    mangum = Mangum(app)
    print("mangum: ", mangum)
    return mangum(event, context)
