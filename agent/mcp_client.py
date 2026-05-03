import asyncio
from typing import Any

import anyio
import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_PATH = "/mcp"


def _ensure_mcp_url(base_url: str) -> str:
    if base_url.endswith(MCP_PATH):
        return base_url
    return base_url.rstrip("/") + MCP_PATH


def _content_block_to_text(block: types.ContentBlock | dict[str, Any]) -> str:
    if isinstance(block, dict):
        block_type = block.get("type")
        if block_type == "text":
            return block.get("text", "")
        if block_type == "tool_result":
            return " ".join(_content_block_to_text(item) for item in block.get("content", []))
        if block_type == "resource_link":
            return block.get("uri", "")
        return str(block)

    block_type = getattr(block, "type", None)
    if block_type == "text":
        return getattr(block, "text", "")
    if block_type == "tool_result":
        return " ".join(_content_block_to_text(item) for item in getattr(block, "content", []))
    if block_type == "resource_link":
        return getattr(block, "uri", "")
    return str(block)


def _format_tool_result(result: types.CallToolResult) -> str:
    if result.structuredContent is not None:
        return str(result.structuredContent)

    if result.content:
        return "\n".join(
            _content_block_to_text(block)
            for block in result.content
        ).strip()

    return ""


async def _call_tool_async(
    url: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> str:
    async with streamable_http_client(_ensure_mcp_url(url)) as (read_stream, write_stream, _):
        async with ClientSession(
            read_stream,
            write_stream,
            client_info=types.Implementation(name="travel-agent", version="0.1"),
        ) as session:
            await session.initialize()
            tool_result = await session.call_tool(name=tool_name, arguments=arguments or {})
            if tool_result.isError:
                raise RuntimeError(f"MCP tool {tool_name} returned an error")
            return _format_tool_result(tool_result)


def _run_async(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return anyio.from_thread.run(lambda: asyncio.run(coro))


def call_tool(url: str, tool_name: str, arguments: dict[str, Any] | None = None) -> str:
    try:
        return _run_async(_call_tool_async(url, tool_name, arguments))
    except Exception as exc:
        return f"Error calling MCP tool {tool_name}: {exc}"
