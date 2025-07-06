#!/usr/bin/env python3
"""
Terminal-based chat interface for the LangGraph agentic chatbot.
"""

import sys
from agentic_chatbot import AgenticChatbot
from config import config

def print_welcome():
    """Print welcome message and configuration info."""
    print("\n🤖 Welcome to LangGraph Agentic Chatbot")
    print("=" * 50)
    print("\n📝 Current Configuration:")
    print(f"Chat Model: {config.chat_model}")
    print(f"Temperature: {config.temperature}")
    print(f"Max History Pairs: {config.max_history_pairs}")
    print(f"LangSmith Project: {config.langsmith_project}")
    print(f"Tracing Enabled: {config.tracing_enabled}")
    print("\n" + "=" * 50)
    print("\nType 'exit', 'quit', or press Ctrl+C to end the conversation.")
    print("=" * 50)

def main():
    """Run the terminal chat interface."""
    try:
        # Initialize chatbot
        print("\n🔧 Initializing chatbot...")
        chatbot = AgenticChatbot()
        print("✅ Chatbot initialized successfully!")

        # Print welcome message
        print_welcome()

        # Main chat loop
        while True:
            try:
                # Get user input
                user_message = input("\nYou: ").strip()
                
                # Check for exit commands
                if user_message.lower() in ['exit', 'quit']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_message:
                    continue
                
                # Get chatbot response
                print("\n🤖 Thinking...")
                response = chatbot.chat(user_message)
                print(f"\nAssistant: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again.")
                continue
    
    except Exception as e:
        print(f"\n❌ Error initializing chatbot: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main()) 