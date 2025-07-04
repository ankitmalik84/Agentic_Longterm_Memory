# MCP Notion Integration

This integration adds Notion support to your chatbot using the Model Context Protocol (MCP).

## 🚀 Features

- **Search Notion Pages**: Search through your Notion workspace
- **Get Page Content**: Retrieve detailed content from specific pages
- **Create New Pages**: Create new pages in your Notion workspace
- **Query Databases**: Search and filter Notion databases

## 📋 Prerequisites

1. **Notion Integration Token**: You need a Notion integration token
2. **Python 3.11+**: Required for MCP support
3. **Dependencies**: Install required packages

## 🔧 Installation

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:

   ```bash
   export NOTION_TOKEN="your_notion_token_here"
   ```

   Or add to your `.env` file:

   ```
   NOTION_TOKEN=your_notion_token_here
   ```

## 🎯 Usage

### Option 1: Integrated with Chatbot

The MCP Notion integration is automatically initialized when you create a `Chatbot` instance:

```python
from src.utils.chatbot_agentic_v3 import Chatbot

# Initialize chatbot with Notion integration
chatbot = Chatbot()

# Chat with Notion capabilities
response = chatbot.chat("Search for pages about 'project planning' in my Notion workspace")
print(response)
```

### Option 2: Standalone MCP Server

Run the MCP server independently:

```bash
# Set your token
export NOTION_TOKEN="your_notion_token_here"

# Run the server
python -m src.utils.notion_mcp_server
```

### Option 3: Docker Deployment

Use Docker for containerized deployment:

```bash
# Build and run with docker-compose
cd docker
docker-compose up -d

# Or build manually
docker build -f docker/Dockerfile.notion-mcp -t notion-mcp-server .
docker run -e NOTION_TOKEN="your_token" -p 8080:8080 notion-mcp-server
```

## 🛠️ Available Functions

Your chatbot now has access to these Notion functions:

### 1. Search Notion Pages

```python
# Example: "Search for pages about 'marketing' in my Notion workspace"
function_name: "search_notion_pages"
arguments: {
    "query": "marketing",
    "page_size": 10
}
```

### 2. Get Page Content

```python
# Example: "Get the content of page ID abc123"
function_name: "get_notion_page"
arguments: {
    "page_id": "abc123"
}
```

### 3. Create New Page

```python
# Example: "Create a new page called 'Meeting Notes' with content 'Today's agenda...'"
function_name: "create_notion_page"
arguments: {
    "title": "Meeting Notes",
    "content": "Today's agenda...",
    "parent_id": "optional_parent_id"
}
```

### 4. Query Database

```python
# Example: "Search the tasks database for items containing 'urgent'"
function_name: "get_notion_database"
arguments: {
    "database_id": "database_id_here",
    "filter_property": "Name",
    "filter_value": "urgent"
}
```

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
python test_notion_mcp.py
```

Expected output:

```
🧪 MCP Notion Integration Test Suite
============================================================
✅ NotionMCPServer initialized successfully
✅ Notion client: True
✅ MCP server: True
✅ Standalone server test completed!

✅ Chatbot initialized successfully
✅ Notion MCP server initialized successfully
📋 Available functions: 6
  1. <function add_user_info_to_database>
  2. <function search_vector_db>
  3. search_notion_pages
  4. get_notion_page
  5. create_notion_page
  6. get_notion_database

🎉 All tests passed! MCP Notion integration is working correctly.
```

## 🔄 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your Chatbot  │───▶│  MCP Client     │───▶│  Notion MCP     │
│                 │    │  Manager        │    │  Server         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │   Notion API    │
                                               └─────────────────┘
```

## 📝 Example Chat Interactions

Here are some example conversations your chatbot can now handle:

**User**: "Search for pages about 'project planning' in my Notion workspace"
**Bot**: _Uses search_notion_pages function and returns results_

**User**: "Create a new page called 'Weekly Review' with content about this week's accomplishments"
**Bot**: _Uses create_notion_page function and creates the page_

**User**: "Get the content from page ID abc123"
**Bot**: _Uses get_notion_page function and returns the page content_

## 🛡️ Security

- The Notion token is securely handled through environment variables
- MCP server runs in isolated process
- All API calls use official Notion SDK

## 🐛 Troubleshooting

### Common Issues:

1. **"Notion MCP server failed to initialize"**

   - Check your `NOTION_TOKEN` environment variable
   - Ensure the token has proper permissions
   - Verify internet connectivity

2. **"Function call failed"**

   - Check if the page/database IDs are valid
   - Ensure your integration has access to the requested resources
   - Review the error message for specific details

3. **"Import Error"**
   - Run `pip install -r requirements.txt` to install dependencies
   - Check Python version (3.11+ required)

### Debug Mode:

Enable debug logging by setting:

```bash
export MCP_DEBUG=1
```

## 📚 Next Steps

1. **Extend Functions**: Add more Notion operations (update pages, manage databases)
2. **Add Authentication**: Implement OAuth flow for better user experience
3. **Create Templates**: Set up page templates for common use cases
4. **Add Webhooks**: Enable real-time updates from Notion

## 🤝 Contributing

Feel free to extend this integration:

- Add new Notion operations
- Improve error handling
- Add more test cases
- Create documentation

## 📄 License

This MCP Notion integration follows the same license as the main project.
