#!/bin/bash
# Stop LinkedIn MCP Server (Playwright)

PORT=8809

echo "Stopping LinkedIn MCP server on port $PORT..."

# Close browser first (clean shutdown)
python3 scripts/mcp-client.py call -u http://localhost:$PORT -t browser_close -p '{}' 2>/dev/null

# Give it a moment
sleep 1

# Kill the server process
pkill -f "@playwright/mcp.*$PORT"

# Verify it's stopped
if pgrep -f "@playwright/mcp.*$PORT" > /dev/null; then
    echo "✗ Failed to stop LinkedIn MCP server"
    exit 1
else
    echo "✓ LinkedIn MCP server stopped successfully"
    exit 0
fi
