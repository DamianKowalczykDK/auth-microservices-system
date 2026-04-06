from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from typing import Annotated
from jose import jwt, JWTError #type: ignore
from apigateway.clients.users_client import UsersClient
from apigateway.core.config import settings
from apigateway.core.http_client import ServiceRequestClient
from apigateway.domain.schemas import TokenPayload, UserRead
from apigateway.services.account_service import AccountService
from apigateway.services.admin_service import AdminService
from apigateway.services.auth_service import AuthService
from apigateway.services.user_service import UserService
import httpx


@lru_cache()
def get_httpx_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)

HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]

@lru_cache()
def get_service_request_client(client: HttpClientDep) -> ServiceRequestClient:
    return ServiceRequestClient(client=client)

ServiceRequestClientDep = Annotated[ServiceRequestClient, Depends(get_service_request_client)]

@lru_cache()
def get_users_client(request_client: ServiceRequestClientDep) -> UsersClient:
    return UsersClient(request_client=request_client)

UsersClientDep = Annotated[UsersClient, Depends(get_users_client)]

@lru_cache()
def get_auth_service(users_client: UsersClientDep) -> AuthService:
    return AuthService(users_client)

@lru_cache()
def get_account_service(users_client: UsersClientDep) -> AccountService:
    return AccountService(users_client)

@lru_cache()
def get_user_service(users_client: UsersClientDep) -> UserService:
    return UserService(users_client)

@lru_cache()
def get_admin_service(users_client: UsersClientDep) -> AdminService:
    return AdminService(users_client)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")

async def get_token_payload(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
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
    try:
        user = await users_client.get_user_by_id(token_data.sub)
        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail="User inactive"
            )
        return user
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=503, detail="Could not validate user profile")

CurrentUserDep = Annotated[UserRead, Depends(get_current_active_user)]

class RoleChecker:
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
AdminOnly = Annotated[UserRead, Depends(RoleChecker(["admin"]))]
