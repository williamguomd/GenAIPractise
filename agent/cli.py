"""
Agent CLI - Interactive command-line interface for MCP tools and LLM integration
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown

from agent.mcp_manager import MCPManager
from agent.llm_client import LLMClient

console = Console()


class AgentCLI:
    """Interactive CLI for the agent application"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".agent" / "mcp.json"
        self.mcp_manager = MCPManager(self.config_path)
        try:
            self.llm_client = LLMClient()
        except ValueError:
            # API key not set, but we'll allow the CLI to start
            # and show an error when user tries to use LLM
            self.llm_client = None
        self.running = True
        
    def print_banner(self):
        """Print welcome banner"""
        banner = """
# My Agent CLI

Interactive command-line interface for MCP tools and LLM integration.

Type `/help` for available commands, or `/exit` to quit.
"""
        console.print(Markdown(banner))
        
    def print_help(self):
        """Print help message"""
        help_text = """
## Available Commands

- `/tools` - List all available MCP tools
- `/help` - Show this help message
- `/exit` or `/quit` - Exit the agent
- `/clear` - Clear the screen

## Usage

- Type any text to send a request to the LLM
- Use `/tools` to see available MCP tools that can be used
"""
        console.print(Markdown(help_text))
    
    def list_tools(self):
        """List all available MCP tools"""
        tools = self.mcp_manager.get_all_tools()
        
        # Debug output
        console.print(f"[dim]Debug: tools_cache has {len(tools)} server(s)[/dim]")
        if tools:
            for server_name, server_tools in tools.items():
                console.print(f"[dim]Debug: {server_name} has {len(server_tools)} tool(s)[/dim]")
        
        if not tools:
            console.print("[yellow]No MCP tools available. Check your mcp.json configuration.[/yellow]")
            console.print(f"[dim]Config path: {self.mcp_manager.config_path}[/dim]")
            console.print(f"[dim]Config exists: {self.mcp_manager.config_path.exists()}[/dim]")
            return
        
        # Check if all servers have empty tool lists
        total_tools = sum(len(server_tools) for server_tools in tools.values())
        if total_tools == 0:
            console.print("[yellow]MCP servers found but no tools available.[/yellow]")
            return
        
        console.print("\n[bold cyan]Available MCP Tools:[/bold cyan]\n")
        for server_name, server_tools in tools.items():
            if server_tools:  # Only show servers with tools
                console.print(f"[bold green]{server_name}:[/bold green]")
                for tool in server_tools:
                    console.print(f"  • {tool['name']}: {tool.get('description', 'No description')}")
                console.print()
    
    async def process_user_input(self, user_input: str):
        """Process user input and handle commands or LLM requests"""
        user_input = user_input.strip()
        
        if not user_input:
            return
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input.split()[0]
            
            if command in ['/exit', '/quit']:
                self.running = False
                console.print("[yellow]Goodbye![/yellow]")
                return
            elif command == '/help':
                self.print_help()
                return
            elif command == '/tools':
                self.list_tools()
                return
            elif command == '/clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                return
            else:
                console.print(f"[red]Unknown command: {command}. Type /help for available commands.[/red]")
                return
        
        # Handle LLM request
        if not self.llm_client:
            console.print("[red]LLM not configured. Set OPENAI_API_KEY environment variable.[/red]")
            return
        
        try:
            console.print("[dim]Thinking...[/dim]")
            response = await self.llm_client.chat(user_input)
            console.print(f"\n[bold]Response:[/bold]\n")
            console.print(Markdown(response))
            console.print()
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    async def run(self):
        """Run the interactive CLI"""
        self.print_banner()
        
        # Initialize MCP connections
        try:
            await self.mcp_manager.initialize()
            console.print("[green]✓ MCP tools loaded[/green]\n")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load MCP tools: {str(e)}[/yellow]\n")
        
        # Main loop
        while self.running:
            try:
                user_input = Prompt.ask("[bold cyan]agent>[/bold cyan]")
                await self.process_user_input(user_input)
            except KeyboardInterrupt:
                console.print("\n[yellow]Use /exit to quit[/yellow]")
            except EOFError:
                self.running = False
                console.print("\n[yellow]Goodbye![/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")


def main():
    """Main entry point for the agent CLI"""
    # Check for config file - first try project root, then ~/.agent/mcp.json
    # Try multiple methods to find project root
    project_root = None
    
    # Method 1: Relative to this file
    try:
        file_root = Path(__file__).parent.parent.parent
        if (file_root / "mcp.json").exists() or (file_root / "pyproject.toml").exists():
            project_root = file_root
    except:
        pass
    
    # Method 2: Current working directory
    if not project_root:
        cwd = Path.cwd()
        if (cwd / "mcp.json").exists() or (cwd / "pyproject.toml").exists():
            project_root = cwd
    
    # Method 3: Look for pyproject.toml in parent directories
    if not project_root:
        current = Path.cwd()
        for parent in [current] + list(current.parents)[:3]:  # Check up to 3 levels up
            if (parent / "pyproject.toml").exists():
                project_root = parent
                break
    
    project_config = project_root / "mcp.json" if project_root else None
    home_config = Path.home() / ".agent" / "mcp.json"
    
    # Prefer project root config, fall back to home config
    config_path = None
    if project_config and project_config.exists():
        config_path = project_config
        console.print(f"[dim]Using config from project root: {config_path}[/dim]")
    elif home_config.exists():
        config_path = home_config
        console.print(f"[dim]Using config from home: {config_path}[/dim]")
        # Warn if project root config exists but wasn't used
        if project_config and project_config.exists():
            console.print(f"[yellow]Warning: Project root config exists at {project_config} but using home config instead[/yellow]")
    else:
        # Create default config in home directory
        config_path = home_config
        console.print(f"[yellow]Config file not found. Creating default at {config_path}[/yellow]")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "mcp_servers": []
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        console.print(f"[green]Created default config at {config_path}[/green]")
        console.print("[yellow]Please edit the config file to add MCP servers.[/yellow]\n")
    
    if not config_path:
        console.print("[red]Error: Could not determine config path[/red]")
        return
    
    # Run the CLI
    try:
        cli = AgentCLI(config_path)
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

