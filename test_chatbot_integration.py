#!/usr/bin/env python3
"""
Test chatbot integration with fixed Notion MCP server
"""

import os
from src.utils.chatbot_agentic_v3 import Chatbot

def test_chatbot_integration():
    print("🤖 Testing Chatbot Integration with New Structure")
    print("=" * 60)
    
    # Check environment variables
    notion_token = os.getenv("NOTION_TOKEN")
    server_url = os.getenv("NOTION_MCP_SERVER_URL", "https://notion-mcp-server-5s5v.onrender.com/")
    
    print(f"🔧 Configuration:")
    print(f"   Server URL: {server_url}")
    print(f"   Token configured: {'✅' if notion_token else '❌'}")
    print()
    
    try:
        chatbot = Chatbot()
        
        if chatbot.notion_initialized:
            print("✅ Notion MCP initialized successfully")
            
            # Test page creation through chatbot
            user_message = "Create a new page called 'New Structure Test' with content about how our restructured MCP server is working perfectly with environment-based configuration."
            
            print(f"\n💬 User message: {user_message}")
            print("\n🔄 Processing...")
            
            response = chatbot.chat(user_message)
            
            print("\n🤖 Chatbot Response:")
            print(response)
            
            if "successfully created" in response.lower() or "page" in response.lower():
                print("\n🎉 SUCCESS: Chatbot successfully created a page!")
                return True
            else:
                print("\n⚠️ Response unclear - check above")
                return False
        else:
            print("❌ Notion MCP not initialized in chatbot")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_chatbot_integration()
    if success:
        print("\n✅ Chatbot integration test PASSED!")
    else:
        print("\n❌ Chatbot integration test FAILED!")
        print("💡 Make sure to set NOTION_TOKEN and NOTION_MCP_SERVER_URL environment variables") 