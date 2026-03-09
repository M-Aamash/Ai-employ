#!/usr/bin/env python3
"""
MCP Client for calling Playwright MCP tools.
"""

import sys
import json
import urllib.request
import urllib.error
from typing import Any, Dict

def call_tool(url: str, tool: str, params: Dict[str, Any]) -> Any:
    """Call an MCP tool via HTTP."""
    endpoint = f"{url}/tools/{tool}"
    
    data = json.dumps(params).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        print(f"Response: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        print(f"Is the server running on {url}?", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Call MCP tools')
    parser.add_argument('-u', '--url', required=True, help='MCP server URL')
    parser.add_argument('-t', '--tool', required=True, help='Tool name to call')
    parser.add_argument('-p', '--params', required=True, help='JSON parameters')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in params: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = call_tool(args.url, args.tool, params)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
