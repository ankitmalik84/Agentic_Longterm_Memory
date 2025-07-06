"""
Configuration Management for Notion MCP Server
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ServerConfig:
    """Server configuration settings"""
    
    # Authentication
    notion_token: str = field(default_factory=lambda: os.getenv("NOTION_TOKEN", ""))
    
    # Server settings
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8081")))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # API settings
    max_page_size: int = field(default_factory=lambda: int(os.getenv("MAX_PAGE_SIZE", "100")))
    default_page_size: int = field(default_factory=lambda: int(os.getenv("DEFAULT_PAGE_SIZE", "20")))
    request_timeout: int = field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30")))
    
    # Content limits
    max_content_length: int = field(default_factory=lambda: int(os.getenv("MAX_CONTENT_LENGTH", "2000")))
    max_bulk_operations: int = field(default_factory=lambda: int(os.getenv("MAX_BULK_OPERATIONS", "50")))
    
    # Rate limiting
    rate_limit_requests: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "100")))
    rate_limit_window: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW", "60")))
    
    # Caching
    enable_cache: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHE", "false").lower() == "true")
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "300")))
    
    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))
    
    # Features
    enable_analytics: bool = field(default_factory=lambda: os.getenv("ENABLE_ANALYTICS", "true").lower() == "true")
    enable_bulk_operations: bool = field(default_factory=lambda: os.getenv("ENABLE_BULK_OPERATIONS", "true").lower() == "true")
    enable_content_updates: bool = field(default_factory=lambda: os.getenv("ENABLE_CONTENT_UPDATES", "true").lower() == "true")
    
    # CORS settings
    cors_origins: List[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
    
    def validate(self):
        """Validate configuration settings"""
        errors = []
        
        # Check required settings
        if not self.notion_token:
            errors.append("NOTION_TOKEN is required")
        
        if not self.notion_token.startswith("ntn_"):
            errors.append("NOTION_TOKEN must start with 'ntn_'")
        
        # Validate numeric ranges
        if not (1 <= self.port <= 65535):
            errors.append("PORT must be between 1 and 65535")
        
        if not (1 <= self.max_page_size <= 100):
            errors.append("MAX_PAGE_SIZE must be between 1 and 100")
        
        if not (1 <= self.default_page_size <= self.max_page_size):
            errors.append("DEFAULT_PAGE_SIZE must be between 1 and MAX_PAGE_SIZE")
        
        if not (1 <= self.request_timeout <= 300):
            errors.append("REQUEST_TIMEOUT must be between 1 and 300 seconds")
        
        if not (100 <= self.max_content_length <= 5000):
            errors.append("MAX_CONTENT_LENGTH must be between 100 and 5000 characters")
        
        if not (1 <= self.max_bulk_operations <= 100):
            errors.append("MAX_BULK_OPERATIONS must be between 1 and 100")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "notion_token": "***" if self.notion_token else "",
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "max_page_size": self.max_page_size,
            "default_page_size": self.default_page_size,
            "request_timeout": self.request_timeout,
            "max_content_length": self.max_content_length,
            "max_bulk_operations": self.max_bulk_operations,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "enable_analytics": self.enable_analytics,
            "enable_bulk_operations": self.enable_bulk_operations,
            "enable_content_updates": self.enable_content_updates,
            "cors_origins": self.cors_origins
        }
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables"""
        return cls()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ServerConfig":
        """Create configuration from dictionary"""
        return cls(**config_dict)


# Global configuration instance
config = ServerConfig()


def get_config() -> ServerConfig:
    """Get the global configuration instance"""
    return config


def validate_config():
    """Validate the current configuration"""
    config.validate()


def print_config():
    """Print current configuration (masking sensitive data)"""
    print("\n🔧 Notion MCP Server Configuration:")
    print("=" * 50)
    
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        if isinstance(value, list):
            value_str = ", ".join(str(v) for v in value)
        else:
            value_str = str(value)
        
        print(f"  {key.replace('_', ' ').title()}: {value_str}")
    
    print("=" * 50)