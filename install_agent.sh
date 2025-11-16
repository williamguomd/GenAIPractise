#!/bin/bash

# Install Agent CLI Script for macOS
# This script installs the agent command system-wide

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "Installing agent CLI..."

# Check if uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Sync dependencies
echo "Installing dependencies..."
uv sync

# Create symlink in a location that's in PATH
# For macOS, we'll use /usr/local/bin (requires sudo) or ~/.local/bin
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

# Create a wrapper script
WRAPPER_SCRIPT="$BIN_DIR/agent"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Agent CLI wrapper script
cd "$PROJECT_DIR" || exit 1
uv run agent "\$@"
EOF

# Make it executable
chmod +x "$WRAPPER_SCRIPT"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  Warning: ~/.local/bin is not in your PATH"
    echo ""
    echo "Add this to your ~/.zshrc (or ~/.bash_profile):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then run:"
    echo "  source ~/.zshrc"
    echo ""
else
    echo "✓ ~/.local/bin is already in PATH"
fi

# Create default config directory and copy mcp.json
CONFIG_DIR="$HOME/.agent"
mkdir -p "$CONFIG_DIR"

# Always copy mcp.json from project root if it exists
if [ -f "$PROJECT_DIR/mcp.json" ]; then
    # Copy the project's mcp.json and update paths if needed
    cp "$PROJECT_DIR/mcp.json" "$CONFIG_DIR/mcp.json"
    # Update the cwd path in the config to use the actual project directory
    sed -i.bak "s|\"cwd\": \".*\"|\"cwd\": \"$PROJECT_DIR\"|g" "$CONFIG_DIR/mcp.json"
    rm -f "$CONFIG_DIR/mcp.json.bak" 2>/dev/null
    echo "✓ Copied mcp.json from project to $CONFIG_DIR/mcp.json"
elif [ -f "$PROJECT_DIR/mcp.json.example" ]; then
    # Update the example config with the actual project path
    sed "s|/Users/danielguo/PycharmProjects/GenAIPractise|$PROJECT_DIR|g" \
        "$PROJECT_DIR/mcp.json.example" > "$CONFIG_DIR/mcp.json"
    echo "✓ Created config from example at $CONFIG_DIR/mcp.json"
else
    # Create minimal config if neither exists
    cat > "$CONFIG_DIR/mcp.json" << EOF
{
  "mcp_servers": []
}
EOF
    echo "✓ Created default config at $CONFIG_DIR/mcp.json"
fi


echo ""
echo "✓ Installation complete!"
echo ""
echo "You can now use the 'agent' command:"
echo "  agent"
echo ""
echo "Make sure to:"
echo "  1. Set OPENAI_API_KEY in your environment or .env file"
echo "  2. Configure MCP servers in $CONFIG_DIR/mcp.json"
echo ""

