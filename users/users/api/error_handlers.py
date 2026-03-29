from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from users.core.exceptions import ApiException
from users.domain.schemas import ErrorApi


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiException)
    async def api_exception_handler(_: Request, exc: ApiException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorApi(error=exc.error_code, detail=[exc.message]).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in exc.errors()]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorApi(error="validation_error", detail=details).model_dump()
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorApi(error="internal server error", detail=[str(exc)]).model_dump()
        )