"""
Main entry point for the GenAI Practise project.

This project contains multiple MCP servers. To run a specific server,
use: uv run python -m mcp_servers.<server_name>.server
"""


def main():
    print("GenAI Practise - MCP Servers Project")
    print("\nTo run a specific MCP server, use:")
    print("  uv run python -m mcp_servers.<server_name>.server")
    print("\nAvailable servers:")
    print("  - example_server: uv run python -m mcp_servers.example_server.server")


if __name__ == "__main__":
    main()
