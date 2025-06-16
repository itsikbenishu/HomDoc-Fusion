from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from entities.abstracts.response_model import ResponseModel


async def global_exception_handler(request: Request, exc: Exception):
    response = ResponseModel[None](
        message=f"Unexpected error: {str(exc)}",
        status=500,
        data=None
    )
    return JSONResponse(status_code=500, content=response.model_dump())


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    response = ResponseModel[None](
        message=str(exc.detail),
        status=exc.status_code,
        data=None
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = ResponseModel[None](
        message="Validation error",
        status=422,
        data=exc.errors()
    )
    return JSONResponse(status_code=422, content=response.model_dump())
