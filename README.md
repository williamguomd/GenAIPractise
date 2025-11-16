# GenAI Practise - MCP Servers & Agent CLI

This project contains 
- sample MCP (Model Context Protocol) servers 
- an interactive Agent CLI 
- multi-agents orchestration samples -- TODO

## Project Structure

```
.
├── agent/               # Agent CLI application
│   ├── __init__.py
│   ├── cli.py          # Main CLI interface
│   ├── mcp_manager.py  # MCP server integration
│   └── llm_client.py   # LLM API client
├── mcp_servers/        # Directory containing all MCP servers
│   ├── __init__.py
│   ├── start_mcp_server.sh # Shell script to start MCP servers
│   └── example_server/ # Example MCP server
│       ├── __init__.py
│       └── server.py
├── main.py             # Main entry point
├── pyproject.toml      # Project configuration
├── install_agent.sh    # Installation script for agent CLI
├── mcp.json            # MCP configuration
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run a specific MCP server:

   **Using the shell script (recommended):**
   ```bash
   ./mcp_servers/start_mcp_server.sh [server_name]
   ```
   
   Example:
   ```bash
   ./mcp_servers/start_mcp_server.sh example_server
   ```
   
   If no server name is provided, it defaults to `example_server`.
   
   **Or directly with uv:**
   ```bash
   uv run python -m mcp_servers.example_server.server
   ```

## Agent CLI

The Agent CLI is an interactive command-line interface that integrates with MCP tools and LLM APIs.

### Installation

1. Run the installation script:
   ```bash
   ./install_agent.sh
   ```

2. Add `~/.local/bin` to your PATH (if not already):
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. Set your OpenAI API key:
   
   Edit the `.env` file in the project root and add your API key:
   ```bash
   OPENAI_API_KEY=your-actual-api-key-here
   ```
   
   Or set it as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   The `.env` file is already in `.gitignore` to keep your API key secure.

4. Configure MCP servers in `~/.agent/mcp.json` (see `mcp.json.example` for format)

### Usage

Start the agent:
```bash
agent
```

You'll see an interactive prompt:
```
agent>
```

### Commands

- `/tools` - List all available MCP tools
- `/help` - Show help message
- `/exit` or `/quit` - Exit the agent
- `/clear` - Clear the screen

### Features

- **Interactive REPL**: Similar to Python's interactive shell with `agent>` prompt
- **MCP Integration**: Automatically discovers and lists tools from configured MCP servers
- **LLM Integration**: Send requests directly to LLM and get responses
- **Rich UI**: Beautiful terminal interface with colors and markdown support

### MCP Configuration

The agent reads MCP server configuration from `~/.agent/mcp.json`. Example:

```json
{
  "mcp_servers": [
    {
      "name": "example_server",
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_servers.example_server.server"],
      "cwd": "/path/to/project"
    }
  ]
}
```

## Adding a New MCP Server

1. Create a new directory under `mcp_servers/`
2. Add your server implementation
3. Follow the MCP protocol specifications

