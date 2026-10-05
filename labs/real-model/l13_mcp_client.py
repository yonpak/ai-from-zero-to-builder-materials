#!/usr/bin/env python3
"""Optional Level 13 extension: discover and call the real MCP server through the official SDK."""

from __future__ import annotations

import asyncio
import json

from mcp import Client

from l13_mcp_server import mcp


async def run() -> None:
    async with Client(mcp, raise_exceptions=True) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools.tools]
        if "get_order_status" not in names:
            raise RuntimeError(f"expected get_order_status in discovered tools: {names}")

        result = await client.call_tool("get_order_status", {"order_id": "4172"})
        if result.is_error:
            raise RuntimeError(f"MCP tool call failed: {result.content}")

        print(f"negotiated_protocol: {client.protocol_version}")
        print(f"discovered_tools: {names}")
        print("structured_result:")
        print(json.dumps(result.structured_content, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(run())
