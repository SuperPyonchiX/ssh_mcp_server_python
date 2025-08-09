#!/usr/bin/env python3

"""
SSH MCP Server のツールリスト取得テスト
"""

import json
import sys
import subprocess
import asyncio
from pathlib import Path

def test_tools_list():
    """tools/listリクエストをテストする"""
    
    # MCPリクエストのJSONメッセージ
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    
    tools_list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    # メッセージを準備
    messages = [
        json.dumps(initialize_request),
        json.dumps(initialized_notification),
        json.dumps(tools_list_request)
    ]
    
    input_data = "\n".join(messages)
    
    print("Testing SSH MCP Server tools/list response")
    print("=" * 50)
    
    try:
        # サーバーを起動してリクエストを送信
        process = subprocess.Popen(
            [sys.executable, "src/main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Path(__file__).parent
        )
        
        # リクエストを送信
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        print("STDOUT:")
        print("-" * 20)
        
        # JSONレスポンスを解析
        lines = stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    response = json.loads(line)
                    if response.get('method') == 'tools/list' or (response.get('id') == 2):
                        print("Tools List Response:")
                        print(json.dumps(response, indent=2, ensure_ascii=False))
                        
                        # ツールの詳細を表示
                        if 'result' in response and 'tools' in response['result']:
                            tools = response['result']['tools']
                            print(f"\nFound {len(tools)} tools:")
                            for i, tool in enumerate(tools, 1):
                                print(f"\n{i}. Tool: {tool['name']}")
                                print(f"   Description: {tool.get('description', 'No description')}")
                                if 'inputSchema' in tool:
                                    schema = tool['inputSchema']
                                    if 'properties' in schema:
                                        print("   Parameters:")
                                        for param, details in schema['properties'].items():
                                            param_type = details.get('type', 'unknown')
                                            param_desc = details.get('description', '')
                                            required = param in schema.get('required', [])
                                            req_mark = " (required)" if required else " (optional)"
                                            print(f"     - {param}: {param_type}{req_mark}")
                                            if param_desc:
                                                print(f"       {param_desc}")
                    else:
                        print("Response:")
                        print(json.dumps(response, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"Non-JSON line: {line}")
        
        if stderr:
            print("\nSTDERR:")
            print("-" * 20)
            print(stderr)
        
        print(f"\nProcess exit code: {process.returncode}")
        
    except subprocess.TimeoutExpired:
        print("ERROR: Process timed out")
        process.kill()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_tools_list()
