from contextlib import asynccontextmanager

import pytest

from nanomuse.config import MCPServerSettings
from nanomuse.tools import MCPManager


def test_api_request_preserves_headers():
    from nanomuse.server.api import MCPBody

    body = MCPBody.model_validate(
        {
            "name": "remote",
            "url": "https://example.test/mcp",
            "headers": {"Authorization": "{{vault:MCP_REMOTE_HEADER}}"},
        }
    )
    cfg = MCPServerSettings.model_validate(body.model_dump())
    assert cfg.headers == {"Authorization": "{{vault:MCP_REMOTE_HEADER}}"}


@pytest.mark.parametrize("fallback", [False, True])
async def test_remote_headers_reach_http_and_sse(monkeypatch, fallback):
    import mcp.client.sse as sse
    import mcp.client.streamable_http as http

    headers = {"Authorization": "Bearer private-key"}
    seen = []

    @asynccontextmanager
    async def transport(url, **kwargs):
        actual = kwargs["http_client"].headers if "http_client" in kwargs else kwargs["headers"]
        assert actual["Authorization"] == headers["Authorization"]
        seen.append("http")
        if fallback:
            raise RuntimeError("SSE-only server")
        yield ("read", "write", None)

    @asynccontextmanager
    async def legacy(url, **kwargs):
        assert kwargs["headers"] == headers
        seen.append("sse")
        yield ("read", "write")

    name = (
        "streamable_http_client"
        if hasattr(http, "streamable_http_client")
        else "streamablehttp_client"
    )
    monkeypatch.setattr(http, name, transport)
    monkeypatch.setattr(sse, "sse_client", legacy)
    manager = MCPManager(
        [MCPServerSettings(name="remote", url="https://example.test/mcp", headers=headers)]
    )
    try:
        assert await manager._open_transport(manager.servers[0]) == ("read", "write")
        assert seen == (["http", "sse"] if fallback else ["http"])
    finally:
        await manager.close()
