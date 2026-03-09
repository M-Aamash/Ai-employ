#!/bin/bash
# Start LinkedIn MCP Server (Playwright)

PORT=8809

echo "Starting LinkedIn MCP server on port $PORT..."

# Check if already running
if pgrep -f "@playwright/mcp.*$PORT" > /dev/null; then
    echo "LinkedIn MCP server already running on port $PORT"
    exit 0
fi

# Start the server
npx @playwright/mcp@latest --port $PORT --shared-browser-context &

# Wait for server to be ready
sleep 3

# Verify it's running
if pgrep -f "@playwright/mcp.*$PORT" > /dev/null; then
    echo "✓ LinkedIn MCP server started successfully on port $PORT"
    echo "  Use: python3 scripts/mcp-client.py call -u http://localhost:$PORT -t <tool> -p '<params>'"
else
    echo "✗ Failed to start LinkedIn MCP server"
    exit 1
fi
