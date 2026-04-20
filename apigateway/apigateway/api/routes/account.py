from typing import Annotated
from fastapi import APIRouter, status, Body, Query
from apigateway.api.dependencies import AccountServiceDep
from apigateway.domain.schemas import UserRead, UserCreate, UserResetPassword

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def create_user(
        payload: Annotated[UserCreate, Body(description="User to create")],
        service: AccountServiceDep
) -> UserRead:
    """
    Register a new user account.

    Args:
        payload (UserCreate): User registration data.
        service (AccountService): Account service dependency.

    Returns:
        UserRead: Created user data.
    """
    return await service.create_user(payload)


@router.patch(
    "/activation",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Activate user account"
)
async def activate_user(
        code: Annotated[str, Query(description="The unique activation code")],
        service: AccountServiceDep
) -> UserRead:
    """
    Activate a user account using an activation code.

    Args:
        code (str): Activation code.
        service (AccountService): Account service dependency.

    Returns:
        UserRead: Activated user data.
    """
    return await service.activate_user(code)


@router.post(
    "/activation/code",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Resend activation code"
)
async def resend_activation_code(
        identifier: Annotated[str, Query(description="Username or email")],
        service: AccountServiceDep
) -> dict[str, str]:
    """
    Resend activation code to a user.

    Args:
        identifier (str): Username or email.
        service (AccountService): Account service dependency.

    Returns:
        dict[str, str]: Confirmation message.
    """
    return await service.resend_activation_code(identifier)


@router.post(
    "/password/forgot",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Forgot password"
)
async def forgot_password(
        identifier: Annotated[str, Query(description="Username or email")],
        service: AccountServiceDep
) -> dict[str, str]:
    """
    Initiate password reset process.

    Args:
        identifier (str): Username or email.
        service (AccountService): Account service dependency.

    Returns:
        dict[str, str]: Confirmation message.
    """
    return await service.forgot_password(identifier)


@router.post(
    "/password/reset",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Reset password"
)
async def reset_password(
        payload: UserResetPassword,
        service: AccountServiceDep
) -> dict[str, str]:
    """
    Reset user password using a valid token.

    Args:
        payload (UserResetPassword): Password reset payload.
        service (AccountService): Account service dependency.

    Returns:
        dict[str, str]: Confirmation message.
    """
    return await service.reset_password(payload)