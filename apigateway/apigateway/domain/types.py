from typing import TypedDict, Literal


class UserReadDict(TypedDict):
    """
    Typed dictionary representing user data structure.

    This structure mirrors the user response returned from the users service,
    typically used for type hinting when working with raw dictionaries.
    """

    id: str
    """Unique identifier of the user."""

    username: str
    """Username of the user."""

    email: str
    """Email address of the user."""

    role: Literal["admin", "user"]
    """Role assigned to the user."""

    is_active: bool
    """Indicates whether the user account is active."""

    mfa_secret: str | None
    """Optional MFA secret (if MFA is enabled)."""


class MfaSetupDict(TypedDict):
    """
    Typed dictionary representing MFA setup response.

    Contains data required to configure MFA in an authenticator app.
    """

    user_id: str
    """Identifier of the user."""

    provisioning_uri: str
    """URI used by authenticator apps to configure MFA."""

    qr_code_base64: str
    """Base64-encoded QR code image for MFA setup."""