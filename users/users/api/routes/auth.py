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
    """
    Authenticate a user using username/email and password.

    This endpoint verifies user credentials and returns user data
    if authentication is successful.

    Args:
        payload (UserLogin): Login credentials (identifier + password).
        service (AuthServiceDep): Authentication service dependency.

    Returns:
        UserRead: Authenticated user data.
    """
    return await service.verify_credentials(payload)


@router.post(
    "/mfa/verify",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Verify MFA for user"
)
async def verify_mfa(payload: MfaVerify, service: AuthServiceDep) -> UserRead:
    """
    Verify multi-factor authentication (MFA) code for a user.

    Args:
        payload (MfaVerify): MFA verification data (user_id + code).
        service (AuthServiceDep): Authentication service dependency.

    Returns:
        UserRead: User data if MFA verification is successful.
    """
    return await service.verify_user_mfa(payload)