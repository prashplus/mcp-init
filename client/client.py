#!/usr/bin/env python3
"""
MCP Client Tutorial - A simple Model Context Protocol client implementation
This client connects to MCP servers and demonstrates basic interactions.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional
import logging

class MCPClient:
    def __init__(self):
        self.request_id = 0
        self.process = None
        self.initialized = False
        
    def get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def connect_to_server(self, server_command: List[str]) -> bool:
        """Connect to MCP server using subprocess"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="."
            )
            # Give the server a moment to start
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logging.error(f"Failed to connect to server: {e}")
            return False
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        if not self.process:
            raise Exception("Not connected to server")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line.encode())
        await self.process.stdin.drain()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(), 
                timeout=10.0
            )
            if not response_line:
                raise Exception("Server closed connection")
            
            return json.loads(response_line.decode().strip())
        except asyncio.TimeoutError:
            raise Exception("Request timed out")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    async def initialize(self) -> bool:
        """Initialize connection with the server"""
        try:
            response = await self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "tutorial-mcp-client",
                    "version": "1.0.0"
                }
            })
            
            if "error" in response:
                logging.error(f"Initialization failed: {response['error']}")
                return False
            
            self.initialized = True
            logging.info("Successfully initialized connection")
            return True
            
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server"""
        if not self.initialized:
            raise Exception("Client not initialized")
        
        response = await self.send_request("tools/list")
        
        if "error" in response:
            raise Exception(f"Error listing tools: {response['error']}")
        
        return response["result"]["tools"]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the server"""
        if not self.initialized:
            raise Exception("Client not initialized")
        
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in response:
            raise Exception(f"Error calling tool: {response['error']}")
        
        # Extract text from response
        content = response["result"]["content"]
        if content and len(content) > 0:
            return content[0]["text"]
        return ""
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from the server"""
        if not self.initialized:
            raise Exception("Client not initialized")
        
        response = await self.send_request("resources/list")
        
        if "error" in response:
            raise Exception(f"Error listing resources: {response['error']}")
        
        return response["result"]["resources"]
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource from the server"""
        if not self.initialized:
            raise Exception("Client not initialized")
        
        response = await self.send_request("resources/read", {
            "uri": uri
        })
        
        if "error" in response:
            raise Exception(f"Error reading resource: {response['error']}")
        
        contents = response["result"]["contents"]
        if contents and len(contents) > 0:
            return contents[0]["text"]
        return ""
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts from the server"""
        if not self.initialized:
            raise Exception("Client not initialized")
        
        response = await self.send_request("prompts/list")
        
        if "error" in response:
            raise Exception(f"Error listing prompts: {response['error']}")
        
        return response["result"]["prompts"]
    
    async def get_prompt(self, prompt_name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Get a prompt from the server"""
        if not self.initialized:
            raise Exception("Client not initialized")
        
        params = {"name": prompt_name}
        if arguments:
            params["arguments"] = arguments
        
        response = await self.send_request("prompts/get", params)
        
        if "error" in response:
            raise Exception(f"Error getting prompt: {response['error']}")
        
        messages = response["result"]["messages"]
        if messages and len(messages) > 0:
            return messages[0]["content"]["text"]
        return ""
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
        self.initialized = False

async def demo_client():
    """Demonstrate the MCP client functionality"""
    client = MCPClient()
    
    # Connect to local server (adjust path for current directory)
    import os
    server_path = os.path.join("..", "server", "server.py")
    server_command = [sys.executable, server_path]
    
    print("Connecting to MCP server...")
    if not await client.connect_to_server(server_command):
        print("Failed to connect to server")
        return
    
    print("Initializing connection...")
    if not await client.initialize():
        print("Failed to initialize connection")
        return
    
    try:
        # List and demonstrate tools
        print("\n=== TOOLS ===")
        tools = await client.list_tools()
        print(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # Test echo tool
        echo_result = await client.call_tool("echo", {"message": "Hello, MCP!"})
        print(f"Echo tool result: {echo_result}")
        
        # Test calculate tool
        calc_result = await client.call_tool("calculate", {"expression": "10 + 5 * 2"})
        print(f"Calculate tool result: {calc_result}")
        
        # Test get_time tool
        time_result = await client.call_tool("get_time", {})
        print(f"Get time tool result: {time_result}")
        
        # List and demonstrate resources
        print("\n=== RESOURCES ===")
        resources = await client.list_resources()
        print(f"Available resources: {[resource['name'] for resource in resources]}")
        
        # Read greeting resource
        greeting = await client.read_resource("resource://greeting")
        print(f"Greeting resource: {greeting}")
        
        # Read system info resource
        system_info = await client.read_resource("resource://system_info")
        print(f"System info resource: {system_info}")
        
        # List and demonstrate prompts
        print("\n=== PROMPTS ===")
        prompts = await client.list_prompts()
        print(f"Available prompts: {[prompt['name'] for prompt in prompts]}")
        
        # Get helpful assistant prompt
        prompt = await client.get_prompt("helpful_assistant", {"topic": "Python programming"})
        print(f"Helpful assistant prompt: {prompt}")
        
    except Exception as e:
        print(f"Error during demo: {e}")
    
    finally:
        await client.disconnect()
        print("\nDisconnected from server")

async def interactive_client():
    """Interactive MCP client for testing"""
    client = MCPClient()
    
    # Connect to local server (adjust path for current directory)
    import os
    server_path = os.path.join("..", "server", "server.py")
    server_command = [sys.executable, server_path]
    
    print("Connecting to MCP server...")
    if not await client.connect_to_server(server_command):
        print("Failed to connect to server")
        return
    
    if not await client.initialize():
        print("Failed to initialize connection")
        return
    
    print("Connected! Type 'help' for commands, 'quit' to exit.")
    
    try:
        while True:
            command = input("\n> ").strip().lower()
            
            if command == "quit":
                break
            elif command == "help":
                print("Commands:")
                print("  tools - List available tools")
                print("  echo <message> - Test echo tool")
                print("  calc <expression> - Test calculator tool")
                print("  time - Get current time")
                print("  resources - List available resources")
                print("  greeting - Read greeting resource")
                print("  sysinfo - Read system info resource")
                print("  prompts - List available prompts")
                print("  quit - Exit")
            elif command == "tools":
                tools = await client.list_tools()
                for tool in tools:
                    print(f"  {tool['name']}: {tool['description']}")
            elif command.startswith("echo "):
                message = command[5:]
                result = await client.call_tool("echo", {"message": message})
                print(f"Result: {result}")
            elif command.startswith("calc "):
                expression = command[5:]
                result = await client.call_tool("calculate", {"expression": expression})
                print(f"Result: {result}")
            elif command == "time":
                result = await client.call_tool("get_time", {})
                print(f"Current time: {result}")
            elif command == "resources":
                resources = await client.list_resources()
                for resource in resources:
                    print(f"  {resource['name']}: {resource['description']}")
            elif command == "greeting":
                result = await client.read_resource("resource://greeting")
                print(f"Greeting: {result}")
            elif command == "sysinfo":
                result = await client.read_resource("resource://system_info")
                print(f"System info: {result}")
            elif command == "prompts":
                prompts = await client.list_prompts()
                for prompt in prompts:
                    print(f"  {prompt['name']}: {prompt['description']}")
            else:
                print("Unknown command. Type 'help' for available commands.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_client())
    else:
        asyncio.run(demo_client())
