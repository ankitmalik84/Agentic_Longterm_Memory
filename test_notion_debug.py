#!/usr/bin/env python3
"""
Debug script to test Notion integration and find issues
"""

import requests
import json

def test_notion_debug():
    """Debug Notion integration step by step"""
    
    server_url = "https://notion-mcp-server-5s5v.onrender.com/"
    
    print("🔍 Notion Integration Debug")
    print("=" * 50)
    
    try:
        # Test 1: Search with empty query
        print("\n📋 Test 1: Search with empty query")
        search_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_notion_pages",
                "arguments": {
                    "query": "",
                    "page_size": 10
                }
            },
            "id": 1
        }
        
        response = requests.post(
            server_url,
            json=search_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            content = result.get("content", [])
            if content:
                search_result = content[0].get("text", "No text content")
                print(f"🔍 Empty search result:")
                print(f"   {search_result[:300]}...")
            else:
                print("📝 No content in result")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test 2: Search with different queries
        test_queries = ["", "page", "note", "document", "task", "project"]
        
        for query in test_queries:
            print(f"\n📋 Testing query: '{query}'")
            search_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_notion_pages",
                    "arguments": {
                        "query": query,
                        "page_size": 5
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
                result = data.get("result", {})
                content = result.get("content", [])
                if content:
                    search_result = content[0].get("text", "No text content")
                    # Count pages found
                    if "Found" in search_result:
                        pages_count = search_result.split("Found ")[1].split(" pages")[0]
                        print(f"   📄 Found {pages_count} pages")
                        if int(pages_count) > 0:
                            print(f"   ✅ SUCCESS! Found pages with query '{query}'")
                            print(f"   📝 Preview: {search_result[:200]}...")
                            break
                    else:
                        print(f"   📝 Response: {search_result[:100]}...")
                else:
                    print("   📝 No content in result")
            else:
                print(f"   ❌ Search failed: {response.status_code}")
        
        # Test 3: Test page creation (to verify write access)
        print(f"\n📋 Test 3: Test page creation")
        create_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "create_notion_page",
                "arguments": {
                    "title": "MCP Test Page",
                    "content": "This is a test page created by the MCP integration to verify it's working correctly."
                }
            },
            "id": 3
        }
        
        response = requests.post(
            server_url,
            json=create_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            content = result.get("content", [])
            if content:
                create_result = content[0].get("text", "No text content")
                print(f"🔍 Create result:")
                print(f"   {create_result}")
                
                if "Successfully created" in create_result:
                    print("   ✅ SUCCESS! Page creation works")
                    print("   📝 Your integration has write access")
                    
                    # Now try searching again
                    print("\n📋 Test 4: Search after creation")
                    search_request = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "search_notion_pages",
                            "arguments": {
                                "query": "MCP Test",
                                "page_size": 5
                            }
                        },
                        "id": 4
                    }
                    
                    response = requests.post(
                        server_url,
                        json=search_request,
                        headers={"Content-Type": "application/json"},
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        result = data.get("result", {})
                        content = result.get("content", [])
                        if content:
                            search_result = content[0].get("text", "No text content")
                            print(f"🔍 Search after creation:")
                            print(f"   {search_result[:300]}...")
                        else:
                            print("📝 Still no content found")
                else:
                    print("   ❌ Page creation failed")
                    print(f"   Error details: {create_result}")
            else:
                print("📝 No content in create result")
        else:
            print(f"❌ Create failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        print("\n🎉 Debug test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_notion_debug() 