# Notion MCP Server V2 🚀

A comprehensive **Model Context Protocol (MCP) server** for Notion integration with enhanced functionality, robust error handling, production-ready features, and **bulletproof validation**.

## ✨ Features

### 🔧 **Core Operations**

- ✅ **Search**: Find pages and databases with advanced filtering
- ✅ **Page Operations**: Create, read, update pages with full content support
- ✅ **Content Management**: Add paragraphs, headings, bullet points, todos, **links, and bookmarks**
- ✅ **Database Operations**: List and query databases

### 🔗 **Advanced Content Types** _(NEW)_

- ✅ **Bookmarks**: Add external website links with URL validation
- ✅ **Link to Page**: Create internal links between Notion pages
- ✅ **Rich Content**: Support for all major Notion block types
- ✅ **Content Splitting**: Automatic handling of long content (2000+ chars)

### 📊 **Analytics & Insights**

- ✅ **Workspace Analytics**: Total pages, databases, recent activity
- ✅ **Content Analytics**: Structure analysis and metrics
- ✅ **Activity Tracking**: Recent edits and usage patterns
- ✅ **Performance Metrics**: Optimized with configurable timeouts

### 🔄 **Bulk Operations** _(OPTIMIZED)_

- ✅ **Smart Pagination**: Prevents timeouts with configurable limits
- ✅ **Bulk Content Addition**: Add multiple content blocks at once
- ✅ **Bulk Page Operations**: Create and manage multiple pages
- ✅ **Performance Controls**: Optional block counts for faster responses

### 🌐 **API Interfaces**

- ✅ **FastAPI REST API**: Production-ready HTTP endpoints
- ✅ **Interactive CLI**: Command-line interface for direct usage
- ✅ **MCP Compatible**: Full Model Context Protocol support
- ✅ **Agent Integration**: Unified endpoint for AI agents

### 🛡️ **Production Features** _(ENHANCED)_

- ✅ **Bulletproof Validation**: Comprehensive input validation and error handling
- ✅ **Configuration Management**: Environment-based settings
- ✅ **Smart Error Recovery**: Detailed error messages and recovery guidance
- ✅ **Health Checks**: Monitoring and status endpoints with feature detection
- ✅ **Structured Logging**: Configurable logging with performance insights
- ✅ **CORS Support**: Cross-origin resource sharing
- ✅ **Timeout Optimization**: Dynamic timeouts based on operation complexity

### 🧪 **Testing & Quality** _(COMPREHENSIVE)_

- ✅ **46KB Test Suite**: 1,158 lines of comprehensive tests
- ✅ **13+ Test Categories**: Core, content, bulk, links, analytics, edge cases
- ✅ **Validation Testing**: Tests for all error scenarios and edge cases
- ✅ **Performance Testing**: Timeout and optimization validation
- ✅ **Detailed Reporting**: JSON reports with timing and categorization

## 🏗️ Architecture

```
notion_mcp_server/
├── 📄 __init__.py           # Package initialization
├── 🔧 config.py             # Configuration management
├── 🌐 api_serverV2.py       # FastAPI REST API server (49KB)
├── 💻 serverV2.py           # Interactive CLI server
├── ⚙️ core_operations.py    # Basic CRUD operations
├── 📊 analytics_operations.py # Analytics and metrics
├── 🔄 bulk_operations.py    # Bulk processing
├── ✏️ update_operations.py  # Content updates (35KB)
├── 🛠️ notion_utils.py      # Utility functions
├── 🧪 test_server.py        # Comprehensive test suite (48KB)
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

### ✏️ **Add Content** _(ENHANCED)_

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
- `bookmark` - External website link _(NEW)_
- `link_to_page` - Internal page link _(NEW)_

### 🔗 **Link Content Types** _(NEW)_

**Add Bookmark (External Link):**

```http
POST /api/page/add-content
Content-Type: application/json

{
  "page_id": "page-id",
  "content_type": "bookmark",
  "content": "OpenAI Website",
  "url": "https://www.openai.com"
}
```

**Add Link to Page (Internal Link):**

```http
POST /api/page/add-content
Content-Type: application/json

{
  "page_id": "page-id",
  "content_type": "link_to_page",
  "content": "Link to related page",
  "page_reference": "target-page-id-or-title"
}
```

### 🔄 **Bulk Content Addition** _(ENHANCED)_

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
      "content_type": "bookmark",
      "url": "https://example.com",
      "content": "External Link"
    },
    {
      "content_type": "link_to_page",
      "page_reference": "other-page-id",
      "content": "Internal Link"
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

**Analytics types:** `workspace`, `content`, `activity`, `database`

### 🔄 **Bulk Operations** _(OPTIMIZED)_

```http
POST /api/bulk
Content-Type: application/json

{
  "operation": "list",
  "query": "{\"limit\": 10, \"include_block_counts\": false}"
}
```

**Optimization options:**

- `limit`: Number of pages to process (1-50)
- `include_block_counts`: Whether to calculate block counts (slower)

**Operations:** `list`, `analyze`, `create`

### 🤖 **Agent Integration**

```http
POST /api/agent/query
Content-Type: application/json

{
  "action": "search",
  "parameters": {
    "query": "search term",
    "page_size": 10
  }
}
```

**Available actions:** `search`, `read_page`, `create_page`, `add_content`, `bulk_add_content`, `analytics`, `bulk_operations`

## 🧪 Testing _(COMPREHENSIVE)_

Run the comprehensive test suite:

```bash
# Start the server first
python -m notion_mcp_server.api_serverV2

# In another terminal, run tests
cd src/notion_mcp_server
python test_server.py
```

**Test Coverage (1,158 lines, 13+ categories):**

- ✅ **Core Operations**: Health checks, search, page creation/reading
- ✅ **Content Addition**: All content types including links and bookmarks
- ✅ **Bulk Content**: Multiple content blocks and optimization
- ✅ **Link Functionality**: Bookmark and link_to_page validation
- ✅ **Analytics**: All analytics types and performance
- ✅ **Bulk Operations**: Optimized pagination and limits
- ✅ **Agent Integration**: All agent query actions
- ✅ **Edge Cases**: Error handling, validation, timeouts
- ✅ **Exception Handling**: Network issues, invalid inputs

**Test Features:**

- 🎯 **Detailed Reporting**: Success rates, timing, categorization
- 📊 **Performance Insights**: Response times and bottlenecks
- 📄 **JSON Reports**: Exportable test results with timestamps
- 🧹 **Cleanup Scripts**: Automatic test data management

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
    "parameters": {"query": "project notes"}
})

# Create a new page with links
response = requests.post("http://localhost:8081/api/agent/query", json={
    "action": "create_page",
    "parameters": {
        "title": "AI Generated Page",
        "content": "This page was created by an AI agent"
    }
})

# Add bookmark to page
response = requests.post("http://localhost:8081/api/agent/query", json={
    "action": "add_content",
    "parameters": {
        "page_id": "page-id",
        "content_type": "bookmark",
        "content": "Useful Resource",
        "url": "https://example.com"
    }
})
```

### With Your Chatbot

```python
# Already integrated in your chatbot_agentic_v3.py!
# Enhanced with ALL new functions:

# Core functions
server.notion_search_content()
server.notion_read_page()
server.notion_create_page()

# Content addition with links
server.notion_add_paragraph()
server.notion_add_heading()
server.notion_add_bullet_point()
server.notion_add_todo()

# Smart content helpers
server.notion_add_structured_content()  # Multi-section content
server.notion_add_smart_content()       # AI-friendly content parsing

# Bulk operations
server.notion_bulk_create_pages()
server.notion_bulk_list_pages()
server.notion_bulk_analyze_pages()

# Analytics
server.notion_workspace_analytics()
server.notion_content_analytics()
server.notion_activity_analytics()
```

## 📈 Performance Features _(ENHANCED)_

- **Async Operations**: Non-blocking I/O for better performance
- **Smart Timeouts**: Dynamic timeouts (30s standard, 60s bulk, 45s analytics)
- **Pagination Controls**: Configurable limits to prevent timeouts
- **Connection Pooling**: Efficient Notion API connections
- **Request Validation**: Fast input validation and sanitization
- **Error Recovery**: Graceful handling of API failures
- **Memory Efficient**: Optimized for low memory usage
- **Progress Yielding**: Prevents blocking during bulk operations

## 🛡️ Security & Validation Features _(BULLETPROOF)_

- **Token Validation**: Automatic Notion token validation
- **Input Sanitization**: Protection against malicious input
- **Comprehensive Validation**: All content types validated
  - Bookmark URLs must be valid HTTP/HTTPS
  - Page references must exist
  - Content length limits enforced
  - Required fields validation
- **Rate Limiting Ready**: Framework for rate limiting (configurable)
- **CORS Support**: Secure cross-origin requests
- **Environment Isolation**: Secure environment variable handling
- **HTTP Status Handling**: Proper error code processing

## 📋 Error Handling _(ENHANCED)_

The server provides detailed error messages for all scenarios:

### Validation Errors

- **Missing URLs**: "URL is required for bookmark content type"
- **Invalid Page References**: "Target page not found: page-name"
- **Empty Content**: "Content cannot be empty"
- **Invalid Content Types**: Clear list of supported types

### API Errors

- **Invalid Tokens**: Clear guidance for token setup
- **Missing Pages**: Helpful suggestions for page access
- **API Limits**: Graceful handling of Notion API limits
- **Network Issues**: Automatic retry mechanisms
- **Timeout Prevention**: Smart limits and pagination

### HTTP Status Codes

- **200**: Successful operations
- **400**: Validation errors (missing fields, invalid formats)
- **404**: Resource not found (pages, invalid references)
- **500**: Server errors (with detailed diagnostics)
- **503**: Server not initialized

## 🆔 Version History

### V2.1.0 (Current) _(MAJOR UPDATE)_

- 🔗 **Link Functionality**: Bookmarks and link_to_page support
- 🛡️ **Bulletproof Validation**: Comprehensive input validation
- ⚡ **Timeout Optimization**: Fixed bulk operations with smart pagination
- 🧪 **Enhanced Test Suite**: 48KB comprehensive testing (1,158 lines)
- 📊 **HTTP Status Handling**: Proper error code processing in tests
- 🎯 **Performance Controls**: Configurable timeouts and limits
- 📈 **Smart Content**: AI-friendly content parsing helpers

### V2.0.0 (Previous)

- ✅ Complete rewrite with enhanced features
- ✅ Configuration management system
- ✅ Basic test suite
- ✅ Production-ready error handling
- ✅ Bulk operations support
- ✅ Enhanced content management
- ✅ Agent integration endpoints

### V1.0.0 (Legacy)

- ✅ Basic MCP server functionality
- ✅ Core operations (search, read, create)
- ✅ Simple CLI interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run the comprehensive test suite: `python test_server.py`
5. Ensure all tests pass (aim for 90%+ success rate)
6. Submit a pull request

**Testing Requirements:**

- All new features must include tests
- Validation scenarios must be covered
- Performance implications should be documented
- Error handling paths must be tested

## 📞 Support

If you encounter issues:

1. **Check Configuration**: Ensure all environment variables are set correctly
2. **Verify Token**: Make sure your Notion token is valid and has proper permissions
3. **Run Health Check**: Visit `/health` endpoint to verify server status
4. **Run Test Suite**: Use `python test_server.py` to identify specific issues
5. **Check Logs**: Review server logs for detailed error messages
6. **Test Validation**: Ensure your content meets validation requirements

**Common Issues:**

- **Link validation errors**: Ensure URLs start with http/https
- **Timeout issues**: Use pagination controls for large operations
- **Page not found**: Verify page sharing with integration
- **Content too long**: Content blocks limited to 2000 characters

### 📧 **Contact Information**

For direct support or questions:

- **📱 Phone**: +918449035579
- **📧 Email**: ankitmalik844903@gmail.com
- **👨‍💻 Developer**: Ankit Malik

Feel free to reach out for:

- ✅ Technical support and troubleshooting
- ✅ Feature requests and suggestions
- ✅ Integration assistance
- ✅ Bug reports and issues
- ✅ Custom development needs

## 📄 License

This project is part of the Agentic Long-Term Memory system.

---

**🎉 Your Notion MCP Server V2.1 is bulletproof and production-ready!**

**⚡ New in V2.1:**

- 🔗 **Link Support** - Bookmarks and internal page links
- 🛡️ **Bulletproof Validation** - Comprehensive error prevention
- ⚡ **Timeout Optimization** - Smart pagination and limits
- 🧪 **48KB Test Suite** - Comprehensive testing and reporting
- 🎯 **Performance Controls** - Configurable timeouts and limits

**📊 Quality Metrics:**

- **1,158 lines** of test coverage
- **13+ test categories** including edge cases
- **90%+ success rate** target for all operations
- **Sub-5 second** response times for optimized operations
