"""
Bulk Operations for Notion API
Handle bulk operations efficiently
"""

import os
from typing import Any, Dict, List, Optional, Union
from notion_client import Client
from notion_client.errors import APIResponseError
from .notion_utils import NotionUtils


class BulkOperations:
    """Bulk operations for Notion API"""
    
    def __init__(self, notion_client: Client):
        self.notion = notion_client
    
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
                print(f"{i}. {NotionUtils.extract_title(page)}")
            
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
                title = NotionUtils.extract_title(page)
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
                title = NotionUtils.extract_title(page)
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
    
    async def bulk_create_pages(self, pages_data: List[Dict[str, str]]):
        """Create multiple pages in bulk"""
        print(f"\n🔄 Creating {len(pages_data)} pages in bulk...")
        
        created_pages = []
        failed_pages = []
        
        for page_data in pages_data:
            try:
                # Get a suitable parent page
                parent_id = await NotionUtils.get_suitable_parent(self.notion)
                if not parent_id:
                    failed_pages.append({"data": page_data, "error": "No suitable parent found"})
                    continue
                
                # Create page with parent
                page_payload = {
                    "parent": {"page_id": parent_id},
                    "properties": {"title": {"title": [{"text": {"content": page_data["title"]}}]}}
                }
                
                # Add content if provided
                if page_data.get("content"):
                    page_payload["children"] = [{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"text": {"content": page_data["content"]}}]}
                    }]
                
                page = self.notion.pages.create(**page_payload)
                created_pages.append({
                    "title": page_data["title"],
                    "id": page["id"],
                    "url": page["url"]
                })
                
            except Exception as e:
                failed_pages.append({"data": page_data, "error": str(e)})
        
        # Report results
        print(f"\n✅ Successfully created {len(created_pages)} pages")
        if failed_pages:
            print(f"❌ Failed to create {len(failed_pages)} pages")
            
        return {"created": created_pages, "failed": failed_pages}
    
    async def bulk_update_pages(self, updates: List[Dict[str, Any]]):
        """Update multiple pages in bulk"""
        print(f"\n🔄 Updating {len(updates)} pages in bulk...")
        
        updated_pages = []
        failed_updates = []
        
        for update in updates:
            try:
                page_id = update["page_id"]
                properties = update.get("properties", {})
                
                # Update page
                updated_page = self.notion.pages.update(page_id, properties=properties)
                updated_pages.append({
                    "id": page_id,
                    "title": NotionUtils.extract_title(updated_page)
                })
                
            except Exception as e:
                failed_updates.append({"update": update, "error": str(e)})
        
        # Report results
        print(f"\n✅ Successfully updated {len(updated_pages)} pages")
        if failed_updates:
            print(f"❌ Failed to update {len(failed_updates)} pages")
            
        return {"updated": updated_pages, "failed": failed_updates}
    
    async def bulk_delete_pages(self, page_ids: List[str]):
        """Delete multiple pages in bulk"""
        print(f"\n🔄 Deleting {len(page_ids)} pages in bulk...")
        
        deleted_pages = []
        failed_deletions = []
        
        for page_id in page_ids:
            try:
                # Archive page (Notion doesn't support true deletion)
                self.notion.pages.update(page_id, archived=True)
                deleted_pages.append(page_id)
                
            except Exception as e:
                failed_deletions.append({"page_id": page_id, "error": str(e)})
        
        # Report results
        print(f"\n✅ Successfully archived {len(deleted_pages)} pages")
        if failed_deletions:
            print(f"❌ Failed to archive {len(failed_deletions)} pages")
            
        return {"deleted": deleted_pages, "failed": failed_deletions}
    
    async def bulk_export_pages(self, page_ids: List[str], format: str = "markdown"):
        """Export multiple pages in bulk"""
        print(f"\n🔄 Exporting {len(page_ids)} pages in {format} format...")
        
        exported_pages = []
        failed_exports = []
        
        for page_id in page_ids:
            try:
                # Get page content
                page = self.notion.pages.retrieve(page_id)
                blocks = self.notion.blocks.children.list(page_id)
                
                # Extract page data
                title = NotionUtils.extract_title(page)
                content = await self._extract_page_content_for_export(blocks["results"])
                
                exported_pages.append({
                    "id": page_id,
                    "title": title,
                    "content": content,
                    "created_time": page["created_time"],
                    "last_edited_time": page["last_edited_time"]
                })
                
            except Exception as e:
                failed_exports.append({"page_id": page_id, "error": str(e)})
        
        # Report results
        print(f"\n✅ Successfully exported {len(exported_pages)} pages")
        if failed_exports:
            print(f"❌ Failed to export {len(failed_exports)} pages")
            
        return {"exported": exported_pages, "failed": failed_exports}
    
    async def _extract_page_content_for_export(self, blocks: List[dict]) -> str:
        """Extract page content for export (simplified markdown)"""
        content_lines = []
        
        for block in blocks:
            block_type = block.get("type", "")
            
            if block_type == "paragraph":
                text = NotionUtils.extract_rich_text(block["paragraph"]["rich_text"])
                if text:
                    content_lines.append(text)
            
            elif block_type == "heading_1":
                text = NotionUtils.extract_rich_text(block["heading_1"]["rich_text"])
                content_lines.append(f"# {text}")
            
            elif block_type == "heading_2":
                text = NotionUtils.extract_rich_text(block["heading_2"]["rich_text"])
                content_lines.append(f"## {text}")
            
            elif block_type == "heading_3":
                text = NotionUtils.extract_rich_text(block["heading_3"]["rich_text"])
                content_lines.append(f"### {text}")
            
            elif block_type == "bulleted_list_item":
                text = NotionUtils.extract_rich_text(block["bulleted_list_item"]["rich_text"])
                content_lines.append(f"• {text}")
            
            elif block_type == "numbered_list_item":
                text = NotionUtils.extract_rich_text(block["numbered_list_item"]["rich_text"])
                content_lines.append(f"1. {text}")
            
            elif block_type == "code":
                language = block["code"].get("language", "")
                text = NotionUtils.extract_rich_text(block["code"]["rich_text"])
                content_lines.append(f"```{language}")
                content_lines.append(text)
                content_lines.append("```")
            
            elif block_type == "quote":
                text = NotionUtils.extract_rich_text(block["quote"]["rich_text"])
                content_lines.append(f"> {text}")
            
            elif block_type == "divider":
                content_lines.append("---")
        
        return "\n".join(content_lines) 