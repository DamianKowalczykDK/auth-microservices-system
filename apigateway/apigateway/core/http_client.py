from typing import Mapping, Sequence, Any
from fastapi import HTTPException
from httpx import QueryParams
from starlette import status
import httpx

ParamsType = QueryParams | Mapping[str, str | int | float | bool | None | Sequence[str | int | float | bool | None]] | list[tuple[str, str | int | float | bool | None]] | tuple[tuple[str, str | int | float | bool | None], ...] | str | bytes | None
"""Supported types for HTTP query parameters."""

HeadersType = Mapping[str, str] | None
"""Supported type for HTTP headers."""

JsonType = dict[str, Any] | list[Any] | str | int | float | bool | None
"""Supported types for JSON request body."""


class ServiceRequestClient:
    """
    Wrapper around httpx.AsyncClient for making HTTP requests to external services.

    This client standardizes request handling, error mapping, and response parsing,
    providing consistent behavior across service-to-service communication.
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        """
        Initialize ServiceRequestClient.

        Args:
            client (httpx.AsyncClient): Configured HTTP client instance.
        """
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
        """
        Perform an HTTP request and return parsed JSON response.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): Target URL.
            json (JsonType, optional): JSON payload.
            params (ParamsType, optional): Query parameters.
            headers (HeadersType, optional): Request headers.

        Returns:
            T | None: Parsed JSON response or None for 204 responses.

        Raises:
            HTTPException: If request fails or response contains an error status.
        """
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
        """
        Perform an HTTP request and ensure a non-empty response.

        This method wraps `request` and raises an error if the response
        is unexpectedly empty (e.g., HTTP 204).

        Args:
            method (str): HTTP method.
            url (str): Target URL.
            json (JsonType, optional): JSON payload.
            params (ParamsType, optional): Query parameters.
            headers (HeadersType, optional): Request headers.

        Returns:
            T: Parsed JSON response.

        Raises:
            HTTPException: If response is empty or request fails.
        """
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
                detail="Upstream service returned unexpected empty response",
            )

        return response