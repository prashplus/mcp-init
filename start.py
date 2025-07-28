#!/usr/bin/env python3
"""
MCP Tutorial Launcher
Quick start script for different MCP demonstration modes
"""

import sys
import subprocess
import os

def print_banner():
    print("=" * 60)
    print("  MCP (Model Context Protocol) Tutorial")
    print("=" * 60)
    print()

def print_menu():
    print("Choose a demonstration mode:")
    print("1. Basic MCP Demo (server + client)")
    print("2. Interactive MCP Client")
    print("3. Ollama + MCP Integration Demo")
    print("4. Interactive Ollama Chat with MCP")
    print("5. Exit")
    print()

def run_command(cmd, cwd=None):
    """Run a command and handle errors"""
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")

def main():
    print_banner()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\nRunning basic MCP demo...")
            run_command([sys.executable, "client.py"], cwd="client")
            
        elif choice == "2":
            print("\nStarting interactive MCP client...")
            print("(Type 'help' for commands, 'quit' to exit)")
            run_command([sys.executable, "client.py", "interactive"], cwd="client")
            
        elif choice == "3":
            print("\nRunning Ollama + MCP integration demo...")
            run_command([sys.executable, "ollama_integration.py"], cwd="client")
            
        elif choice == "4":
            print("\nStarting interactive Ollama chat with MCP...")
            print("(Type 'quit' to exit, 'model <name>' to change model)")
            run_command([sys.executable, "ollama_integration.py", "chat"], cwd="client")
            
        elif choice == "5":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-5.")
        
        print()

if __name__ == "__main__":
    main()
