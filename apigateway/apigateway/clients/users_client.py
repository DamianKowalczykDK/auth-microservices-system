from apigateway.core.http_client import ServiceRequestClient
from apigateway.core.config import Settings
from apigateway.domain.schemas import UserLogin, UserRead, MfaVerify, UserCreate, UserResetPassword, MfaSetup
from apigateway.domain.types import UserReadDict, MfaSetupDict


class UsersClient:
    """
    Client for communicating with the Users service.

    This class provides methods for interacting with the external users service API,
    handling request/response mapping and converting raw responses into domain schemas.
    """

    def __init__(self, request_client: ServiceRequestClient, settings: Settings) -> None:
        """
        Initialize UsersClient.

        Args:
            request_client (ServiceRequestClient): HTTP client wrapper.
            settings (Settings): Application settings containing service URL.
        """
        self.http = request_client
        self.base_url = settings.USERS_SERVICE_URL

    async def create_user(self, payload: UserCreate) -> UserRead:
        """
        Create a new user.

        Args:
            payload (UserCreate): User registration data.

        Returns:
            UserRead: Created user.
        """
        data: UserReadDict = await self.http.safe_request(
            "POST",
            f"{self.base_url}",
            json=payload.model_dump()
        )
        return UserRead.model_validate(data)

    async def activate_user(self, code: str) -> UserRead:
        """
        Activate a user account.

        Args:
            code (str): Activation code.

        Returns:
            UserRead: Activated user.
        """
        data: UserReadDict = await self.http.safe_request(
            "PATCH",
            f"{self.base_url}/activation",
            params={"code": code}
        )
        return UserRead.model_validate(data)

    async def resend_activation_code(self, identifier: str) -> dict[str, str]:
        """
        Resend activation code to a user.

        Args:
            identifier (str): Username or email.

        Returns:
            dict[str, str]: Confirmation message.
        """
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/activation/code",
            params={"identifier": identifier}
        )

    async def login(self, payload: UserLogin) -> UserRead:
        """
        Authenticate a user.

        Args:
            payload (UserLogin): Login credentials.

        Returns:
            UserRead: Authenticated user.
        """
        data: UserReadDict = await self.http.safe_request(
            "POST",
            f"{self.base_url}/auth",
            json=payload.model_dump()
        )
        return UserRead.model_validate(data)

    async def forgot_password(self, identifier: str) -> dict[str, str]:
        """
        Initiate password reset process.

        Args:
            identifier (str): Username or email.

        Returns:
            dict[str, str]: Confirmation message.
        """
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/password/forgot",
            params={"identifier": identifier}
        )

    async def reset_password(self, payload: UserResetPassword) -> dict[str, str]:
        """
        Reset user password.

        Args:
            payload (UserResetPassword): Reset token and new password.

        Returns:
            dict[str, str]: Confirmation message.
        """
        return await self.http.safe_request(
            "POST",
            f"{self.base_url}/password/reset",
            json=payload.model_dump()
        )

    async def enable_mfa(self, user_id: str) -> MfaSetup:
        """
        Enable MFA for a user.

        Args:
            user_id (str): User ID.

        Returns:
            MfaSetup: MFA setup data.
        """
        data: MfaSetupDict = await self.http.safe_request(
            "PATCH",
            f"{self.base_url}/mfa/enable",
            params={"user_id": user_id}
        )
        return MfaSetup.model_validate(data)

    async def disable_mfa(self, user_id: str) -> UserRead:
        """
        Disable MFA for a user.

        Args:
            user_id (str): User ID.

        Returns:
            UserRead: Updated user.
        """
        data: UserReadDict = await self.http.safe_request(
            "PATCH",
            f"{self.base_url}/mfa/disable",
            params={"user_id": user_id}
        )
        return UserRead.model_validate(data)

    async def verify_user_mfa(self, payload: MfaVerify) -> UserRead:
        """
        Verify MFA code for a user.

        Args:
            payload (MfaVerify): MFA verification data.

        Returns:
            UserRead: Authenticated user.
        """
        data: UserReadDict = await self.http.safe_request(
            "POST",
            f"{self.base_url}/mfa/verify",
            json=payload.model_dump()
        )
        return UserRead.model_validate(data)

    async def get_user_by_id(self, user_id: str) -> UserRead:
        """
        Retrieve a user by ID.

        Args:
            user_id (str): User ID.

        Returns:
            UserRead: User data.
        """
        data: UserReadDict = await self.http.safe_request(
            "GET",
            f"{self.base_url}/",
            params={"user_id": user_id}
        )
        return UserRead.model_validate(data)

    async def delete_user(self, identifier: str) -> None:
        """
        Delete a user account.

        Args:
            identifier (str): Username or email.

        Returns:
            None
        """
        await self.http.request(
            "DELETE",
            f"{self.base_url}",
            params={"identifier": identifier}
        )