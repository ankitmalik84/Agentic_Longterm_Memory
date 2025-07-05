#!/usr/bin/env python3
"""
Simple test script to verify Notion token
"""
import os
from dotenv import load_dotenv

def test_notion_token():
    # Load environment
    load_dotenv()
    
    # Get token
    token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    
    print(f"🔍 Token found: {'✅ Yes' if token else '❌ No'}")
    
    if not token:
        print("❌ No token found in environment variables")
        print("💡 Set NOTION_TOKEN environment variable")
        return False
    
    # Test basic connection
    try:
        from notion_client import Client
        print("✅ notion-client imported successfully")
        
        client = Client(auth=token)
        print("✅ Client created successfully")
        
        # Test API call
        user_info = client.users.me()
        print(f"✅ API call successful!")
        print(f"📧 User: {user_info.get('name', 'N/A')} ({user_info.get('id', 'N/A')})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install notion-client")
        return False
    except Exception as e:
        print(f"❌ API error: {e}")
        print(f"📋 Error type: {type(e).__name__}")
        print("💡 Check your NOTION_TOKEN is valid")
        return False

if __name__ == "__main__":
    success = test_notion_token()
    exit(0 if success else 1) 