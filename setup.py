#!/usr/bin/env python3
"""
Setup script for MCP Tutorial
Installs dependencies and verifies the setup
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "run_tests.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MCP Tutorial Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Setup completed but tests failed. Please check the output above.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nYou can now run:")
    print("  python start.py           # Interactive launcher")
    print("  python test_server.py     # Test basic functionality")
    print("  python run_tests.py       # Run full test suite")

if __name__ == "__main__":
    main()
