#!/usr/bin/env python3
"""
Verify LinkedIn MCP Server is running.
"""

import sys
import urllib.request
import json
from pathlib import Path

PORT = 8809

def check_server():
    """Check if the LinkedIn MCP server is running."""
    try:
        url = f"http://localhost:{PORT}"
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                return True, "LinkedIn MCP server is running"
    except Exception as e:
        return False, f"Server not responding: {e}"
    
    return False, "Unknown error"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   LinkedIn MCP Verification")
    print("=" * 60 + "\n")
    
    success, message = check_server()
    
    if success:
        print(f"✓ {message}")
        print("\nServer Details:")
        print(f"  Port: {PORT}")
        print(f"  URL: http://localhost:{PORT}")
        print("\nReady to automate LinkedIn activities!")
    else:
        print(f"✗ {message}")
        print("\nTo start the server:")
        print("  bash scripts/start-server.sh")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
