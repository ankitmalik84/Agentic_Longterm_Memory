# How MCP Tools Work: Complete Explanation

## 🎯 **Understanding the Magic**

MCP (Model Context Protocol) tools work through a sophisticated flow that connects your chatbot to external services. Here's the complete breakdown:

## 🔧 **1. Tool Definition (MCP Server Side)**

### The Decorators Explained

```python
# In src/utils/notion_mcp_server.py

@self.server.list_tools()  # ← This is the REGISTRATION decorator
async def list_tools() -> List[Tool]:
    """
    This function is called when a client asks:
    "What tools are available on this MCP server?"
    """
    return [
        Tool(
            name="search_notion_pages",        # ← Tool identifier
            description="Search for pages...", # ← What the tool does
            inputSchema={                      # ← Parameters it accepts
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        )
    ]

@self.server.call_tool()  # ← This is the EXECUTION decorator
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """
    This function is called when a client says:
    "Execute tool X with arguments Y"
    """
    if name == "search_notion_pages":
        return await self.search_pages(arguments)  # ← Route to implementation
    # ... handle other tools
```

### What the Decorators Do

1. **`@self.server.list_tools()`**

   - Registers the function as a "tool discovery" handler
   - When MCP client asks "what tools are available?", this function is called
   - Returns a list of available tools with their schemas

2. **`@self.server.call_tool()`**
   - Registers the function as a "tool execution" handler
   - When MCP client says "execute tool X", this function is called
   - Routes the call to the appropriate implementation method

## 🔄 **2. Tool Registration (Chatbot Side)**

### Making Tools Available to the LLM

```python
# In src/utils/chatbot_agentic_v3.py

# The chatbot creates function schemas for OpenAI API
self.agent_functions = [
    # ... existing functions
    {
        "name": "search_notion_pages",     # ← Must match MCP server tool name
        "description": "Search for pages in Notion workspace",
        "parameters": {                    # ← OpenAI function calling schema
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"}
            },
            "required": ["query"]
        }
    }
]
```

### Why This Duplication?

- **MCP Server**: Defines what tools exist and how they work
- **Chatbot**: Tells the LLM what functions it can call
- **Two different protocols**: MCP for tool execution, OpenAI for function calling

## 🎬 **3. Real-World Execution Flow**

### Example: User asks "Search for pages about 'project planning'"

```python
# Step 1: User message
user_message = "Search for pages about 'project planning' in my Notion workspace"

# Step 2: LLM sees available functions
response = self.client.chat.completions.create(
    model=self.chat_model,
    messages=[{"role": "user", "content": user_message}],
    functions=self.agent_functions,  # ← LLM sees search_notion_pages
    function_call="auto"
)

# Step 3: LLM decides to call search_notion_pages
if response.choices[0].message.function_call:
    function_name = "search_notion_pages"
    function_args = {"query": "project planning", "page_size": 10}

    # Step 4: Route to MCP client
    self.execute_function_call(function_name, function_args)
```

## 📡 **4. MCP Client-Server Communication**

### The Communication Bridge

```python
# In src/utils/mcp_client_manager.py

def call_tool_sync(self, server_name: str, tool_name: str, arguments: dict):
    """
    This is the bridge between your chatbot and MCP server
    """
    # Convert sync call to async for MCP
    future = self.executor.submit(
        self._run_async_call, server_name, tool_name, arguments
    )
    return future.result(timeout=30)

async def _call_tool_async(self, server_name: str, tool_name: str, arguments: dict):
    """
    This actually calls the MCP server
    """
    client = self.clients[server_name]  # ← MCP client connected to server

    # This triggers the MCP server's @call_tool() decorated function
    result = await client.call_tool(tool_name, arguments)
    return result
```

## 🔍 **5. MCP Server Execution**

### What Happens on the Server

```python
# When client.call_tool() is called, this function is triggered:

@self.server.call_tool()  # ← This decorator caught the call
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    if name == "search_notion_pages":
        return await self.search_pages(arguments)  # ← Route to implementation

# The actual implementation
async def search_pages(self, arguments: dict) -> List[TextContent]:
    query = arguments.get("query", "")

    # Make actual Notion API call
    results = self.notion.search(query=query, page_size=10)

    # Format results for MCP
    return [TextContent(
        type="text",
        text=f"Found {len(results['results'])} pages matching '{query}'"
    )]
```

## 🎯 **Complete Flow Diagram**

```
1. User: "Search for pages about 'project planning'"
   ↓
2. Chatbot.chat() → OpenAI API with functions=agent_functions
   ↓
3. LLM: "I'll call search_notion_pages with query='project planning'"
   ↓
4. execute_function_call("search_notion_pages", {"query": "project planning"})
   ↓
5. mcp_client_manager.call_tool_sync("notion", "search_notion_pages", {...})
   ↓
6. MCP Client → MCP Server (stdio/network communication)
   ↓
7. MCP Server @call_tool() decorator catches the call
   ↓
8. Routes to search_pages({"query": "project planning"})
   ↓
9. search_pages() → Notion API call
   ↓
10. Notion API → Returns search results
    ↓
11. search_pages() → Formats as TextContent
    ↓
12. MCP Server → Returns TextContent to MCP Client
    ↓
13. MCP Client → Returns result to chatbot
    ↓
14. Chatbot → Returns result to LLM
    ↓
15. LLM → Formats friendly response for user
    ↓
16. User sees: "I found 5 pages about project planning: ..."
```

## 🧠 **Key Insights**

### Why This Architecture?

1. **Separation of Concerns**

   - MCP Server: Handles external API integration
   - Chatbot: Handles conversation flow
   - LLM: Handles natural language understanding

2. **Reusability**

   - One MCP server can serve multiple chatbots
   - One chatbot can connect to multiple MCP servers
   - Tools are standardized across the ecosystem

3. **Scalability**
   - MCP servers can run locally or remotely
   - Multiple instances can be deployed
   - Load balancing is possible

### Why Not Direct Integration?

```python
# You COULD do this (direct integration):
def search_notion_pages(self, query: str):
    return self.notion.search(query=query)

# But MCP provides:
# ✅ Standardized protocol
# ✅ Language-agnostic servers
# ✅ Remote deployment capability
# ✅ Tool discovery
# ✅ Better error handling
# ✅ Ecosystem compatibility
```

## 🔧 **Tool Definition Best Practices**

### 1. Clear Tool Names

```python
# Good
"search_notion_pages"
"create_notion_page"
"get_user_profile"

# Bad
"search"
"create"
"get"
```

### 2. Detailed Descriptions

```python
# Good
"Search for pages in Notion workspace using text query"

# Bad
"Search pages"
```

### 3. Comprehensive Schemas

```python
# Good
{
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Text to search for in page titles and content"
        },
        "page_size": {
            "type": "integer",
            "description": "Number of results to return (1-100)",
            "minimum": 1,
            "maximum": 100,
            "default": 10
        }
    },
    "required": ["query"]
}

# Bad
{
    "type": "object",
    "properties": {
        "query": {"type": "string"}
    }
}
```

## 🚀 **Testing Your Understanding**

Run the explanation example:

```bash
python mcp_tools_explanation.py
```

This will show you exactly how the decorators and flow work with a simple example.

## 📋 **Summary**

MCP tools work through:

1. **Definition**: `@server.list_tools()` and `@server.call_tool()` decorators
2. **Registration**: Adding function schemas to `agent_functions`
3. **Discovery**: LLM sees available functions
4. **Selection**: LLM chooses appropriate function
5. **Routing**: Chatbot routes to MCP client
6. **Communication**: MCP client calls MCP server
7. **Execution**: MCP server executes the tool
8. **Response**: Results flow back to user

The "magic" is in the decorators - they create the bridge between the MCP protocol and your actual tool implementations!

## 🎯 **Next Steps**

1. **Try the test**: `python test_notion_mcp.py`
2. **Examine the logs**: See the flow in action
3. **Add new tools**: Follow the same pattern
4. **Scale up**: Deploy MCP servers remotely

The MCP architecture enables powerful, scalable AI integrations while maintaining clean separation of concerns!
