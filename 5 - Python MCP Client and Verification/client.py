"""Small Streamable HTTP client for the loopback Exograph MCP lab."""

from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from mcp import ClientSession
from mcp import types
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS


class ExographClientSession(ClientSession):
    async def initialize(self):
        result = await self.send_request(
            types.ClientRequest(
                types.InitializeRequest(
                    params=types.InitializeRequestParams(
                        protocolVersion="2025-06-18",
                        capabilities=types.ClientCapabilities(),
                        clientInfo=types.Implementation(
                            name="exograph-course-client", version="1.0"
                        ),
                    )
                )
            ),
            types.InitializeResult,
        )
        if result.protocolVersion not in SUPPORTED_PROTOCOL_VERSIONS:
            raise RuntimeError(
                f"Unsupported protocol version from server: {result.protocolVersion}"
            )
        self._server_capabilities = result.capabilities
        await self.send_notification(
            types.ClientNotification(types.InitializedNotification())
        )
        return result


def validate_loopback_url(url: str) -> None:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "::1", "localhost"}
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError("MCP_TEST_URL must be an HTTP loopback URL without credentials")


@asynccontextmanager
async def connect(url: str, token: str | None = None):
    validate_loopback_url(url)
    header_value = " ".join(("Bearer", token)) if token else None
    headers = {"Authorization": header_value} if header_value else None
    async with streamablehttp_client(url=url, headers=headers) as (read, write, _):
        async with ExographClientSession(read, write) as session:
            await session.initialize()
            yield session
