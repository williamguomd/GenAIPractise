"""
Example MCP Server Implementation

This is a basic template for an MCP server using FastMCP with stdio transport.
Replace this with your actual server implementation.
"""

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("example-server")


# Example: Define a tool
@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


# Example: Define another tool
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    # Run the server using stdio transport (default)
    mcp.run()

