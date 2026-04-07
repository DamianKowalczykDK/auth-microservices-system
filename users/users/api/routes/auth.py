from fastapi import APIRouter, status
from users.api.dependencies import AuthServiceDep
from users.domain.schemas import (
    UserLogin,
    UserRead,
    MfaVerify
)

router = APIRouter(prefix="/api/users", tags=["Auth"])

@router.post(
    "/auth",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Verify user credentials"
)
async def login_user(payload: UserLogin, service: AuthServiceDep) -> UserRead:
    return await service.verify_credentials(payload)

@router.post(
    "/mfa/verify",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary=f"Verify MFA for user"
)
async def verify_mfa(payload: MfaVerify, service: AuthServiceDep) -> UserRead:
    return await service.verify_user_mfa(payload)