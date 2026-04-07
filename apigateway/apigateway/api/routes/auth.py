from typing import Annotated
from apigateway.api.dependencies import AuthServiceDep, RefreshTokenPayloadDep
from apigateway.domain.schemas import UserLogin, TokenPair, MfaRequired, MfaVerify, TokenPayload, TokenPairResponse
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
    return result #type: ignore



@router.post(
    "/mfa",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary=f"Verify MFA for user"
)
async def verify_mfa(
        resp: Response,
        user_id: Annotated[str, Form()],code: Annotated[str, Form()],
        service: AuthServiceDep,

) -> TokenPairResponse:
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
    return result #type: ignore

@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary=f"Refresh token"
)
async def refresh_token(resp: Response, token_data: RefreshTokenPayloadDep, service: AuthServiceDep) -> TokenPairResponse:
    new_tokens = await service.refresh_token(token_data)

    resp.set_cookie(
        key="refresh_token",
        value=new_tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return new_tokens #type: ignore

@router.post(
    "/logout",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary=f"Logout user"
)
async def logout_user(resp: Response) -> dict[str, str]:
    resp.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return {"msg": "Logout successful"}

