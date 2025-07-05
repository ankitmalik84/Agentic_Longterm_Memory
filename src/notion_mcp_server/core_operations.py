"""
Core Notion Operations
Basic CRUD operations for Notion API
"""

import os
from typing import Any, Dict, List, Optional, Union
from notion_client import Client
from notion_client.errors import APIResponseError
from src.notion_mcp_server.notion_utils import NotionUtils


class CoreOperations:
    """Core operations for Notion API"""
    
    def __init__(self, notion_client: Client):
        self.notion = notion_client
    
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
                    title = NotionUtils.extract_title(page)
                    print(f"  {i}. {title}")
                    print(f"     🆔 {page['id']}")
                    print(f"     🔗 {page['url']}")
                    print(f"     📅 {page['last_edited_time']}")
                    print()
            
            if databases:
                print(f"\n🗄️  Databases:")
                for i, db in enumerate(databases[:5], 1):
                    title = NotionUtils.extract_database_title(db)
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
                    title = NotionUtils.extract_title(result)
                    if title.lower() == identifier.lower():
                        page = result
                        break
                
                if not page:
                    page = results["results"][0]  # Use first result
                
                page_id = page["id"]
                page = self.notion.pages.retrieve(page_id)
            
            # Extract page info
            title = NotionUtils.extract_title(page)
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
                await NotionUtils.display_page_blocks(blocks["results"])
            
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
            parent_id = await NotionUtils.get_suitable_parent(self.notion)
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
    
    async def list_content_interactive(self):
        """Interactive content listing"""
        print("\n📋 List Content")
        print("Choose what to list:")
        print("• All pages")
        print("• All databases")
        
        choice = input("Enter choice (pages/databases): ").strip().lower()
        
        if choice == "pages":
            await self.list_all_pages()
        elif choice == "databases":
            await self.list_databases()
        else:
            print("Invalid choice")
    
    async def list_all_pages(self):
        """List all pages with details"""
        try:
            pages = self.notion.search(filter={"property": "object", "value": "page"})
            
            print(f"\n📋 All Pages ({len(pages['results'])} total):")
            print("-" * 60)
            
            for i, page in enumerate(pages["results"], 1):
                title = NotionUtils.extract_title(page)
                print(f"{i}. {title}")
                print(f"   🆔 ID: {page['id']}")
                print(f"   🔗 URL: {page['url']}")
                print(f"   📅 Last edited: {page['last_edited_time']}")
                print()
            
        except Exception as e:
            print(f"❌ Error listing pages: {e}")
    
    async def list_databases(self):
        """List all databases"""
        try:
            databases = self.notion.search(filter={"property": "object", "value": "database"})
            
            print(f"\n🗄️  All Databases ({len(databases['results'])} total):")
            print("-" * 60)
            
            for i, db in enumerate(databases["results"], 1):
                title = NotionUtils.extract_database_title(db)
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
                properties = NotionUtils.extract_properties(entry["properties"])
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