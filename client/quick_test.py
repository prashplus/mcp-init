#!/usr/bin/env python3
"""
Quick test script for Ollama + MCP integration
"""

import requests
import asyncio
import sys
import os

# Add the client directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ollama_integration import OllamaMCPIntegration

async def quick_test():
    """Quick test of Ollama + MCP integration"""
    print("🔍 Quick Test: Ollama + MCP Integration")
    print("=" * 50)
    
    # Test Ollama connection first
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model["name"] for model in response.json().get("models", [])]
            print(f"✅ Ollama is running with models: {models}")
        else:
            print(f"❌ Ollama connection failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return
    
    # Test MCP + Ollama integration
    integration = OllamaMCPIntegration()
    
    if await integration.initialize_mcp():
        print("\n🧮 Testing calculation with AI assistance...")
        response = await integration.enhanced_chat("What is 25 times 8?")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        
        print("\n⏰ Testing time query...")
        response = await integration.enhanced_chat("What time is it?")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        
        await integration.mcp_client.disconnect()
        print("\n✅ All tests completed successfully!")
    else:
        print("❌ Failed to initialize MCP connection")

if __name__ == "__main__":
    asyncio.run(quick_test())
