#!/usr/bin/env python3
"""
Test script for the LangGraph Agentic Chatbot implementation.
This script validates that the chatbot can be initialized and basic functionality works.
"""

import sys
import os
import traceback

# Add the langgraph directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'langgraph'))

def test_initialization():
    """Test if the LangGraph agent can be initialized successfully."""
    try:
        from langgraph.agentic_chatbot import AgenticChatbot
        print("✅ Successfully imported AgenticChatbot")
        
        # Try to initialize
        chatbot = AgenticChatbot()
        print("✅ Successfully initialized AgenticChatbot")
        
        return True, chatbot
    except Exception as e:
        print(f"❌ Failed to initialize AgenticChatbot: {str(e)}")
        traceback.print_exc()
        return False, None

def test_basic_chat(chatbot):
    """Test basic chat functionality."""
    try:
        response = chatbot.chat("Hello, this is a test message.")
        print(f"✅ Basic chat test successful. Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Basic chat test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_state_import():
    """Test if the AgentState can be imported."""
    try:
        from langgraph.agent_state import AgentState
        print("✅ Successfully imported AgentState")
        return True
    except Exception as e:
        print(f"❌ Failed to import AgentState: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing LangGraph Agentic Chatbot")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports...")
    state_import_success = test_state_import()
    
    # Test initialization
    print("\n2. Testing initialization...")
    init_success, chatbot = test_initialization()
    
    # Test basic functionality
    chat_success = False
    if init_success and chatbot:
        print("\n3. Testing basic chat...")
        chat_success = test_basic_chat(chatbot)
    else:
        print("\n3. Skipping chat test due to initialization failure")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   State Import: {'✅ PASS' if state_import_success else '❌ FAIL'}")
    print(f"   Initialization: {'✅ PASS' if init_success else '❌ FAIL'}")
    print(f"   Basic Chat: {'✅ PASS' if chat_success else '❌ FAIL'}")
    
    if all([state_import_success, init_success, chat_success]):
        print("\n🎉 All tests passed! The LangGraph agent is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 