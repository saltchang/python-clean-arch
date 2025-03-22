from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPI_HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as Starlette_HTTPException

from core.enum.error import ErrorCode
from core.error import DuplicateError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def default_exception_handler(_: Request, exception: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'message': 'internal error',
                'code': ErrorCode.CORE_1000_UNEXPECTED_ERROR,
            },
        )

    @app.exception_handler(NotImplementedError)
    async def not_implemented_exception_handler(_: Request, exception: NotImplementedError):
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content={
                'message': 'not implemented',
                'code': ErrorCode.CORE_1001_NOT_IMPLEMENTED,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                'message': str(exc),
                'code': ErrorCode.API_2000_REQUEST_VALIDATION_FAILED,
            },
        )

    @app.exception_handler(FastAPI_HTTPException)
    @app.exception_handler(Starlette_HTTPException)
    async def http_exception_handler(_: Request, exception: FastAPI_HTTPException | Starlette_HTTPException):
        return JSONResponse(
            status_code=exception.status_code,
            content={
                'message': exception.detail,
                'code': ErrorCode.API_2001_API_SERVICE_ERROR,
            },
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(_: Request, exception: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': str(exception), 'code': ErrorCode.CORE_1002_NOT_FOUND},
        )

    @app.exception_handler(DuplicateError)
    async def duplicate_error_handler(_: Request, exception: DuplicateError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                'message': str(exception),
                'code': ErrorCode.CORE_1003_DUPLICATE_ERROR,
            },
        )
