import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette import status

from config.logger import init_logger
from config.settings import APP_NAME, BUILD_VERSION, SHOULD_RESET_DATABASE
from repository.psql.connection import psql_db

from .error_handler import register_exception_handlers
from .router import (
    health,
    user,
)

openapi_tags: list[dict[str, Any]] = [
    {
        'name': 'Health',
        'description': 'Health check endpoints',
    }
]

logger = logging.getLogger(__name__)

init_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        if SHOULD_RESET_DATABASE:
            await psql_db.drop_all_tables()
        await psql_db.create_all_tables()
        yield
    finally:
        logger.info('Application is shutting down...')


_fastapi = FastAPI(
    title=APP_NAME,
    version=BUILD_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

register_exception_handlers(_fastapi)

_fastapi.include_router(health.router)
_fastapi.include_router(user.router)


@_fastapi.get('/', include_in_schema=False)
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'message': 'OK', 'server_time': datetime.now(UTC).isoformat()},
    )


@_fastapi.get('/docs', include_in_schema=False)
async def get_docs():
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        title=APP_NAME,
        swagger_favicon_url='/favicon.ico',
    )


@_fastapi.get('/openapi.json', include_in_schema=False)
async def get_openapi_json():
    if _fastapi.openapi_schema:
        return _fastapi.openapi_schema
    openapi_schema = get_openapi(
        title=APP_NAME,
        version='0.1.0',
        routes=_fastapi.routes,
    )
    _fastapi.openapi_schema = openapi_schema
    return _fastapi.openapi_schema


http_api = _fastapi
