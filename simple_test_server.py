#!/usr/bin/env python3
"""
Simple test server to isolate the issue
"""
import os
import asyncio
from dotenv import load_dotenv

async def simple_server():
    """Simple test server"""
    
    print("🚀 Starting simple test server...")
    
    # Load environment
    load_dotenv()
    token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    
    print(f"🔍 Token found: {'✅ Yes' if token else '❌ No'}")
    
    if not token:
        print("❌ No token found")
        return
    
    # Test Notion connection
    try:
        from notion_client import Client
        client = Client(auth=token)
        user_info = client.users.me()
        print(f"✅ Notion API working! User: {user_info.get('name', 'N/A')}")
    except Exception as e:
        print(f"❌ Notion API failed: {e}")
        return
    
    # Test MCP import
    try:
        from mcp import ClientSession, StdioServerParameters
        print("✅ MCP imports successful")
    except ImportError as e:
        print(f"⚠️ MCP import failed: {e}")
        print("💡 This is OK - will use direct API")
    
    # Simple interactive loop
    print("\n📋 Simple test - type 'test' to search, 'quit' to exit")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                break
            elif user_input.lower() == 'test':
                print("🔍 Testing search...")
                try:
                    results = client.search(query="ai agent", page_size=5)
                    print(f"✅ Found {len(results['results'])} items")
                    for item in results['results']:
                        print(f"  - {item}")
                        print(f"    - {item['url']}")
                except Exception as e:
                    print(f"❌ Search failed: {e}")
            else:
                print("💡 Type 'test' to search or 'quit' to exit")
                
        except KeyboardInterrupt:
            break
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(simple_server())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 