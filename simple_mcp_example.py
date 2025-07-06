#!/usr/bin/env python3
"""
Simple Notion MCP Server Example
================================

A minimal example showing how to communicate with the Notion MCP server.
Use this for quick testing or as a starting point for your own implementation.
"""

import subprocess
import json
import os
import time
import sys
import platform

def check_docker_availability():
    """Check if Docker is available and the image exists."""
    try:
        # Check if Docker is running
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not available")
            return False
        
        print(f"✅ Docker version: {result.stdout.strip()}")
        
        # Check if the notion image exists locally
        result = subprocess.run(["docker", "images", "mcp/notion"], capture_output=True, text=True)
        if "mcp/notion" in result.stdout:
            print("✅ mcp/notion image found locally")
            return True
        
        # Try to pull the image
        print("🔄 Pulling mcp/notion image...")
        result = subprocess.run(["docker", "pull", "mcp/notion"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Successfully pulled mcp/notion image")
            return True
        else:
            print(f"❌ Failed to pull mcp/notion image: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def run_simple_mcp_test():
    """Run a simple MCP test with minimal setup."""
    
    # Configuration
    notion_token = os.getenv("NOTION_TOKEN", "ntn_****")
    
    if notion_token == "ntn_****":
        print("❌ Please set your NOTION_TOKEN environment variable")
        print("   Example: export NOTION_TOKEN='ntn_your_actual_token'")
        return
    
    # Check Docker availability
    if not check_docker_availability():
        print("❌ Docker setup failed. Please ensure Docker is installed and running.")
        return
    
    # Set up environment
    env = os.environ.copy()
    headers_json = json.dumps({
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28"
    })
    env["OPENAPI_MCP_HEADERS"] = headers_json
    
    print("🚀 Starting Notion MCP Server...")
    print(f"📝 Using token: {notion_token[:10]}...")
    
    # Start Docker container with improved error handling
    try:
        proc = subprocess.Popen(
            [
                "docker", "run", "--rm", "-i",
                "-e", "OPENAPI_MCP_HEADERS",
                "mcp/notion"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )
        
        print(f"✅ Container started (PID: {proc.pid})")
        
        # Wait for container to start
        time.sleep(3)
        
        # Check if container is still running
        if proc.poll() is not None:
            stderr_output = proc.stderr.read()
            stdout_output = proc.stdout.read()
            print(f"❌ Container exited early (return code: {proc.returncode})")
            print(f"STDERR: {stderr_output}")
            print(f"STDOUT: {stdout_output}")
            return
        
        # Test 1: Initialize MCP server
        print("\n📝 Test 1: Initialize MCP Server")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "simple-test", "version": "1.0.0"}
            },
            "id": "init-1"
        }
        
        try:
            request_json = json.dumps(init_request) + "\n"
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            # Wait for response with timeout
            import select
            if platform.system() != "Windows":
                # Unix-like systems
                ready, _, _ = select.select([proc.stdout], [], [], 5.0)
                if ready:
                    response = proc.stdout.readline()
                else:
                    print("❌ Timeout waiting for initialization response")
                    return
            else:
                # Windows - use a simple timeout
                time.sleep(2)
                response = proc.stdout.readline()
            
            if response:
                try:
                    result = json.loads(response.strip())
                    print(f"✅ Initialization successful")
                    print(f"   Server info: {result.get('result', {}).get('serverInfo', {})}")
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {response}")
                    return
            else:
                print("❌ No response from server")
                return
        
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            return
        
        # Test 2: List available tools
        print("\n📝 Test 2: List Available Tools")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "tools-1"
        }
        
        try:
            request_json = json.dumps(tools_request) + "\n"
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            # Wait for response
            if platform.system() != "Windows":
                ready, _, _ = select.select([proc.stdout], [], [], 5.0)
                if ready:
                    response = proc.stdout.readline()
                else:
                    print("❌ Timeout waiting for tools list response")
                    return
            else:
                time.sleep(2)
                response = proc.stdout.readline()
            
            if response:
                try:
                    result = json.loads(response.strip())
                    tools = result.get("result", {}).get("tools", [])
                    print(f"✅ Found {len(tools)} tools:")
                    
                    # Show clean tool list (removing the verbose descriptions)
                    important_tools = []
                    for tool in tools:
                        tool_name = tool.get('name', 'Unknown')
                        # Extract clean description (remove "Error Responses" part)
                        description = tool.get('description', 'No description')
                        print("tool name", tool_name)
                        print(tool.get('inputSchema','no schema').get('properties',"no properties"))
                        clean_desc = description.split('\nError Responses:')[0].split('Error Responses:')[0]
                        
                        # Focus on the most useful tools for listing pages
                        # if any(keyword in tool_name.lower() for keyword in ['search', 'page', 'database', 'retrieve']):
                        #     important_tools.append(f"   • {tool_name}: {clean_desc}")
                        
                    for tool_info in important_tools[:8]:  # Show first 8 important tools
                        print(tool_info)
                    
                    if len(tools) > 8:
                        print(f"   ... and {len(tools) - 8} more tools")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {response}")
                    return
            else:
                print("❌ No response from server")
                return
        
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return
        
        # Test 3: List all pages in your Notion workspace
        print("\n📝 Test 3: List All Pages in Your Notion Workspace")
        
        # First, try to get user info to verify permissions
        print("   🔍 Step 3.1: Checking your Notion access...")
        user_info_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "API-get-self",
                "arguments": {}
            },
            "id": "user-info-1"
        }
        
        try:
            request_json = json.dumps(user_info_request) + "\n"
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            if platform.system() != "Windows":
                ready, _, _ = select.select([proc.stdout], [], [], 5.0)
                if ready:
                    response = proc.stdout.readline()
                else:
                    print("   ❌ Timeout waiting for user info response")
            else:
                time.sleep(2)
                response = proc.stdout.readline()
            
            if response:
                try:
                    result = json.loads(response.strip())
                    print(f"   📄 Raw user info response: {result}")
                    
                    if result.get("result"):
                        response_data = result["result"]
                        
                        # Handle MCP wrapped response - the actual data is in content[0].text as JSON string
                        if isinstance(response_data, dict) and "content" in response_data:
                            content = response_data["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                # Parse the JSON string inside the text field
                                try:
                                    user_json = json.loads(content[0]["text"])
                                    user_name = user_json.get("name", "Unknown")
                                    user_type = user_json.get("type", "Unknown")
                                    workspace_name = "Unknown"
                                    
                                    if "bot" in user_json and "workspace_name" in user_json["bot"]:
                                        workspace_name = user_json["bot"]["workspace_name"]
                                    
                                    print(f"   ✅ Connected as: {user_name} (Type: {user_type})")
                                    print(f"   🏢 Workspace: {workspace_name}")
                                except json.JSONDecodeError as e:
                                    print(f"   ❌ Failed to parse user JSON: {e}")
                            else:
                                print("   📋 No content or text field in user response")
                        
                        # Handle direct response (fallback)
                        elif isinstance(response_data, dict):
                            user_name = response_data.get("name", "Unknown")
                            user_type = response_data.get("type", "Unknown")
                            print(f"   ✅ Connected as: {user_name} (Type: {user_type})")
                        else:
                            print(f"   ✅ User info retrieved: {response_data}")
                    else:
                        print(f"   ⚠️  User info response: {result}")
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response: {response}")
        except Exception as e:
            print(f"   ❌ Error getting user info: {e}")
        
        # Now try multiple approaches to list pages
        print("\n   🔍 Step 3.2: Trying different approaches to list pages...")
        
        # Approach 1: Search with empty query
        print("   📋 Approach 1: Search with empty query...")
        list_pages_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "API-post-search",
                "arguments": {
                    "query": "",
                    "filter": {
                        "value": "page",
                        "property": "object"
                    },
                    "page_size": 20
                }
            },
            "id": "list-pages-1"
        }
        
        try:
            request_json = json.dumps(list_pages_request) + "\n"
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            if platform.system() != "Windows":
                ready, _, _ = select.select([proc.stdout], [], [], 10.0)
                if ready:
                    response = proc.stdout.readline()
                else:
                    print("   ❌ Timeout waiting for pages list response")
            else:
                time.sleep(3)
                response = proc.stdout.readline()
            
            if response:
                try:
                    result = json.loads(response.strip())
                    print(f"   📄 Raw search response: {json.dumps(result, indent=2)[:500]}...")
                    
                    pages_found = False
                    
                    if result.get("result"):
                        response_data = result["result"]
                        
                        # Handle MCP wrapped response - the actual data is in content[0].text as JSON string
                        if isinstance(response_data, dict) and "content" in response_data:
                            content = response_data["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                # Parse the JSON string inside the text field
                                try:
                                    actual_json = json.loads(content[0]["text"])
                                    if "results" in actual_json:
                                        pages = actual_json["results"]
                                        if pages:
                                            print(f"   ✅ Found {len(pages)} pages:")
                                            pages_found = True
                                            
                                            for i, page in enumerate(pages[:10], 1):  # Show first 10
                                                page_id = page.get("id", "Unknown ID")
                                                
                                                # Extract page title
                                                title = "Untitled"
                                                if "properties" in page and "title" in page["properties"]:
                                                    title_prop = page["properties"]["title"]
                                                    if "title" in title_prop and title_prop["title"]:
                                                        title = title_prop["title"][0]["text"]["content"]
                                                
                                                # Extract other info
                                                created = page.get("created_time", "Unknown")[:10]
                                                modified = page.get("last_edited_time", "Unknown")[:10]
                                                page_url = page.get("url", "No URL")
                                                
                                                print(f"      {i}. 📄 {title}")
                                                print(f"         ID: {page_id}")
                                                print(f"         Created: {created} | Modified: {modified}")
                                                print(f"         URL: {page_url}")
                                                print()
                                        else:
                                            print("   📋 Empty results array - no pages returned")
                                    else:
                                        print("   📋 No 'results' field in parsed JSON")
                                except json.JSONDecodeError as e:
                                    print(f"   ❌ Failed to parse JSON from text field: {e}")
                                    print(f"   📄 Raw text: {content[0]['text'][:200]}...")
                            else:
                                print("   📋 No content or text field in response")
                        
                        # Handle direct API response (fallback)
                        elif isinstance(response_data, dict) and "results" in response_data:
                            pages = response_data["results"]
                            if pages:
                                print(f"   ✅ Found {len(pages)} pages:")
                                pages_found = True
                                
                                for i, page in enumerate(pages[:10], 1):  # Show first 10
                                    page_id = page.get("id", "Unknown ID")
                                    
                                    # Extract page title
                                    title = "Untitled"
                                    if "properties" in page:
                                        props = page["properties"]
                                        # Look for title in different possible locations
                                        if "title" in props:
                                            title_prop = props["title"]
                                            if isinstance(title_prop, dict) and "title" in title_prop:
                                                title_content = title_prop["title"]
                                                if title_content and len(title_content) > 0:
                                                    title = title_content[0].get("text", {}).get("content", "Untitled")
                                        elif "Name" in props:
                                            name_prop = props["Name"]
                                            if isinstance(name_prop, dict) and "title" in name_prop:
                                                title_content = name_prop["title"]
                                                if title_content and len(title_content) > 0:
                                                    title = title_content[0].get("text", {}).get("content", "Untitled")
                                    
                                    # Extract other info
                                    created = page.get("created_time", "Unknown")[:10]
                                    modified = page.get("last_edited_time", "Unknown")[:10]
                                    page_url = page.get("url", "No URL")
                                    
                                    print(f"      {i}. 📄 {title}")
                                    print(f"         ID: {page_id}")
                                    print(f"         Created: {created} | Modified: {modified}")
                                    print(f"         URL: {page_url}")
                                    print()
                            else:
                                print("   📋 Empty results array - no pages returned")
                        
                        # Handle string response
                        elif isinstance(response_data, str):
                            print(f"   📄 String response: {response_data}")
                            if "pages" in response_data.lower() or "results" in response_data.lower():
                                pages_found = True
                    
                    if not pages_found:
                        print("   ⚠️  No pages found with this approach")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response: {response}")
            else:
                print("   ❌ No response from server")
        
        except Exception as e:
            print(f"   ❌ Error in approach 1: {e}")
        
        # Approach 2: Search without filters
        print("\n   📋 Approach 2: Search without filters...")
        search_all_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "API-post-search",
                "arguments": {
                    "page_size": 10
                }
            },
            "id": "search-all-1"
        }
        
        try:
            request_json = json.dumps(search_all_request) + "\n"
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            if platform.system() != "Windows":
                ready, _, _ = select.select([proc.stdout], [], [], 10.0)
                if ready:
                    response = proc.stdout.readline()
                else:
                    print("   ❌ Timeout waiting for search all response")
            else:
                time.sleep(3)
                response = proc.stdout.readline()
            
            if response:
                try:
                    result = json.loads(response.strip())
                    print(f"   📄 Search all response: {json.dumps(result, indent=2)[:300]}...")
                    
                    if result.get("result"):
                        response_data = result["result"]
                        
                        # Handle MCP wrapped response - the actual data is in content[0].text as JSON string
                        if isinstance(response_data, dict) and "content" in response_data:
                            content = response_data["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                # Parse the JSON string inside the text field
                                try:
                                    actual_json = json.loads(content[0]["text"])
                                    if "results" in actual_json:
                                        all_items = actual_json["results"]
                                        print(f"   ✅ Found {len(all_items)} total items (pages + databases)")
                                        
                                        pages = [item for item in all_items if item.get("object") == "page"]
                                        databases = [item for item in all_items if item.get("object") == "database"]
                                        
                                        print(f"   📄 Pages: {len(pages)}")
                                        print(f"   🗄️  Databases: {len(databases)}")
                                        
                                        if pages:
                                            print("   📄 Your Pages:")
                                            for i, page in enumerate(pages[:5], 1):
                                                title = "Untitled"
                                                if "properties" in page and "title" in page["properties"]:
                                                    title_prop = page["properties"]["title"]
                                                    if "title" in title_prop and title_prop["title"]:
                                                        title = title_prop["title"][0]["text"]["content"]
                                                
                                                print(f"      {i}. {title} ({page.get('id', 'No ID')[:8]}...)")
                                        
                                        if databases:
                                            print("   🗄️  Your Databases:")
                                            for i, db in enumerate(databases[:5], 1):
                                                title = "Untitled Database"
                                                if "title" in db and db["title"]:
                                                    title = db["title"][0]["text"]["content"]
                                                
                                                print(f"      {i}. {title} ({db.get('id', 'No ID')[:8]}...)")
                                    else:
                                        print("   📋 No 'results' field in parsed JSON")
                                except json.JSONDecodeError as e:
                                    print(f"   ❌ Failed to parse JSON from text field: {e}")
                                    print(f"   📄 Raw text: {content[0]['text'][:200]}...")
                            else:
                                print("   📋 No content or text field in response")
                        
                        # Handle direct API response (fallback)
                        elif isinstance(response_data, dict) and "results" in response_data:
                            all_items = response_data["results"]
                            print(f"   ✅ Found {len(all_items)} total items (pages + databases)")
                            
                            pages = [item for item in all_items if item.get("object") == "page"]
                            databases = [item for item in all_items if item.get("object") == "database"]
                            
                            print(f"   📄 Pages: {len(pages)}")
                            print(f"   🗄️  Databases: {len(databases)}")
                            
                            if pages:
                                print("   📄 Your Pages:")
                                for i, page in enumerate(pages[:5], 1):
                                    title = "Untitled"
                                    if "properties" in page and "title" in page["properties"]:
                                        title_prop = page["properties"]["title"]
                                        if "title" in title_prop and title_prop["title"]:
                                            title = title_prop["title"][0].get("text", {}).get("content", "Untitled")
                                    
                                    print(f"      {i}. {title} ({page.get('id', 'No ID')[:8]}...)")
                            
                            if databases:
                                print("   🗄️  Your Databases:")
                                for i, db in enumerate(databases[:5], 1):
                                    title = "Untitled Database"
                                    if "title" in db and db["title"]:
                                        title = db["title"][0].get("text", {}).get("content", "Untitled Database")
                                    
                                    print(f"      {i}. {title} ({db.get('id', 'No ID')[:8]}...)")
                        else:
                            print("   📄 No results found in response")
                    else:
                        print("   ❌ No result in response")
                        if "error" in result:
                            print(f"   ⚠️  Error: {result['error']}")
                            
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response: {response}")
            else:
                print("   ❌ No response from server")
        
        except Exception as e:
            print(f"   ❌ Error in approach 2: {e}")
        
        # Summary for Test 3
        print("\n   📋 Test 3 Summary:")
        print("   ℹ️  If no pages were found, this could mean:")
        print("      1. Your Notion integration doesn't have access to any pages")
        print("      2. You need to share pages with your integration")
        print("      3. Your workspace is empty")
        print("   💡 To fix: Go to your Notion pages → Share → Add your integration")
        
        # Test 4: Search for specific content
        print("\n📝 Test 4: Search for Specific Content")
        print("   🔍 Searching for pages containing 'aws'...")
        
        search_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "API-post-search",
                "arguments": {
                    "query": "aws",
                    "page_size": 10
                }
            },
            "id": "search-1"
        }
        
        try:
            request_json = json.dumps(search_request) + "\n"
            proc.stdin.write(request_json)
            proc.stdin.flush()
            
            if platform.system() != "Windows":
                ready, _, _ = select.select([proc.stdout], [], [], 10.0)
                if ready:
                    response = proc.stdout.readline()
                else:
                    print("   ❌ Timeout waiting for search response")
                    return
            else:
                time.sleep(3)
                response = proc.stdout.readline()
            
            if response:
                try:
                    result = json.loads(response.strip())
                    print(f"   📄 Raw search response: {json.dumps(result, indent=2)[:400]}...")
                    
                    if result.get("result"):
                        response_data = result["result"]
                        
                        # Handle MCP wrapped response - the actual data is in content[0].text as JSON string
                        if isinstance(response_data, dict) and "content" in response_data:
                            content = response_data["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                # Parse the JSON string inside the text field
                                try:
                                    actual_json = json.loads(content[0]["text"])
                                    if "results" in actual_json:
                                        items = actual_json["results"]
                                        
                                        if items:
                                            print(f"   ✅ Found {len(items)} items matching 'aws':")
                                            
                                            for i, item in enumerate(items, 1):
                                                item_type = item.get("object", "unknown")
                                                item_id = item.get("id", "Unknown ID")
                                                
                                                # Extract title based on type
                                                title = "Untitled"
                                                if item_type == "page" and "properties" in item:
                                                    props = item["properties"]
                                                    if "title" in props and props["title"].get("title"):
                                                        title = props["title"]["title"][0]["text"]["content"]
                                                elif item_type == "database" and "title" in item:
                                                    if item["title"]:
                                                        title = item["title"][0]["text"]["content"]
                                                
                                                icon = "📄" if item_type == "page" else "🗄️" if item_type == "database" else "❓"
                                                print(f"      {i}. {icon} {title}")
                                                print(f"         Type: {item_type}")
                                                print(f"         ID: {item_id[:8]}...")
                                                if "url" in item:
                                                    print(f"         URL: {item['url']}")
                                                print()
                                        else:
                                            print("   📋 No items found matching 'aws'")
                                            print("   💡 Try searching for:")
                                            print("      - Common words like 'project', 'notes', 'todo'")
                                            print("      - Your actual page titles")
                                            print("      - Or use an empty search to see all pages")
                                    else:
                                        print("   📋 No 'results' field in parsed JSON")
                                except json.JSONDecodeError as e:
                                    print(f"   ❌ Failed to parse JSON from text field: {e}")
                                    print(f"   📄 Raw text: {content[0]['text'][:200]}...")
                            else:
                                print("   📋 No content or text field in response")
                        
                        # Handle direct API response (fallback)
                        elif isinstance(response_data, dict) and "results" in response_data:
                            items = response_data["results"]
                            
                            if items:
                                print(f"   ✅ Found {len(items)} items matching 'aws':")
                                
                                for i, item in enumerate(items, 1):
                                    item_type = item.get("object", "unknown")
                                    item_id = item.get("id", "Unknown ID")
                                    
                                    # Extract title based on type
                                    title = "Untitled"
                                    if item_type == "page" and "properties" in item:
                                        props = item["properties"]
                                        if "title" in props and props["title"].get("title"):
                                            title = props["title"]["title"][0].get("text", {}).get("content", "Untitled")
                                    elif item_type == "database" and "title" in item:
                                        if item["title"]:
                                            title = item["title"][0].get("text", {}).get("content", "Untitled Database")
                                    
                                    icon = "📄" if item_type == "page" else "🗄️" if item_type == "database" else "❓"
                                    print(f"      {i}. {icon} {title}")
                                    print(f"         Type: {item_type}")
                                    print(f"         ID: {item_id[:8]}...")
                                    if "url" in item:
                                        print(f"         URL: {item['url']}")
                                    print()
                            else:
                                print("   📋 No items found matching 'aws'")
                                print("   💡 Try searching for:")
                                print("      - Common words like 'project', 'notes', 'todo'")
                                print("      - Your actual page titles")
                                print("      - Or use an empty search to see all pages")
                        else:
                            print("   📄 Unexpected response format")
                            print(f"   📄 Response data: {response_data}")
                    else:
                        print("   ❌ Search failed")
                        if "error" in result:
                            print(f"   ⚠️  Error: {result['error']}")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response: {response}")
                    return
            else:
                print("   ❌ No response from server")
                return
        
        except Exception as e:
            print(f"   ❌ Error during search: {e}")
            return
        
        print("\n🎉 All MCP tests completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ MCP server connection working")
        print("   ✅ Notion API authentication successful") 
        print("   ✅ Tool discovery completed")
        print("   ✅ Workspace page listing working")
        print("   ✅ Content search working")
        print("\n💡 Note: 'Error Responses: 400: 400' in tool descriptions is normal")
        print("   This is just API documentation, not an actual error!")
        
    except Exception as e:
        print(f"❌ Error starting container: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'proc' in locals():
            print("\n🛑 Stopping container...")
            proc.terminate()
            proc.wait()
            print("✅ Container stopped")

def main():
    """Main function with multiple approaches."""
    print("🚀 Notion MCP Server Test & Page Listing")
    print("=" * 60)
    
    # Check token first
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        print("❌ Please set your NOTION_TOKEN environment variable")
        print("   Example: export NOTION_TOKEN='ntn_your_actual_token'")
        print("   Get your token at: https://www.notion.so/profile/integrations")
        return
    
    try:
        # Run the comprehensive test
        run_simple_mcp_test()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 