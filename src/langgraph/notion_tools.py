from langchain.tools import tool
import requests
from datetime import datetime
import json
from typing import List, Optional

from .notion_types import (
    # Literal types
    NotionContentType,
    AnalyticsType,
    BulkOperationType,
    AgentActionType,
    
    # Search types
    NotionSearchResponse,
    
    # Page types
    NotionPageResponse,
    
    # Create page types
    NotionCreatePageResponse,
    
    # Content addition types
    NotionAddContentResponse,
    
    # Analytics types
    NotionAnalyticsResponse,

    # Bulk operation types
    NotionContentItem,
    NotionBulkAddContentResponse,
    NotionBulkResponse,
    BulkOperationQuery,
    
    # Agent query types
    AgentQueryParameters,
    AgentQueryResponse
)

@tool
def search_notion(query: str, page_size: int = 10) -> NotionSearchResponse:
    """
    Searches Notion pages and databases using the MCP Notion API.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/search
    
    Args:
        query (str): The search query string
        page_size (int, optional): Number of results to return. Defaults to 10.
        
    Returns:
        NotionSearchResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (dict): Contains:
                - results (List[NotionSearchResult]): List of found pages
                - total_count (int): Total number of results
                - query (str): The original search query
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example Response:
        {
            "success": true,
            "data": {
                "results": [
                    {
                        "id": "22750c4e-aa2a-81c3-9c41-ee93538f8508",
                        "object": "page",
                        "created_time": "2025-07-05T14:39:00.000Z",
                        "last_edited_time": "2025-07-07T06:02:00.000Z",
                        "url": "https://www.notion.so/AWS-22750c4eaa2a81c39c41ee93538f8508",
                        "title": "AWS"
                    }
                ],
                "total_count": 1,
                "query": "aws"
            },
            "message": "Found 1 results",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/search with query: {query}, page_size: {page_size} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/search",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "page_size": page_size
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to call Notion MCP search API {e}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def read_notion_page(identifier: str) -> NotionPageResponse:
    """
    Reads the content of a specific Notion page by ID or title.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/page/read
    
    Args:
        identifier (str): The page ID or title to read
        
    Returns:
        NotionPageResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (NotionPageData): Contains:
                - id (str): Page ID
                - title (str): Page title
                - created_time (str): Creation timestamp
                - last_edited_time (str): Last edit timestamp
                - url (str): Notion page URL
                - properties (dict): Page properties including title
                - content (List[NotionPageContent]): List of content blocks
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example Response:
        {
            "success": true,
            "data": {
                "id": "22750c4e-aa2a-81c3-9c41-ee93538f8508",
                "title": "AWS",
                "created_time": "2025-07-05T14:39:00.000Z",
                "last_edited_time": "2025-07-07T06:02:00.000Z",
                "url": "https://www.notion.so/AWS-22750c4eaa2a81c39c41ee93538f8508",
                "properties": {
                    "title": {
                        "id": "title",
                        "type": "title",
                        "title": [...]
                    }
                },
                "content": [
                    {
                        "id": "22750c4e-aa2a-814e-b994-f80196521d2f",
                        "type": "paragraph",
                        "created_time": "2025-07-05T14:40:00.000Z",
                        "last_edited_time": "2025-07-05T14:40:00.000Z",
                        "text": "🚀 Integrating AWS with AI Agents",
                        "has_children": false
                    }
                ]
            },
            "message": "Page retrieved successfully",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/page/read for identifier: {identifier} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/page/read",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "identifier": identifier
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to read Notion page: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def create_notion_page(title: str, content: str = "", parent_id: str = "") -> NotionCreatePageResponse:
    """
    Creates a new page in Notion. If parent_id is empty, creates a root page. Otherwise creates a subpage under the specified parent.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/page/create
    
    Args:
        title (str): The title of the new page
        content (str, optional): Initial content for the page. Defaults to empty string.
        parent_id (str, optional): ID of parent page. If empty, creates root page. Defaults to empty string.
        
    Returns:
        NotionCreatePageResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (NotionCreatePageData): Contains:
                - id (str): New page ID
                - title (str): Page title
                - url (str): Notion page URL
                - created_time (str): Creation timestamp
                - parent_id (str): ID of parent page (if any)
                - content_blocks_created (int): Number of content blocks created
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example Response:
        {
            "success": true,
            "data": {
                "id": "22950c4e-aa2a-81f2-86e8-e80916333349",
                "title": "ai agent tutorial",
                "url": "https://www.notion.so/ai-agent-tutorial-22950c4eaa2a81f286e8e80916333349",
                "created_time": "2025-07-07T18:08:00.000Z",
                "parent_id": "22150c4e-aa2a-8078-b15a-cd26efe9dfb1",
                "content_blocks_created": 1
            },
            "message": "Page created successfully",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/page/create with title: {title} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/page/create",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "title": title,
                "content": content,
                "parent_id": parent_id
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create Notion page: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def add_content_to_notion_page(
    page_id: str,
    content_type: NotionContentType,
    content: str,
    checked: bool = False,
    url: str = "",
    page_reference: str = ""
) -> NotionAddContentResponse:
    """
    Adds a content block to a Notion page.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/page/add-content
    
    Args:
        page_id (str): The ID of the page to add content to
        content_type (str): Type of content block. One of:
            - paragraph: Basic text block
            - heading_1: Large heading
            - heading_2: Medium heading
            - heading_3: Small heading
            - bulleted_list_item: Bullet point
            - to_do: Checkbox item
            - bookmark: Web bookmark
            - link_to_page: Link to another Notion page
        content (str): The text content for the block
        checked (bool, optional): For to_do items only. Defaults to False.
        url (str, optional): For bookmark and link_to_page types. Defaults to empty string.
        page_reference (str, optional): For link_to_page type - can be page ID or title. Defaults to empty string.
        
    Returns:
        NotionAddContentResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (NotionAddContentData): Contains:
                - page_id (str): ID of the page
                - content_type (str): Type of content added
                - blocks_added (int): Number of blocks added
                - block_ids (List[str]): IDs of created blocks
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example Response:
        {
            "success": true,
            "data": {
                "page_id": "22950c4e-aa2a-81f2-86e8-e80916333349",
                "content_type": "bulleted_list_item",
                "blocks_added": 1,
                "block_ids": [
                    "22950c4e-aa2a-819c-91b8-ca1ec48dded2"
                ]
            },
            "message": "Added 1 bulleted_list_item block(s) to page",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/page/add-content for page_id: {page_id}, type: {content_type} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/page/add-content",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "page_id": page_id,
                "content_type": content_type,
                "content": content,
                "checked": checked,
                "url": url,
                "page_reference": page_reference
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to add content to Notion page: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def bulk_add_content_to_notion_page(
    page_id: str,
    items: List[NotionContentItem]
) -> NotionBulkAddContentResponse:
    """
    Adds multiple content blocks to a Notion page in bulk.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/page/bulk-add-content
    
    Args:
        page_id (str): The ID of the page to add content to
        items (List[NotionContentItem]): List of content items to add. Each item is a dict with:
            - content_type (str): Type of content block (required). One of:
                - paragraph: Basic text block
                - heading_1: Large heading
                - heading_2: Medium heading
                - heading_3: Small heading
                - bulleted_list_item: Bullet point
                - to_do: Checkbox item
                - bookmark: Web bookmark
                - link_to_page: Link to another Notion page
            - content (str): The text content for the block (required)
            - checked (bool, optional): For to_do items only
            - url (str, optional): For bookmark and link_to_page types
            - page_reference (str, optional): For link_to_page type - can be page ID or title
        
    Returns:
        NotionBulkAddContentResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (NotionBulkAddContentData): Contains:
                - page_id (str): ID of the page
                - items_processed (int): Number of items processed
                - blocks_added (int): Number of blocks successfully added
                - block_ids (List[str]): IDs of all created blocks
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example:
        items = [
            {"content_type": "heading_1", "content": "Bulk Content Section"},
            {"content_type": "paragraph", "content": "This is the second paragraph."},
            {"content_type": "bulleted_list_item", "content": "First bullet point"},
            {"content_type": "to_do", "content": "Second task", "checked": True}
        ]
        response = bulk_add_content_to_notion_page(page_id="...", items=items)
        
    Example Response:
        {
            "success": true,
            "data": {
                "page_id": "22950c4e-aa2a-81f2-86e8-e80916333349",
                "items_processed": 4,
                "blocks_added": 4,
                "block_ids": [
                    "22950c4e-aa2a-811f-8b12-fc5a6e2ebd8e",
                    "22950c4e-aa2a-817b-9c66-ed9d6bf26891",
                    "22950c4e-aa2a-81d1-8fc9-d50c76ae104f",
                    "22950c4e-aa2a-81ca-9208-cc88470d25c9"
                ]
            },
            "message": "Added 4 blocks from 4 items to page",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/page/bulk-add-content for page_id: {page_id}, items: {len(items)} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/page/bulk-add-content",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "page_id": page_id,
                "items": items
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to bulk add content to Notion page: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def get_notion_analytics(analytics_type: AnalyticsType = "workspace") -> NotionAnalyticsResponse:
    """
    Retrieves analytics data from Notion.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/analytics
    
    Args:
        analytics_type (str, optional): Type of analytics to retrieve. One of:
            - workspace: Workspace overview (default)
            - content: Content analysis
            - activity: Activity patterns
            - database: Database analysis
        
    Returns:
        NotionAnalyticsResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (NotionAnalyticsData): Contains:
                - type (str): Type of analytics retrieved
                - total_pages (int): Total number of pages
                - total_databases (int): Total number of databases
                - recent_activity_7_days (int): Activity count in last 7 days
                - recent_pages (List[NotionRecentPage]): Recently edited pages, each with:
                    - title (str): Page title
                    - last_edited (str): Last edit timestamp
                    - id (str): Page ID
                - timestamp (str): Analytics data timestamp
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example Response:
        {
            "success": true,
            "data": {
                "type": "workspace",
                "total_pages": 9,
                "total_databases": 0,
                "recent_activity_7_days": 9,
                "recent_pages": [
                    {
                        "title": "ai agent tutorial",
                        "last_edited": "2025-07-07T18:26:00.000Z",
                        "id": "22950c4e-aa2a-81f2-86e8-e80916333349"
                    }
                ],
                "timestamp": "2025-07-07T18:29:54.246590"
            },
            "message": "Workspace analytics retrieved successfully",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/analytics for type: {analytics_type} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/analytics",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "type": analytics_type
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to retrieve Notion analytics: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def perform_bulk_notion_operations(
    operation: BulkOperationType,
    query: Optional[BulkOperationQuery] = None
) -> NotionBulkResponse:
    """
    Performs bulk operations in Notion.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/bulk
    
    Args:
        operation (str): Type of bulk operation. One of:
            - list: List pages (optimized)
            - list_pages: List pages with block counts
            - analyze: Analyze pages (limited)
            - analyze_pages: Analyze pages (alt format)
        query (dict, optional): Query parameters. Can include:
            - limit (int): Number of pages to return
            - include_block_counts (bool): Whether to include block counts
            
    Returns:
        NotionBulkResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (NotionBulkListData): Contains:
                - operation (str): Operation performed
                - total (int): Total pages found
                - returned (int): Number of pages returned
                - pages (List[NotionPageInfo]): List of pages, each with:
                    - id (str): Page ID
                    - title (str): Page title
                    - created_time (str): Creation timestamp
                    - last_edited_time (str): Last edit timestamp
                    - url (str): Notion page URL
                    - block_count (Union[int, str]): Block count or "not_calculated"
                - pagination_info (NotionPaginationInfo): Pagination details
                - timestamp (str): Operation timestamp
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example:
        # List pages with block counts
        query = {
            "limit": 5,
            "include_block_counts": True
        }
        response = perform_bulk_notion_operations("list_pages", query)
        
    Example Response:
        {
            "success": true,
            "data": {
                "operation": "list",
                "total": 9,
                "returned": 9,
                "pages": [
                    {
                        "id": "22950c4e-aa2a-81f2-86e8-e80916333349",
                        "title": "ai agent tutorial",
                        "created_time": "2025-07-07T18:08:00.000Z",
                        "last_edited_time": "2025-07-07T18:26:00.000Z",
                        "url": "https://www.notion.so/ai-agent-tutorial-22950c4eaa2a81f286e8e80916333349",
                        "block_count": "not_calculated"
                    }
                ],
                "pagination_info": {
                    "limit_applied": 20,
                    "include_block_counts": false,
                    "note": "Use query parameter to request block counts: {\"include_block_counts\": true, \"limit\": 10}"
                },
                "timestamp": "2025-07-07T18:35:38.561539"
            },
            "message": "Bulk list operation completed successfully",
            "timestamp": "2025-07-07T17:38:50.777743"
        }
    """
    print(f"--- Calling Notion API: POST /api/bulk for operation: {operation} ---")
    
    try:
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/bulk",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "operation": operation,
                "query": json.dumps(query) if query else ""
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to perform bulk operation: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

@tool
def query_notion_agent_api(
    action: AgentActionType,
    parameters: AgentQueryParameters
) -> AgentQueryResponse:
    """
    Queries the Notion agent API with various actions.
    
    Endpoint: POST https://notion-mcp-server-latest.onrender.com/api/agent/query
    
    Args:
        action (str): The action to perform. One of:
            - search: Search pages
            - read_page: Read a specific page
            - create_page: Create a new page
            - add_content: Add content to a page
            - bulk_add_content: Add multiple content blocks
            - analytics: Get analytics data
            - bulk_operations: Perform bulk operations
        parameters (dict): Parameters for the action. Examples:
            - For search: {"query": "test", "page_size": 5}
            - For analytics: {"type": "workspace"}
            - For bulk_operations: {
                "operation": "list",
                "query": {"limit": 5, "include_block_counts": false}
              }
            
    Returns:
        AgentQueryResponse: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (dict): Response data (varies by action)
            - message (str): Human readable response message
            - timestamp (str): Server timestamp of the response
            
    Example:
        # Search query
        response = query_notion_agent_api(
            action="search",
            parameters={"query": "test", "page_size": 5}
        )
        
        # Analytics query
        response = query_notion_agent_api(
            action="analytics",
            parameters={"type": "workspace"}
        )
        
        # Bulk operations query
        response = query_notion_agent_api(
            action="bulk_operations",
            parameters={
                "operation": "list",
                "query": {"limit": 5, "include_block_counts": False}
            }
        )
    """
    print(f"--- Calling Notion API: POST /api/agent/query for action: {action} ---")
    
    try:
        # If parameters contain a 'query' field that's a dict, convert it to JSON string
        if action == "bulk_operations" and isinstance(parameters.get("query"), dict):
            parameters = {**parameters, "query": json.dumps(parameters["query"])}
            
        response = requests.post(
            "https://notion-mcp-server-latest.onrender.com/api/agent/query",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "action": action,
                "parameters": parameters
            },
            timeout=10  # optional timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to query Notion agent: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }

# List of all Notion tools for easy import
notion_tools = [
    search_notion,
    read_notion_page,
    create_notion_page,
    add_content_to_notion_page,
    bulk_add_content_to_notion_page,
    get_notion_analytics,
    perform_bulk_notion_operations,
    query_notion_agent_api,
] 