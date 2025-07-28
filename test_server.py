#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""

import subprocess
import json
import sys
import time

def test_server():
    """Test the MCP server directly"""
    print("Testing MCP server...")
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "server/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send request
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("Initialization response:", response)
            
            # Test tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            server_process.stdin.write(json.dumps(tools_request) + "\n")
            server_process.stdin.flush()
            
            tools_response_line = server_process.stdout.readline()
            if tools_response_line:
                tools_response = json.loads(tools_response_line.strip())
                print("Tools list response:", tools_response)
                
                # Test echo tool
                echo_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "echo",
                        "arguments": {"message": "Hello, MCP!"}
                    }
                }
                
                server_process.stdin.write(json.dumps(echo_request) + "\n")
                server_process.stdin.flush()
                
                echo_response_line = server_process.stdout.readline()
                if echo_response_line:
                    echo_response = json.loads(echo_response_line.strip())
                    print("Echo tool response:", echo_response)
                    print("✅ Basic MCP functionality working!")
                else:
                    print("❌ No response from echo tool")
            else:
                print("❌ No response from tools list")
        else:
            print("❌ No response from initialization")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_server()
