"""
Configuration settings for the LangGraph implementation.
Handles environment variables, model settings, and other configurations.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LangGraphConfig:
    """Configuration class for LangGraph implementation."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4o")
        self.summary_model = os.getenv("SUMMARY_MODEL", "gpt-4o")
        self.rag_model = os.getenv("RAG_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("TEMPERATURE", "0.0"))
        
        # LangSmith Configuration
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        # Remove any trailing slashes and ensure proper URL format
        base_url = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com").rstrip('/')
        self.langsmith_endpoint = base_url
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "memory-agent")
        self.langsmith_tracing = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
        # Alias for langsmith_tracing to maintain compatibility
        self.tracing_enabled = self.langsmith_tracing
        
        # Set environment variables for LangSmith
        if self.langsmith_tracing:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = self.langsmith_endpoint
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key or ""
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project
        
        # Directory Configuration
        self.db_path = os.getenv("DB_PATH", "data/chatbot.db")
        self.vectordb_dir = os.getenv("VECTORDB_DIR", "data/vectordb")
        
        # Chat History Configuration
        self.max_history_pairs = int(os.getenv("MAX_HISTORY_PAIRS", "2"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.max_characters = int(os.getenv("MAX_CHARACTERS", "1000"))
        
        # Function Call Configuration
        self.max_function_calls = int(os.getenv("MAX_FUNCTION_CALLS", "3"))

        # Vector DB Configuration
        self.collection_name = os.getenv("COLLECTION_NAME", "chat_history")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.k = int(os.getenv("K", "3"))
        
        # Validate required configurations
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration settings."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env")
            
        if not self.langsmith_api_key and self.langsmith_tracing:
            raise ValueError("LangSmith API key is required for tracing. Set LANGSMITH_API_KEY in .env")
    
    def get_langsmith_config(self) -> Dict[str, Any]:
        """Get LangSmith configuration dictionary."""
        return {
            "api_key": self.langsmith_api_key,
            "api_url": self.langsmith_endpoint
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration dictionary."""
        return {
            "api_key": self.openai_api_key,
            "chat_model": self.chat_model,
            "summary_model": self.summary_model,
            "rag_model": self.rag_model,
            "temperature": self.temperature
        }
    
    def get_db_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "db_path": self.db_path,
            "vectordb_dir": self.vectordb_dir
        }
    
    def get_chat_config(self) -> Dict[str, Any]:
        """Get chat configuration dictionary."""
        return {
            "max_history_pairs": self.max_history_pairs,
            "max_tokens": self.max_tokens,
            "max_characters": self.max_characters,
            "max_function_calls": self.max_function_calls
        }

    def get_vectordb_config(self) -> Dict[str, Any]:
        """Get vector database configuration dictionary."""
        return {
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "k": self.k
        }

# Create a global instance
config = LangGraphConfig() 