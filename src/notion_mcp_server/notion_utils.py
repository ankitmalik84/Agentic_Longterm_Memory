"""
Notion API Utilities
Helper functions for parsing and formatting Notion API responses
"""

import os
import re
from typing import Any, Dict, List, Optional, Union
from notion_client import Client


class NotionUtils:
    """Utility class for Notion API operations"""
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Check if a string is a valid UUID format"""
        if not uuid_string:
            return False
        
        # Check if it's a valid UUID pattern (with or without hyphens)
        # Notion page IDs are typically 32 characters without hyphens
        # or 36 characters with hyphens in format 8-4-4-4-12
        
        # Remove hyphens for consistency
        clean_uuid = uuid_string.replace('-', '')
        
        # Check if it's 32 hexadecimal characters
        if len(clean_uuid) == 32 and re.match(r'^[0-9a-fA-F]{32}$', clean_uuid):
            return True
        
        return False
    
    @staticmethod
    def extract_block_text(block: dict) -> str:
        """Extract text content from a block"""
        block_type = block.get("type", "")
        
        if block_type == "paragraph":
            return NotionUtils.extract_rich_text(block["paragraph"]["rich_text"])
        elif block_type == "heading_1":
            return NotionUtils.extract_rich_text(block["heading_1"]["rich_text"])
        elif block_type == "heading_2":
            return NotionUtils.extract_rich_text(block["heading_2"]["rich_text"])
        elif block_type == "heading_3":
            return NotionUtils.extract_rich_text(block["heading_3"]["rich_text"])
        elif block_type == "bulleted_list_item":
            return NotionUtils.extract_rich_text(block["bulleted_list_item"]["rich_text"])
        elif block_type == "numbered_list_item":
            return NotionUtils.extract_rich_text(block["numbered_list_item"]["rich_text"])
        elif block_type == "to_do":
            return NotionUtils.extract_rich_text(block["to_do"]["rich_text"])
        elif block_type == "quote":
            return NotionUtils.extract_rich_text(block["quote"]["rich_text"])
        elif block_type == "callout":
            return NotionUtils.extract_rich_text(block["callout"]["rich_text"])
        elif block_type == "code":
            return NotionUtils.extract_rich_text(block["code"]["rich_text"])
        elif block_type == "divider":
            return "---"
        elif block_type == "image":
            image_info = block["image"]
            if image_info.get("type") == "external":
                return f"Image: {image_info['external']['url']}"
            elif image_info.get("type") == "file":
                return f"Image: {image_info['file']['url']}"
            else:
                return "Image (embedded)"
        elif block_type == "embed":
            return f"Embed: {block['embed']['url']}"
        elif block_type == "bookmark":
            return f"Bookmark: {block['bookmark']['url']}"
        else:
            return f"[{block_type.upper()}] content"
    
    @staticmethod
    def extract_page_identifier(user_input: str) -> Optional[str]:
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
    
    @staticmethod
    def extract_title(page: dict) -> str:
        """Extract title from page"""
        properties = page.get("properties", {})
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_list = prop_value.get("title", [])
                if title_list:
                    return title_list[0].get("text", {}).get("content", "Untitled")
        return "Untitled"
    
    @staticmethod
    def extract_database_title(database: dict) -> str:
        """Extract title from database"""
        title = database.get("title", [])
        if title:
            return title[0].get("text", {}).get("content", "Untitled")
        return "Untitled"
    
    @staticmethod
    def extract_rich_text(rich_text: List[dict]) -> str:
        """Extract plain text from rich text array"""
        return "".join([
            item.get("text", {}).get("content", "")
            for item in rich_text
        ])
    
    @staticmethod
    def extract_properties(properties: dict) -> dict:
        """Extract properties from database entry"""
        extracted = {}
        
        for prop_name, prop_value in properties.items():
            prop_type = prop_value.get("type", "")
            
            if prop_type == "title":
                extracted[prop_name] = NotionUtils.extract_rich_text(prop_value["title"])
            elif prop_type == "rich_text":
                extracted[prop_name] = NotionUtils.extract_rich_text(prop_value["rich_text"])
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
    
    @staticmethod
    async def display_page_blocks(blocks: List[dict]):
        """Display page blocks in a readable format"""
        for block in blocks:
            block_type = block.get("type", "")
            block_id = block.get("id", "")
            
            if block_type == "paragraph":
                text = NotionUtils.extract_rich_text(block["paragraph"]["rich_text"])
                if text:
                    print(f"{text}")
                else:
                    print("(empty paragraph)")
            
            elif block_type == "heading_1":
                text = NotionUtils.extract_rich_text(block["heading_1"]["rich_text"])
                print(f"\n# {text}")
            
            elif block_type == "heading_2":
                text = NotionUtils.extract_rich_text(block["heading_2"]["rich_text"])
                print(f"\n## {text}")
            
            elif block_type == "heading_3":
                text = NotionUtils.extract_rich_text(block["heading_3"]["rich_text"])
                print(f"\n### {text}")
            
            elif block_type == "bulleted_list_item":
                text = NotionUtils.extract_rich_text(block["bulleted_list_item"]["rich_text"])
                print(f"• {text}")
            
            elif block_type == "numbered_list_item":
                text = NotionUtils.extract_rich_text(block["numbered_list_item"]["rich_text"])
                print(f"1. {text}")
            
            elif block_type == "code":
                language = block["code"].get("language", "")
                text = NotionUtils.extract_rich_text(block["code"]["rich_text"])
                print(f"\n```{language}")
                print(text)
                print("```")
            
            elif block_type == "quote":
                text = NotionUtils.extract_rich_text(block["quote"]["rich_text"])
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
    
    @staticmethod
    def split_long_content(content: str, max_length: int = 2000) -> list:
        """
        Split long content into chunks respecting the character limit.
        
        Args:
            content (str): The content to split
            max_length (int): Maximum length per chunk (default: 2000 for Notion)
            
        Returns:
            list: List of content chunks
        """
        if len(content) <= max_length:
            return [content]
        
        chunks = []
        remaining_content = content
        
        while remaining_content:
            if len(remaining_content) <= max_length:
                # Last chunk
                chunks.append(remaining_content.strip())
                break
            else:
                # Find the best break point within the limit
                chunk = remaining_content[:max_length]
                
                # Try to break at sentence endings
                last_sentence = max(
                    chunk.rfind('. '),
                    chunk.rfind('! '),
                    chunk.rfind('? '),
                    chunk.rfind('\n')
                )
                
                if last_sentence > max_length * 0.7:  # Don't break too early
                    chunk = remaining_content[:last_sentence + 1]
                    remaining_content = remaining_content[last_sentence + 1:].strip()
                else:
                    # Break at word boundary
                    last_space = chunk.rfind(' ')
                    if last_space > max_length * 0.8:
                        chunk = remaining_content[:last_space]
                        remaining_content = remaining_content[last_space:].strip()
                    else:
                        # Hard break (rare case)
                        chunk = remaining_content[:max_length]
                        remaining_content = remaining_content[max_length:]
                
                chunks.append(chunk.strip())
        
        return [chunk for chunk in chunks if chunk]  # Remove empty chunks
    
    @staticmethod
    def get_suitable_parent_sync(notion_client: Client) -> Optional[str]:
        """Get a suitable parent page ID (synchronous version)"""
        try:
            # Strategy 1: Environment variable
            env_parent = os.getenv("NOTION_DEFAULT_PARENT_ID")
            if env_parent:
                try:
                    notion_client.pages.retrieve(env_parent)
                    return env_parent
                except:
                    pass
            
            # Strategy 2: Search for common parent page names
            parent_names = ["AI Agent Journey", "Notes", "Projects", "MCP Pages"]
            
            for name in parent_names:
                try:
                    results = notion_client.search(
                        query=name,
                        filter={"property": "object", "value": "page"}
                    )
                    
                    for page in results.get("results", []):
                        page_title = NotionUtils.extract_title(page)
                        if name.lower() in page_title.lower():
                            print(f"✅ Using parent: {page_title}")
                            return page["id"]
                except:
                    continue
            
            # Strategy 3: Use any available page as parent
            results = notion_client.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=5
            )
            
            if results.get("results"):
                first_page = results["results"][0]
                page_title = NotionUtils.extract_title(first_page)
                print(f"⚠️ Using first available page as parent: {page_title}")
                return first_page["id"]
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding parent: {e}")
            return None
    
    @staticmethod
    async def get_suitable_parent(notion_client: Client) -> Optional[str]:
        """Get a suitable parent page ID"""
        try:
            # Strategy 1: Environment variable
            env_parent = os.getenv("NOTION_DEFAULT_PARENT_ID")
            if env_parent:
                try:
                    notion_client.pages.retrieve(env_parent)
                    return env_parent
                except:
                    pass
            
            # Strategy 2: Search for common parent page names
            parent_names = ["AI Agent Journey", "Notes", "Projects", "MCP Pages"]
            
            for name in parent_names:
                try:
                    results = notion_client.search(
                        query=name,
                        filter={"property": "object", "value": "page"}
                    )
                    
                    for page in results.get("results", []):
                        page_title = NotionUtils.extract_title(page)
                        if name.lower() in page_title.lower():
                            print(f"✅ Using parent: {page_title}")
                            return page["id"]
                except:
                    continue
            
            # Strategy 3: Use any available page as parent
            results = notion_client.search(
                query="",
                filter={"property": "object", "value": "page"},
                page_size=5
            )
            
            if results.get("results"):
                first_page = results["results"][0]
                page_title = NotionUtils.extract_title(first_page)
                print(f"⚠️ Using first available page as parent: {page_title}")
                return first_page["id"]
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding parent: {e}")
            return None