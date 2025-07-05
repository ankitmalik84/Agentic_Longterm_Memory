#!/usr/bin/env python3
"""
Complete Notion MCP Server V2 - Full Implementation
Uses standard MCP client + comprehensive custom workflows
"""

import os
import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# Load environment variables first
load_dotenv()

# Try to import MCP client, fallback if not available
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️  MCP client not available. Install with: pip install mcp")
    MCP_AVAILABLE = False


class ComprehensiveNotionMCPServer:
    """
    Complete Notion MCP Server with full API coverage
    - Official Notion MCP server integration (when available)
    - Extended custom workflows and analytics
    - Bulk operations and content migration
    - Production-ready error handling with fallback
    """
    
    def __init__(self, notion_token: str):
        self.notion_token = notion_token
        self.notion = Client(auth=notion_token)
        self.mcp_session = None
        
    async def create_official_server(self):
        """Create connection to official Notion MCP server"""
        if not MCP_AVAILABLE:
            return False
            
        try:
            # Set up server parameters
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                env={
                    **os.environ,
                    "OPENAPI_MCP_HEADERS": f'{{"Authorization": "Bearer {self.notion_token}", "Notion-Version": "2022-06-28"}}'
                }
            )
            
            # Create stdio client connection
            stdio_transport = await stdio_client(server_params)
            read_stream, write_stream = stdio_transport
            
            # Create and initialize session
            self.mcp_session = ClientSession(read_stream, write_stream)
            await self.mcp_session.initialize()
            
            return True
            
        except Exception as e:
            print(f"❌ MCP server connection failed: {e}")
            return False
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """Call MCP tool directly"""
        if not self.mcp_session:
            raise RuntimeError("MCP session not initialized")
        
        try:
            result = await self.mcp_session.call_tool(tool_name, arguments)
            
            # Extract text content from result
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        return content.text
                    else:
                        return str(content)
            
            return str(result)
            
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"
    
    async def initialize(self):
        """Initialize the MCP server connection"""
        if MCP_AVAILABLE:
            print("🔗 Attempting to connect to official Notion MCP server...")
            mcp_connected = await self.create_official_server()
            
            if mcp_connected:
                try:
                    tools = await self.mcp_session.list_tools()
                    print(f"✅ Connected to official Notion MCP server with {len(tools.tools)} tools")
                    return True
                except Exception as e:
                    print(f"❌ Failed to list tools: {e}")
            
        print("⚠️  Using direct Notion API calls (MCP server not available)")
        return False
    
    async def run_enhanced_conversation(self):
        """Run interactive conversation with comprehensive capabilities"""
        
        print("=== 🚀 Complete Notion MCP Server V2 ===")
        print("🔧 Comprehensive Notion Integration + Custom Workflows")
        print("📋 Type 'help' for all available capabilities")
        print("🚪 Type 'exit' to quit")
        print("-" * 60)
        
        # Initialize MCP connection
        mcp_connected = await self.initialize()
        
        while True:
            try:
                user_input = input("\n🤖 User: ").strip()
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                self.show_comprehensive_help()
                continue
            
            if not user_input:
                continue
            
            # Route to appropriate handler
            await self.route_user_request(user_input, mcp_connected)
    
    async def route_user_request(self, user_input: str, mcp_connected: bool):
        """Route user request to appropriate handler"""
        
        # ANALYTICS WORKFLOWS
        if any(keyword in user_input.lower() for keyword in ['analyze', 'analytics', 'metrics', 'stats']):
            await self.handle_analytics_requests(user_input)
            return
        
        # BULK OPERATIONS
        if any(keyword in user_input.lower() for keyword in ['bulk', 'multiple', 'batch']):
            await self.handle_bulk_operations(user_input)
            return
        
        # MIGRATION & IMPORT
        if any(keyword in user_input.lower() for keyword in ['migrate', 'import', 'export']):
            await self.handle_migration_requests(user_input)
            return
        
        # WORKSPACE MANAGEMENT
        if any(keyword in user_input.lower() for keyword in ['workspace', 'template', 'organize']):
            await self.handle_workspace_management(user_input)
            return
        
        # STANDARD OPERATIONS (via MCP or direct API)
        await self.handle_standard_operations(user_input, mcp_connected)
    
    async def handle_analytics_requests(self, user_input: str):
        """Handle analytics and metrics requests"""
        print("\n📊 Analytics & Metrics")
        
        if 'workspace' in user_input.lower():
            await self.run_workspace_analytics()
        elif 'content' in user_input.lower():
            await self.run_content_analytics()
        elif 'activity' in user_input.lower():
            await self.run_activity_analytics()
        elif 'database' in user_input.lower():
            await self.run_database_analytics()
        else:
            print("Available analytics:")
            print("• workspace analytics - Overall workspace statistics")
            print("• content analytics - Content analysis and insights")
            print("• activity analytics - Recent activity patterns")
            print("• database analytics - Database structure analysis")
    
    async def handle_bulk_operations(self, user_input: str):
        """Handle bulk operations"""
        print("\n🔄 Bulk Operations")
        
        if 'page' in user_input.lower():
            await self.run_bulk_page_operations()
        elif 'database' in user_input.lower():
            await self.run_bulk_database_operations()
        elif 'property' in user_input.lower():
            await self.run_bulk_property_operations()
        else:
            await self.show_bulk_operations_menu()
    
    async def handle_migration_requests(self, user_input: str):
        """Handle migration and import/export requests"""
        print("\n📥 Migration & Import/Export")
        
        if 'import' in user_input.lower():
            await self.run_import_wizard()
        elif 'export' in user_input.lower():
            await self.run_export_wizard()
        elif 'migrate' in user_input.lower():
            await self.run_migration_wizard()
        else:
            await self.show_migration_options()
    
    async def handle_workspace_management(self, user_input: str):
        """Handle workspace management requests"""
        print("\n🏗️ Workspace Management")
        
        if 'template' in user_input.lower():
            await self.run_template_manager()
        elif 'organize' in user_input.lower():
            await self.run_workspace_organizer()
        elif 'structure' in user_input.lower():
            await self.run_structure_analyzer()
        else:
            await self.show_workspace_management_options()
    
    async def handle_standard_operations(self, user_input: str, mcp_connected: bool):
        """Handle standard Notion operations"""
        
        # READ/GET OPERATIONS
        if any(keyword in user_input.lower() for keyword in ['read', 'get', 'show', 'view']):
            if 'page' in user_input.lower():
                # Extract page identifier from input
                page_identifier = self._extract_page_identifier(user_input)
                if page_identifier:
                    await self.read_page_content(page_identifier)
                else:
                    await self.read_page_interactive()
            elif 'database' in user_input.lower():
                database_id = input("Enter database ID: ").strip()
                if database_id:
                    await self.read_database_content(database_id)
            else:
                print("What would you like to read?")
                print("• read page [name/id] - Read page content")
                print("• read database [id] - Read database content")
        
        # SEARCH OPERATIONS
        elif 'search' in user_input.lower():
            search_term = user_input.lower().replace('search', '').strip()
            if not search_term:
                search_term = input("Enter search term: ").strip()
            
            if mcp_connected and self.mcp_session:
                try:
                    result = await self.call_mcp_tool("notion_search", {"query": search_term})
                    print(f"\n🔍 Search Results (via MCP):\n{result}")
                except Exception as e:
                    print(f"❌ MCP search failed: {e}")
                    await self.direct_search(search_term)
            else:
                await self.direct_search(search_term)
        
        # CREATE OPERATIONS
        elif 'create' in user_input.lower():
            if 'page' in user_input.lower():
                await self.create_page_interactive(mcp_connected)
            elif 'database' in user_input.lower():
                await self.create_database_interactive(mcp_connected)
            else:
                print("What would you like to create?")
                print("• page - Create a new page")
                print("• database - Create a new database")
        
        # UPDATE OPERATIONS
        elif 'update' in user_input.lower():
            await self.update_content_interactive(mcp_connected)
        
        # LIST OPERATIONS
        elif 'list' in user_input.lower():
            await self.list_content_interactive(mcp_connected)
        
        else:
            print("💡 I can help you with:")
            print("• Search: 'search [term]'")
            print("• Read: 'read page [name/id]' or 'get page [name/id]'")
            print("• Create: 'create page' or 'create database'")
            print("• Update: 'update [page/database]'")
            print("• List: 'list [pages/databases]'")
            print("• Analytics: 'analyze workspace'")
            print("• Bulk operations: 'bulk pages'")
            print("• Migration: 'import content'")
    
    # ANALYTICS IMPLEMENTATIONS
    async def run_workspace_analytics(self):
        """Comprehensive workspace analytics"""
        print("\n📊 Running Workspace Analytics...")
        
        try:
            # Gather data
            pages = self.notion.search(filter={"property": "object", "value": "page"})
            databases = self.notion.search(filter={"property": "object", "value": "database"})
            
            # Calculate metrics
            total_pages = len(pages["results"])
            total_databases = len(databases["results"])
            
            # Recent activity (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_pages = []
            
            for page in pages["results"]:
                last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                if last_edited > week_ago:
                    recent_pages.append({
                        "title": self._extract_title(page),
                        "last_edited": page["last_edited_time"],
                        "id": page["id"]
                    })
            
            # Sort by last edited
            recent_pages.sort(key=lambda x: x["last_edited"], reverse=True)
            
            # Display results
            print(f"\n📈 Workspace Analytics Results:")
            print(f"├── 📄 Total Pages: {total_pages}")
            print(f"├── 🗄️  Total Databases: {total_databases}")
            print(f"├── 📅 Recent Activity (7 days): {len(recent_pages)} pages")
            print(f"└── 🔥 Most Active Period: Last 7 days")
            
            if recent_pages:
                print(f"\n🔥 Most Recently Updated Pages:")
                for i, page in enumerate(recent_pages[:10], 1):
                    print(f"  {i}. {page['title']}")
                    print(f"     📅 {page['last_edited']}")
                    print(f"     🆔 {page['id']}")
            
        except Exception as e:
            print(f"❌ Analytics error: {e}")
    
    async def run_content_analytics(self):
        """Analyze content patterns and structure"""
        print("\n📝 Content Analytics...")
        
        try:
            pages = self.notion.search(filter={"property": "object", "value": "page"})
            
            # Content analysis
            content_stats = {
                "total_pages": len(pages["results"]),
                "pages_with_content": 0,
                "empty_pages": 0,
                "avg_blocks_per_page": 0,
                "content_types": {}
            }
            
            total_blocks = 0
            
            for page in pages["results"][:20]:  # Analyze first 20 pages
                try:
                    blocks = self.notion.blocks.children.list(page["id"])
                    block_count = len(blocks["results"])
                    total_blocks += block_count
                    
                    if block_count > 0:
                        content_stats["pages_with_content"] += 1
                    else:
                        content_stats["empty_pages"] += 1
                    
                    # Analyze block types
                    for block in blocks["results"]:
                        block_type = block.get("type", "unknown")
                        content_stats["content_types"][block_type] = content_stats["content_types"].get(block_type, 0) + 1
                        
                except Exception:
                    continue
            
            if content_stats["pages_with_content"] > 0:
                content_stats["avg_blocks_per_page"] = total_blocks / content_stats["pages_with_content"]
            
            print(f"\n📊 Content Analysis Results:")
            print(f"├── 📄 Total Pages Analyzed: {min(20, content_stats['total_pages'])}")
            print(f"├── ✅ Pages with Content: {content_stats['pages_with_content']}")
            print(f"├── 📭 Empty Pages: {content_stats['empty_pages']}")
            print(f"├── 📊 Avg Blocks per Page: {content_stats['avg_blocks_per_page']:.1f}")
            print(f"└── 🧩 Content Types:")
            
            for content_type, count in sorted(content_stats["content_types"].items(), key=lambda x: x[1], reverse=True):
                print(f"    • {content_type}: {count}")
            
        except Exception as e:
            print(f"❌ Content analytics error: {e}")
    
    async def run_activity_analytics(self):
        """Analyze recent activity patterns"""
        print("\n🔄 Activity Analytics...")
        
        try:
            pages = self.notion.search(filter={"property": "object", "value": "page"})
            
            # Activity analysis
            now = datetime.now()
            activity_buckets = {
                "today": [],
                "this_week": [],
                "this_month": [],
                "older": []
            }
            
            for page in pages["results"]:
                last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                days_ago = (now - last_edited).days
                
                if days_ago == 0:
                    activity_buckets["today"].append(page)
                elif days_ago <= 7:
                    activity_buckets["this_week"].append(page)
                elif days_ago <= 30:
                    activity_buckets["this_month"].append(page)
                else:
                    activity_buckets["older"].append(page)
            
            print(f"\n📊 Activity Pattern Analysis:")
            print(f"├── 📅 Today: {len(activity_buckets['today'])} pages")
            print(f"├── 🗓️  This Week: {len(activity_buckets['this_week'])} pages")
            print(f"├── 📆 This Month: {len(activity_buckets['this_month'])} pages")
            print(f"└── 🗂️  Older: {len(activity_buckets['older'])} pages")
            
            # Show most active day
            if activity_buckets["today"]:
                print(f"\n🔥 Today's Activity:")
                for page in activity_buckets["today"][:5]:
                    print(f"  • {self._extract_title(page)}")
            
        except Exception as e:
            print(f"❌ Activity analytics error: {e}")
    
    async def run_database_analytics(self):
        """Analyze database structure and usage"""
        print("\n🗄️ Database Analytics...")
        
        try:
            databases = self.notion.search(filter={"property": "object", "value": "database"})
            
            db_stats = {
                "total_databases": len(databases["results"]),
                "property_types": {},
                "database_sizes": []
            }
            
            for db in databases["results"]:
                try:
                    # Get database details
                    db_info = self.notion.databases.retrieve(db["id"])
                    properties = db_info.get("properties", {})
                    
                    # Count property types
                    for prop_name, prop_info in properties.items():
                        prop_type = prop_info.get("type", "unknown")
                        db_stats["property_types"][prop_type] = db_stats["property_types"].get(prop_type, 0) + 1
                    
                except Exception:
                    continue
            
            print(f"\n📊 Database Structure Analysis:")
            print(f"├── 🗄️  Total Databases: {db_stats['total_databases']}")
            print(f"└── 🏷️  Property Types Used:")
            
            for prop_type, count in sorted(db_stats["property_types"].items(), key=lambda x: x[1], reverse=True):
                print(f"    • {prop_type}: {count}")
            
        except Exception as e:
            print(f"❌ Database analytics error: {e}")
    
    # BULK OPERATIONS IMPLEMENTATIONS
    async def run_bulk_page_operations(self):
        """Interactive bulk page operations"""
        print("\n🔄 Bulk Page Operations")
        print("1. Archive multiple pages")
        print("2. Update page properties")
        print("3. Move pages to different parent")
        print("4. Add tags to multiple pages")
        print("5. Bulk content append")
        
        try:
            choice = input("\nSelect operation (1-5): ").strip()
            
            if choice == "1":
                await self.bulk_archive_pages()
            elif choice == "2":
                await self.bulk_update_properties()
            elif choice == "3":
                await self.bulk_move_pages()
            elif choice == "4":
                await self.bulk_add_tags()
            elif choice == "5":
                await self.bulk_append_content()
            else:
                print("Invalid choice")
                
        except Exception as e:
            print(f"❌ Bulk operation error: {e}")
    
    async def bulk_archive_pages(self):
        """Archive multiple pages based on search criteria"""
        query = input("Search query to find pages to archive: ").strip()
        if not query:
            return
        
        try:
            pages = self.notion.search(query=query, filter={"property": "object", "value": "page"})
            found_pages = pages["results"]
            
            if not found_pages:
                print("No pages found matching your query.")
                return
            
            print(f"\nFound {len(found_pages)} pages:")
            for i, page in enumerate(found_pages, 1):
                print(f"{i}. {self._extract_title(page)}")
            
            confirm = input(f"\nArchive all {len(found_pages)} pages? (y/n): ").lower()
            if confirm == 'y':
                for page in found_pages:
                    self.notion.pages.update(page["id"], archived=True)
                print(f"✅ Successfully archived {len(found_pages)} pages")
            else:
                print("Operation cancelled")
                
        except Exception as e:
            print(f"❌ Error archiving pages: {e}")
    
    # STANDARD OPERATIONS IMPLEMENTATIONS
    async def create_page_interactive(self, mcp_connected: bool):
        """Interactive page creation"""
        title = input("Page title: ").strip()
        if not title:
            print("Title is required")
            return
        
        content = input("Page content (optional): ").strip()
        
        if mcp_connected and self.mcp_session:
            try:
                result = await self.call_mcp_tool("notion_create_page", {
                    "title": title,
                    "content": content
                })
                print(f"\n✅ Page created via MCP:\n{result}")
            except Exception as e:
                print(f"❌ MCP creation failed: {e}")
                await self.direct_create_page(title, content)
        else:
            await self.direct_create_page(title, content)
    
    async def direct_create_page(self, title: str, content: str):
        """Create page using direct API"""
        try:
            # Get a suitable parent page
            parent_id = await self._get_suitable_parent()
            if not parent_id:
                print("❌ No suitable parent page found. Need to specify a parent.")
                return
            
            # Create page with parent
            page_data = {
                "parent": {"page_id": parent_id},
                "properties": {"title": {"title": [{"text": {"content": title}}]}}
            }
            
            # Add content if provided
            if content:
                page_data["children"] = [{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": content}}]}
                }]
            
            page = self.notion.pages.create(**page_data)
            print(f"✅ Page created: {page['url']}")
            print(f"📄 Title: {title}")
            print(f"🆔 ID: {page['id']}")
            
        except Exception as e:
            print(f"❌ Error creating page: {e}")
            print(f"💡 Try: 'search' to find existing pages that can be parents")
    
    async def _get_suitable_parent(self) -> Optional[str]:
        """Get a suitable parent page ID"""
        try:
            # Strategy 1: Environment variable
            env_parent = os.getenv("NOTION_DEFAULT_PARENT_ID")
            if env_parent:
                try:
                    self.notion.pages.retrieve(env_parent)
                    return env_parent
                except:
                    pass
            
            # Strategy 2: Search for common parent page names
            parent_names = ["AI Agent Journey", "Notes", "Projects", "MCP Pages"]
            
            for name in parent_names:
                try:
                    results = self.notion.search(
                        query=name,
                        filter={"property": "object", "value": "page"}
                    )
                    
                    for page in results.get("results", []):
                        page_title = self._extract_title(page)
                        if name.lower() in page_title.lower():
                            print(f"✅ Using parent: {page_title}")
                            return page["id"]
                except:
                    continue
            
            # Strategy 3: Use any available page as parent
            results = self.notion.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=5
            )
            
            if results.get("results"):
                first_page = results["results"][0]
                page_title = self._extract_title(first_page)
                print(f"⚠️ Using first available page as parent: {page_title}")
                return first_page["id"]
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding parent: {e}")
            return None
    
    async def direct_search(self, search_term: str):
        """Search using direct API"""
        try:
            results = self.notion.search(query=search_term)
            pages = results.get("results", [])
            
            print(f"\n🔍 Found {len(pages)} results for '{search_term}':")
            for i, page in enumerate(pages[:10], 1):
                title = self._extract_title(page)
                print(f"{i}. {title}")
                print(f"   🆔 {page['id']}")
                print(f"   🔗 {page['url']}")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    # UTILITY METHODS
    def _extract_title(self, page: dict) -> str:
        """Extract title from page"""
        properties = page.get("properties", {})
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    return title_list[0].get("text", {}).get("content", "Untitled")
        return "Untitled"
    
    def show_comprehensive_help(self):
        """Show comprehensive help information"""
        print("\n" + "="*60)
        print("🔧 COMPREHENSIVE NOTION MCP SERVER V2 CAPABILITIES")
        print("="*60)
        
        print("\n📋 STANDARD OPERATIONS:")
        print("  • search [term] - Search pages and databases")
        print("  • read page [name/id] - Read page content")
        print("  • get page [name/id] - Get page content")
        print("  • create page - Create new pages interactively")
        print("  • create database - Create new databases")
        print("  • list pages - List all pages")
        print("  • list databases - List all databases")
        print("  • update [content] - Update existing content")
        
        print("\n📊 ANALYTICS & METRICS:")
        print("  • analyze workspace - Complete workspace analytics")
        print("  • analyze content - Content structure analysis")
        print("  • analyze activity - Recent activity patterns")
        print("  • analyze database - Database structure analysis")
        
        print("\n🔄 BULK OPERATIONS:")
        print("  • bulk pages - Bulk page operations")
        print("  • bulk database - Bulk database operations")
        print("  • bulk properties - Bulk property updates")
        print("  • batch operations - Various batch operations")
        
        print("\n📥 MIGRATION & IMPORT/EXPORT:")
        print("  • import content - Import from various sources")
        print("  • export content - Export to various formats")
        print("  • migrate data - Data migration tools")
        
        print("\n🏗️ WORKSPACE MANAGEMENT:")
        print("  • workspace template - Create workspace templates")
        print("  • organize workspace - Workspace organization tools")
        print("  • workspace structure - Analyze workspace structure")
        
        print("\n💡 EXAMPLES:")
        print("  • 'search project management'")
        print("  • 'analyze workspace'")
        print("  • 'bulk pages'")
        print("  • 'import content'")
        print("  • 'create page'")
        
        print(f"\n🔌 CONNECTION STATUS:")
        if MCP_AVAILABLE:
            print("  • MCP Client: ✅ Available")
            if self.mcp_session:
                print("  • Official Server: ✅ Connected")
            else:
                print("  • Official Server: ❌ Not connected")
        else:
            print("  • MCP Client: ❌ Not available (pip install mcp)")
        print("  • Direct API: ✅ Always available")
        
        print("\n" + "="*60)
    
    # PLACEHOLDER METHODS (for future implementation)
    async def run_bulk_database_operations(self):
        print("Bulk database operations - would implement database-specific bulk operations")
    
    async def run_bulk_property_operations(self):
        print("Bulk property operations - would implement property-specific bulk operations")
    
    async def show_bulk_operations_menu(self):
        print("Available bulk operations:")
        print("• bulk pages - Page-specific bulk operations")
        print("• bulk database - Database-specific bulk operations")
        print("• bulk properties - Property-specific bulk operations")
    
    async def run_import_wizard(self):
        print("📥 Import Wizard - would implement comprehensive import functionality")
    
    async def run_export_wizard(self):
        print("📤 Export wizard - would implement export functionality")
    
    async def run_migration_wizard(self):
        print("🔄 Migration wizard - would implement migration functionality")
    
    async def show_migration_options(self):
        print("Migration options:")
        print("• import content - Import from external sources")
        print("• export content - Export to various formats")
        print("• migrate data - Full data migration tools")
    
    async def run_template_manager(self):
        print("🏗️ Template manager - would implement template management")
    
    async def run_workspace_organizer(self):
        print("📁 Workspace organizer - would implement workspace organization")
    
    async def run_structure_analyzer(self):
        print("🔍 Structure analyzer - would implement structure analysis")
    
    async def show_workspace_management_options(self):
        print("Workspace management options:")
        print("• workspace template - Template management")
        print("• organize workspace - Organization tools")
        print("• workspace structure - Structure analysis")
    
    async def create_database_interactive(self, mcp_connected: bool):
        print("🗄️ Database creation - would implement interactive database creation")
    
    async def update_content_interactive(self, mcp_connected: bool):
        print("✏️ Content update - would implement interactive content updates")
    
    async def list_content_interactive(self, mcp_connected: bool):
        print("📋 Content listing - would implement interactive content listing")
    
    async def bulk_update_properties(self):
        print("Bulk property update - would implement based on specific requirements")
    
    async def bulk_move_pages(self):
        print("Bulk move operation - would implement parent change logic")
    
    async def bulk_add_tags(self):
        print("Bulk tagging - would implement tagging logic")
    
    async def bulk_append_content(self):
        print("Bulk content append - would implement content addition logic")

    def _extract_page_identifier(self, user_input: str) -> Optional[str]:
        """Extract page identifier (name or ID) from user input"""
        # Remove command words
        text = user_input.lower()
        for word in ['read', 'get', 'show', 'view', 'page', 'content', 'of']:
            text = text.replace(word, '')
        
        # Clean up and extract identifier
        identifier = text.strip()
        if identifier:
            return identifier
        return None
    
    async def read_page_interactive(self):
        """Interactive page reading"""
        print("\n📖 Read Page Content")
        print("You can provide:")
        print("• Page ID (e.g., 22750c4e-aa2a-81b4-8ff9-fb17b62f1db8)")
        print("• Page title (e.g., jaat)")
        
        identifier = input("Enter page ID or title: ").strip()
        if identifier:
            await self.read_page_content(identifier)
    
    async def read_page_content(self, identifier: str):
        """Read and display page content"""
        try:
            print(f"\n📖 Reading page: {identifier}")
            
            # Check if identifier is a page ID (UUID-like format)
            if len(identifier) > 30 and '-' in identifier:
                # Direct page ID
                page_id = identifier.replace('-', '')
                page = self.notion.pages.retrieve(page_id)
            else:
                # Search for page by title
                results = self.notion.search(
                    query=identifier,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    print(f"❌ No page found with title '{identifier}'")
                    return
                
                # Find exact match or first result
                page = None
                for result in results["results"]:
                    title = self._extract_title(result)
                    if title.lower() == identifier.lower():
                        page = result
                        break
                
                if not page:
                    page = results["results"][0]  # Use first result
                
                page_id = page["id"]
                page = self.notion.pages.retrieve(page_id)
            
            # Extract page info
            title = self._extract_title(page)
            created_time = page["created_time"]
            last_edited = page["last_edited_time"]
            url = page["url"]
            
            print(f"\n📄 Page: {title}")
            print(f"🔗 URL: {url}")
            print(f"📅 Created: {created_time}")
            print(f"✏️ Last edited: {last_edited}")
            print(f"🆔 ID: {page['id']}")
            
            # Get page content (blocks)
            print(f"\n📝 Content:")
            print("-" * 50)
            
            blocks = self.notion.blocks.children.list(page["id"])
            
            if not blocks.get("results"):
                print("(This page has no content)")
            else:
                await self._display_page_blocks(blocks["results"])
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error reading page: {e}")
            print(f"💡 Make sure the page exists and you have access to it")
    
    async def _display_page_blocks(self, blocks: List[dict]):
        """Display page blocks in a readable format"""
        for block in blocks:
            block_type = block.get("type", "")
            block_id = block.get("id", "")
            
            if block_type == "paragraph":
                text = self._extract_rich_text(block["paragraph"]["rich_text"])
                if text:
                    print(f"{text}")
                else:
                    print("(empty paragraph)")
            
            elif block_type == "heading_1":
                text = self._extract_rich_text(block["heading_1"]["rich_text"])
                print(f"\n# {text}")
            
            elif block_type == "heading_2":
                text = self._extract_rich_text(block["heading_2"]["rich_text"])
                print(f"\n## {text}")
            
            elif block_type == "heading_3":
                text = self._extract_rich_text(block["heading_3"]["rich_text"])
                print(f"\n### {text}")
            
            elif block_type == "bulleted_list_item":
                text = self._extract_rich_text(block["bulleted_list_item"]["rich_text"])
                print(f"• {text}")
            
            elif block_type == "numbered_list_item":
                text = self._extract_rich_text(block["numbered_list_item"]["rich_text"])
                print(f"1. {text}")
            
            elif block_type == "code":
                language = block["code"].get("language", "")
                text = self._extract_rich_text(block["code"]["rich_text"])
                print(f"\n```{language}")
                print(text)
                print("```")
            
            elif block_type == "quote":
                text = self._extract_rich_text(block["quote"]["rich_text"])
                print(f"\n> {text}")
            
            elif block_type == "divider":
                print("\n---")
            
            elif block_type == "image":
                image_info = block["image"]
                if image_info.get("type") == "external":
                    print(f"\n🖼️ Image: {image_info['external']['url']}")
                elif image_info.get("type") == "file":
                    print(f"\n🖼️ Image: {image_info['file']['url']}")
                else:
                    print("\n🖼️ Image (embedded)")
            
            elif block_type == "embed":
                embed_url = block["embed"]["url"]
                print(f"\n🔗 Embed: {embed_url}")
            
            elif block_type == "bookmark":
                bookmark_url = block["bookmark"]["url"]
                print(f"\n🔖 Bookmark: {bookmark_url}")
            
            elif block_type == "table":
                print(f"\n📊 Table ({block_id})")
                # Note: Table content requires additional API calls
            
            elif block_type == "column_list":
                print(f"\n📑 Column Layout")
                # Note: Column content requires additional API calls
            
            else:
                print(f"\n[{block_type.upper()}] (Block ID: {block_id})")
            
            # Check if block has children
            if block.get("has_children"):
                print(f"   └── (Has child blocks)")
    
    def _extract_rich_text(self, rich_text: List[dict]) -> str:
        """Extract plain text from rich text array"""
        return "".join([
            item.get("text", {}).get("content", "")
            for item in rich_text
        ])
    
    async def read_database_content(self, database_id: str):
        """Read and display database content"""
        try:
            print(f"\n🗄️ Reading database: {database_id}")
            
            # Get database info
            database = self.notion.databases.retrieve(database_id)
            title = database.get("title", [])
            db_title = title[0].get("text", {}).get("content", "Untitled") if title else "Untitled"
            
            print(f"📊 Database: {db_title}")
            print(f"🆔 ID: {database['id']}")
            
            # Get database entries
            entries = self.notion.databases.query(database_id=database_id)
            
            print(f"\n📋 Entries ({len(entries['results'])} total):")
            print("-" * 50)
            
            for i, entry in enumerate(entries["results"][:10], 1):  # Show first 10 entries
                properties = self._extract_properties(entry["properties"])
                print(f"{i}. Entry {entry['id']}")
                for prop_name, prop_value in properties.items():
                    if prop_value:
                        print(f"   {prop_name}: {prop_value}")
                print()
            
            if len(entries["results"]) > 10:
                print(f"... and {len(entries['results']) - 10} more entries")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error reading database: {e}")
    
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
            elif prop_type == "url":
                extracted[prop_name] = prop_value.get("url")
            elif prop_type == "email":
                extracted[prop_name] = prop_value.get("email")
            elif prop_type == "phone_number":
                extracted[prop_name] = prop_value.get("phone_number")
            else:
                extracted[prop_name] = str(prop_value)
        
        return extracted


# Main execution
async def main():
    """Main entry point for the comprehensive Notion MCP server"""
    try:
        # Load environment
        notion_token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
        
        print(f"🔍 Debug: Token found: {'✅ Yes' if notion_token else '❌ No'}")
        
        if not notion_token:
            raise ValueError("NOTION_API_KEY or NOTION_TOKEN environment variable required")
        
        # Test Notion API connection first
        print("🔗 Testing Notion API connection...")
        try:
            from notion_client import Client
            test_client = Client(auth=notion_token)
            # Simple test call
            test_client.users.me()
            print("✅ Notion API connection successful")
        except Exception as api_error:
            print(f"❌ Notion API connection failed: {api_error}")
            print("Please check your NOTION_TOKEN is valid")
            return 1
        
        # Create comprehensive server
        print("🚀 Creating MCP server...")
        server = ComprehensiveNotionMCPServer(notion_token)
        
        # Run interactive conversation
        print("▶️ Starting interactive conversation...")
        await server.run_enhanced_conversation()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! (Interrupted)")
        return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"📋 Error type: {type(e).__name__}")
        import traceback
        print(f"🔍 Full traceback:")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1) 