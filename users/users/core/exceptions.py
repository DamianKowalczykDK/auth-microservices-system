from fastapi import status


class ApiException(Exception):
    """
    Base application exception used for API error handling.

    This exception provides a consistent structure for API errors,
    including a human-readable message, HTTP status code, and
    machine-readable error code.
    """

    def __init__(self, message: str, status_code: int = 400, error_code: str = "error") -> None:
        """
        Initialize API exception.

        Args:
            message (str): Human-readable error message.
            status_code (int): HTTP status code associated with the error.
            error_code (str): Internal application error code.
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class NotFoundException(ApiException):
    """
    Exception raised when a requested resource cannot be found.

    Maps to HTTP 404 Not Found.
    """

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, error_code="not found")


class ConflictException(ApiException):
    """
    Exception raised when a request conflicts with the current state of the resource.

    Maps to HTTP 409 Conflict.
    """

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, error_code="conflict")


class ValidationException(ApiException):
    """
    Exception raised when input data fails validation rules.

    Maps to HTTP 400 Bad Request.
    """

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, error_code="validation error")