#!/usr/bin/env python3
"""
Test script to verify the new MCP structure and environment-based configuration
"""

import os
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all imports work with the new structure"""
    print("🔧 Testing Imports...")
    print("=" * 50)
    
    try:
        # Test new structure imports
        from src.notion_mcp_server import NotionMCPServer
        print("✅ NotionMCPServer import successful")
        
        from src.utils.mcp_client_manager import MCPClientManager
        print("✅ MCPClientManager import successful")
        
        from src.utils.chatbot_agentic_v3 import Chatbot
        print("✅ Chatbot import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment_config():
    """Test environment variable configuration"""
    print("\n🔧 Testing Environment Configuration...")
    print("=" * 50)
    
    # Check required environment variables
    config = {
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
        "NOTION_MCP_SERVER_URL": os.getenv("NOTION_MCP_SERVER_URL", "https://notion-mcp-server-5s5v.onrender.com/"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
    
    for key, value in config.items():
        status = "✅" if value else "❌"
        display_value = value[:20] + "..." if value and len(value) > 20 else value or "Not set"
        print(f"   {key}: {status} {display_value}")
    
    return bool(config["NOTION_TOKEN"]) and bool(config["OPENAI_API_KEY"])

def test_mcp_client_manager():
    """Test MCP Client Manager with new configuration"""
    print("\n🔧 Testing MCP Client Manager...")
    print("=" * 50)
    
    try:
        from src.utils.mcp_client_manager import MCPClientManager
        
        # Test initialization
        client_manager = MCPClientManager()
        print("✅ MCPClientManager initialized successfully")
        print(f"   Server URL: {client_manager.notion_server_url}")
        print(f"   Token configured: {'✅' if client_manager.notion_token else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCPClientManager test failed: {e}")
        return False

async def test_server_connection():
    """Test connection to the deployed server"""
    print("\n🔧 Testing Server Connection...")
    print("=" * 50)
    
    try:
        import aiohttp
        
        server_url = os.getenv("NOTION_MCP_SERVER_URL", "https://notion-mcp-server-5s5v.onrender.com/")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(server_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Server connection successful")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Available tools: {len(data.get('available_tools', []))}")
                    return True
                else:
                    print(f"❌ Server returned status: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_file_structure():
    """Test that the new file structure exists"""
    print("\n🔧 Testing File Structure...")
    print("=" * 50)
    
    required_files = [
        "src/notion_mcp_server/__init__.py",
        "src/notion_mcp_server/server.py",
        "src/utils/mcp_client_manager.py",
        "src/utils/chatbot_agentic_v3.py",
        "docker/Dockerfile.notion-mcp",
        "config.env.example"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

async def main():
    """Run all tests"""
    print("🧪 New Structure Verification Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("File Structure", test_file_structure()))
    test_results.append(("Imports", test_imports()))
    test_results.append(("Environment Config", test_environment_config()))
    test_results.append(("MCP Client Manager", test_mcp_client_manager()))
    test_results.append(("Server Connection", await test_server_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("\n🎉 All tests passed! New structure is working correctly.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1) 