#!/usr/bin/env python3
"""
MCP Ollama Integration Example
This demonstrates how to integrate the MCP server with Ollama for AI interactions.
"""

import asyncio
import json
import requests
import sys
from typing import Dict, List, Any
from client import MCPClient

class OllamaMCPIntegration:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.mcp_client = MCPClient()
        self.available_tools = []
        self.available_models = []
        
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.available_models = [model["name"] for model in models]
                return self.available_models
            else:
                print(f"Error getting models: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return []
        
    async def initialize_mcp(self) -> bool:
        """Initialize MCP client connection"""
        server_command = [sys.executable, "../server/server.py"]
        
        if not await self.mcp_client.connect_to_server(server_command):
            print("Failed to connect to MCP server")
            return False
            
        if not await self.mcp_client.initialize():
            print("Failed to initialize MCP connection")
            return False
            
        # Get available tools
        self.available_tools = await self.mcp_client.list_tools()
        print(f"Connected to MCP server with tools: {[tool['name'] for tool in self.available_tools]}")
        
        # Get available Ollama models
        self.available_models = self.get_available_models()
        if self.available_models:
            print(f"Available Ollama models: {self.available_models}")
        else:
            print("Warning: No Ollama models found or Ollama not accessible")
            
        return True
    
    def call_ollama(self, prompt: str, model: str = "llama3.2:latest") -> str:
        """Call Ollama API"""
        try:
            # First check if the model exists
            models_response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if models_response.status_code != 200:
                return f"Error: Cannot connect to Ollama at {self.ollama_url}"
            
            available_models = [m["name"] for m in models_response.json().get("models", [])]
            if not available_models:
                return "Error: No models available in Ollama"
            
            # Use the first available model if specified model doesn't exist
            if model not in available_models:
                model = available_models[0]
                print(f"Model '{model}' not found, using '{available_models[0]}'")
            
            # Call the chat API (newer endpoint)
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "No response from model")
            else:
                # Try the legacy generate endpoint as fallback
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "No response from model")
                else:
                    return f"Error calling Ollama: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434"
        except requests.exceptions.Timeout:
            return "Error: Ollama request timed out"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    async def enhanced_chat(self, user_message: str, model: str = "llama3.2:latest") -> str:
        """Enhanced chat that can use MCP tools when needed"""
        
        # Check if the user message might need tool assistance
        tool_keywords = {
            "calculate": ["calculate", "compute", "math", "arithmetic"],
            "time": ["time", "date", "when", "now"],
            "echo": ["echo", "repeat", "say back"]
        }
        
        suggested_tools = []
        for tool_name, keywords in tool_keywords.items():
            if any(keyword in user_message.lower() for keyword in keywords):
                suggested_tools.append(tool_name)
        
        # Create enhanced prompt with tool information
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in self.available_tools
        ])
        
        enhanced_prompt = f"""You are an AI assistant with access to the following tools through MCP (Model Context Protocol):

{tools_info}

User message: {user_message}

If the user's request could benefit from using one of these tools, please indicate which tool should be used and what parameters should be passed. Format your tool usage as:
TOOL: tool_name
PARAMS: {{"param1": "value1", "param2": "value2"}}

Otherwise, respond normally to the user's message."""
        
        # Get Ollama response
        ollama_response = self.call_ollama(enhanced_prompt, model)
        
        # Check if Ollama suggested using a tool
        if "TOOL:" in ollama_response and "PARAMS:" in ollama_response:
            try:
                lines = ollama_response.split('\n')
                tool_line = next(line for line in lines if line.startswith("TOOL:"))
                params_line = next(line for line in lines if line.startswith("PARAMS:"))
                
                tool_name = tool_line.split("TOOL:")[1].strip()
                params_str = params_line.split("PARAMS:")[1].strip()
                params = json.loads(params_str)
                
                # Execute the tool
                tool_result = await self.mcp_client.call_tool(tool_name, params)
                
                # Get final response with tool result
                final_prompt = f"""The user asked: {user_message}

I used the {tool_name} tool and got this result: {tool_result}

Please provide a natural response to the user incorporating this information."""
                
                return self.call_ollama(final_prompt, model)
                
            except Exception as e:
                return f"{ollama_response}\n\n(Tool execution failed: {str(e)})"
        
        return ollama_response
    
    async def interactive_chat(self, model: str = "llama3.2:latest"):
        """Interactive chat session with Ollama and MCP integration"""
        
        if not await self.initialize_mcp():
            return
            
        print(f"\nEnhanced Chat with Ollama ({model}) + MCP Tools")
        print("Available MCP tools:", [tool['name'] for tool in self.available_tools])
        if self.available_models:
            print("Available Ollama models:", self.available_models)
        print("Type 'quit' to exit, 'model <name>' to change model, 'models' to list models\n")
        
        try:
            while True:
                user_input = input("You: ").strip()
                
                if user_input.lower() == "quit":
                    break
                elif user_input.lower().startswith("model "):
                    new_model = user_input[6:].strip()
                    if new_model in self.available_models or not self.available_models:
                        model = new_model
                        print(f"Switched to model: {model}")
                    else:
                        print(f"Model '{new_model}' not available. Available models: {self.available_models}")
                    continue
                elif user_input.lower() == "models":
                    if self.available_models:
                        print("Available models:", self.available_models)
                    else:
                        print("No models available or Ollama not accessible")
                    continue
                elif user_input.lower() == "tools":
                    print("Available MCP tools:")
                    for tool in self.available_tools:
                        print(f"  {tool['name']}: {tool['description']}")
                    continue
                
                if not user_input:
                    continue
                
                print("Assistant: ", end="", flush=True)
                response = await self.enhanced_chat(user_input, model)
                print(response)
                print()
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
        finally:
            await self.mcp_client.disconnect()

async def demo_ollama_integration():
    """Demonstrate Ollama + MCP integration"""
    integration = OllamaMCPIntegration()
    
    print("Testing Ollama + MCP Integration...")
    
    if not await integration.initialize_mcp():
        return
    
    test_queries = [
        "What is 15 * 24?",
        "What time is it?",
        "Echo back 'Hello from MCP!'",
        "Tell me about Python programming"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await integration.enhanced_chat(query)
        print(f"Response: {response}")
        print("-" * 50)
    
    await integration.mcp_client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        asyncio.run(OllamaMCPIntegration().interactive_chat())
    else:
        asyncio.run(demo_ollama_integration())
