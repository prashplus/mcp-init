# MCP (Model Context Protocol) Tutorial

[![CI Tests](https://github.com/prashplus/mcp-init/actions/workflows/test.yml/badge.svg)](https://github.com/prashplus/mcp-init/actions/workflows/test.yml)

A comprehensive tutorial for implementing Model Context Protocol (MCP) servers and clients in Python, with Ollama integration for enhanced AI interactions.

## Overview

This project demonstrates how to build MCP servers and clients from scratch in Python. MCP is a protocol that allows AI assistants to securely connect to data sources and tools, enabling more powerful and contextual interactions.

## Features

- **MCP Server**: A fully functional MCP server with tools, resources, and prompts
- **MCP Client**: A client that can connect to and interact with MCP servers
- **Ollama Integration**: Enhanced chat experience using Ollama with MCP tool support
- **Interactive Mode**: Command-line interface for testing MCP functionality

## Project Structure

```
mcp-init/
├── README.md                  # This documentation
├── requirements.txt           # Python dependencies
├── setup.py                  # Setup script for easy installation
├── run_tests.py              # Comprehensive test suite
├── config.json               # Configuration example
├── start.py                  # Python launcher script
├── start.ps1                 # PowerShell launcher script
├── test_server.py            # Simple server test script
├── .gitignore                # Git ignore file
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions CI workflow
├── server/
│   └── server.py             # MCP Server implementation
└── client/
    ├── client.py             # MCP Client implementation
    ├── ollama_integration.py # Ollama + MCP integration
    └── quick_test.py         # Quick integration test
```

### File Descriptions

- **`server/server.py`**: Complete MCP server implementation with tools, resources, and prompts
- **`client/client.py`**: MCP client with demo and interactive modes
- **`client/ollama_integration.py`**: Integration layer between Ollama and MCP
- **`client/quick_test.py`**: Quick test script for Ollama + MCP integration
- **`start.py`**: User-friendly launcher for all demonstration modes
- **`test_server.py`**: Simple script to verify server functionality
- **`config.json`**: Example configuration for MCP setup

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running locally (for AI integration)
   - Install from: https://ollama.ai/
   - Pull a model: `ollama pull llama3.2` or `ollama pull deepseek-r1:8b`
   - Start Ollama: `ollama serve` (if not running as a service)

> **Note**: The integration automatically detects available models and uses the best one available. Models like `deepseek-r1:8b` show reasoning steps, while `llama3.2` provides direct responses.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/prashplus/mcp-init.git
cd mcp-init
```

2. Install Python dependencies:
```bash
# Option 1: Use the setup script (recommended)
python setup.py

# Option 2: Manual installation
pip install -r requirements.txt
```

3. Verify installation:
```bash
python run_tests.py
```

4. (Optional) Verify Ollama is running for AI integration:
```bash
# Check if Ollama is accessible
curl http://localhost:11434/api/tags

# Or on Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
```

## Quick Start

The fastest way to get started is using the launcher script:

```bash
# Python launcher (cross-platform)
python start.py

# Or PowerShell launcher (Windows)
.\start.ps1
```

This will show you a menu with all available demonstration modes.

## Usage

### 1. Basic MCP Server & Client Demo

Run the basic demo to see MCP in action:

```bash
cd client
python client.py
```

This will:
- Start the MCP server
- Connect the client to the server
- Demonstrate tools (echo, calculator, time)
- Show resources (greeting, system info)
- Display available prompts

### 2. Interactive MCP Client

For hands-on testing:

```bash
cd client
python client.py interactive
```

Available commands:
- `tools` - List available tools
- `echo <message>` - Test echo tool
- `calc <expression>` - Test calculator (e.g., `calc 10 + 5 * 2`)
- `time` - Get current time
- `resources` - List available resources
- `greeting` - Read greeting resource
- `sysinfo` - Read system information
- `prompts` - List available prompts
- `quit` - Exit

### 3. Ollama + MCP Integration

#### Demo Mode
Test the integration with predefined queries:

```bash
cd client
python ollama_integration.py
```

#### Interactive Chat Mode
Chat with Ollama enhanced by MCP tools:

```bash
cd client
python ollama_integration.py chat
```

#### Quick Test
Run a quick verification of the integration:

```bash
cd client
python quick_test.py
```

Try these example queries:
- "What is 25 * 47?" (uses calculator tool)
- "What time is it?" (uses time tool)
- "Echo back 'Hello World!'" (uses echo tool)
- "Tell me about machine learning" (regular AI response)

Commands in chat mode:
- `model <name>` - Switch Ollama model (e.g., `model llama3.2:latest`)
- `models` - List all available models
- `tools` - List available MCP tools
- `quit` - Exit chat

> **Model Tips**: 
> - `llama3.2:latest` - Fast, direct responses
> - `deepseek-r1:8b` - Shows reasoning process (good for learning)
> - `codellama:7b` - Specialized for coding tasks

## MCP Server Capabilities

### Tools
1. **echo** - Echo back input messages
2. **calculate** - Perform mathematical calculations
3. **get_time** - Get current date and time

### Resources
1. **greeting** - A simple greeting message
2. **system_info** - Basic system information (platform, Python version, etc.)

### Prompts
1. **helpful_assistant** - A customizable helpful assistant prompt

## How It Works

### MCP Protocol Flow

1. **Initialization**: Client connects to server and exchanges capabilities
2. **Discovery**: Client lists available tools, resources, and prompts
3. **Interaction**: Client calls tools, reads resources, or gets prompts
4. **Transport**: Communication happens over JSON-RPC via stdio

### Ollama Integration Flow

1. User sends a message to the enhanced chat
2. System analyzes if MCP tools could help
3. Ollama determines which tool to use and with what parameters
4. MCP client executes the tool
5. Ollama incorporates tool results into the final response

## Extending the Server

To add new tools, modify `server/server.py`:

```python
# In setup_tools method, add:
"new_tool": {
    "name": "new_tool",
    "description": "Description of what this tool does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
}

# In handle_tool_call method, add:
elif tool_name == "new_tool":
    param1 = arguments.get("param1", "")
    result = f"Tool result: {param1}"
```

## Configuration

### Ollama Settings
- Default URL: `http://localhost:11434`
- Auto-detected models from your Ollama installation
- Default model: First available model (usually `llama3.2:latest` or `deepseek-r1:8b`)
- Timeout: 30 seconds

### MCP Transport
- Uses stdio (stdin/stdout) for communication
- JSON-RPC 2.0 protocol
- Supports async operations

## Troubleshooting

### Common Issues

1. **"Failed to connect to MCP server"**
   - Ensure Python can execute `server/server.py`
   - Check that the server script has no syntax errors

2. **"Error calling Ollama"**
   - Verify Ollama is running: `ollama serve`
   - Check if models are available: `ollama list`
   - Pull a model if needed: `ollama pull llama3.2`
   - Test connection: `curl http://localhost:11434/api/tags`

3. **Tool execution errors**
   - Check tool parameters match the expected schema
   - Verify the server is properly handling the tool call

### Debug Mode

Enable logging for more details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly (CI will run automatically)
5. Submit a pull request

### Continuous Integration

This repository includes a GitHub Actions CI workflow that:
- Tests on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Runs on Ubuntu, Windows, and macOS
- Performs syntax checks and linting
- Tests basic MCP server functionality
- Validates all Python scripts compile correctly

The CI runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`

## License

This project is provided as-is for educational purposes. Feel free to modify and distribute.

## Learn More

- [Model Context Protocol Specification](https://modelcontextprotocol.io/introduction)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)


## Authors

* **Prashant Piprotar** - - [Prash+](https://github.com/prashplus)

Visit my blog for more Tech Stuff
### http://prashplus.blogspot.com
