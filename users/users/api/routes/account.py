from typing import Annotated
from fastapi import APIRouter, status, Query, BackgroundTasks
from users.api.dependencies import AccountServiceDep
from users.domain.schemas import (
    UserCreate,
    UserRead,
    UserResetPassword,
    MfaSetup
)

router = APIRouter(prefix="/api/users", tags=["Account"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def create_user(
        payload: UserCreate,
        service: AccountServiceDep,
        bg_tasks: BackgroundTasks
) -> UserRead:
    """
    Create a new user account.

    This endpoint registers a new user, stores them in the database,
    and triggers an activation email via background task.

    Args:
        payload (UserCreate): User registration data.
        service (AccountServiceDep): Account service dependency.
        bg_tasks (BackgroundTasks): FastAPI background task manager.

    Returns:
        UserRead: Created user data.
    """
    return await service.create_user(payload, bg_tasks)


@router.patch(
    "/activation",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Activation user account"
)
async def activate_user(
        code: Annotated[str, Query(description="The Unique activation code")],
        service: AccountServiceDep
) -> UserRead:
    """
    Activate a user account using an activation code.

    Args:
        code (str): Activation code provided to the user.
        service (AccountServiceDep): Account service dependency.

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
        service: AccountServiceDep,
        bg_tasks: BackgroundTasks
) -> dict[str, str]:
    """
    Resend activation code to a user.

    Args:
        identifier (str): Username or email.
        service (AccountServiceDep): Account service dependency.
        bg_tasks (BackgroundTasks): Background task manager.

    Returns:
        dict[str, str]: Confirmation message.
    """
    user = await service.resend_activation_code(identifier, bg_tasks)
    return {"message": f"{user.username}'s activation code has been sent."}


@router.post(
    "/password/forgot",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Forgot password"
)
async def forgot_password(
        identifier: Annotated[str, Query(description="Username or email")],
        service: AccountServiceDep,
        bg_tasks: BackgroundTasks
) -> dict[str, str]:
    """
    Trigger password reset process.

    Args:
        identifier (str): Username or email.
        service (AccountServiceDep): Account service dependency.
        bg_tasks (BackgroundTasks): Background task manager.

    Returns:
        dict[str, str]: Confirmation message.
    """
    await service.forgot_password(identifier, bg_tasks)
    return {"message": "If the account exist email has been sent."}


@router.post(
    "/password/reset",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Reset password"
)
async def reset_password(payload: UserResetPassword, service: AccountServiceDep) -> dict[str, str]:
    """
    Reset user password using a reset token.

    Args:
        payload (UserResetPassword): Reset token and new password.
        service (AccountServiceDep): Account service dependency.

    Returns:
        dict[str, str]: Confirmation message.
    """
    await service.reset_password(payload.token, payload.new_password)
    return {"message": "Password has been reset."}


@router.patch(
    "/mfa/enable",
    response_model=MfaSetup,
    status_code=status.HTTP_200_OK,
    summary="Initialize MFA for user"
)
async def enable_mfa(
        user_id: Annotated[str, Query(description="User ID")],
        service: AccountServiceDep
) -> MfaSetup:
    """
    Enable multi-factor authentication for a user.

    Args:
        user_id (str): User ID.
        service (AccountServiceDep): Account service dependency.

    Returns:
        MfaSetup: MFA setup data (QR code + provisioning URI).
    """
    return await service.enable_mfa(user_id)


@router.patch(
    "/mfa/disable",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Disable MFA for user"
)
async def disable_mfa(
        user_id: Annotated[str, Query(description="User ID")],
        service: AccountServiceDep
) -> UserRead:
    """
    Disable multi-factor authentication for a user.

    Args:
        user_id (str): User ID.
        service (AccountServiceDep): Account service dependency.

    Returns:
        UserRead: Updated user data.
    """
    return await service.disable_mfa(user_id)


@router.get(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get user by id"
)
async def get_user(
        user_id: Annotated[str, Query(description="The database ID of the user")],
        service: AccountServiceDep
) -> UserRead:
    """
    Retrieve a user by ID.

    Args:
        user_id (str): User ID.
        service (AccountServiceDep): Account service dependency.

    Returns:
        UserRead: User data.
    """
    return await service.get_user_by_id(user_id)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user account"
)
async def delete_user(
        identifier: Annotated[str, Query(description="Username or email")],
        service: AccountServiceDep
) -> None:
    """
    Delete a user account by username or email.

    Args:
        identifier (str): Username or email.
        service (AccountServiceDep): Account service dependency.

    Returns:
        None
    """
    await service.delete_user(identifier)