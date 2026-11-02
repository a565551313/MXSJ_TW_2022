"""MXSJ client-native MCP access tools.

This package provides a standard MCP server that exposes read-only
client-native testing capabilities through a local test channel. The first
implementation stage (M3) targets the Linux dev mode: the server talks to a
fake probe so protocol, transport, tools and session-lock behaviour can be
verified without a real Windows game client.
"""

__version__ = "0.1.0"
