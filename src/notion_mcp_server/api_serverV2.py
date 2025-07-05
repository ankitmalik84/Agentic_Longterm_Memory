"""
Fast API Server for Notion API V2
Direct API implementation with FastAPI endpoints
"""

import os
import logging
from typing import  Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our Notion server
from .serverV2 import ComprehensiveNotionServer

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Notion Server V2 API",
    description="HTTP API for AI agents to interact with Notion",
    version="2.0.0"
)

# CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Notion server instance
notion_server: Optional[ComprehensiveNotionServer] = None

# Pydantic models for API requests
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

@app.on_event("startup")
async def startup_event():
    """Initialize the Notion server on startup"""
    global notion_server
    
    try:
        notion_token = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
        if not notion_token:
            logger.error("NOTION_TOKEN not found in environment variables")
            raise ValueError("NOTION_TOKEN required")
        
        notion_server = ComprehensiveNotionServer(notion_token)
        logger.info("✅ Notion Server initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Notion server: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for container orchestration"""
    try:
        if notion_server:
            # Test API connection
            user = notion_server.notion.users.me()
            return {
                "status": "healthy",
                "service": "notion-server-v2",
                "user": user.get("name", "N/A"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Server not initialized")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

# Core API endpoints
@app.post("/api/search", response_model=APIResponse)
async def search_content(request: SearchRequest):
    """Search for pages and databases"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Search using the server's search method
        all_results = notion_server.notion.search(query=request.query)
        pages = [r for r in all_results.get("results", []) if r["object"] == "page"]
        databases = [r for r in all_results.get("results", []) if r["object"] == "database"]
        
        # Format results
        formatted_pages = []
        for page in pages[:request.page_size]:
            formatted_pages.append({
                "id": page["id"],
                "title": notion_server._extract_title(page),
                "url": page["url"],
                "last_edited": page["last_edited_time"],
                "type": "page"
            })
        
        formatted_databases = []
        for db in databases[:5]:
            formatted_databases.append({
                "id": db["id"],
                "title": notion_server._extract_database_title(db),
                "url": db["url"],
                "last_edited": db["last_edited_time"],
                "type": "database"
            })
        
        return APIResponse(
            success=True,
            data={
                "query": request.query,
                "pages": formatted_pages,
                "databases": formatted_databases,
                "total_pages": len(pages),
                "total_databases": len(databases)
            },
            message=f"Found {len(pages)} pages and {len(databases)} databases"
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Search failed: {str(e)}"
        )

@app.post("/api/page/read", response_model=APIResponse)
async def read_page(request: ReadPageRequest):
    """Read page content by ID or title"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        identifier = request.identifier
        
        # Check if identifier is a page ID (UUID-like format)
        if len(identifier) > 30 and '-' in identifier:
            # Direct page ID
            page_id = identifier.replace('-', '')
            page = notion_server.notion.pages.retrieve(page_id)
        else:
            # Search for page by title
            results = notion_server.notion.search(
                query=identifier,
                filter={"property": "object", "value": "page"}
            )
            
            if not results.get("results"):
                return APIResponse(
                    success=False,
                    message=f"No page found with title '{identifier}'"
                )
            
            # Find exact match or first result
            page = None
            for result in results["results"]:
                title = notion_server._extract_title(result)
                if title.lower() == identifier.lower():
                    page = result
                    break
            
            if not page:
                page = results["results"][0]  # Use first result
            
            page_id = page["id"]
            page = notion_server.notion.pages.retrieve(page_id)
        
        # Get page content (blocks)
        blocks = notion_server.notion.blocks.children.list(page["id"])
        
        # Extract content as text
        content_text = []
        for block in blocks.get("results", []):
            block_type = block.get("type", "")
            
            if block_type == "paragraph":
                text = notion_server._extract_rich_text(block["paragraph"]["rich_text"])
                if text:
                    content_text.append(text)
            elif block_type == "heading_1":
                text = notion_server._extract_rich_text(block["heading_1"]["rich_text"])
                content_text.append(f"# {text}")
            elif block_type == "heading_2":
                text = notion_server._extract_rich_text(block["heading_2"]["rich_text"])
                content_text.append(f"## {text}")
            elif block_type == "heading_3":
                text = notion_server._extract_rich_text(block["heading_3"]["rich_text"])
                content_text.append(f"### {text}")
            elif block_type == "bulleted_list_item":
                text = notion_server._extract_rich_text(block["bulleted_list_item"]["rich_text"])
                content_text.append(f"• {text}")
            elif block_type == "numbered_list_item":
                text = notion_server._extract_rich_text(block["numbered_list_item"]["rich_text"])
                content_text.append(f"1. {text}")
        
        return APIResponse(
            success=True,
            data={
                "id": page["id"],
                "title": notion_server._extract_title(page),
                "url": page["url"],
                "content": "\n\n".join(content_text),
                "created_time": page["created_time"],
                "last_edited_time": page["last_edited_time"],
                "block_count": len(blocks.get("results", []))
            },
            message="Page content retrieved successfully"
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to read page: {str(e)}"
        )

@app.post("/api/page/create", response_model=APIResponse)
async def create_page(request: CreatePageRequest):
    """Create a new page"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        # Get parent ID
        if request.parent_id:
            parent_id = request.parent_id
        else:
            parent_id = await notion_server._get_suitable_parent()
            if not parent_id:
                return APIResponse(
                    success=False,
                    message="No suitable parent page found. Please specify parent_id."
                )
        
        # Create page with parent
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {"title": {"title": [{"text": {"content": request.title}}]}}
        }
        
        # Add content if provided
        if request.content:
            page_data["children"] = [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": request.content}}]}
            }]
        
        page = notion_server.notion.pages.create(**page_data)
        
        return APIResponse(
            success=True,
            data={
                "id": page["id"],
                "title": request.title,
                "url": page["url"],
                "parent_id": parent_id
            },
            message="Page created successfully"
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to create page: {str(e)}"
        )

@app.post("/api/analytics", response_model=APIResponse)
async def get_analytics(request: AnalyticsRequest):
    """Get workspace analytics"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        if request.type == "workspace":
            # Get workspace analytics
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            databases = notion_server.notion.search(filter={"property": "object", "value": "database"})
            
            from datetime import timezone, timedelta
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_pages = []
            
            for page in pages["results"]:
                try:
                    last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                    if last_edited > week_ago:
                        recent_pages.append({
                            "title": notion_server._extract_title(page),
                            "last_edited": page["last_edited_time"],
                            "id": page["id"]
                        })
                except Exception:
                    continue
            
            return APIResponse(
                success=True,
                data={
                    "total_pages": len(pages["results"]),
                    "total_databases": len(databases["results"]),
                    "recent_activity_7_days": len(recent_pages),
                    "recent_pages": sorted(recent_pages, key=lambda x: x["last_edited"], reverse=True)[:10]
                },
                message="Workspace analytics retrieved successfully"
            )
        
        else:
            return APIResponse(
                success=False,
                message=f"Analytics type '{request.type}' not yet implemented"
            )
            
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Analytics failed: {str(e)}"
        )

@app.post("/api/bulk", response_model=APIResponse)
async def bulk_operations(request: BulkOperationRequest):
    """Perform bulk operations"""
    try:
        if not notion_server:
            raise HTTPException(status_code=503, detail="Server not initialized")
        
        if request.operation == "list_pages":
            pages = notion_server.notion.search(filter={"property": "object", "value": "page"})
            
            formatted_pages = []
            for page in pages["results"]:
                formatted_pages.append({
                    "id": page["id"],
                    "title": notion_server._extract_title(page),
                    "url": page["url"],
                    "last_edited": page["last_edited_time"]
                })
            
            return APIResponse(
                success=True,
                data={
                    "pages": formatted_pages,
                    "total": len(formatted_pages)
                },
                message=f"Retrieved {len(formatted_pages)} pages"
            )
        
        else:
            return APIResponse(
                success=False,
                message=f"Bulk operation '{request.operation}' not yet implemented"
            )
            
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Bulk operation failed: {str(e)}"
        )

# AI Agent integration endpoint
@app.post("/api/agent/query")
async def agent_query(query: dict):
    """Unified endpoint for AI agents to query the Notion server"""
    try:
        action = query.get("action")
        params = query.get("params", {})
        
        if action == "search":
            request = SearchRequest(**params)
            return await search_content(request)
        
        elif action == "read_page":
            request = ReadPageRequest(**params)
            return await read_page(request)
        
        elif action == "create_page":
            request = CreatePageRequest(**params)
            return await create_page(request)
        
        elif action == "analytics":
            request = AnalyticsRequest(**params)
            return await get_analytics(request)
        
        elif action == "bulk":
            request = BulkOperationRequest(**params)
            return await bulk_operations(request)
        
        else:
            return APIResponse(
                success=False,
                message=f"Unknown action: {action}"
            )
            
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Query failed: {str(e)}"
        )

# Main server execution
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8081"))  # Changed from 8080 to 8081
    
    logger.info(f"🚀 Starting Notion Server V2 API on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 