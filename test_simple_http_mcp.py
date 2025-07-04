#!/usr/bin/env python3
"""
Simple test script for HTTP MCP Notion server using requests library
"""

import requests
import json

def test_http_mcp_server():
    """Test the deployed HTTP MCP server"""
    
    server_url = "https://notion-mcp-server-5s5v.onrender.com/"
    
    print("🧪 Testing HTTP MCP Server (Simple Version)")
    print("=" * 50)
    print(f"🌐 Server URL: {server_url}")
    
    try:
        # Test 1: Health Check
        print("\n📋 Test 1: Health Check")
        response = requests.get(server_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running")
            print(f"📝 Status: {data.get('status')}")
            print(f"🔧 Transport: {data.get('transport')}")
            print(f"🛠️ Available tools: {', '.join(data.get('available_tools', []))}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: List Tools
        print("\n📋 Test 2: List Tools")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        
        response = requests.post(
            server_url,
            json=tools_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Tools list retrieved successfully")
            tools = data.get("result", {}).get("tools", [])
            print(f"📊 Found {len(tools)} tools:")
            for tool in tools:
                print(f"  • {tool.get('name')}: {tool.get('description')}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"Error: {response.text}")
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
        
        response = requests.post(
            server_url,
            json=search_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
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
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        print("\n🎉 All HTTP MCP tests completed!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 HTTP MCP Server Test Suite (Simple)")
    print("=" * 60)
    
    try:
        # Test the deployed server
        result = test_http_mcp_server()
        
        print("\n" + "=" * 60)
        if result:
            print("🎉 HTTP MCP server is working perfectly!")
            print("🚀 Your deployed server is ready!")
            print("\n📝 Next steps:")
            print("  1. Install aiohttp: pip install aiohttp")
            print("  2. Run the full integration test: python test_notion_mcp.py")
            print("  3. Try your chatbot with Notion integration!")
        else:
            print("❌ HTTP MCP server has issues")
            
        return 0 if result else 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 