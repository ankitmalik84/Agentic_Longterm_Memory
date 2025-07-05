#!/usr/bin/env python3
"""
Test script for Notion ServerV2 integration with chatbot_agentic_v3
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append('src')

from utils.chatbot_agentic_v3 import Chatbot

load_dotenv()

def test_notion_integration():
    """Test the Notion integration with the chatbot"""
    
    print("🚀 Testing Notion ServerV2 Integration with Chatbot")
    print("=" * 60)
    
    # Initialize chatbot
    try:
        chatbot = Chatbot()
        print("✅ Chatbot initialized successfully!")
        
        # Check if Notion is available
        if chatbot.notion_client:
            print("✅ Notion integration is active!")
            print(f"📊 Available Notion functions: {len([f for f in chatbot.agent_functions if 'notion' in str(f)])}")
        else:
            print("❌ Notion integration not available (check NOTION_TOKEN)")
            return
            
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        return
    
    # Test some Notion operations
    print("\n🔍 Testing Notion Operations:")
    print("-" * 40)
    
    # Test 1: Search content
    print("1. Testing search function...")
    try:
        state, result = chatbot.notion_search_content("test")
        print(f"   Status: {state}")
        print(f"   Result: {result[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: List pages
    print("\n2. Testing list pages function...")
    try:
        state, result = chatbot.notion_list_pages(limit=3)
        print(f"   Status: {state}")
        print(f"   Result: {result[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Workspace analytics
    print("\n3. Testing workspace analytics...")
    try:
        state, result = chatbot.notion_workspace_analytics()
        print(f"   Status: {state}")
        print(f"   Result: {result[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Integration test completed!")
    print("\n💡 Available Notion Functions:")
    notion_functions = [
        "notion_search_content - Search pages and databases",
        "notion_read_page - Read page content",
        "notion_create_page - Create new pages",
        "notion_list_pages - List all pages",
        "notion_list_databases - List all databases",
        "notion_workspace_analytics - Get workspace analytics",
        "notion_content_analytics - Get content analytics", 
        "notion_activity_analytics - Get activity analytics",
        "notion_add_paragraph - Add paragraph to page",
        "notion_add_heading - Add heading to page",
        "notion_add_bullet_point - Add bullet point to page",
        "notion_add_todo - Add to-do item to page",
        "notion_bulk_create_pages - Create multiple pages",
        "notion_bulk_list_pages - List pages with details",
        "notion_bulk_analyze_pages - Analyze pages"
    ]
    
    for func in notion_functions:
        print(f"  • {func}")

def test_chat_with_notion():
    """Test chatbot conversation with Notion capabilities"""
    
    print("\n🤖 Testing Chatbot Chat with Notion Functions")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = Chatbot()
    
    # Test chat messages that should trigger Notion functions
    test_messages = [
        "Can you search for pages about 'project' in my Notion workspace?",
        "List all pages in my Notion workspace",
        "Show me analytics for my Notion workspace",
        "Create a new page called 'Test Page' with some content"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        print("-" * 30)
        
        try:
            response = chatbot.chat(message)
            print(f"Response: {response[:300]}...")
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    # Check environment
    if not os.getenv("NOTION_TOKEN") and not os.getenv("NOTION_API_KEY"):
        print("❌ NOTION_TOKEN or NOTION_API_KEY not found in environment variables")
        print("💡 Please set up your Notion integration token first")
        sys.exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please set up your OpenAI API key first")
        sys.exit(1)
    
    # Run tests
    test_notion_integration()
    
    # Uncomment to test chat functionality
    # test_chat_with_notion() 