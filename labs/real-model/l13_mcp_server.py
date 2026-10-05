#!/usr/bin/env python3
"""Optional Level 13 extension: a real MCP server built with the official Python SDK."""

from __future__ import annotations

from mcp.server import MCPServer

mcp = MCPServer("order-status-demo")

ORDERS = {
    "4172": {"order_id": "4172", "status": "shipped", "eta_days": 2},
    "9001": {"order_id": "9001", "status": "processing", "eta_days": 5},
}


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """Read the status of one demo order.

    Args:
        order_id: The order identifier to retrieve.
    """
    return ORDERS.get(order_id, {"order_id": order_id, "status": "not_found"})
