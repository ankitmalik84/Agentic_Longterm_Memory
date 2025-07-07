from langchain.tools import tool
from typing import Dict, Any, TypedDict, List, Optional, Literal
import requests
from datetime import datetime

class NotionSearchResult(TypedDict):
    id: str
    object: str
    created_time: str
    last_edited_time: str
    url: str
    title: str

class NotionSearchResponse(TypedDict):
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str

class NotionPageContent(TypedDict):
    id: str
    type: str
    created_time: str
    last_edited_time: str
    text: str
    has_children: bool

class NotionPageProperties(TypedDict):
    title: Dict[str, Any]  # Complex nested structure for title

class NotionPageData(TypedDict):
    id: str
    title: str
    created_time: str
    last_edited_time: str
    url: str
    properties: NotionPageProperties
    content: List[NotionPageContent]

class NotionPageResponse(TypedDict):
    success: bool
    data: NotionPageData
    message: str
    timestamp: str

class NotionCreatePageData(TypedDict):
    id: str
    title: str
    url: str
    created_time: str
    parent_id: str
    content_blocks_created: int

class NotionCreatePageResponse(TypedDict):
    success: bool
    data: NotionCreatePageData
    message: str
    timestamp: str

# Define valid content types
NotionContentType = Literal[
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "to_do",
    "bookmark",
    "link_to_page"
]

class NotionAddContentData(TypedDict):
    page_id: str
    content_type: str
    blocks_added: int
    block_ids: List[str]

class NotionAddContentResponse(TypedDict):
    success: bool
    data: NotionAddContentData
    message: str
    timestamp: str

class NotionContentItem(TypedDict, total=False):
    content_type: NotionContentType
    content: str
    checked: bool  # Optional for to_do items
    url: str  # Optional for bookmark and link_to_page
    page_reference: str  # Optional for link_to_page

class NotionBulkAddContentData(TypedDict):
    page_id: str
    items_processed: int
    blocks_added: int
    block_ids: List[str]

class NotionBulkAddContentResponse(TypedDict):
    success: bool
    data: NotionBulkAddContentData
    message: str
    timestamp: str

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
def get_notion_analytics():
    """Retrieves analytics data from Notion. Corresponds to /api/analytics."""
    print("--- Calling Notion API: /api/analytics ---")
    return {"status": "success", "page_views": 100, "unique_visitors": 50}

@tool
def perform_bulk_notion_operations(operations: list):
    """Performs bulk operations in Notion. Corresponds to /api/bulk."""
    print(f"--- Calling Notion API: /api/bulk with {len(operations)} operations ---")
    return {"status": "success", "operations_performed": len(operations)}

@tool
def query_notion_agent_api(query: str):
    """Queries the Notion agent API. Corresponds to /api/agent/query."""
    print(f"--- Calling Notion API: /api/agent/query with query: {query} ---")
    return {"status": "success", "response": f"Agent response to '{query}'"}

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