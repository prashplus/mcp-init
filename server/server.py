#!/usr/bin/env python3
"""
MCP Server Tutorial - A simple Model Context Protocol server implementation
This server provides basic tools and resources for demonstration purposes.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import logging

# MCP Server implementation
class MCPServer:
    def __init__(self):
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        self.setup_tools()
        self.setup_resources()
        self.setup_prompts()
        
    def setup_tools(self):
        """Setup available tools for the MCP server"""
        self.tools = {
            "echo": {
                "name": "echo",
                "description": "Echo back the input message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "Perform basic mathematical calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')"
                        }
                    },
                    "required": ["expression"]
                }
            },
            "get_time": {
                "name": "get_time",
                "description": "Get current date and time",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    def setup_resources(self):
        """Setup available resources for the MCP server"""
        self.resources = {
            "greeting": {
                "uri": "resource://greeting",
                "name": "Greeting Message",
                "description": "A simple greeting message",
                "mimeType": "text/plain"
            },
            "system_info": {
                "uri": "resource://system_info", 
                "name": "System Information",
                "description": "Basic system information",
                "mimeType": "application/json"
            }
        }
    
    def setup_prompts(self):
        """Setup available prompts for the MCP server"""
        self.prompts = {
            "helpful_assistant": {
                "name": "helpful_assistant",
                "description": "A helpful assistant prompt",
                "arguments": [
                    {
                        "name": "topic",
                        "description": "The topic to be helpful about",
                        "required": False
                    }
                ]
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return await self.handle_initialize(request_id, params)
            elif method == "tools/list":
                return await self.handle_tools_list(request_id)
            elif method == "tools/call":
                return await self.handle_tool_call(request_id, params)
            elif method == "resources/list":
                return await self.handle_resources_list(request_id)
            elif method == "resources/read":
                return await self.handle_resource_read(request_id, params)
            elif method == "prompts/list":
                return await self.handle_prompts_list(request_id)
            elif method == "prompts/get":
                return await self.handle_prompt_get(request_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_initialize(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "tutorial-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_tools_list(self, request_id: int) -> Dict[str, Any]:
        """Handle tools list request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    async def handle_tool_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "echo":
            message = arguments.get("message", "")
            result = f"Echo: {message}"
        elif tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # Simple evaluation - in production, use a safer parser
                result = str(eval(expression))
            except Exception as e:
                result = f"Error calculating: {str(e)}"
        elif tool_name == "get_time":
            import datetime
            result = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        }
    
    async def handle_resources_list(self, request_id: int) -> Dict[str, Any]:
        """Handle resources list request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": list(self.resources.values())
            }
        }
    
    async def handle_resource_read(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource read request"""
        uri = params.get("uri", "")
        
        if uri == "resource://greeting":
            content = "Hello! Welcome to the MCP Tutorial Server!"
        elif uri == "resource://system_info":
            import platform
            content = json.dumps({
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0]
            })
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown resource: {uri}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain" if uri == "resource://greeting" else "application/json",
                        "text": content
                    }
                ]
            }
        }
    
    async def handle_prompts_list(self, request_id: int) -> Dict[str, Any]:
        """Handle prompts list request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": list(self.prompts.values())
            }
        }
    
    async def handle_prompt_get(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompt get request"""
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name == "helpful_assistant":
            topic = arguments.get("topic", "general assistance")
            prompt_text = f"You are a helpful assistant specialized in {topic}. Please provide clear, accurate, and helpful responses."
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown prompt: {prompt_name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "description": f"Helpful assistant prompt for {topic}",
                "messages": [
                    {
                        "role": "system",
                        "content": {
                            "type": "text",
                            "text": prompt_text
                        }
                    }
                ]
            }
        }

async def run_stdio_server():
    """Run the MCP server using stdio transport"""
    server = MCPServer()
    
    # Read from stdin and write to stdout
    while True:
        try:
            # Read line from stdin asynchronously
            loop = asyncio.get_event_loop()
            line = await loop.run_in_executor(None, sys.stdin.readline)
            
            if not line.strip():
                continue
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            continue
        except EOFError:
            logging.info("EOF received, shutting down")
            break
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            # Send error response if we have a request ID
            try:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except:
                pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_stdio_server())
