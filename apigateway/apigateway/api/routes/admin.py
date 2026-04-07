from typing import Annotated

from fastapi import APIRouter, status, Query
from apigateway.api.dependencies import AdminServiceDep, AdminOnly

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete(
    "/users",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user account"
)
async def delete_user(
        identifier: Annotated[str, Query(description="Username or email")],
        service: AdminServiceDep,
        _: AdminOnly
) -> None:
    await service.delete_user(identifier)