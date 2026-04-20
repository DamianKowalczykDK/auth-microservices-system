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
    """
    Delete a user account (admin-only operation).

    This endpoint allows administrators to remove a user
    identified by username or email.

    Args:
        identifier (str): Username or email of the user to delete.
        service (AdminService): Admin service dependency.
        _ (UserRead): Admin-only dependency guard (ensures access control).

    Returns:
        None
    """
    await service.delete_user(identifier)