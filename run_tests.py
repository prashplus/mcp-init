#!/usr/bin/env python3
"""
Tests for the MCP Tutorial project
Run this script to validate basic functionality before CI
"""

import asyncio
import json
import subprocess
import sys
import os
import tempfile
import time
from typing import Dict, Any

def test_syntax_compilation():
    """Test that all Python files compile without syntax errors"""
    print("🔍 Testing Python syntax compilation...")
    
    files_to_test = [
        "server/server.py",
        "client/client.py", 
        "client/ollama_integration.py",
        "client/quick_test.py",
        "test_server.py",
        "start.py"
    ]
    
    for file_path in files_to_test:
        try:
            result = subprocess.run([sys.executable, "-m", "py_compile", file_path], 
                                  capture_output=True, text=True, check=True)
            print(f"  ✅ {file_path} - syntax OK")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ {file_path} - syntax error: {e.stderr}")
            return False
    
    return True

def test_server_functionality():
    """Test basic MCP server functionality"""
    print("\n🔍 Testing MCP server functionality...")
    
    try:
        # Start the server process
        server_process = subprocess.Popen(
            [sys.executable, "server/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if not response_line:
            print("  ❌ No initialization response")
            return False
            
        response = json.loads(response_line.strip())
        if "result" not in response:
            print(f"  ❌ Initialization failed: {response}")
            return False
            
        print("  ✅ Server initialization - OK")
        
        # Test calculator tool with safe evaluation
        calc_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"expression": "10 + 5 * 2"}
            }
        }
        
        server_process.stdin.write(json.dumps(calc_request) + "\n")
        server_process.stdin.flush()
        
        calc_response_line = server_process.stdout.readline()
        if calc_response_line:
            calc_response = json.loads(calc_response_line.strip())
            if "result" in calc_response:
                result_text = calc_response["result"]["content"][0]["text"]
                if result_text == "20":
                    print("  ✅ Calculator tool - OK")
                else:
                    print(f"  ❌ Calculator tool returned wrong result: {result_text}")
                    return False
            else:
                print(f"  ❌ Calculator tool failed: {calc_response}")
                return False
        else:
            print("  ❌ No calculator response")
            return False
            
        # Test that dangerous expressions are blocked
        dangerous_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"expression": "import os"}
            }
        }
        
        server_process.stdin.write(json.dumps(dangerous_request) + "\n")
        server_process.stdin.flush()
        
        dangerous_response_line = server_process.stdout.readline()
        if dangerous_response_line:
            dangerous_response = json.loads(dangerous_response_line.strip())
            if "result" in dangerous_response:
                result_text = dangerous_response["result"]["content"][0]["text"]
                if "Error calculating" in result_text:
                    print("  ✅ Security - dangerous expressions blocked")
                else:
                    print(f"  ❌ Security - dangerous expression not blocked: {result_text}")
                    return False
            else:
                print("  ❌ No response to dangerous expression test")
                return False
        
        server_process.terminate()
        server_process.wait()
        print("  ✅ Server functionality - OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Server test failed: {e}")
        return False

def test_client_imports():
    """Test that client modules can be imported"""
    print("\n🔍 Testing client imports...")
    
    try:
        # Test client import
        sys.path.append("client")
        from client import MCPClient
        print("  ✅ MCPClient import - OK")
        
        # Test ollama integration import
        from ollama_integration import OllamaMCPIntegration
        print("  ✅ OllamaMCPIntegration import - OK")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running MCP Tutorial Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test syntax compilation
    if not test_syntax_compilation():
        all_passed = False
    
    # Test server functionality
    if not test_server_functionality():
        all_passed = False
    
    # Test client imports
    if not test_client_imports():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Ready for CI.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix issues before CI.")
        sys.exit(1)

if __name__ == "__main__":
    main()
