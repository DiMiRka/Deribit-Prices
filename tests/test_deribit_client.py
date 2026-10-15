import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from decimal import Decimal

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.clients.deribit import (
    DeribitAPIError,
    DeribitClient,
    DeribitNetworkError,
    DeribitResponseError,
)

type Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

SUCCESS_BODY = '{"result": {"index_price": 83392.04}, "usOut": 1791962818645921}'


@asynccontextmanager
async def deribit_client(handler: Handler) -> AsyncIterator[DeribitClient]:
    app = web.Application()
    app.router.add_get("/api/v2/public/get_index_price", handler)
    async with TestServer(app) as server, aiohttp.ClientSession() as session:
        yield DeribitClient(session, str(server.make_url("/api/v2")), timeout=0.2)


async def test_returns_exact_price_and_server_timestamp() -> None:
    async def handler(request: web.Request) -> web.Response:
        assert request.query["index_name"] == "btc_usd"
        return web.Response(
            text=SUCCESS_BODY,
            content_type="application/json",
        )

    async with deribit_client(handler) as client:
        index_price = await client.get_index_price("btc_usd")

    assert index_price.ticker == "btc_usd"
    assert index_price.price == Decimal("83392.04")
    assert index_price.timestamp == 1791962818


async def test_rpc_error_raises_api_error() -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid params"},
                "usOut": 1791962818892193,
            },
            status=400,
        )

    async with deribit_client(handler) as client:
        with pytest.raises(DeribitAPIError) as exc_info:
            await client.get_index_price("btc_usd")

    assert exc_info.value.code == -32602


async def test_timeout_raises_network_error() -> None:
    async def handler(request: web.Request) -> web.Response:
        await asyncio.sleep(1)
        return web.json_response({})

    async with deribit_client(handler) as client:
        with pytest.raises(DeribitNetworkError):
            await client.get_index_price("btc_usd")


async def test_non_json_error_page_raises_response_error() -> None:
    async def handler(request: web.Request) -> web.Response:
        return web.Response(status=502, text="<html>Bad Gateway</html>", content_type="text/html")

    async with deribit_client(handler) as client:
        with pytest.raises(DeribitResponseError):
            await client.get_index_price("btc_usd")
