from fastapi import APIRouter, status
from apigateway.api.dependencies import UserOnly, UserServiceDep, CurrentUserDep
from apigateway.domain.schemas import MfaSetup, UserRead

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user"
)
async def get_user(
        user: CurrentUserDep,
) -> UserRead:
    """
    Retrieve the currently authenticated user.

    This endpoint returns the user data extracted from the authentication context.

    Args:
        user (UserRead): Current authenticated user dependency.

    Returns:
        UserRead: Current user data.
    """
    return user


@router.patch(
    "/mfa/enable",
    response_model=MfaSetup,
    status_code=status.HTTP_200_OK,
    summary="Initialize MFA for user"
)
async def enable_mfa(
        user: UserOnly,
        service: UserServiceDep,
) -> MfaSetup:
    """
    Enable multi-factor authentication for the current user.

    Args:
        user (UserRead): Authenticated user with 'user' role.
        service (UserService): User service dependency.

    Returns:
        MfaSetup: MFA setup data (QR code + provisioning URI).
    """
    return await service.enable_mfa(user.id)


@router.patch(
    "/mfa/disable",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Disable MFA for user"
)
async def disable_mfa(
        user: UserOnly,
        service: UserServiceDep,
) -> UserRead:
    """
    Disable multi-factor authentication for the current user.

    Args:
        user (UserRead): Authenticated user with 'user' role.
        service (UserService): User service dependency.

    Returns:
        UserRead: Updated user data after disabling MFA.
    """
    return await service.disable_mfa(user.id)