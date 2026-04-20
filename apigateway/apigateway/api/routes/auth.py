from typing import Annotated
from apigateway.api.dependencies import AuthServiceDep, RefreshTokenPayloadDep
from apigateway.domain.schemas import (
    UserLogin,
    TokenPair,
    MfaRequired,
    MfaVerify,
    TokenPairResponse
)
from fastapi import APIRouter, status, Depends, Form, Response
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "",
    response_model=TokenPairResponse | MfaRequired,
    status_code=status.HTTP_200_OK,
    summary="Login user"
)
async def login_user(
        from_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        service: AuthServiceDep,
        resp: Response,
) -> TokenPairResponse | MfaRequired:
    """
    Authenticate user and return tokens or MFA requirement.

    If MFA is enabled, returns MFA challenge instead of tokens.
    Otherwise, sets refresh token cookie and returns access token.

    Args:
        from_data (OAuth2PasswordRequestForm): Login form data.
        service (AuthService): Authentication service dependency.
        resp (Response): FastAPI response object for setting cookies.

    Returns:
        TokenPairResponse | MfaRequired: Authentication result.
    """
    payload: UserLogin = UserLogin(
        identifier=from_data.username,
        password=from_data.password
    )

    result = await service.login(payload)

    if isinstance(result, TokenPair):
        resp.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
        )

    return result  # type: ignore


@router.post(
    "/mfa",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify MFA for user"
)
async def verify_mfa(
        resp: Response,
        user_id: Annotated[str, Form()],
        code: Annotated[str, Form()],
        service: AuthServiceDep,
) -> TokenPairResponse:
    """
    Verify MFA code and issue authentication tokens.

    Args:
        resp (Response): FastAPI response object for setting cookies.
        user_id (str): User identifier.
        code (str): MFA verification code.
        service (AuthService): Authentication service dependency.

    Returns:
        TokenPairResponse: Access token and token type.
    """
    payload: MfaVerify = MfaVerify(
        user_id=user_id,
        code=code
    )

    result = await service.verify_mfa(payload)

    resp.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return result  # type: ignore


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh token"
)
async def refresh_token(
        resp: Response,
        token_data: RefreshTokenPayloadDep,
        service: AuthServiceDep
) -> TokenPairResponse:
    """
    Refresh access and refresh tokens using a valid refresh token.

    Args:
        resp (Response): FastAPI response object for setting cookies.
        token_data (TokenPayload): Decoded refresh token payload.
        service (AuthService): Authentication service dependency.

    Returns:
        TokenPairResponse: New access token.
    """
    new_tokens = await service.refresh_token(token_data)

    resp.set_cookie(
        key="refresh_token",
        value=new_tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return new_tokens  # type: ignore


@router.post(
    "/logout",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Logout user"
)
async def logout_user(resp: Response) -> dict[str, str]:
    """
    Log out user by clearing authentication cookies.

    Args:
        resp (Response): FastAPI response object.

    Returns:
        dict[str, str]: Logout confirmation message.
    """
    resp.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"msg": "Logout successful"}