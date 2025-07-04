import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
import threading

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from mcp.server.stdio import stdio_server
from notion_client import Client
from notion_client.errors import APIResponseError


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP requests"""
    
    def __init__(self, mcp_server, *args, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "running",
            "server": "notion-mcp-server",
            "transport": "http",
            "available_tools": [
                "search_notion_pages",
                "get_notion_page", 
                "create_notion_page",
                "get_notion_database"
            ]
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_POST(self):
        """Handle POST requests (MCP JSON-RPC)"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Handle MCP JSON-RPC request
            response = self.handle_mcp_request(request_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "error": str(e),
                "message": "Failed to process MCP request"
            }
            
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_mcp_request(self, request_data):
        """Handle MCP JSON-RPC request"""
        method = request_data.get("method", "")
        params = request_data.get("params", {})
        request_id = request_data.get("id", 1)
        
        if method == "tools/list":
            tools = [
                {
                    "name": "search_notion_pages",
                    "description": "Search for pages in Notion workspace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query text"},
                            "page_size": {"type": "integer", "description": "Number of results", "default": 10}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_notion_page",
                    "description": "Get detailed content of a specific Notion page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Notion page ID"}
                        },
                        "required": ["page_id"]
                    }
                },
                {
                    "name": "create_notion_page",
                    "description": "Create a new page in Notion",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Page title"},
                            "content": {"type": "string", "description": "Page content"},
                            "parent_id": {"type": "string", "description": "Parent page ID (optional)"}
                        },
                        "required": ["title", "content"]
                    }
                },
                {
                    "name": "get_notion_database",
                    "description": "Query a Notion database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "database_id": {"type": "string", "description": "Database ID"},
                            "filter_property": {"type": "string", "description": "Property to filter by"},
                            "filter_value": {"type": "string", "description": "Value to filter by"}
                        },
                        "required": ["database_id"]
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            # Execute the tool
            result = self.execute_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": result}]}
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
    
    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result"""
        try:
            if tool_name == "search_notion_pages":
                return self.search_notion_pages(arguments)
            elif tool_name == "get_notion_page":
                return self.get_notion_page(arguments)
            elif tool_name == "create_notion_page":
                return self.create_notion_page(arguments)
            elif tool_name == "get_notion_database":
                return self.get_notion_database(arguments)
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def search_notion_pages(self, arguments: dict) -> str:
        """Search for pages in Notion"""
        query = arguments.get("query", "")
        page_size = arguments.get("page_size", 10)
        
        try:
            results = self.mcp_server.notion.search(
                query=query,
                page_size=page_size,
                filter={"property": "object", "value": "page"}
            )
            
            pages = []
            for page in results["results"]:
                page_info = {
                    "id": page["id"],
                    "title": self.mcp_server._extract_title(page),
                    "url": page["url"],
                    "last_edited": page["last_edited_time"],
                    "created": page["created_time"]
                }
                pages.append(page_info)
            
            return f"Found {len(pages)} pages:\n\n" + \
                   "\n".join([f"• {p['title']} (ID: {p['id']})" for p in pages]) + \
                   f"\n\nDetailed results:\n{json.dumps(pages, indent=2)}"
            
        except APIResponseError as e:
            return f"Notion API error: {str(e)}"
    
    def get_notion_page(self, arguments: dict) -> str:
        """Get detailed content of a specific page"""
        page_id = arguments.get("page_id", "")
        
        try:
            page = self.mcp_server.notion.pages.retrieve(page_id)
            blocks = self.mcp_server.notion.blocks.children.list(page_id)
            content = self.mcp_server._extract_page_content(blocks["results"])
            
            page_info = {
                "id": page["id"],
                "title": self.mcp_server._extract_title(page),
                "url": page["url"],
                "content": content,
                "last_edited": page["last_edited_time"],
                "created": page["created_time"]
            }
            
            return f"Page: {page_info['title']}\n\n{page_info['content']}\n\nMetadata:\n{json.dumps({k: v for k, v in page_info.items() if k != 'content'}, indent=2)}"
            
        except APIResponseError as e:
            return f"Notion API error: {str(e)}"
    
    def create_notion_page(self, arguments: dict) -> str:
        """Create a new page in Notion"""
        title = arguments.get("title", "")
        content = arguments.get("content", "")
        parent_id = arguments.get("parent_id")
        
        try:
            page_properties = {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
            
            # Set parent - use provided parent_id or find a suitable default
            create_params = {
                "properties": page_properties
            }
            
            if parent_id:
                create_params["parent"] = {"page_id": parent_id}
            else:
                # Production-ready approach: Try multiple strategies
                default_parent = self._get_default_parent()
                if default_parent:
                    create_params["parent"] = {"page_id": default_parent}
                    print(f"📄 Using default parent: {default_parent}")
                else:
                    # If no suitable parent found, this will fail with a clear error
                    return "Error: No suitable parent page found. Please specify a parent_id or configure NOTION_DEFAULT_PARENT_ID environment variable."
            
            new_page = self.mcp_server.notion.pages.create(**create_params)
            
            if content:
                self.mcp_server.notion.blocks.children.append(
                    new_page["id"],
                    children=[{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": content}}]
                        }
                    }]
                )
            
            return f"Successfully created page: {title}\nPage ID: {new_page['id']}\nURL: {new_page['url']}\nParent: {'Custom' if parent_id else 'Auto-discovered'}"
            
        except APIResponseError as e:
            return f"Notion API error: {str(e)}"
    
    def _get_default_parent(self) -> Optional[str]:
        """Get default parent page ID using production-ready strategies"""
        
        # Strategy 1: Environment variable (user-configured)
        env_parent = os.getenv("NOTION_DEFAULT_PARENT_ID")
        if env_parent:
            try:
                # Verify the page exists and is accessible
                page = self.mcp_server.notion.pages.retrieve(env_parent)
                print(f"✅ Using configured parent from NOTION_DEFAULT_PARENT_ID")
                return env_parent
            except APIResponseError:
                print(f"⚠️ Configured parent page {env_parent} not accessible")
        
        # Strategy 2: Look for a page with specific title pattern
        default_titles = [
            "AWS Interview",           # Dedicated parent for MCP-created pages
            "AI Assistant Pages",  # Alternative title
            "AWS GenAI",   # Another alternative
            "Notes"               # Common workspace structure
        ]
        
        for title in default_titles:
            try:
                # Search for pages with these titles
                results = self.mcp_server.notion.search(
                    query=title,
                    filter={"property": "object", "value": "page"}
                )
                
                for page in results.get("results", []):
                    page_title = self.mcp_server._extract_title(page)
                    if page_title.lower() == title.lower():
                        print(f"✅ Found suitable parent page: {page_title}")
                        return page["id"]
                        
            except APIResponseError:
                continue
        
        # Strategy 3: Find any accessible page (last resort)
        try:
            results = self.mcp_server.notion.search(
                query="",
                page_size=5,
                filter={"property": "object", "value": "page"}
            )
            
            if results.get("results"):
                first_page = results["results"][0]
                page_title = self.mcp_server._extract_title(first_page)
                print(f"⚠️ Using first available page as parent: {page_title}")
                return first_page["id"]
                
        except APIResponseError:
            pass
        
        # Strategy 4: Auto-create a dedicated parent page (if we have permissions)
        try:
            return self._create_default_parent()
        except APIResponseError:
            pass
            
        print("❌ No suitable parent page found")
        return None
    
    def _create_default_parent(self) -> Optional[str]:
        """Attempt to create a dedicated parent page for MCP operations"""
        try:
            # Try to create a dedicated parent page
            # This will only work if the integration has appropriate permissions
            parent_page = self.mcp_server.notion.pages.create(
                properties={
                    "title": {
                        "title": [{"text": {"content": "MCP Generated Pages"}}]
                    }
                }
                # Note: No parent specified - will try workspace root
            )
            
            # Add description content
            self.mcp_server.notion.blocks.children.append(
                parent_page["id"],
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": "This page contains pages created by the MCP (Model Context Protocol) integration. Pages created via AI assistant will appear as sub-pages here."}}]
                    }
                }]
            )
            
            print(f"✅ Created dedicated parent page: MCP Generated Pages")
            return parent_page["id"]
            
        except APIResponseError as e:
            print(f"⚠️ Could not create default parent page: {str(e)}")
            return None
    
    def get_notion_database(self, arguments: dict) -> str:
        """Query a Notion database"""
        database_id = arguments.get("database_id", "")
        filter_property = arguments.get("filter_property")
        filter_value = arguments.get("filter_value")
        
        try:
            query_filter = {}
            if filter_property and filter_value:
                query_filter = {
                    "property": filter_property,
                    "rich_text": {"contains": filter_value}
                }
            
            results = self.mcp_server.notion.databases.query(
                database_id=database_id,
                filter=query_filter if query_filter else None
            )
            
            entries = []
            for entry in results["results"]:
                entry_info = {
                    "id": entry["id"],
                    "properties": self.mcp_server._extract_properties(entry["properties"]),
                    "url": entry["url"],
                    "last_edited": entry["last_edited_time"]
                }
                entries.append(entry_info)
            
            return f"Found {len(entries)} database entries:\n\n{json.dumps(entries, indent=2)}"
            
        except APIResponseError as e:
            return f"Notion API error: {str(e)}"


class NotionMCPServer:
    """MCP Server for Notion integration"""
    
    def __init__(self, notion_token: str):
        self.notion = Client(auth=notion_token)
        self.server = Server("notion-mcp-server")
        self.setup_tools()
    
    def setup_tools(self):
        """Setup MCP tools for Notion operations"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="search_notion_pages",
                    description="Search for pages in Notion workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query text"
                            },
                            "page_size": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_notion_page",
                    description="Get detailed content of a specific Notion page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {
                                "type": "string",
                                "description": "Notion page ID"
                            }
                        },
                        "required": ["page_id"]
                    }
                ),
                Tool(
                    name="create_notion_page",
                    description="Create a new page in Notion",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Page title"
                            },
                            "content": {
                                "type": "string",
                                "description": "Page content in plain text"
                            },
                            "parent_id": {
                                "type": "string",
                                "description": "Parent page ID (optional)"
                            }
                        },
                        "required": ["title", "content"]
                    }
                ),
                Tool(
                    name="get_notion_database",
                    description="Query a Notion database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_id": {
                                "type": "string",
                                "description": "Database ID"
                            },
                            "filter_property": {
                                "type": "string",
                                "description": "Property to filter by (optional)"
                            },
                            "filter_value": {
                                "type": "string",
                                "description": "Value to filter by (optional)"
                            }
                        },
                        "required": ["database_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            try:
                if name == "search_notion_pages":
                    return await self.search_pages(arguments)
                elif name == "get_notion_page":
                    return await self.get_page(arguments)
                elif name == "create_notion_page":
                    return await self.create_page(arguments)
                elif name == "get_notion_database":
                    return await self.get_database(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def search_pages(self, arguments: dict) -> List[TextContent]:
        """Search for pages in Notion"""
        query = arguments.get("query", "")
        page_size = arguments.get("page_size", 10)
        
        try:
            results = self.notion.search(
                query=query,
                page_size=page_size,
                filter={"property": "object", "value": "page"}
            )
            
            pages = []
            for page in results["results"]:
                page_info = {
                    "id": page["id"],
                    "title": self._extract_title(page),
                    "url": page["url"],
                    "last_edited": page["last_edited_time"],
                    "created": page["created_time"]
                }
                pages.append(page_info)
            
            return [TextContent(
                type="text",
                text=f"Found {len(pages)} pages:\n\n" + 
                     "\n".join([f"• {p['title']} (ID: {p['id']})" for p in pages]) +
                     f"\n\nDetailed results:\n{json.dumps(pages, indent=2)}"
            )]
            
        except APIResponseError as e:
            return [TextContent(
                type="text",
                text=f"Notion API error: {str(e)}"
            )]
    
    async def get_page(self, arguments: dict) -> List[TextContent]:
        """Get detailed content of a specific page"""
        page_id = arguments.get("page_id", "")
        
        try:
            # Get page metadata
            page = self.notion.pages.retrieve(page_id)
            
            # Get page content (blocks)
            blocks = self.notion.blocks.children.list(page_id)
            
            content = self._extract_page_content(blocks["results"])
            
            page_info = {
                "id": page["id"],
                "title": self._extract_title(page),
                "url": page["url"],
                "content": content,
                "last_edited": page["last_edited_time"],
                "created": page["created_time"]
            }
            
            return [TextContent(
                type="text",
                text=f"Page: {page_info['title']}\n\n{page_info['content']}\n\nMetadata:\n{json.dumps({k: v for k, v in page_info.items() if k != 'content'}, indent=2)}"
            )]
            
        except APIResponseError as e:
            return [TextContent(
                type="text",
                text=f"Notion API error: {str(e)}"
            )]
    
    async def create_page(self, arguments: dict) -> List[TextContent]:
        """Create a new page in Notion"""
        title = arguments.get("title", "")
        content = arguments.get("content", "")
        parent_id = arguments.get("parent_id")
        
        try:
            # Prepare page properties
            page_properties = {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
            
            # Set parent - use provided parent_id or find a suitable default
            create_params = {
                "properties": page_properties
            }
            
            if parent_id:
                create_params["parent"] = {"page_id": parent_id}
            else:
                # Production-ready approach: Try multiple strategies
                default_parent = self._get_default_parent()
                if default_parent:
                    create_params["parent"] = {"page_id": default_parent}
                    print(f"📄 Using default parent: {default_parent}")
                else:
                    # If no suitable parent found, return clear error
                    return [TextContent(
                        type="text",
                        text="Error: No suitable parent page found. Please specify a parent_id or configure NOTION_DEFAULT_PARENT_ID environment variable."
                    )]
            
            # Create the page
            new_page = self.notion.pages.create(**create_params)
            
            # Add content to the page
            if content:
                self.notion.blocks.children.append(
                    new_page["id"],
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"text": {"content": content}}]
                            }
                        }
                    ]
                )
            
            return [TextContent(
                type="text",
                text=f"Successfully created page: {title}\nPage ID: {new_page['id']}\nURL: {new_page['url']}\nParent: {'Custom' if parent_id else 'Auto-discovered'}"
            )]
            
        except APIResponseError as e:
            return [TextContent(
                type="text",
                text=f"Notion API error: {str(e)}"
            )]
    
    async def get_database(self, arguments: dict) -> List[TextContent]:
        """Query a Notion database"""
        database_id = arguments.get("database_id", "")
        filter_property = arguments.get("filter_property")
        filter_value = arguments.get("filter_value")
        
        try:
            # Build query filter
            query_filter = {}
            if filter_property and filter_value:
                query_filter = {
                    "property": filter_property,
                    "rich_text": {"contains": filter_value}
                }
            
            # Query the database
            results = self.notion.databases.query(
                database_id=database_id,
                filter=query_filter if query_filter else None
            )
            
            entries = []
            for entry in results["results"]:
                entry_info = {
                    "id": entry["id"],
                    "properties": self._extract_properties(entry["properties"]),
                    "url": entry["url"],
                    "last_edited": entry["last_edited_time"]
                }
                entries.append(entry_info)
            
            return [TextContent(
                type="text",
                text=f"Found {len(entries)} database entries:\n\n{json.dumps(entries, indent=2)}"
            )]
            
        except APIResponseError as e:
            return [TextContent(
                type="text",
                text=f"Notion API error: {str(e)}"
            )]
    
    def _extract_title(self, page: dict) -> str:
        """Extract title from page properties"""
        properties = page.get("properties", {})
        
        # Look for title property
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    return title_list[0].get("text", {}).get("content", "Untitled")
        
        return "Untitled"
    
    def _extract_page_content(self, blocks: List[dict]) -> str:
        """Extract text content from page blocks"""
        content = []
        
        for block in blocks:
            block_type = block.get("type", "")
            
            if block_type == "paragraph":
                text = self._extract_rich_text(block["paragraph"]["rich_text"])
                if text:
                    content.append(text)
            elif block_type == "heading_1":
                text = self._extract_rich_text(block["heading_1"]["rich_text"])
                if text:
                    content.append(f"# {text}")
            elif block_type == "heading_2":
                text = self._extract_rich_text(block["heading_2"]["rich_text"])
                if text:
                    content.append(f"## {text}")
            elif block_type == "heading_3":
                text = self._extract_rich_text(block["heading_3"]["rich_text"])
                if text:
                    content.append(f"### {text}")
            elif block_type == "bulleted_list_item":
                text = self._extract_rich_text(block["bulleted_list_item"]["rich_text"])
                if text:
                    content.append(f"• {text}")
            elif block_type == "numbered_list_item":
                text = self._extract_rich_text(block["numbered_list_item"]["rich_text"])
                if text:
                    content.append(f"1. {text}")
        
        return "\n\n".join(content)
    
    def _extract_rich_text(self, rich_text: List[dict]) -> str:
        """Extract plain text from rich text array"""
        return "".join([item.get("text", {}).get("content", "") for item in rich_text])
    
    def _extract_properties(self, properties: dict) -> dict:
        """Extract properties from database entry"""
        extracted = {}
        
        for prop_name, prop_value in properties.items():
            prop_type = prop_value.get("type", "")
            
            if prop_type == "title":
                extracted[prop_name] = self._extract_rich_text(prop_value["title"])
            elif prop_type == "rich_text":
                extracted[prop_name] = self._extract_rich_text(prop_value["rich_text"])
            elif prop_type == "select":
                select_value = prop_value.get("select")
                extracted[prop_name] = select_value["name"] if select_value else None
            elif prop_type == "multi_select":
                multi_select = prop_value.get("multi_select", [])
                extracted[prop_name] = [item["name"] for item in multi_select]
            elif prop_type == "date":
                date_value = prop_value.get("date")
                extracted[prop_name] = date_value["start"] if date_value else None
            elif prop_type == "number":
                extracted[prop_name] = prop_value.get("number")
            elif prop_type == "checkbox":
                extracted[prop_name] = prop_value.get("checkbox")
            else:
                extracted[prop_name] = str(prop_value)
        
        return extracted
    
    def _get_default_parent(self) -> Optional[str]:
        """Get default parent page ID using production-ready strategies"""
        
        # Strategy 1: Environment variable (user-configured)
        env_parent = os.getenv("NOTION_DEFAULT_PARENT_ID")
        if env_parent:
            try:
                # Verify the page exists and is accessible
                page = self.notion.pages.retrieve(env_parent)
                print(f"✅ Using configured parent from NOTION_DEFAULT_PARENT_ID")
                return env_parent
            except APIResponseError:
                print(f"⚠️ Configured parent page {env_parent} not accessible")
        
        # Strategy 2: Look for a page with specific title pattern
        default_titles = [
            "AWS Interview",           # Dedicated parent for MCP-created pages
            "AI Assistant Pages",  # Alternative title
            "AWS GenAI",   # Another alternative
            "Notes"               # Common workspace structure
        ]
        
        for title in default_titles:
            try:
                # Search for pages with these titles
                results = self.notion.search(
                    query=title,
                    filter={"property": "object", "value": "page"}
                )
                
                for page in results.get("results", []):
                    page_title = self._extract_title(page)
                    if page_title.lower() == title.lower():
                        print(f"✅ Found suitable parent page: {page_title}")
                        return page["id"]
                        
            except APIResponseError:
                continue
        
        # Strategy 3: Find any accessible page (last resort)
        try:
            results = self.notion.search(
                query="",
                page_size=5,
                filter={"property": "object", "value": "page"}
            )
            
            if results.get("results"):
                first_page = results["results"][0]
                page_title = self._extract_title(first_page)
                print(f"⚠️ Using first available page as parent: {page_title}")
                return first_page["id"]
                
        except APIResponseError:
            pass
        
        # Strategy 4: Auto-create a dedicated parent page (if we have permissions)
        try:
            return self._create_default_parent()
        except APIResponseError:
            pass
            
        print("❌ No suitable parent page found")
        return None
    
    def _create_default_parent(self) -> Optional[str]:
        """Attempt to create a dedicated parent page for MCP operations"""
        try:
            # Try to create a dedicated parent page
            # This will only work if the integration has appropriate permissions
            parent_page = self.notion.pages.create(
                properties={
                    "title": {
                        "title": [{"text": {"content": "MCP Generated Pages"}}]
                    }
                }
                # Note: No parent specified - will try workspace root
            )
            
            # Add description content
            self.notion.blocks.children.append(
                parent_page["id"],
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": "This page contains pages created by the MCP (Model Context Protocol) integration. Pages created via AI assistant will appear as sub-pages here."}}]
                    }
                }]
            )
            
            print(f"✅ Created dedicated parent page: MCP Generated Pages")
            return parent_page["id"]
            
        except APIResponseError as e:
            print(f"⚠️ Could not create default parent page: {str(e)}")
            return None
    
    def run(self, transport: str = "http", host: str = "0.0.0.0", port: int = 8080):
        """Run the MCP server with specified transport"""
        if transport == "stdio":
            stdio_server(self.server)
        elif transport == "http":
            # Create HTTP server
            def handler(*args, **kwargs):
                return MCPHTTPHandler(self, *args, **kwargs)
            
            httpd = HTTPServer((host, port), handler)
            print(f"🚀 Notion MCP Server running on http://{host}:{port}")
            print(f"📝 Available tools: search_notion_pages, get_notion_page, create_notion_page, get_notion_database")
            print(f"🔗 Health check: http://{host}:{port}/")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n⏹️  Server stopped")
                httpd.server_close()
        else:
            raise ValueError(f"Unsupported transport: {transport}")


# Main entry point for running the server
if __name__ == "__main__":
    notion_token = os.getenv("NOTION_TOKEN", "")
    if not notion_token:
        print("❌ NOTION_TOKEN environment variable is required")
        exit(1)
    
    transport = os.getenv("MCP_TRANSPORT", "http")  # Default to HTTP for web deployment
    host = os.getenv("MCP_HOST", "0.0.0.0")
    # Use PORT environment variable for Render compatibility, fallback to MCP_PORT or 8080
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8080")))
    
    print(f"🚀 Starting Notion MCP Server...")
    print(f"📡 Transport: {transport}")
    print(f"🌐 Host: {host}")
    print(f"🔢 Port: {port}")
    
    server = NotionMCPServer(notion_token)
    server.run(transport=transport, host=host, port=port) 