# Notion MCP Server V2 🚀

A comprehensive **Model Context Protocol (MCP) server** for Notion integration with enhanced functionality, robust error handling, and production-ready features.

## ✨ Features

### 🔧 **Core Operations**

- ✅ **Search**: Find pages and databases with advanced filtering
- ✅ **Page Operations**: Create, read, update pages with full content support
- ✅ **Content Management**: Add paragraphs, headings, bullet points, todos
- ✅ **Database Operations**: List and query databases

### 📊 **Analytics & Insights**

- ✅ **Workspace Analytics**: Total pages, databases, recent activity
- ✅ **Content Analytics**: Structure analysis and metrics
- ✅ **Activity Tracking**: Recent edits and usage patterns

### 🔄 **Bulk Operations**

- ✅ **Bulk Content Addition**: Add multiple content blocks at once
- ✅ **Bulk Page Operations**: Create and manage multiple pages
- ✅ **Batch Processing**: Efficient handling of large operations

### 🌐 **API Interfaces**

- ✅ **FastAPI REST API**: Production-ready HTTP endpoints
- ✅ **Interactive CLI**: Command-line interface for direct usage
- ✅ **MCP Compatible**: Full Model Context Protocol support
- ✅ **Agent Integration**: Unified endpoint for AI agents

### 🛡️ **Production Features**

- ✅ **Configuration Management**: Environment-based settings
- ✅ **Error Handling**: Comprehensive error messages and recovery
- ✅ **Health Checks**: Monitoring and status endpoints
- ✅ **Logging**: Structured logging with configurable levels
- ✅ **CORS Support**: Cross-origin resource sharing
- ✅ **Input Validation**: Request validation and sanitization

## 🏗️ Architecture

```
notion_mcp_server/
├── 📄 __init__.py           # Package initialization
├── 🔧 config.py             # Configuration management
├── 🌐 api_serverV2.py       # FastAPI REST API server
├── 💻 serverV2.py           # Interactive CLI server
├── ⚙️ core_operations.py    # Basic CRUD operations
├── 📊 analytics_operations.py # Analytics and metrics
├── 🔄 bulk_operations.py    # Bulk processing
├── ✏️ update_operations.py  # Content updates
├── 🛠️ notion_utils.py      # Utility functions
├── 🧪 test_server.py        # Comprehensive tests
└── 📖 README.md             # This file
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- Notion account with integration token
- pip or conda package manager

### Setup

1. **Install Dependencies**

```bash
pip install notion-client fastapi uvicorn python-dotenv pydantic requests
```

2. **Environment Configuration**
   Create a `.env` file in your project root:

```env
# Required
NOTION_TOKEN=ntn_your_integration_token_here

# Optional Server Settings
HOST=0.0.0.0
PORT=8081
DEBUG=false

# Optional Feature Settings
MAX_PAGE_SIZE=100
DEFAULT_PAGE_SIZE=20
MAX_CONTENT_LENGTH=2000
ENABLE_ANALYTICS=true
ENABLE_BULK_OPERATIONS=true

# Optional Logging
LOG_LEVEL=INFO
```

3. **Get Your Notion Token**

- Go to [Notion Integrations](https://www.notion.so/profile/integrations)
- Create a new integration
- Copy the token (starts with `ntn_`)
- Share your pages/databases with the integration

## 🚀 Usage

### 1. FastAPI Server (Production)

**Start the server:**

```bash
python -m notion_mcp_server.api_serverV2
```

**Server will be available at:**

- API: `http://localhost:8081`
- Documentation: `http://localhost:8081/docs`
- Health Check: `http://localhost:8081/health`

### 2. Interactive CLI

```bash
python -m notion_mcp_server.serverV2
```

### 3. Python Integration

```python
from notion_mcp_server import ComprehensiveNotionServer
import asyncio

async def example():
    server = ComprehensiveNotionServer("your_notion_token")
    await server.core_ops.search_content("search term")

asyncio.run(example())
```

## 📚 API Documentation

### 🔍 **Search Endpoint**

```http
POST /api/search
Content-Type: application/json

{
  "query": "search term",
  "page_size": 10
}
```

### 📄 **Create Page**

```http
POST /api/page/create
Content-Type: application/json

{
  "title": "My New Page",
  "content": "Initial content",
  "parent_id": "optional-parent-page-id"
}
```

### 📖 **Read Page**

```http
POST /api/page/read
Content-Type: application/json

{
  "identifier": "page-id-or-title"
}
```

### ✏️ **Add Content**

```http
POST /api/page/add-content
Content-Type: application/json

{
  "page_id": "page-id",
  "content_type": "paragraph",
  "content": "New paragraph content"
}
```

**Supported content types:**

- `paragraph` - Regular text
- `heading_1` - Large heading
- `heading_2` - Medium heading
- `heading_3` - Small heading
- `bulleted_list_item` - Bullet point
- `to_do` - Checkbox item

### 🔄 **Bulk Content Addition**

```http
POST /api/page/bulk-add-content
Content-Type: application/json

{
  "page_id": "page-id",
  "items": [
    {
      "content_type": "heading_2",
      "content": "Section Title"
    },
    {
      "content_type": "paragraph",
      "content": "Paragraph content"
    },
    {
      "content_type": "to_do",
      "content": "Task item",
      "checked": false
    }
  ]
}
```

### 📊 **Analytics**

```http
POST /api/analytics
Content-Type: application/json

{
  "type": "workspace"
}
```

### 🔄 **Bulk Operations**

```http
POST /api/bulk
Content-Type: application/json

{
  "operation": "list_pages"
}
```

### 🤖 **Agent Integration**

```http
POST /api/agent/query
Content-Type: application/json

{
  "action": "search",
  "params": {
    "query": "search term",
    "page_size": 10
  }
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Start the server first
python -m notion_mcp_server.api_serverV2

# In another terminal, run tests
python -m notion_mcp_server.test_server
```

**Test Coverage:**

- ✅ Health checks
- ✅ Search functionality
- ✅ Page creation and reading
- ✅ Content addition (single and bulk)
- ✅ Analytics endpoints
- ✅ Bulk operations
- ✅ Agent integration

## ⚙️ Configuration

### Environment Variables

| Variable                 | Default      | Description                   |
| ------------------------ | ------------ | ----------------------------- |
| `NOTION_TOKEN`           | _(required)_ | Your Notion integration token |
| `HOST`                   | `0.0.0.0`    | Server host address           |
| `PORT`                   | `8081`       | Server port                   |
| `DEBUG`                  | `false`      | Enable debug mode             |
| `MAX_PAGE_SIZE`          | `100`        | Maximum results per page      |
| `DEFAULT_PAGE_SIZE`      | `20`         | Default results per page      |
| `MAX_CONTENT_LENGTH`     | `2000`       | Maximum content block length  |
| `ENABLE_ANALYTICS`       | `true`       | Enable analytics endpoints    |
| `ENABLE_BULK_OPERATIONS` | `true`       | Enable bulk operations        |
| `LOG_LEVEL`              | `INFO`       | Logging level                 |

### Configuration Validation

The server automatically validates all configuration on startup and provides clear error messages for invalid settings.

## 🔧 Integration Examples

### With AI Agents

```python
import requests

# Search for content
response = requests.post("http://localhost:8081/api/agent/query", json={
    "action": "search",
    "params": {"query": "project notes"}
})

# Create a new page
response = requests.post("http://localhost:8081/api/agent/query", json={
    "action": "create_page",
    "params": {
        "title": "AI Generated Page",
        "content": "This page was created by an AI agent"
    }
})
```

### With Your Chatbot

```python
# Already integrated in your chatbot_agentic_v3.py!
# The server provides all the notion_* functions:
# - notion_search_content()
# - notion_read_page()
# - notion_create_page()
# - notion_add_paragraph()
# - notion_add_heading()
# - And many more...
```

## 📈 Performance Features

- **Async Operations**: Non-blocking I/O for better performance
- **Connection Pooling**: Efficient Notion API connections
- **Request Validation**: Fast input validation and sanitization
- **Error Recovery**: Graceful handling of API failures
- **Memory Efficient**: Optimized for low memory usage

## 🛡️ Security Features

- **Token Validation**: Automatic Notion token validation
- **Input Sanitization**: Protection against malicious input
- **Rate Limiting Ready**: Framework for rate limiting (configurable)
- **CORS Support**: Secure cross-origin requests
- **Environment Isolation**: Secure environment variable handling

## 📋 Error Handling

The server provides detailed error messages for common issues:

- **Invalid Tokens**: Clear guidance for token setup
- **Missing Pages**: Helpful suggestions for page access
- **API Limits**: Graceful handling of Notion API limits
- **Network Issues**: Automatic retry mechanisms
- **Validation Errors**: Detailed field-level error messages

## 🆔 Version History

### V2.0.0 (Current)

- ✅ Complete rewrite with enhanced features
- ✅ Configuration management system
- ✅ Comprehensive test suite
- ✅ Production-ready error handling
- ✅ Bulk operations support
- ✅ Enhanced content management
- ✅ Agent integration endpoints

### V1.0.0 (Previous)

- ✅ Basic MCP server functionality
- ✅ Core operations (search, read, create)
- ✅ Simple CLI interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run the test suite: `python -m notion_mcp_server.test_server`
5. Submit a pull request

## 📞 Support

If you encounter issues:

1. **Check Configuration**: Ensure all environment variables are set correctly
2. **Verify Token**: Make sure your Notion token is valid and has proper permissions
3. **Check Logs**: Review server logs for detailed error messages
4. **Run Tests**: Use the test suite to identify specific issues
5. **Health Check**: Visit `/health` endpoint to verify server status

## 📄 License

This project is part of the Agentic Long-Term Memory system. Please refer to the main project license.

---

**🎉 Your Notion MCP Server V2 is ready for production use!**
