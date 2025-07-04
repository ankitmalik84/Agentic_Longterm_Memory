#!/usr/bin/env python3
"""
Test script for HTTP MCP Notion server deployed on Render
"""

import asyncio
import aiohttp
import json

async def test_http_mcp_server():
    """Test the deployed HTTP MCP server"""
    
    server_url = "https://notion-mcp-server-5s5v.onrender.com/"
    
    print("🧪 Testing HTTP MCP Server")
    print("=" * 50)
    print(f"🌐 Server URL: {server_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Test 1: Health Check
            print("\n📋 Test 1: Health Check")
            async with session.get(server_url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Server is running")
                    print(f"📝 Status: {data.get('status')}")
                    print(f"🔧 Transport: {data.get('transport')}")
                    print(f"🛠️ Available tools: {', '.join(data.get('available_tools', []))}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
            
            # Test 2: List Tools
            print("\n📋 Test 2: List Tools")
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }
            
            async with session.post(
                server_url,
                json=tools_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Tools list retrieved successfully")
                    tools = data.get("result", {}).get("tools", [])
                    print(f"📊 Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  • {tool.get('name')}: {tool.get('description')}")
                else:
                    print(f"❌ Tools list failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False
            
            # Test 3: Search Notion Pages
            print("\n📋 Test 3: Search Notion Pages")
            search_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_notion_pages",
                    "arguments": {
                        "query": "test",
                        "page_size": 3
                    }
                },
                "id": 2
            }
            
            async with session.post(
                server_url,
                json=search_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Search tool called successfully")
                    result = data.get("result", {})
                    content = result.get("content", [])
                    if content:
                        search_result = content[0].get("text", "No text content")
                        print(f"🔍 Search result preview:")
                        print(f"   {search_result[:200]}..." if len(search_result) > 200 else f"   {search_result}")
                    else:
                        print("📝 No content in result")
                        print(f"Raw result: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Search failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
            
            print("\n🎉 All HTTP MCP tests completed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 HTTP MCP Server Test Suite")
    print("=" * 60)
    
    try:
        # Test the deployed server
        result = asyncio.run(test_http_mcp_server())
        
        print("\n" + "=" * 60)
        if result:
            print("🎉 HTTP MCP server is working perfectly!")
            print("🚀 Ready for integration with your chatbot!")
        else:
            print("❌ HTTP MCP server has issues")
            
        return 0 if result else 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 