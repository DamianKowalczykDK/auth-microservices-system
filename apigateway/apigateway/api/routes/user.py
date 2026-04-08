from fastapi import APIRouter, status
from apigateway.api.dependencies import UserOnly, UserServiceDep, CurrentUserDep
from apigateway.domain.schemas import MfaSetup, UserRead

router = APIRouter(prefix="/user", tags=["User"])

@router.get(
    "",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get user by id"
)
async def get_user(
        user: CurrentUserDep,
) -> UserRead:
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
    return await service.enable_mfa(user.id)

@router.patch(
    "/mfa/disable",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary=f"Disable MFA for user"
)
async def disable_mfa(
        user: UserOnly,
        service: UserServiceDep,
) -> UserRead:
    return await service.disable_mfa(user.id)