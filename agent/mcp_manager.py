"""
MCP Manager - Handles MCP server connections and tool discovery
"""

import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent.logger_config import get_logger

logger = get_logger(__name__)


class MCPManager:
    """Manages connections to MCP servers and provides tool access"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.tools_cache: Dict[str, List[Dict]] = {}
        
    def load_config(self):
        """Load MCP configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
    
    async def initialize(self):
        """Initialize connections to all configured MCP servers"""
        self.load_config()
        
        servers = self.config.get('mcp_servers', [])
        if not servers:
            logger.warning("No MCP servers found in config")
            return
        
        logger.info(f"Found {len(servers)} MCP server(s) in config")
        
        for server_config in servers:
            server_name = server_config.get('name')
            if not server_name:
                continue
            
            # Always try to connect to the server and discover tools dynamically
            logger.info(f"Connecting to {server_name}...")
            try:
                await self.discover_tools(server_config)
                tools_count = len(self.tools_cache.get(server_name, []))
                logger.info(f"Successfully discovered {tools_count} tool(s) from {server_name}")
            except Exception as e:
                # If discovery fails, fall back to config tools if available
                config_tools = server_config.get('tools', [])
                if config_tools:
                    logger.warning(f"Connection failed, using {len(config_tools)} tool(s) from config for {server_name}: {e}")
                    self.tools_cache[server_name] = config_tools
                else:
                    # No config tools and connection failed
                    self.tools_cache[server_name] = []
                    logger.error(f"Could not discover tools from {server_name} and no tools in config: {e}")
    
    async def discover_tools(self, server_config: Dict[str, Any]):
        """Discover tools from an MCP server by connecting to it"""
        server_name = server_config.get('name')
        command = server_config.get('command')
        args = server_config.get('args', [])
        cwd = server_config.get('cwd')
        
        if not command:
            logger.error(f"Server {server_name} missing 'command' in config")
            raise ValueError(f"Server {server_name} missing 'command' in config")
        
        # Build command list - resolve relative paths
        if cwd and not Path(command).is_absolute():
            # If command is relative and we have cwd, make it absolute
            cmd_path = Path(cwd) / command
            if cmd_path.exists():
                command = str(cmd_path)
        
        cmd = [command] + args
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=cmd[0],
            args=cmd[1:] if len(cmd) > 1 else [],
            env=None,
        )
        
        # Create stdio client and session
        logger.debug(f"Connecting to {server_name} with command: {cmd}")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                logger.debug(f"Initializing session for {server_name}")
                await session.initialize()
                
                # List available tools
                logger.debug(f"Listing tools from {server_name}")
                tools_result = await session.list_tools()
                tools = [
                    {
                        'name': tool.name,
                        'description': tool.description or '',
                        'inputSchema': tool.inputSchema
                    }
                    for tool in tools_result.tools
                ]
                
                logger.debug(f"Discovered {len(tools)} tool(s) from {server_name}")
                self.tools_cache[server_name] = tools
    
    def get_all_tools(self) -> Dict[str, List[Dict]]:
        """Get all available tools from all servers"""
        # Filter out servers with empty tool lists
        return {k: v for k, v in self.tools_cache.items() if v}
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific MCP server"""
        # This would require maintaining active sessions
        # For now, return a placeholder
        raise NotImplementedError("Tool calling requires active session management")

