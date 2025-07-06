#!/usr/bin/env python3
"""
Example usage of the LangGraph agentic chatbot with configuration.
"""

from agentic_chatbot import AgenticChatbot
from config import config

def main():
    """
    Demonstrate usage of the LangGraph chatbot with configuration.
    """
    print("🤖 LangGraph Agentic Chatbot Example")
    print("=" * 50)
    
    # Print current configuration
    print("\n📝 Current Configuration:")
    print(f"Chat Model: {config.chat_model}")
    print(f"Temperature: {config.temperature}")
    print(f"Max History Pairs: {config.max_history_pairs}")
    print(f"LangSmith Project: {config.langsmith_project}")
    print(f"Tracing Enabled: {config.tracing_enabled}")
    print("=" * 50)

    try:
        # Initialize chatbot
        print("\n🔧 Initializing chatbot...")
        chatbot = AgenticChatbot()
        print("✅ Chatbot initialized successfully!")

        # Example conversation
        print("\n💬 Starting example conversation...")
        
        # Example 1: Basic greeting
        message = "Hello! Can you help me understand how this chatbot works?"
        print(f"\nUser: {message}")
        response = chatbot.chat(message)
        print(f"Assistant: {response}")

        # Example 2: Function calling capability
        message = "Please remember that I prefer technical explanations with code examples."
        print(f"\nUser: {message}")
        response = chatbot.chat(message)
        print(f"Assistant: {response}")

        # Example 3: Memory usage
        message = "What did I ask you to remember about my preferences?"
        print(f"\nUser: {message}")
        response = chatbot.chat(message)
        print(f"Assistant: {response}")

        print("\n✨ Example conversation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during example: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main()) 