from fastapi import status

class ApiException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "error" ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class NotFoundException(ApiException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, error_code="not found")

class ConflictException(ApiException):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, error_code="conflict")

class ValidationException(ApiException):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, error_code="validation error")
