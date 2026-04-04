from apigateway.core.http_client import ServiceRequestClient
from apigateway.core.config import settings
from apigateway.domain.schemas import UserLogin, UserRead, MfaVerify, UserCreate, UserResetPassword, MfaSetup


class UsersClient:
    def __init__(self, request_client: ServiceRequestClient) -> None:
        self.http = request_client
        self.base_url = settings.USERS_SERVICE_URL

    async def create_user(self, payload: UserCreate) -> UserRead:
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}",
            json=payload.model_dump()
        )

    async def activate_user(self, code: str) -> UserRead:
        return await self.http.safe_request(
            "PATCH",
            f"{self.base_url}/activation",
            params={"code": code}
        )

    async def resend_activation_code(self, identifier: str) -> dict[str, str]:
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/activation/code",
            params={"identifier": identifier}
        )

    async def login(self, payload: UserLogin) -> UserRead:
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/auth",
            json=payload.model_dump()
        )

    async def forgot_password(self, identifier: str) -> dict[str, str]:
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/password/forgot",
            params={"identifier": identifier}
        )

    async def reset_password(self, payload: UserResetPassword) -> dict[str, str]:
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/password/reset",
            json=payload.model_dump()
        )

    async def enable_mfa(self, user_id: str) -> MfaSetup:
        return await self.http.safe_request(
            "PATCH",
            f"{self.base_url}/mfa/enable",
            params={"user_id": user_id}
        )
    async def disable_mfa(self, user_id: str) -> UserRead:
        return await self.http.safe_request(
            "PATCH",
            f"{self.base_url}/mfa/disable",
            params={"user_id": user_id}
        )

    async def verify_user_mfa(self, payload: MfaVerify) -> UserRead:
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/mfa/verify",
            json=payload.model_dump()
        )

    async def get_user_by_id(self, user_id: str) -> UserRead:
        return await self.http.safe_request(
            "GET",
            f"{self.base_url}/",
            params={"user_id": user_id}
        )

    async def delete_user(self, identifier: str) -> None:
        return await self.http.request(
            "DELETE",
            f"{self.base_url}",
            params={"identifier": identifier}
        )
















