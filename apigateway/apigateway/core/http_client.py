from typing import Mapping, Sequence, Any
from fastapi import HTTPException
from httpx import QueryParams
from starlette import status
import httpx

ParamsType = QueryParams | Mapping[str, str | int | float | bool | None | Sequence[str | int | float | bool | None]] | list[tuple[str, str | int | float | bool | None]] | tuple[tuple[str, str | int | float | bool | None], ...] | str | bytes | None
HeadersType = Mapping[str, str] | None
JsonType = dict[str, Any] | list[Any] | str | int | float | bool | None


class ServiceRequestClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def request[T](
            self,
            method: str,
            url: str,
            *,
            json: JsonType = None,
            params: ParamsType = None,
            headers: HeadersType = None,
    ) -> T | None:

        try:
            response = await self.client.request(
                method,
                url,
                json=json,
                params=params,
                headers=headers,
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Request failed: {str(e)}",
            )
        if response.status_code >= 400:
            error_detail: str | JsonType
            try:
                error_detail = response.json()
            except:
                error_detail = response.text
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail,
            )

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return None

        return response.json()


    async def safe_request[T](
            self,
            method: str,
            url: str,
            *,
            json: JsonType = None,
            params: ParamsType = None,
            headers: HeadersType = None,
    ) -> T:
        response: T | None = await self.request(
            method,
            url,
            json=json,
            params=params,
            headers=headers,
        )

        if response is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Upstream service returned unexpected empty response",
            )
        return response

