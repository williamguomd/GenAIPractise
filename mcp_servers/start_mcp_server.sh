#!/bin/bash

# Start MCP Server Script
# This script starts the example MCP server using uv
# It automatically installs uv if not found

set -e  # Exit on error

# Get the directory where the script is located (mcp_servers/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root directory (one level up from mcp_servers)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default server name
SERVER_NAME="${1:-example_server}"

# Change to project root directory
cd "$PROJECT_ROOT" || exit 1

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install uv
install_uv() {
    echo "uv not found. Installing uv..." >&2  # Redirect to stderr
    
    # Check if curl is available
    if ! command_exists curl; then
        echo "Error: curl is required to install uv but is not installed." >&2
        echo "Please install curl first, or install uv manually:" >&2
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
        exit 1
    fi
    
    # Detect OS
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    
    # Set architecture
    case "$ARCH" in
        x86_64)
            UV_ARCH="x86_64"
            ;;
        arm64|aarch64)
            UV_ARCH="aarch64"
            ;;
        *)
            echo "Error: Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    # Install based on OS
    case "$OS" in
        Linux*)
            echo "Installing uv for Linux ($UV_ARCH)..." >&2
            curl -LsSf https://astral.sh/uv/install.sh | sh >&2
            ;;
        Darwin*)
            echo "Installing uv for macOS ($UV_ARCH)..." >&2
            curl -LsSf https://astral.sh/uv/install.sh | sh >&2
            ;;
        *)
            echo "Error: Unsupported operating system: $OS" >&2
            echo "Please install uv manually from https://github.com/astral-sh/uv" >&2
            exit 1
            ;;
    esac
    
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Verify installation
    if command_exists uv; then
        echo "✓ uv installed successfully" >&2  # Redirect to stderr
        uv --version >&2  # Redirect to stderr
    else
        echo "Error: uv installation failed. Please install manually:" >&2
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
        exit 1
    fi
}

# Check if uv is installed, install if not
if ! command_exists uv; then
    install_uv >&2  # Redirect to stderr
else
    echo "✓ uv is already installed" >&2  # Redirect to stderr
    uv --version >&2  # Redirect to stderr
fi

# Ensure uv is in PATH
if ! command_exists uv; then
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check if server exists
if [ ! -d "mcp_servers/$SERVER_NAME" ]; then
    echo "Error: Server '$SERVER_NAME' not found in mcp_servers/" >&2
    echo "Available servers:" >&2
    ls -1 mcp_servers/ 2>/dev/null | grep -v __pycache__ | grep -v __init__.py | grep -v start_mcp_server.sh | grep -v '^$' || echo "  (none found)" >&2
    exit 1
fi

# Start the MCP server (redirect status messages to stderr)
echo "" >&2
echo "Starting MCP server: $SERVER_NAME" >&2
echo "Press Ctrl+C to stop the server" >&2
echo "" >&2

# Run the server - stdout should only contain JSON-RPC messages
uv run python -m "mcp_servers.$SERVER_NAME.server"

