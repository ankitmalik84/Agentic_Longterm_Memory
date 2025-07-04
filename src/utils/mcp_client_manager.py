import asyncio
import subprocess
import json
import os
import time
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientManager:
    """Manager for handling MCP client connections and tool calls"""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.http_clients: Dict[str, str] = {}  # Store HTTP URLs
        self.exit_stack = AsyncExitStack()
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Configuration from environment variables
        self.notion_server_url = os.getenv("NOTION_MCP_SERVER_URL", "https://notion-mcp-server-5s5v.onrender.com/")
        self.notion_token = os.getenv("NOTION_TOKEN", "")
        
        print(f"🔧 MCP Client Manager initialized with server URL: {self.notion_server_url}")
        
    async def initialize_notion_server_http(self, server_url: str = None) -> bool:
        """Initialize Notion MCP server via HTTP transport"""
        try:
            # Use provided URL or default from environment
            url = server_url or self.notion_server_url
            
            # Test the server is reachable
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "running":
                            print(f"✅ HTTP MCP server connected: {url}")
                            print(f"📋 Available tools: {data.get('available_tools', [])}")
                            
                            # Store the HTTP client URL
                            self.http_clients['notion'] = url
                            return True
                        else:
                            print(f"❌ Server not running: {data}")
                            return False
                    else:
                        print(f"❌ Server unreachable: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error connecting to HTTP MCP server: {e}")
            return False
    
    async def initialize_notion_server(self, notion_token: str = None) -> bool:
        """Initialize and connect to Notion MCP server via stdio transport"""
        try:
            # Use provided token or default from environment
            token = notion_token or self.notion_token
            
            # Set up server parameters for stdio transport
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.notion_mcp_server.server"],  # Updated path
                env={**os.environ, "NOTION_TOKEN": token}
            )
            
            # Create stdio client connection
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport
            
            # Create client session
            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize the session
            await session.initialize()
            
            # Store the session
            self.sessions['notion'] = session
            
            # Test the connection by listing tools
            tools_response = await session.list_tools()
            print(f"✅ Notion MCP server connected with {len(tools_response.tools)} tools")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Notion server: {e}")
            return False
    
    async def initialize_notion_with_fallback(self) -> bool:
        """Initialize Notion MCP server with fallback strategy"""
        print("🔗 Attempting to initialize Notion MCP server...")
        
        # Strategy 1: Try HTTP server first (production deployment)
        print(f"🌐 Trying HTTP server: {self.notion_server_url}")
        result = await self.initialize_notion_server_http()
        
        if result:
            print("✅ HTTP Notion MCP server initialized successfully")
            return True
        
        # Strategy 2: Fallback to stdio if HTTP fails
        print("⚠️ HTTP server failed, trying local stdio...")
        result = await self.initialize_notion_server()
        
        if result:
            print("✅ Local Notion MCP server initialized successfully")
            return True
        
        print("⚠️ Both HTTP and stdio failed - continuing without MCP")
        return False
    
    def call_tool_sync(self, server_name: str, tool_name: str, arguments: dict) -> Tuple[str, str]:
        """
        Synchronous wrapper for calling MCP tools
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tuple of (state, result)
        """
        try:
            # Run the async call in a thread
            future = self.executor.submit(
                self._run_async_call, server_name, tool_name, arguments
            )
            
            # Wait for result with timeout
            result = future.result(timeout=30)
            return result
            
        except Exception as e:
            return "Function call failed.", f"Error calling {tool_name}: {str(e)}"
    
    def _run_async_call(self, server_name: str, tool_name: str, arguments: dict) -> Tuple[str, str]:
        """Run async tool call in a new event loop"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self._call_tool_async(server_name, tool_name, arguments)
                )
                return result
            finally:
                loop.close()
                
        except Exception as e:
            return "Function call failed.", f"Error in async call: {str(e)}"
    
    async def _call_tool_async(self, server_name: str, tool_name: str, arguments: dict) -> Tuple[str, str]:
        """
        Async method to call MCP tools
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tuple of (state, result)
        """
        try:
            # Check if it's HTTP client
            if server_name in self.http_clients:
                return await self._call_http_tool(server_name, tool_name, arguments)
            
            # Check if it's stdio client
            if server_name not in self.sessions:
                return "Function call failed.", f"Server {server_name} not connected"
            
            session = self.sessions[server_name]
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            
            # Extract text content from result
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        return "Function call successful.", content.text
                    elif hasattr(content, 'content'):
                        return "Function call successful.", content.content
                    else:
                        return "Function call successful.", str(content)
                else:
                    return "Function call successful.", str(result.content)
            else:
                return "Function call successful.", str(result)
                
        except Exception as e:
            return "Function call failed.", f"Error calling {tool_name}: {str(e)}"
    
    async def _call_http_tool(self, server_name: str, tool_name: str, arguments: dict) -> Tuple[str, str]:
        """Call tool via HTTP transport"""
        try:
            server_url = self.http_clients[server_name]
            
            # Prepare JSON-RPC request
            request_data = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    server_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if "result" in data:
                            content = data["result"].get("content", [])
                            if content and len(content) > 0:
                                text = content[0].get("text", str(content[0]))
                                return "Function call successful.", text
                            else:
                                return "Function call successful.", str(data["result"])
                        elif "error" in data:
                            return "Function call failed.", f"Server error: {data['error']}"
                        else:
                            return "Function call failed.", f"Unexpected response: {data}"
                    else:
                        error_text = await response.text()
                        return "Function call failed.", f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            return "Function call failed.", f"HTTP tool call error: {str(e)}"
    
    def get_available_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """Get available tools from an MCP server"""
        try:
            if server_name not in self.sessions and server_name not in self.http_clients:
                return []
            
            # For now, return the known Notion tools
            if server_name == "notion":
                return [
                    {
                        "name": "search_notion_pages",
                        "description": "Search for pages in Notion workspace",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query text"},
                                "page_size": {"type": "integer", "description": "Number of results to return"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_notion_page",
                        "description": "Get detailed content of a specific Notion page",
                        "parameters": {
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
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Page title"},
                                "content": {"type": "string", "description": "Page content in plain text"},
                                "parent_id": {"type": "string", "description": "Parent page ID (optional)"}
                            },
                            "required": ["title", "content"]
                        }
                    },
                    {
                        "name": "get_notion_database",
                        "description": "Query a Notion database",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "database_id": {"type": "string", "description": "Database ID"},
                                "filter_property": {"type": "string", "description": "Property to filter by (optional)"},
                                "filter_value": {"type": "string", "description": "Value to filter by (optional)"}
                            },
                            "required": ["database_id"]
                        }
                    }
                ]
            
            return []
            
        except Exception as e:
            print(f"Error getting tools from {server_name}: {e}")
            return []
    
    async def shutdown(self):
        """Shutdown all MCP sessions"""
        try:
            await self.exit_stack.aclose()
            self.executor.shutdown(wait=True)
        except Exception as e:
            print(f"Error during shutdown: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        # Note: Can't use async in __del__, so we'll handle this in the main cleanup
        pass 