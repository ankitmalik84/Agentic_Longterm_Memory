"""
Analytics Operations for Notion API
Workspace analytics, content analysis, and metrics
"""

import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, timezone
from notion_client import Client
from notion_client.errors import APIResponseError
from src.notion_mcp_server.notion_utils import NotionUtils


class AnalyticsOperations:
    """Analytics operations for Notion API"""
    
    def __init__(self, notion_client: Client):
        self.notion = notion_client
    
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
                            "title": NotionUtils.extract_title(page),
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
                    print(f"  • {NotionUtils.extract_title(page)}")
            
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