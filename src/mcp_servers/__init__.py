"""
MCP Servers for CO2-Aware Shopping Assistant

This package contains MCP servers for external API integration.
"""

from .boutique_mcp import BoutiqueMCPServer
from .co2_mcp import CO2MCPServer

__all__ = [
    "BoutiqueMCPServer",
    "CO2MCPServer"
]
