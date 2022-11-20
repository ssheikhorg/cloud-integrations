from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

from .utils.response import Response as Rs
from .user.router import routes as user_router
from .idrive.routers import admin as admin_router, reseller as reseller_router


def create_app() -> FastAPI:
    be3_app = FastAPI(docs_url="/", title="Be3 Cloud Serverless Backend",
                      version="0.0.1")
    be3_app.add_middleware(CORSMiddleware, allow_origins=["*"],
                           allow_methods=["*"], allow_headers=["*"])
    # include routers
    be3_app.include_router(user_router)
    be3_app.include_router(admin_router.router)
    be3_app.include_router(reseller_router.router)

    return be3_app


app = create_app()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return Rs.validation_error(exc.errors())


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return Rs.error(exc.detail)


def handler(event, context):
    if not event.get('requestContext'):
        return None
    mangum = Mangum(app)
    return mangum(event, context)
