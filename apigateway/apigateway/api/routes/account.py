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
    return await service.create_user(payload)


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
    return await service.reset_password(payload)