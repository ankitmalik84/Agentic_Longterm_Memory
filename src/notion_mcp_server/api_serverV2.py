"""
Fast API Server for Notion API V2
Direct API implementation with FastAPI endpoints
"""

import os
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError
from .notion_utils import NotionUtils
from .serverV2 import ComprehensiveNotionServer

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Notion server instance
notion_server: Optional[ComprehensiveNotionServer] = None

# === LIFESPAN EVENTS ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global notion_server
    
    # Startup
    try:
        # Get configuration
        from .config import get_config, print_config, validate_config
        config = get_config()
        
        # Print configuration (for debugging)
        print_config()
        
        # Validate configuration
        validate_config()
        
        # Test Notion API connection
        logger.info("🔗 Testing Notion API connection...")
        test_client = Client(auth=config.notion_token)
        user_info = test_client.users.me()
        logger.info(f"✅ Notion API connection successful! User: {user_info.get('name', 'N/A')}")
        
        # Initialize server
        logger.info("🚀 Initializing Notion MCP Server...")
        notion_server = ComprehensiveNotionServer(config.notion_token)
        logger.info("✅ Notion MCP Server initialized successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Server initialization failed: {str(e)}")
        raise RuntimeError(f"Failed to initialize server: {str(e)}")
    
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Notion MCP Server...")
        notion_server = None
        logger.info("✅ Server shutdown complete")

# FastAPI app with lifespan
app = FastAPI(
    title="Notion MCP Server V2 API",
    description="Complete Notion API server with MCP compatibility",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === REQUEST/RESPONSE MODELS ===

class SearchRequest(BaseModel):
    query: str
    page_size: Optional[int] = 10

class CreatePageRequest(BaseModel):
    title: str
    content: Optional[str] = ""
    parent_id: Optional[str] = None

class ReadPageRequest(BaseModel):
    identifier: str  # Can be page ID or title

class AnalyticsRequest(BaseModel):
    type: str  # workspace, content, activity, database

class BulkOperationRequest(BaseModel):
    operation: str  # archive, list, analyze
    query: Optional[str] = ""

# API Response models
class APIResponse(BaseModel):
    success: bool
    data: Any = None
    message: str = ""
    timestamp: str = datetime.now().isoformat()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if not notion_server:
            return {
                "success": False,
                "status": "unhealthy",
                "message": "Server not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        # Test Notion API connection
        try:
            user_info = notion_server.notion.users.me()
            user_name = user_info.get("name", "Unknown")
            
            return {
                "success": True,
                "status": "healthy",
                "message": f"Server operational, connected as: {user_name}",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "features": {
                    "search": True,
                    "page_operations": True,
                    "content_updates": True,
                    "analytics": True,
                    "bulk_operations": True
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "status": "unhealthy",
                "message": f"Notion API connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Notion MCP Server V2 API",
        "version": "2.0.0",
        "description": "Complete Notion API server with MCP compatibility",
        "endpoints": {
            "health": "/health",
            "search": "/api/search",
            "read_page": "/api/page/read",
            "create_page": "/api/page/create",
            "add_content": "/api/page/add-content",
            "bulk_add_content": "/api/page/bulk-add-content",
            "analytics": "/api/analytics",
            "bulk_operations": "/api/bulk",
            "agent_query": "/api/agent/query"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


# === CORE API ENDPOINTS ===

@app.post("/api/search", response_model=APIResponse)
async def search_content(request: SearchRequest):
    """Search for content in Notion workspace"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Use the server's search method
        results = notion_server.notion.search(
            query=request.query,
            page_size=request.page_size
        )
        
        # Format results
        formatted_results = []
        for item in results.get("results", []):
            formatted_item = {
                "id": item.get("id"),
                "object": item.get("object"),
                "created_time": item.get("created_time"),
                "last_edited_time": item.get("last_edited_time"),
                "url": item.get("url")
            }
            
            # Extract title using NotionUtils
            if item.get("object") == "page":
                formatted_item["title"] = NotionUtils.extract_title(item)
            elif item.get("object") == "database":
                formatted_item["title"] = NotionUtils.extract_database_title(item)
            else:
                formatted_item["title"] = "Unknown"
            
            formatted_results.append(formatted_item)
        
        return APIResponse(
            success=True,
            data={
                "results": formatted_results,
                "total_count": len(formatted_results),
                "query": request.query
            },
            message=f"Found {len(formatted_results)} results"
        )
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/page/read", response_model=APIResponse)
async def read_page(request: ReadPageRequest):
    """Read a Notion page by ID or title"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        page_id = request.identifier
        
        # If identifier is not a UUID, search for it
        if not NotionUtils.is_valid_uuid(request.identifier):
            search_results = notion_server.notion.search(
                query=request.identifier,
                filter={"property": "object", "value": "page"}
            )
            
            if not search_results.get("results"):
                raise HTTPException(status_code=404, detail=f"Page not found: {request.identifier}")
            
            page_id = search_results["results"][0]["id"]
        
        # Get page details
        page = notion_server.notion.pages.retrieve(page_id)
        
        # Get page content (blocks)
        blocks = notion_server.notion.blocks.children.list(page_id)
        
        # Format page data
        formatted_page = {
            "id": page["id"],
            "title": NotionUtils.extract_title(page),
            "created_time": page["created_time"],
            "last_edited_time": page["last_edited_time"],
            "url": page["url"],
            "properties": page.get("properties", {}),
            "content": []
        }
        
        # Format blocks
        for block in blocks.get("results", []):
            formatted_block = {
                "id": block["id"],
                "type": block["type"],
                "created_time": block["created_time"],
                "last_edited_time": block["last_edited_time"],
                "text": NotionUtils.extract_block_text(block),
                "has_children": block.get("has_children", False)
            }
            formatted_page["content"].append(formatted_block)
        
        return APIResponse(
            success=True,
            data=formatted_page,
            message="Page retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Read page error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read page: {str(e)}")


@app.post("/api/page/create", response_model=APIResponse)
async def create_page(request: CreatePageRequest):
    """Create a new Notion page"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Get parent ID
        parent_id = request.parent_id
        if not parent_id:
            parent_id = NotionUtils.get_suitable_parent_sync(notion_server.notion)
            if not parent_id:
                raise HTTPException(status_code=400, detail="No suitable parent found and none provided")
        
        # Create page data
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": request.title}}]
                }
            }
        }
        
        # Add content if provided
        if request.content:
            page_data["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": request.content}}]
                    }
                }
            ]
        
        # Create the page
        page = notion_server.notion.pages.create(**page_data)
        
        return APIResponse(
            success=True,
            data={
                "id": page["id"],
                "title": request.title,
                "url": page["url"],
                "created_time": page["created_time"],
                "parent_id": parent_id
            },
            message="Page created successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create page error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create page: {str(e)}")


# === CONTENT MANAGEMENT ENDPOINTS ===

class AddContentRequest(BaseModel):
    page_id: str
    content_type: str  # paragraph, heading_1, heading_2, heading_3, bulleted_list_item, to_do
    content: str
    checked: Optional[bool] = False  # For to_do items

@app.post("/api/page/add-content", response_model=APIResponse)
async def add_content(request: AddContentRequest):
    """Add content to a Notion page"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Validate content type
        valid_types = ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]
        if request.content_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid content type. Must be one of: {valid_types}")
        
        # Handle content length - split if necessary
        content_chunks = NotionUtils.split_long_content(request.content)
        
        # Prepare blocks
        blocks = []
        for chunk in content_chunks:
            block = {
                "object": "block",
                "type": request.content_type,
                request.content_type: {
                    "rich_text": [{"text": {"content": chunk}}]
                }
            }
            
            # Add checked property for to_do items
            if request.content_type == "to_do":
                block[request.content_type]["checked"] = request.checked
            
            blocks.append(block)
        
        # Add blocks to page
        response = notion_server.notion.blocks.children.append(
            block_id=request.page_id,
            children=blocks
        )
        
        return APIResponse(
            success=True,
            data={
                "page_id": request.page_id,
                "content_type": request.content_type,
                "blocks_added": len(blocks),
                "block_ids": [block["id"] for block in response["results"]]
            },
            message=f"Added {len(blocks)} {request.content_type} block(s) to page"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add content error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add content: {str(e)}")


class BulkAddContentRequest(BaseModel):
    page_id: str
    items: List[Dict[str, Any]]  # List of {content_type, content, checked?}

@app.post("/api/page/bulk-add-content", response_model=APIResponse)
async def bulk_add_content(request: BulkAddContentRequest):
    """Add multiple content items to a Notion page"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Validate and prepare blocks
        blocks = []
        valid_types = ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]
        
        for item in request.items:
            content_type = item.get("content_type", "paragraph")
            content = item.get("content", "")
            checked = item.get("checked", False)
            
            if content_type not in valid_types:
                raise HTTPException(status_code=400, detail=f"Invalid content type: {content_type}")
            
            # Handle content length - split if necessary
            content_chunks = NotionUtils.split_long_content(content)
            
            for chunk in content_chunks:
                block = {
                    "object": "block",
                    "type": content_type,
                    content_type: {
                        "rich_text": [{"text": {"content": chunk}}]
                    }
                }
                
                # Add checked property for to_do items
                if content_type == "to_do":
                    block[content_type]["checked"] = checked
                
                blocks.append(block)
        
        # Add blocks to page
        response = notion_server.notion.blocks.children.append(
            block_id=request.page_id,
            children=blocks
        )
        
        return APIResponse(
            success=True,
            data={
                "page_id": request.page_id,
                "items_processed": len(request.items),
                "blocks_added": len(blocks),
                "block_ids": [block["id"] for block in response["results"]]
            },
            message=f"Added {len(blocks)} blocks from {len(request.items)} items to page"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk add content error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk add content: {str(e)}")


# === ANALYTICS ENDPOINTS ===

@app.post("/api/analytics", response_model=APIResponse)
async def get_analytics(request: AnalyticsRequest):
    """Get analytics data from Notion workspace"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Get actual structured data instead of captured output
        if request.type == "workspace":
            # Get pages and databases directly
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            databases = notion_server.notion.search(filter={"property": "object", "value": "database"})
            
            # Calculate recent activity (last 7 days)
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_pages = []
            
            for page in pages.get("results", []):
                try:
                    last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                    if last_edited > week_ago:
                        recent_pages.append({
                            "title": NotionUtils.extract_title(page),
                            "last_edited": page["last_edited_time"],
                            "id": page["id"]
                        })
                except Exception:
                    continue
            
            analytics_data = {
                "type": "workspace",
                "total_pages": len(pages.get("results", [])),
                "total_databases": len(databases.get("results", [])),
                "recent_activity_7_days": len(recent_pages),
                "recent_pages": sorted(recent_pages, key=lambda x: x["last_edited"], reverse=True)[:10],
                "timestamp": datetime.now().isoformat()
            }
            
        elif request.type == "content":
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            
            content_stats = {
                "total_pages": len(pages.get("results", [])),
                "pages_with_content": 0,
                "empty_pages": 0,
                "content_types": {}
            }
            
            total_blocks = 0
            pages_analyzed = 0
            
            for page in pages.get("results", [])[:20]:  # Analyze first 20 pages
                try:
                    blocks = notion_server.notion.blocks.children.list(page["id"])
                    block_count = len(blocks.get("results", []))
                    total_blocks += block_count
                    pages_analyzed += 1
                    
                    if block_count > 0:
                        content_stats["pages_with_content"] += 1
                    else:
                        content_stats["empty_pages"] += 1
                    
                    # Analyze block types
                    for block in blocks.get("results", []):
                        block_type = block.get("type", "unknown")
                        content_stats["content_types"][block_type] = content_stats["content_types"].get(block_type, 0) + 1
                        
                except Exception:
                    continue
            
            if content_stats["pages_with_content"] > 0:
                content_stats["avg_blocks_per_page"] = total_blocks / content_stats["pages_with_content"]
            else:
                content_stats["avg_blocks_per_page"] = 0
            
            analytics_data = {
                "type": "content",
                "pages_analyzed": pages_analyzed,
                **content_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        elif request.type == "activity":
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            
            now = datetime.now(timezone.utc)
            activity_buckets = {
                "today": [],
                "this_week": [],
                "this_month": [],
                "older": []
            }
            
            for page in pages.get("results", []):
                try:
                    last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                    days_ago = (now - last_edited).days
                    
                    page_info = {
                        "title": NotionUtils.extract_title(page),
                        "id": page["id"],
                        "last_edited": page["last_edited_time"]
                    }
                    
                    if days_ago == 0:
                        activity_buckets["today"].append(page_info)
                    elif days_ago <= 7:
                        activity_buckets["this_week"].append(page_info)
                    elif days_ago <= 30:
                        activity_buckets["this_month"].append(page_info)
                    else:
                        activity_buckets["older"].append(page_info)
                except Exception:
                    activity_buckets["older"].append({
                        "title": NotionUtils.extract_title(page),
                        "id": page["id"],
                        "last_edited": page.get("last_edited_time", "Unknown")
                    })
            
            analytics_data = {
                "type": "activity",
                "activity_summary": {
                    "today": len(activity_buckets["today"]),
                    "this_week": len(activity_buckets["this_week"]),
                    "this_month": len(activity_buckets["this_month"]),
                    "older": len(activity_buckets["older"])
                },
                "activity_details": activity_buckets,
                "timestamp": datetime.now().isoformat()
            }
            
        elif request.type == "database":
            databases = notion_server.notion.search(filter={"property": "object", "value": "database"})
            
            database_stats = {
                "total_databases": len(databases.get("results", [])),
                "databases": []
            }
            
            for db in databases.get("results", []):
                try:
                    db_info = {
                        "id": db["id"],
                        "title": NotionUtils.extract_database_title(db),
                        "created_time": db["created_time"],
                        "last_edited_time": db["last_edited_time"],
                        "url": db["url"]
                    }
                    database_stats["databases"].append(db_info)
                except Exception:
                    continue
            
            analytics_data = {
                "type": "database",
                **database_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        else:
            raise HTTPException(status_code=400, detail="Invalid analytics type. Must be: workspace, content, activity, or database")
        
        return APIResponse(
            success=True,
            data=analytics_data,
            message=f"{request.type.capitalize()} analytics retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


# === BULK OPERATIONS ENDPOINTS ===

@app.post("/api/bulk", response_model=APIResponse)
async def bulk_operations(request: BulkOperationRequest):
    """Perform bulk operations on Notion data"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Handle both old and new operation names for backward compatibility
        operation = request.operation
        if operation == "list_pages":
            operation = "list"
        elif operation == "analyze_pages":
            operation = "analyze"
        
        if operation == "list":
            # Get all pages with structured data
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            
            formatted_pages = []
            for page in pages.get("results", []):
                page_data = {
                    "id": page["id"],
                    "title": NotionUtils.extract_title(page),
                    "created_time": page["created_time"],
                    "last_edited_time": page["last_edited_time"],
                    "url": page["url"]
                }
                
                # Get block count
                try:
                    blocks = notion_server.notion.blocks.children.list(page["id"])
                    page_data["block_count"] = len(blocks.get("results", []))
                except:
                    page_data["block_count"] = 0
                
                formatted_pages.append(page_data)
            
            result = {
                "operation": "list",
                "total": len(formatted_pages),
                "pages": formatted_pages,
                "timestamp": datetime.now().isoformat()
            }
            
        elif operation == "analyze":
            # For analyze operation, return structured analysis data
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            
            analysis_result = {
                "total_pages": len(pages.get("results", [])),
                "pages": []
            }
            
            for page in pages.get("results", [])[:10]:  # Limit to first 10 for API response
                page_data = {
                    "id": page["id"],
                    "title": NotionUtils.extract_title(page),
                    "created_time": page["created_time"],
                    "last_edited_time": page["last_edited_time"],
                    "url": page["url"]
                }
                
                # Get block count and types
                try:
                    blocks = notion_server.notion.blocks.children.list(page["id"])
                    page_data["block_count"] = len(blocks.get("results", []))
                    
                    # Analyze block types
                    block_types = {}
                    for block in blocks.get("results", []):
                        block_type = block.get("type", "unknown")
                        block_types[block_type] = block_types.get(block_type, 0) + 1
                    page_data["block_types"] = block_types
                    
                except:
                    page_data["block_count"] = 0
                    page_data["block_types"] = {}
                
                analysis_result["pages"].append(page_data)
            
            result = {
                "operation": "analyze",
                "total": len(pages.get("results", [])),
                "data": analysis_result,
                "timestamp": datetime.now().isoformat()
            }
            
        elif operation == "create":
            # For bulk page creation, expect pages_data in query parameter
            if not request.query:
                raise HTTPException(status_code=400, detail="Query parameter required for bulk create operation with pages data")
            
            try:
                import json
                pages_data = json.loads(request.query)
                result = await notion_server.bulk_ops.bulk_create_pages(pages_data)
                result["timestamp"] = datetime.now().isoformat()
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in query parameter for pages data")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create pages: {str(e)}")
                
        else:
            raise HTTPException(status_code=400, detail="Invalid bulk operation. Must be: list, list_pages, analyze, analyze_pages, or create")
        
        return APIResponse(
            success=True,
            data=result,
            message=f"Bulk {operation} operation completed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk operations error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform bulk operation: {str(e)}")


# === AGENT INTEGRATION ENDPOINT ===

@app.post("/api/agent/query")
async def agent_query(query: dict):
    """Unified endpoint for AI agent queries"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Extract query parameters - handle both "params" and "parameters"
        action = query.get("action", "")
        parameters = query.get("parameters", {}) or query.get("params", {})
        
        # Validate required parameters based on action
        if action == "search":
            if "query" not in parameters:
                parameters["query"] = ""  # Default empty query for search all
            return await search_content(SearchRequest(**parameters))
            
        elif action == "read_page":
            if "identifier" not in parameters:
                raise HTTPException(status_code=400, detail="Missing required parameter: identifier")
            return await read_page(ReadPageRequest(**parameters))
            
        elif action == "create_page":
            if "title" not in parameters:
                raise HTTPException(status_code=400, detail="Missing required parameter: title")
            return await create_page(CreatePageRequest(**parameters))
            
        elif action == "add_content":
            required_params = ["page_id", "content_type", "content"]
            missing_params = [p for p in required_params if p not in parameters]
            if missing_params:
                raise HTTPException(status_code=400, detail=f"Missing required parameters: {missing_params}")
            return await add_content(AddContentRequest(**parameters))
            
        elif action == "bulk_add_content":
            required_params = ["page_id", "items"]
            missing_params = [p for p in required_params if p not in parameters]
            if missing_params:
                raise HTTPException(status_code=400, detail=f"Missing required parameters: {missing_params}")
            return await bulk_add_content(BulkAddContentRequest(**parameters))
            
        elif action == "analytics":
            if "type" not in parameters:
                parameters["type"] = "workspace"  # Default to workspace analytics
            return await get_analytics(AnalyticsRequest(**parameters))
            
        elif action == "bulk_operations":
            if "operation" not in parameters:
                parameters["operation"] = "list"  # Default to list operation
            return await bulk_operations(BulkOperationRequest(**parameters))
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}. Supported actions: search, read_page, create_page, add_content, bulk_add_content, analytics, bulk_operations")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process agent query: {str(e)}")


# === SERVER RUNNER ===

def run_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Run the FastAPI server"""
    uvicorn.run(
        "src.notion_mcp_server.api_serverV2:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )


if __name__ == "__main__":
    run_server(debug=True) 