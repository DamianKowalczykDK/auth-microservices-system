from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from users.core.exceptions import ApiException
from users.domain.schemas import ErrorApi


def register_error_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the FastAPI application.

    This function defines centralized error handling for:
    - Custom application exceptions (ApiException)
    - Request validation errors (RequestValidationError)
    - Unhandled generic exceptions

    All errors are returned in a consistent ErrorApi response format.
    """

    @app.exception_handler(ApiException)
    async def api_exception_handler(_: Request, exc: ApiException) -> JSONResponse:
        """
        Handle custom API exceptions.

        Args:
            _: Incoming request (unused).
            exc (ApiException): Raised application exception.

        Returns:
            JSONResponse: Standardized error response.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorApi(error=exc.error_code, detail=[exc.message]).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle FastAPI request validation errors.

        Args:
            _: Incoming request (unused).
            exc (RequestValidationError): Validation exception from FastAPI.

        Returns:
            JSONResponse: Structured validation error response.
        """
        details = [
            f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorApi(error="validation_error", detail=details).model_dump()
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        """
        Handle all uncaught exceptions.

        Args:
            _: Incoming request (unused).
            exc (Exception): Unexpected server-side exception.

        Returns:
            JSONResponse: Generic internal server error response.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorApi(error="internal server error", detail=[str(exc)]).model_dump()
        )