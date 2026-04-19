from unittest.mock import AsyncMock

import pytest
import respx
from fastapi import HTTPException
from httpx import AsyncClient, ConnectError, Response

from apigateway.core.http_client import ServiceRequestClient


@respx.mock
async def test_connection_error() -> None:
    async with AsyncClient() as ac:
        client = ServiceRequestClient(ac)
        respx.get("http://fail").side_effect = ConnectError("error")

        with pytest.raises(HTTPException) as exc:
            await client.request("GET", "http://fail")

        assert exc.value.status_code == 503

@respx.mock
async def test_bad_gateway_html_response() -> None:
    async with AsyncClient() as ac:
        client = ServiceRequestClient(ac)
        respx.get("http://nginx-error").mock(
            return_value=Response(status_code=502, text="<html><body>Bad Gateway</body></html>")
        )
        with pytest.raises(HTTPException) as exc:
            await client.request("GET", "http://nginx-error")
        assert exc.value.status_code == 502

@respx.mock
async def test_safe_request_empty_response() -> None:
    async with AsyncClient() as ac:
        client = ServiceRequestClient(ac)
        respx.get("http://empty").mock(
            return_value=Response(status_code=204))

        with pytest.raises(HTTPException) as exc:
            await client.safe_request("GET", "http://empty")
        assert exc.value.status_code == 502
        assert exc.value.detail == "Upstream service returned unexpected empty response"
