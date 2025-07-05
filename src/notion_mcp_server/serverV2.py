#!/usr/bin/env python3
"""
Complete Notion Server V2 - Direct API Implementation
Clean implementation using only Notion API - no MCP client complexity
"""

import os
import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# Load environment variables first
load_dotenv()


class ComprehensiveNotionServer:
    """
    Complete Notion Server with full API coverage
    - Direct Notion API calls only
    - Comprehensive workflows and analytics
    - Bulk operations and content management
    - Production-ready error handling
    """
    
    def __init__(self, notion_token: str):
        self.notion_token = notion_token
        self.notion = Client(auth=notion_token)
        
    async def run_enhanced_conversation(self):
        """Run interactive conversation with comprehensive capabilities"""
        
        print("=== 🚀 Complete Notion Server V2 ===")
        print("🔧 Direct Notion API Integration + Custom Workflows")
        print("📋 Type 'help' for all available capabilities")
        print("🚪 Type 'exit' to quit")
        print("-" * 60)
        
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
            await self.route_user_request(user_input)
    
    async def route_user_request(self, user_input: str):
        """Route user request to appropriate handler"""
        
        # READ/GET OPERATIONS
        if any(keyword in user_input.lower() for keyword in ['read', 'get', 'show', 'view']):
            if 'page' in user_input.lower():
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
            await self.search_content(search_term)
        
        # CREATE OPERATIONS
        elif 'create' in user_input.lower():
            if 'page' in user_input.lower():
                await self.create_page_interactive()
            elif 'database' in user_input.lower():
                await self.create_database_interactive()
            else:
                print("What would you like to create?")
                print("• create page - Create a new page")
                print("• create database - Create a new database")
        
        # UPDATE OPERATIONS
        elif 'update' in user_input.lower():
            await self.update_content_interactive()
        
        # LIST OPERATIONS
        elif 'list' in user_input.lower():
            await self.list_content_interactive()
        
        # ANALYTICS WORKFLOWS
        elif any(keyword in user_input.lower() for keyword in ['analyze', 'analytics', 'metrics', 'stats']):
            await self.handle_analytics_requests(user_input)
        
        # BULK OPERATIONS
        elif any(keyword in user_input.lower() for keyword in ['bulk', 'multiple', 'batch']):
            await self.handle_bulk_operations(user_input)
        
        # MIGRATION & IMPORT
        elif any(keyword in user_input.lower() for keyword in ['migrate', 'import', 'export']):
            await self.handle_migration_requests(user_input)
        
        # WORKSPACE MANAGEMENT
        elif any(keyword in user_input.lower() for keyword in ['workspace', 'template', 'organize']):
            await self.handle_workspace_management(user_input)
        
        else:
            print("💡 I can help you with:")
            print("• Search: 'search [term]'")
            print("• Read: 'read page [name/id]'")
            print("• Create: 'create page'")
            print("• Update: 'update content'")
            print("• List: 'list pages'")
            print("• Analytics: 'analyze workspace'")
            print("• Bulk operations: 'bulk pages'")
            print("• Migration: 'import content'")
    
    # CORE OPERATIONS
    async def search_content(self, search_term: str):
        """Search for content using direct API"""
        try:
            print(f"\n🔍 Searching for: {search_term}")
            
            # Search all content
            all_results = self.notion.search(query=search_term)
            pages = [r for r in all_results.get("results", []) if r["object"] == "page"]
            databases = [r for r in all_results.get("results", []) if r["object"] == "database"]
            
            print(f"\n📊 Search Results:")
            print(f"├── 📄 Pages: {len(pages)}")
            print(f"└── 🗄️  Databases: {len(databases)}")
            
            if pages:
                print(f"\n📄 Pages:")
                for i, page in enumerate(pages[:10], 1):
                    title = self._extract_title(page)
                    print(f"  {i}. {title}")
                    print(f"     🆔 {page['id']}")
                    print(f"     🔗 {page['url']}")
                    print(f"     📅 {page['last_edited_time']}")
                    print()
            
            if databases:
                print(f"\n🗄️  Databases:")
                for i, db in enumerate(databases[:5], 1):
                    title = self._extract_database_title(db)
                    print(f"  {i}. {title}")
                    print(f"     🆔 {db['id']}")
                    print(f"     🔗 {db['url']}")
                    print()
            
            if not pages and not databases:
                print(f"❌ No results found for '{search_term}'")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
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
    
    async def create_page_interactive(self):
        """Interactive page creation"""
        print("\n📝 Create New Page")
        
        title = input("Page title: ").strip()
        if not title:
            print("❌ Title is required")
            return
        
        content = input("Page content (optional): ").strip()
        
        await self.create_page_direct(title, content)
    
    async def create_page_direct(self, title: str, content: str = ""):
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
            print(f"✅ Page created successfully!")
            print(f"📄 Title: {title}")
            print(f"🔗 URL: {page['url']}")
            print(f"🆔 ID: {page['id']}")
            
        except Exception as e:
            print(f"❌ Error creating page: {e}")
            print(f"💡 Try: 'search' to find existing pages that can be parents")
    
    async def read_page_interactive(self):
        """Interactive page reading"""
        print("\n📖 Read Page Content")
        print("You can provide:")
        print("• Page ID (e.g., 22750c4e-aa2a-81b4-8ff9-fb17b62f1db8)")
        print("• Page title (e.g., jaat)")
        
        identifier = input("Enter page ID or title: ").strip()
        if identifier:
            await self.read_page_content(identifier)
    
    # ANALYTICS IMPLEMENTATIONS
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
            print("• analyze workspace - Overall workspace statistics")
            print("• analyze content - Content analysis and insights")
            print("• analyze activity - Recent activity patterns")
            print("• analyze database - Database structure analysis")
    
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
            
            # Recent activity (last 7 days) - use timezone-aware datetime
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_pages = []
            
            for page in pages["results"]:
                try:
                    last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                    if last_edited > week_ago:
                        recent_pages.append({
                            "title": self._extract_title(page),
                            "last_edited": page["last_edited_time"],
                            "id": page["id"]
                        })
                except Exception:
                    # Skip pages with invalid dates
                    continue
            
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
            import traceback
            traceback.print_exc()
    
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
            
            # Activity analysis - use timezone-aware datetime
            now = datetime.now(timezone.utc)
            activity_buckets = {
                "today": [],
                "this_week": [],
                "this_month": [],
                "older": []
            }
            
            for page in pages["results"]:
                try:
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
                except Exception:
                    # Skip pages with invalid dates
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
            import traceback
            traceback.print_exc()
    
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
    
    # BULK OPERATIONS
    async def handle_bulk_operations(self, user_input: str):
        """Handle bulk operations"""
        print("\n🔄 Bulk Operations")
        
        if 'page' in user_input.lower():
            await self.run_bulk_page_operations()
        elif 'database' in user_input.lower():
            print("🗄️  Bulk database operations - Available soon")
        else:
            print("Available bulk operations:")
            print("• bulk pages - Page-specific bulk operations")
            print("• bulk database - Database-specific bulk operations")
    
    async def run_bulk_page_operations(self):
        """Interactive bulk page operations"""
        print("\n🔄 Bulk Page Operations")
        print("1. Archive multiple pages")
        print("2. List all pages")
        print("3. Search and analyze pages")
        
        try:
            choice = input("\nSelect operation (1-3): ").strip()
            
            if choice == "1":
                await self.bulk_archive_pages()
            elif choice == "2":
                await self.bulk_list_pages()
            elif choice == "3":
                await self.bulk_analyze_pages()
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
    
    async def bulk_list_pages(self):
        """List all pages with details"""
        try:
            pages = self.notion.search(filter={"property": "object", "value": "page"})
            
            print(f"\n📋 All Pages ({len(pages['results'])} total):")
            print("-" * 60)
            
            for i, page in enumerate(pages["results"], 1):
                title = self._extract_title(page)
                print(f"{i}. {title}")
                print(f"   🆔 ID: {page['id']}")
                print(f"   🔗 URL: {page['url']}")
                print(f"   📅 Last edited: {page['last_edited_time']}")
                print()
            
        except Exception as e:
            print(f"❌ Error listing pages: {e}")
    
    async def bulk_analyze_pages(self):
        """Analyze pages by search criteria"""
        query = input("Search query to analyze pages: ").strip()
        if not query:
            return
        
        try:
            pages = self.notion.search(query=query, filter={"property": "object", "value": "page"})
            found_pages = pages["results"]
            
            if not found_pages:
                print("No pages found matching your query.")
                return
            
            print(f"\n📊 Analysis of {len(found_pages)} pages matching '{query}':")
            print("-" * 50)
            
            for i, page in enumerate(found_pages, 1):
                title = self._extract_title(page)
                print(f"{i}. {title}")
                print(f"   📅 Created: {page['created_time']}")
                print(f"   ✏️  Last edited: {page['last_edited_time']}")
                
                # Get content summary
                try:
                    blocks = self.notion.blocks.children.list(page["id"])
                    block_count = len(blocks["results"])
                    print(f"   📝 Blocks: {block_count}")
                except:
                    print(f"   📝 Blocks: Unable to retrieve")
                
                print()
            
        except Exception as e:
            print(f"❌ Error analyzing pages: {e}")
    
    # PLACEHOLDER IMPLEMENTATIONS
    async def handle_migration_requests(self, user_input: str):
        """Handle migration and import/export requests"""
        print("\n📥 Migration & Import/Export")
        print("📥 Import/Export functionality - Available soon")
        print("Available commands:")
        print("• import content - Import from external sources")
        print("• export content - Export to various formats")
    
    async def handle_workspace_management(self, user_input: str):
        """Handle workspace management requests"""
        print("\n🏗️ Workspace Management")
        print("🏗️ Workspace management - Available soon")
        print("Available commands:")
        print("• workspace template - Template management")
        print("• organize workspace - Organization tools")
    
    async def update_content_interactive(self):
        """Interactive content updates"""
        print("\n✏️ Update Content")
        print("Content update functionality - Available soon")
        print("You can currently use 'read page' and 'create page'")
    
    async def list_content_interactive(self):
        """Interactive content listing"""
        print("\n📋 List Content")
        print("Choose what to list:")
        print("• All pages")
        print("• All databases")
        
        choice = input("Enter choice (pages/databases): ").strip().lower()
        
        if choice == "pages":
            await self.bulk_list_pages()
        elif choice == "databases":
            await self.list_databases()
        else:
            print("Invalid choice")
    
    async def list_databases(self):
        """List all databases"""
        try:
            databases = self.notion.search(filter={"property": "object", "value": "database"})
            
            print(f"\n🗄️  All Databases ({len(databases['results'])} total):")
            print("-" * 60)
            
            for i, db in enumerate(databases["results"], 1):
                title = self._extract_database_title(db)
                print(f"{i}. {title}")
                print(f"   🆔 ID: {db['id']}")
                print(f"   🔗 URL: {db['url']}")
                print(f"   📅 Last edited: {db['last_edited_time']}")
                print()
            
        except Exception as e:
            print(f"❌ Error listing databases: {e}")
    
    async def create_database_interactive(self):
        """Interactive database creation"""
        print("\n🗄️ Create Database")
        print("Database creation functionality - Available soon")
        print("You can currently use 'create page' to create pages")
    
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
    
    # UTILITY METHODS
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
    
    def _extract_title(self, page: dict) -> str:
        """Extract title from page"""
        properties = page.get("properties", {})
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    return title_list[0].get("text", {}).get("content", "Untitled")
        return "Untitled"
    
    def _extract_database_title(self, database: dict) -> str:
        """Extract title from database"""
        title = database.get("title", [])
        if title:
            return title[0].get("text", {}).get("content", "Untitled")
        return "Untitled"
    
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
    
    def show_comprehensive_help(self):
        """Show comprehensive help information"""
        print("\n" + "="*60)
        print("🔧 COMPLETE NOTION SERVER V2 CAPABILITIES")
        print("="*60)
        
        print("\n📋 CORE OPERATIONS:")
        print("  • search [term] - Search pages and databases")
        print("  • read page [name/id] - Read page content")
        print("  • create page - Create new pages")
        print("  • list pages - List all pages")
        print("  • list databases - List all databases")
        
        print("\n📊 ANALYTICS & METRICS:")
        print("  • analyze workspace - Complete workspace analytics")
        print("  • analyze content - Content structure analysis")
        print("  • analyze activity - Recent activity patterns")
        print("  • analyze database - Database structure analysis")
        
        print("\n🔄 BULK OPERATIONS:")
        print("  • bulk pages - Bulk page operations")
        print("  • bulk database - Bulk database operations")
        
        print("\n💡 EXAMPLES:")
        print("  • 'search jaat'")
        print("  • 'read page jaat'")
        print("  • 'create page'")
        print("  • 'analyze workspace'")
        print("  • 'bulk pages'")
        print("  • 'list pages'")
        
        print("\n🔌 CONNECTION:")
        print("  • Direct Notion API: ✅ Always available")
        print("  • Clean implementation: ✅ No MCP complexity")
        
        print("\n" + "="*60)


# Main execution
async def main():
    """Main entry point for the comprehensive Notion server"""
    try:
        # Get token
        notion_token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
        
        print(f"🔍 Debug: Token found: {'✅ Yes' if notion_token else '❌ No'}")
        
        if not notion_token:
            raise ValueError("NOTION_API_KEY or NOTION_TOKEN environment variable required")
        
        # Test Notion API connection first
        print("🔗 Testing Notion API connection...")
        try:
            test_client = Client(auth=notion_token)
            user_info = test_client.users.me()
            print(f"✅ Notion API connection successful! User: {user_info.get('name', 'N/A')}")
        except Exception as api_error:
            print(f"❌ Notion API connection failed: {api_error}")
            print("Please check your NOTION_TOKEN is valid")
            return 1
        
        # Create server
        print("🚀 Creating Notion server...")
        server = ComprehensiveNotionServer(notion_token)
        
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