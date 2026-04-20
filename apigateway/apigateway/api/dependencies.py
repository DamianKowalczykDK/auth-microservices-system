from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from typing import Annotated
from jose import jwt, JWTError  # type: ignore
from apigateway.clients.users_client import UsersClient
from apigateway.core.config import Settings
from apigateway.core.http_client import ServiceRequestClient
from apigateway.domain.schemas import TokenPayload, UserRead
from apigateway.services.account_service import AccountService
from apigateway.services.admin_service import AdminService
from apigateway.services.auth_service import AuthService
from apigateway.services.user_service import UserService
import httpx


@lru_cache
def get_settings() -> Settings:
    """
    Provide application settings as a cached dependency.

    Returns:
        Settings: Application configuration loaded from environment variables.
    """
    return Settings()  # type: ignore


SettingsDep = Annotated[Settings, Depends(get_settings)]
"""FastAPI dependency type for Settings."""


@lru_cache()
def get_httpx_client(settings: SettingsDep) -> httpx.AsyncClient:
    """
    Create and cache a shared HTTPX AsyncClient.

    Args:
        settings (Settings): Application settings containing timeout config.

    Returns:
        httpx.AsyncClient: Configured HTTP client.
    """
    return httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]
"""Dependency type for HTTPX AsyncClient."""


@lru_cache()
def get_service_request_client(client: HttpClientDep) -> ServiceRequestClient:
    """
    Create ServiceRequestClient wrapper around HTTPX client.

    Args:
        client (httpx.AsyncClient): HTTP client dependency.

    Returns:
        ServiceRequestClient: Wrapped HTTP client.
    """
    return ServiceRequestClient(client=client)


ServiceRequestClientDep = Annotated[ServiceRequestClient, Depends(get_service_request_client)]
"""Dependency type for ServiceRequestClient."""


@lru_cache()
def get_users_client(request_client: ServiceRequestClientDep, settings: SettingsDep) -> UsersClient:
    """
    Create UsersClient for communication with Users service.

    Args:
        request_client (ServiceRequestClient): HTTP wrapper client.
        settings (Settings): Application settings.

    Returns:
        UsersClient: Client for Users service API.
    """
    return UsersClient(request_client=request_client, settings=settings)


UsersClientDep = Annotated[UsersClient, Depends(get_users_client)]
"""Dependency type for UsersClient."""


@lru_cache()
def get_auth_service(users_client: UsersClientDep, settings: SettingsDep) -> AuthService:
    """
    Provide AuthService instance.

    Args:
        users_client (UsersClient): Users service client.
        settings (Settings): Application settings.

    Returns:
        AuthService: Authentication service.
    """
    return AuthService(users_client=users_client, settings=settings)


@lru_cache()
def get_account_service(users_client: UsersClientDep) -> AccountService:
    """
    Provide AccountService instance.

    Args:
        users_client (UsersClient): Users service client.

    Returns:
        AccountService: Account management service.
    """
    return AccountService(users_client)


@lru_cache()
def get_user_service(users_client: UsersClientDep) -> UserService:
    """
    Provide UserService instance.

    Args:
        users_client (UsersClient): Users service client.

    Returns:
        UserService: User management service.
    """
    return UserService(users_client)


@lru_cache()
def get_admin_service(users_client: UsersClientDep) -> AdminService:
    """
    Provide AdminService instance.

    Args:
        users_client (UsersClient): Users service client.

    Returns:
        AdminService: Admin-level service.
    """
    return AdminService(users_client)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")
"""OAuth2 password bearer scheme for access token extraction."""


async def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: SettingsDep
) -> TokenPayload:
    """
    Decode and validate JWT access token.

    Args:
        token (str): JWT access token.
        settings (Settings): Application settings with JWT config.

    Returns:
        TokenPayload: Decoded token payload.

    Raises:
        HTTPException: If token is invalid or missing required fields.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return TokenPayload(sub=user_id, type="access")

    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    token_data: Annotated[TokenPayload, Depends(get_token_payload)],
    users_client: UsersClientDep
) -> UserRead:
    """
    Retrieve the current authenticated active user.

    Args:
        token_data (TokenPayload): Decoded JWT token payload.
        users_client (UsersClient): Users service client.

    Returns:
        UserRead: Active user data.

    Raises:
        HTTPException: If user is inactive or cannot be validated.
    """
    try:
        user = await users_client.get_user_by_id(token_data.sub)

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User inactive")

        return user

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=503, detail="Could not validate user profile")


CurrentUserDep = Annotated[UserRead, Depends(get_current_active_user)]
"""Dependency type for the currently authenticated user."""


class RoleChecker:
    """
    Dependency class for role-based access control.

    Ensures that a user has one of the allowed roles.
    """

    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: CurrentUserDep) -> UserRead:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this resource",
            )
        return user


UserOnly = Annotated[UserRead, Depends(RoleChecker(["user"]))]
"""Dependency restricting access to users with 'user' role."""

AdminOnly = Annotated[UserRead, Depends(RoleChecker(["admin"]))]
"""Dependency restricting access to users with 'admin' role."""


def get_refresh_token(
    request: Request,
    settings: SettingsDep
) -> TokenPayload:
    """
    Validate and decode refresh token from cookies.

    Args:
        request (Request): Incoming HTTP request.
        settings (Settings): Application settings.

    Returns:
        TokenPayload: Decoded refresh token payload.

    Raises:
        HTTPException: If token is missing or invalid.
    """
    token = request.cookies.get("refresh_token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token is invalid",
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

        return TokenPayload(sub=user_id, type=token_type)

    except JWTError:
        raise credentials_exception


RefreshTokenPayloadDep = Annotated[TokenPayload, Depends(get_refresh_token)]
"""Dependency type for refresh token payload."""