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
from .notion_utils import NotionUtils
from .core_operations import CoreOperations
from .analytics_operations import AnalyticsOperations
from .bulk_operations import BulkOperations
from .update_operations import UpdateOperations

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
        
        # Initialize operation classes
        self.core_ops = CoreOperations(self.notion)
        self.analytics_ops = AnalyticsOperations(self.notion)
        self.bulk_ops = BulkOperations(self.notion)
        self.update_ops = UpdateOperations(self.notion)
        
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
                page_identifier = NotionUtils.extract_page_identifier(user_input)
                if page_identifier:
                    await self.core_ops.read_page_content(page_identifier)
                else:
                    await self.core_ops.read_page_interactive()
            elif 'database' in user_input.lower():
                database_id = input("Enter database ID: ").strip()
                if database_id:
                    await self.core_ops.read_database_content(database_id)
            else:
                print("What would you like to read?")
                print("• read page [name/id] - Read page content")
                print("• read database [id] - Read database content")
        
        # SEARCH OPERATIONS
        elif 'search' in user_input.lower():
            search_term = user_input.lower().replace('search', '').strip()
            if not search_term:
                search_term = input("Enter search term: ").strip()
            await self.core_ops.search_content(search_term)
        
        # CREATE OPERATIONS
        elif 'create' in user_input.lower():
            if 'page' in user_input.lower():
                await self.core_ops.create_page_interactive()
            elif 'database' in user_input.lower():
                await self.core_ops.create_database_interactive()
            else:
                print("What would you like to create?")
                print("• create page - Create a new page")
                print("• create database - Create a new database")
        
        # UPDATE OPERATIONS
        elif 'update' in user_input.lower():
            await self.update_ops.update_content_interactive()
        
        # LIST OPERATIONS
        elif 'list' in user_input.lower():
            await self.core_ops.list_content_interactive()
        
        # ANALYTICS WORKFLOWS
        elif any(keyword in user_input.lower() for keyword in ['analyze', 'analytics', 'metrics', 'stats']):
            await self.analytics_ops.handle_analytics_requests(user_input)
        
        # BULK OPERATIONS
        elif any(keyword in user_input.lower() for keyword in ['bulk', 'multiple', 'batch']):
            await self.bulk_ops.handle_bulk_operations(user_input)
        
        else:
            print("💡 I can help you with:")
            print("• Search: 'search [term]'")
            print("• Read: 'read page [name/id]'")
            print("• Create: 'create page'")
            print("• Update: 'update content'")
            print("• List: 'list pages'")
            print("• Analytics: 'analyze workspace'")
            print("• Bulk operations: 'bulk pages'")
    
    def show_comprehensive_help(self):
        """Show comprehensive help information"""
        print("\n" + "="*60)
        print("🔧 COMPLETE NOTION SERVER V2 CAPABILITIES")
        print("="*60)
        
        print("\n📋 CORE OPERATIONS:")
        print("  • search [term] - Search pages and databases")
        print("  • read page [name/id] - Read page content")
        print("  • create page - Create new pages")
        print("  • update content - Add content to existing pages")
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
        print("  • 'update content'")
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