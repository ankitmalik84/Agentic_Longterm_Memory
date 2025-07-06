#!/usr/bin/env python3
"""
Comprehensive Test Suite for Notion MCP Server V2
Tests ALL endpoints and functionality with detailed reporting and validation.
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_mcp_server.config import get_config, print_config

# Load environment variables
load_dotenv()


class ComprehensiveNotionTester:
    """Comprehensive test suite for ALL Notion MCP Server V2 operations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.config = get_config()
        self.test_results = []
        self.test_page_ids = []  # Store created page IDs for cleanup
        self.test_start_time = datetime.now()
        
        # Test categories - include all categories used in tests
        self.categories = {
            "core": [],
            "content": [],           # For content addition tests
            "bulk_content": [],      # For bulk content tests  
            "links": [],             # For link functionality tests
            "update": [],
            "analytics": [],
            "bulk": [],
            "agent": [],
            "edge_cases": [],
            "exception": []          # For exception handling
        }
        
    def log_test(self, test_name: str, category: str, success: bool, message: str = "", data: Any = None, duration: float = 0):
        """Log test results with categorization"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().isoformat()
        
        result = {
            "test_name": test_name,
            "category": category,
            "success": success,
            "message": message,
            "timestamp": timestamp,
            "duration": duration,
            "data": data
        }
        
        self.test_results.append(result)
        self.categories[category].append(result)
        
        duration_str = f"({duration:.2f}s)" if duration > 0 else ""
        print(f"{status} | {category.upper():<8} | {test_name:<35} | {message} {duration_str}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Tuple[Dict, float]:
        """Make HTTP request with timing and error handling"""
        start_time = time.time()
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Set different timeouts based on endpoint
            timeout = 30  # Default timeout
            if endpoint == "/api/bulk" or "bulk" in endpoint:
                timeout = 60  # Longer timeout for bulk operations
            elif endpoint == "/api/analytics":
                timeout = 45  # Longer timeout for analytics
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            duration = time.time() - start_time
            
            # Handle different response types
            if response.headers.get('content-type', '').startswith('application/json'):
                response_data = response.json()
                
                # FIXED: Add success field based on HTTP status code
                if response.status_code >= 200 and response.status_code < 300:
                    # Success response - keep existing success field or add it
                    if "success" not in response_data:
                        response_data["success"] = True
                else:
                    # Error response (400, 404, etc.) - mark as not successful
                    response_data["success"] = False
                    response_data["status_code"] = response.status_code
                    # Move 'detail' to 'message' for consistency
                    if "detail" in response_data and "message" not in response_data:
                        response_data["message"] = response_data["detail"]
                
                return response_data, duration
            else:
                return {"status_code": response.status_code, "text": response.text, "success": False}, duration
            
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            return {"error": str(e), "success": False}, duration
        except Exception as e:
            duration = time.time() - start_time
            return {"error": str(e), "success": False}, duration
    
    # ==================== CORE OPERATIONS TESTS ====================
    
    def test_health_check(self):
        """Test server health and basic connectivity"""
        response, duration = self.make_request("GET", "/health")
        
        success = response.get("success", False) and response.get("status") == "healthy"
        message = response.get("message", "") if success else response.get("error", "Health check failed")
        
        if success and "features" in response:
            features = response["features"]
            enabled_features = [k for k, v in features.items() if v]
            message += f" | Features: {', '.join(enabled_features)}"
        
        self.log_test("Health Check", "core", success, message, duration=duration)
        return success
    
    def test_search_functionality(self):
        """Test search endpoint with various queries"""
        test_cases = [
            {"query": "", "description": "empty query (list all)"},
            {"query": "aws", "description": "specific term search"},
            {"query": "test", "description": "common term search"},
            {"query": "nonexistent_random_term_12345", "description": "no results search"}
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            test_data = {
                "query": test_case["query"],
                "page_size": 10
            }
            
            response, duration = self.make_request("POST", "/api/search", test_data)
            
            success = response.get("success", False)
            message = f"{test_case['description']}"
            
            if success and response.get("data"):
                data = response["data"]
                total_count = data.get("total_count", 0)
                message += f" | Found {total_count} items"
            else:
                message += f" | {response.get('error', 'Failed')}"
                all_passed = False
            
            self.log_test(f"Search: {test_case['description']}", "core", success, message, duration=duration)
        
        return all_passed
    
    def test_page_creation(self):
        """Test page creation with various scenarios"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        test_cases = [
            {
                "title": f"Basic Test Page {timestamp}",
                "content": "This is a basic test page.",
                "description": "basic page creation"
            },
            {
                "title": f"Empty Content Page {timestamp}",
                "content": "",
                "description": "page with no content"
            },
            {
                "title": f"Long Content Page {timestamp}",
                "content": "This is a test page with longer content. " * 50,
                "description": "page with long content"
            }
        ]
        
        created_pages = []
        all_passed = True
        
        for test_case in test_cases:
            test_data = {
                "title": test_case["title"],
                "content": test_case["content"]
            }
            
            response, duration = self.make_request("POST", "/api/page/create", test_data)
            
            success = response.get("success", False)
            message = test_case["description"]
            
            if success and response.get("data", {}).get("id"):
                page_id = response["data"]["id"]
                self.test_page_ids.append(page_id)
                created_pages.append(page_id)
                message += f" | Page ID: {page_id[:8]}..."
            else:
                message += f" | {response.get('error', 'Failed')}"
                all_passed = False
            
            self.log_test(f"Create Page: {test_case['description']}", "core", success, message, duration=duration)
        
        return all_passed, created_pages
    
    def test_page_reading(self, page_ids: List[str]):
        """Test page reading with various identifiers"""
        if not page_ids:
            self.log_test("Page Reading", "core", False, "No page IDs provided for testing")
            return False
        
        all_passed = True
        
        for i, page_id in enumerate(page_ids[:3]):  # Test first 3 pages
            test_data = {"identifier": page_id}
            
            response, duration = self.make_request("POST", "/api/page/read", test_data)
            
            success = response.get("success", False)
            message = f"read page {i+1}"
            
            if success and response.get("data"):
                data = response["data"]
                title = data.get("title", "Untitled")
                content_blocks = len(data.get("content", []))
                message += f" | '{title}' | {content_blocks} blocks"
            else:
                message += f" | {response.get('error', 'Failed')}"
                all_passed = False
            
            self.log_test(f"Read Page: {message}", "core", success, message, duration=duration)
        
        return all_passed
    
    def test_list_operations(self):
        """Test listing pages and databases"""
        # Test via search with empty query (equivalent to list all)
        response, duration = self.make_request("POST", "/api/search", {"query": "", "page_size": 50})
        
        success = response.get("success", False)
        message = "list all content"
        
        if success and response.get("data"):
            data = response["data"]
            total_count = data.get("total_count", 0)
            message += f" | {total_count} total items"
        else:
            message += f" | {response.get('error', 'Failed')}"
        
        self.log_test("List All Content", "core", success, message, duration=duration)
        return success
    
    # ==================== UPDATE OPERATIONS TESTS ====================
    
    def test_content_addition_operations(self, page_ids: List[str]):
        """Test all content addition operations including links"""
        if not page_ids:
            self.log_test("Content Addition", "content", False, "No test pages available")
            return False
        
        all_passed = True
        test_page_id = page_ids[0]
        
        # Test 1: Add paragraph
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "paragraph",
            "content": "This is a test paragraph from the comprehensive test suite."
        })
        
        test_passed = response.get("success", False)
        message = "Added paragraph content"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Paragraph", "content", test_passed, message, duration=duration)
        
        # Test 2: Add heading_1
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "heading_1",
            "content": "Test Heading 1"
        })
        
        test_passed = response.get("success", False)
        message = "Added heading_1 content"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Heading 1", "content", test_passed, message, duration=duration)
        
        # Test 3: Add heading_2
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "heading_2",
            "content": "Test Heading 2"
        })
        
        test_passed = response.get("success", False)
        message = "Added heading_2 content"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Heading 2", "content", test_passed, message, duration=duration)
        
        # Test 4: Add heading_3
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "heading_3",
            "content": "Test Heading 3"
        })
        
        test_passed = response.get("success", False)
        message = "Added heading_3 content"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Heading 3", "content", test_passed, message, duration=duration)
        
        # Test 5: Add bullet point
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "bulleted_list_item",
            "content": "Test bullet point item"
        })
        
        test_passed = response.get("success", False)
        message = "Added bullet point content"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Bullet Point", "content", test_passed, message, duration=duration)
        
        # Test 6: Add to-do (unchecked)
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "to_do",
            "content": "Test to-do item (unchecked)",
            "checked": False
        })
        
        test_passed = response.get("success", False)
        message = "Added unchecked to-do item"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add To-Do (Unchecked)", "content", test_passed, message, duration=duration)
        
        # Test 7: Add to-do (checked)
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "to_do",
            "content": "Test to-do item (checked)",
            "checked": True
        })
        
        test_passed = response.get("success", False)
        message = "Added checked to-do item"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add To-Do (Checked)", "content", test_passed, message, duration=duration)
        
        # Test 8: Add bookmark (NEW)
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "bookmark",
            "content": "Test Bookmark",
            "url": "https://www.example.com"
        })
        
        test_passed = response.get("success", False)
        message = "Added bookmark content"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Bookmark", "content", test_passed, message, duration=duration)
        
        # Test 9: Add link_to_page (NEW)
        if len(page_ids) > 1:
            response, duration = self.make_request("POST", "/api/page/add-content", {
                "page_id": test_page_id,
                "content_type": "link_to_page",
                "content": "Link to another page",
                "page_reference": page_ids[1]  # Link to second test page
            })
            
            test_passed = response.get("success", False)
            message = "Added link_to_page content"
            if not test_passed:
                message += f" | Error: {response.get('message', 'Unknown error')}"
                all_passed = False
            
            self.log_test("Add Link to Page", "content", test_passed, message, duration=duration)
        else:
            self.log_test("Add Link to Page", "content", False, "Not enough test pages available")
            all_passed = False
        
        # Test 10: Add long content (should split)
        long_content = "This is a very long content that should be split into multiple blocks. " * 50
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "paragraph",
            "content": long_content
        })
        
        test_passed = response.get("success", False)
        message = "Added long content (should split)"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Add Long Content", "content", test_passed, message, duration=duration)
        
        return all_passed
    
    def test_bulk_content_addition(self, page_ids: List[str]):
        """Test bulk content addition operations including links"""
        if not page_ids:
            self.log_test("Bulk Content Addition", "bulk_content", False, "No test pages available")
            return False
        
        all_passed = True
        test_page_id = page_ids[0]
        
        # Test 1: Basic bulk content addition
        bulk_items = [
            {"content_type": "heading_1", "content": "Bulk Content Section"},
            {"content_type": "paragraph", "content": "This is the first paragraph."},
            {"content_type": "paragraph", "content": "This is the second paragraph."},
            {"content_type": "bulleted_list_item", "content": "First bullet point"},
            {"content_type": "bulleted_list_item", "content": "Second bullet point"},
            {"content_type": "to_do", "content": "First task", "checked": False},
            {"content_type": "to_do", "content": "Second task", "checked": True}
        ]
        
        response, duration = self.make_request("POST", "/api/page/bulk-add-content", {
            "page_id": test_page_id,
            "items": bulk_items
        })
        
        test_passed = response.get("success", False)
        message = f"Added {len(bulk_items)} bulk items"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Bulk Content: Mixed Types", "bulk_content", test_passed, message, duration=duration)
        
        # Test 2: Bulk content with links (NEW)
        link_items = [
            {"content_type": "heading_2", "content": "Links Section"},
            {"content_type": "bookmark", "url": "https://www.google.com", "content": "Google"},
            {"content_type": "bookmark", "url": "https://www.github.com", "content": "GitHub"},
            {"content_type": "paragraph", "content": "Here are some external links above."}
        ]
        
        # Add link_to_page if we have multiple pages
        if len(page_ids) > 1:
            link_items.append({
                "content_type": "link_to_page",
                "page_reference": page_ids[1],
                "content": "Link to test page"
            })
        
        response, duration = self.make_request("POST", "/api/page/bulk-add-content", {
            "page_id": test_page_id,
            "items": link_items
        })
        
        test_passed = response.get("success", False)
        message = f"Added {len(link_items)} link items"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Bulk Content: Links", "bulk_content", test_passed, message, duration=duration)
        
        # Test 3: Bulk to-do items
        todo_items = [
            {"content_type": "heading_3", "content": "Task List"},
            {"content_type": "to_do", "content": "Complete project documentation", "checked": False},
            {"content_type": "to_do", "content": "Review code changes", "checked": True},
            {"content_type": "to_do", "content": "Deploy to production", "checked": False},
            {"content_type": "to_do", "content": "Send update email", "checked": False}
        ]
        
        response, duration = self.make_request("POST", "/api/page/bulk-add-content", {
            "page_id": test_page_id,
            "items": todo_items
        })
        
        test_passed = response.get("success", False)
        message = f"Added {len(todo_items)} to-do items"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Bulk Content: To-Do List", "bulk_content", test_passed, message, duration=duration)
        
        # Test 4: Large bulk operation
        large_items = []
        for i in range(1, 21):  # Create 20 items
            large_items.append({
                "content_type": "paragraph",
                "content": f"This is paragraph number {i} in the large bulk test."
            })
        
        response, duration = self.make_request("POST", "/api/page/bulk-add-content", {
            "page_id": test_page_id,
            "items": large_items
        })
        
        test_passed = response.get("success", False)
        message = f"Added {len(large_items)} large bulk items"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Bulk Content: Large Operation", "bulk_content", test_passed, message, duration=duration)
        
        return all_passed
    
    def test_link_functionality(self, page_ids: List[str]):
        """Test link functionality specifically"""
        if not page_ids:
            self.log_test("Link Functionality", "links", False, "No test pages available")
            return False
        
        all_passed = True
        test_page_id = page_ids[0]
        
        # Test 1: Add bookmark with URL
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "bookmark",
            "content": "OpenAI Website",
            "url": "https://www.openai.com"
        })
        
        test_passed = response.get("success", False)
        message = "Added bookmark with URL"
        if not test_passed:
            message += f" | Error: {response.get('message', 'Unknown error')}"
            all_passed = False
        
        self.log_test("Bookmark: Valid URL", "links", test_passed, message, duration=duration)
        
        # Test 2: Add bookmark without URL (should fail)
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "bookmark",
            "content": "Invalid bookmark"
        })
        
        test_passed = not response.get("success", True)  # Should fail
        message = "Bookmark without URL correctly rejected"
        if not test_passed:
            message = "Bookmark without URL was incorrectly accepted"
            all_passed = False
        
        self.log_test("Bookmark: Missing URL", "links", test_passed, message, duration=duration)
        
        # Test 3: Add link_to_page with valid page ID
        if len(page_ids) > 1:
            response, duration = self.make_request("POST", "/api/page/add-content", {
                "page_id": test_page_id,
                "content_type": "link_to_page",
                "content": "Link to test page",
                "page_reference": page_ids[1]
            })
            
            test_passed = response.get("success", False)
            message = "Added link_to_page with valid page ID"
            if not test_passed:
                message += f" | Error: {response.get('message', 'Unknown error')}"
                all_passed = False
            
            self.log_test("Link to Page: Valid ID", "links", test_passed, message, duration=duration)
        else:
            self.log_test("Link to Page: Valid ID", "links", False, "Not enough test pages")
            all_passed = False
        
        # Test 4: Add link_to_page with invalid page reference
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "link_to_page",
            "content": "Link to invalid page",
            "page_reference": "invalid-page-reference-12345"
        })
        
        test_passed = not response.get("success", True)  # Should fail
        message = "Link to invalid page correctly rejected"
        if not test_passed:
            message = "Link to invalid page was incorrectly accepted"
            all_passed = False
        
        self.log_test("Link to Page: Invalid Reference", "links", test_passed, message, duration=duration)
        
        # Test 5: Add link_to_page without page_reference (should fail)
        response, duration = self.make_request("POST", "/api/page/add-content", {
            "page_id": test_page_id,
            "content_type": "link_to_page",
            "content": "Link without reference"
        })
        
        test_passed = not response.get("success", True)  # Should fail
        message = "Link without page_reference correctly rejected"
        if not test_passed:
            message = "Link without page_reference was incorrectly accepted"
            all_passed = False
        
        self.log_test("Link to Page: Missing Reference", "links", test_passed, message, duration=duration)
        
        return all_passed
    
    # ==================== ANALYTICS OPERATIONS TESTS ====================
    
    def test_analytics_operations(self):
        """Test all analytics endpoints"""
        analytics_types = [
            {"type": "workspace", "description": "workspace overview"},
            {"type": "content", "description": "content analysis"},
            {"type": "activity", "description": "activity patterns"},
            {"type": "database", "description": "database analysis"}
        ]
        
        all_passed = True
        
        for analytics_test in analytics_types:
            test_data = {"type": analytics_test["type"]}
            
            response, duration = self.make_request("POST", "/api/analytics", test_data)
            
            success = response.get("success", False)
            message = analytics_test["description"]
            
            if success and response.get("data"):
                data = response["data"]
                
                if analytics_test["type"] == "workspace":
                    total_pages = data.get("total_pages", 0)
                    total_databases = data.get("total_databases", 0)
                    recent_activity = data.get("recent_activity_7_days", 0)
                    message += f" | {total_pages} pages, {total_databases} databases, {recent_activity} recent"
                
                elif analytics_test["type"] == "content":
                    pages_analyzed = data.get("pages_analyzed", 0)
                    pages_with_content = data.get("pages_with_content", 0)
                    message += f" | {pages_analyzed} analyzed, {pages_with_content} with content"
                
                elif analytics_test["type"] == "activity":
                    summary = data.get("activity_summary", {})
                    today = summary.get("today", 0)
                    this_week = summary.get("this_week", 0)
                    message += f" | {today} today, {this_week} this week"
                
                elif analytics_test["type"] == "database":
                    total_databases = data.get("total_databases", 0)
                    message += f" | {total_databases} databases"
                    
            else:
                message += f" | {response.get('error', 'Failed')}"
                all_passed = False
            
            self.log_test(f"Analytics: {analytics_test['description']}", "analytics", success, message, duration=duration)
        
        return all_passed
    
    # ==================== BULK OPERATIONS TESTS ====================
    
    def test_bulk_operations(self):
        """Test all bulk operations"""
        bulk_tests = [
            {
                "operation": "list", 
                "query": json.dumps({"limit": 10, "include_block_counts": False}),
                "description": "list pages (optimized)"
            },
            {
                "operation": "list_pages", 
                "query": json.dumps({"limit": 5, "include_block_counts": True}),
                "description": "list pages with block counts"
            },
            {
                "operation": "analyze", 
                "query": json.dumps({"limit": 5}),
                "description": "analyze pages (limited)"
            },
            {
                "operation": "analyze_pages", 
                "query": json.dumps({"limit": 3}),
                "description": "analyze pages (alt format)"
            }
        ]
        
        all_passed = True
        
        for bulk_test in bulk_tests:
            test_data = {
                "operation": bulk_test["operation"],
                "query": bulk_test["query"]
            }
            
            response, duration = self.make_request("POST", "/api/bulk", test_data)
            
            success = response.get("success", False)
            message = bulk_test["description"]
            
            if success and response.get("data"):
                data = response["data"]
                
                # Handle new response format
                if "total" in data:
                    total = data["total"]
                    returned = data.get("returned", data.get("analyzed", total))
                    message += f" | {returned}/{total} pages processed"
                elif "pages" in data:
                    pages_count = len(data["pages"])
                    message += f" | {pages_count} pages returned"
                
                # Add pagination info if available
                if "pagination_info" in data:
                    pagination = data["pagination_info"]
                    if "limit_applied" in pagination:
                        message += f" | limit: {pagination['limit_applied']}"
                    
            else:
                message += f" | {response.get('error', 'Failed')}"
                all_passed = False
            
            self.log_test(f"Bulk: {bulk_test['description']}", "bulk", success, message, duration=duration)
        
        return all_passed
    
    def test_bulk_page_creation(self):
        """Test bulk page creation"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        pages_data = [
            {"title": f"Bulk Test Page 1 {timestamp}", "content": "Content for bulk page 1"},
            {"title": f"Bulk Test Page 2 {timestamp}", "content": "Content for bulk page 2"},
            {"title": f"Bulk Test Page 3 {timestamp}", "content": "Content for bulk page 3"}
        ]
        
        test_data = {
            "operation": "create",
            "query": json.dumps(pages_data)
        }
        
        response, duration = self.make_request("POST", "/api/bulk", test_data)
        
        success = response.get("success", False)
        message = "bulk page creation"
        
        if success and response.get("data"):
            data = response["data"]
            created = len(data.get("created", []))
            failed = len(data.get("failed", []))
            message += f" | {created} created, {failed} failed"
            
            # Store created page IDs for cleanup
            for page in data.get("created", []):
                if "id" in page:
                    self.test_page_ids.append(page["id"])
        else:
            message += f" | {response.get('error', 'Failed')}"
        
        self.log_test("Bulk Page Creation", "bulk", success, message, duration=duration)
        return success
    
    # ==================== AGENT INTEGRATION TESTS ====================
    
    def test_agent_integration(self):
        """Test agent query endpoint with various actions"""
        agent_tests = [
            {
                "action": "search",
                "parameters": {"query": "test", "page_size": 5},
                "description": "agent search query"
            },
            {
                "action": "analytics",
                "parameters": {"type": "workspace"},
                "description": "agent analytics query"
            },
            {
                "action": "bulk_operations",
                "parameters": {
                    "operation": "list", 
                    "query": json.dumps({"limit": 5, "include_block_counts": False})
                },
                "description": "agent bulk operations (optimized)"
            }
        ]
        
        all_passed = True
        
        for agent_test in agent_tests:
            test_data = {
                "action": agent_test["action"],
                "parameters": agent_test["parameters"]
            }
            
            response, duration = self.make_request("POST", "/api/agent/query", test_data)
            
            success = response.get("success", False)
            message = agent_test["description"]
            
            if success:
                message += " | Agent query processed successfully"
            else:
                message += f" | {response.get('error', 'Failed')}"
                all_passed = False
            
            self.log_test(f"Agent: {agent_test['description']}", "agent", success, message, duration=duration)
        
        # Test with legacy "params" format
        legacy_test_data = {
            "action": "search",
            "params": {"query": "legacy", "page_size": 3}  # Using "params" instead of "parameters"
        }
        
        response, duration = self.make_request("POST", "/api/agent/query", legacy_test_data)
        success = response.get("success", False)
        message = "legacy params format" + (" | Success" if success else f" | {response.get('error', 'Failed')}")
        
        self.log_test("Agent: legacy params format", "agent", success, message, duration=duration)
        
        return all_passed
    
    # ==================== EDGE CASES AND ERROR HANDLING ====================
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        edge_tests = [
            {
                "test": "empty page title",
                "endpoint": "/api/page/create", 
                "data": {"title": "", "content": "test"},
                "expect_success": False
            },
            {
                "test": "invalid content type",
                "endpoint": "/api/page/add-content",
                "data": {"page_id": "test-page-id", "content_type": "invalid_type", "content": "test"},
                "expect_success": False
            },
            {
                "test": "bookmark without URL",
                "endpoint": "/api/page/add-content",
                "data": {"page_id": "test-page-id", "content_type": "bookmark", "content": "test"},
                "expect_success": False
            },
            {
                "test": "link_to_page without reference",
                "endpoint": "/api/page/add-content",
                "data": {"page_id": "test-page-id", "content_type": "link_to_page", "content": "test"},
                "expect_success": False
            },
            {
                "test": "invalid analytics type",
                "endpoint": "/api/analytics",
                "data": {"type": "invalid_analytics_type"},
                "expect_success": False
            },
            {
                "test": "invalid bulk operation",
                "endpoint": "/api/bulk",
                "data": {"operation": "invalid_operation"},
                "expect_success": False
            },
            {
                "test": "missing required parameters",
                "endpoint": "/api/agent/query",
                "data": {"action": "search"},  # Missing parameters
                "expect_success": True  # Should default to empty query
            }
        ]
        
        all_passed = True
        
        for edge_test in edge_tests:
            response, duration = self.make_request("POST", edge_test["endpoint"], edge_test["data"])
            
            success = response.get("success", False)
            expected_success = edge_test["expect_success"]
            
            # Check if result matches expectation
            test_passed = (success == expected_success)
            message = edge_test["test"]
            
            if test_passed:
                message += f" | Handled correctly ({'success' if success else 'error'} as expected)"
            else:
                message += f" | Unexpected result (got {'success' if success else 'error'}, expected {'success' if expected_success else 'error'})"
                # Add more debug info for invalid page ID case
                if edge_test["test"] == "invalid page ID":
                    message += f" | Response: {response.get('message', 'No message')}"
                all_passed = False
            
            self.log_test(f"Edge Case: {edge_test['test']}", "edge_cases", test_passed, message, duration=duration)
        
        return all_passed
    
    # ==================== TEST EXECUTION AND REPORTING ====================
    
    def run_comprehensive_test_suite(self):
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive Notion MCP Server V2 Test Suite")
        print("=" * 80)
        
        # Print configuration
        print_config()
        
        print(f"\n📋 Running Tests against: {self.base_url}")
        print("=" * 80)
        
        # Test execution order
        test_functions = [
            ("Server Health & Connectivity", self.test_health_check),
            ("Core Operations - Search", self.test_search_functionality),
            ("Core Operations - Listing", self.test_list_operations),
            ("Core Operations - Page Creation", lambda: self.test_page_creation()),
            ("Core Operations - Page Reading", lambda: self.test_page_reading(self.test_page_ids)),
            ("Update Operations - Content Addition", lambda: self.test_content_addition_operations(self.test_page_ids)),
            ("Update Operations - Bulk Content", lambda: self.test_bulk_content_addition(self.test_page_ids)),
            ("Link Functionality", lambda: self.test_link_functionality(self.test_page_ids)),
            ("Analytics Operations", self.test_analytics_operations),
            ("Bulk Operations - Basic", self.test_bulk_operations),
            ("Bulk Operations - Page Creation", self.test_bulk_page_creation),
            ("Agent Integration", self.test_agent_integration),
            ("Edge Cases & Error Handling", self.test_edge_cases)
        ]
        
        # Execute tests
        for test_name, test_func in test_functions:
            print(f"\n📝 Running: {test_name}")
            print("-" * 60)
            
            try:
                result = test_func()
                if isinstance(result, tuple):
                    # Handle functions that return multiple values
                    pass
                elif not result:
                    print(f"⚠️  {test_name} had some failures")
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                self.log_test(test_name, "exception", False, f"Exception: {str(e)}")
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
        return True
    
    def generate_comprehensive_report(self):
        """Generate detailed test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.test_start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"├── Total Tests: {total_tests}")
        print(f"├── ✅ Passed: {passed_tests}")
        print(f"├── ❌ Failed: {failed_tests}")
        print(f"├── 📊 Success Rate: {success_rate:.1f}%")
        print(f"├── ⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"└── 🎯 Average per Test: {total_duration/total_tests:.2f} seconds")
        
        # Category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in self.categories.items():
            if results:
                category_passed = sum(1 for r in results if r["success"])
                category_total = len(results)
                category_rate = (category_passed / category_total) * 100
                print(f"├── {category.upper():<12}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"├── {result['category'].upper():<8} | {result['test_name']:<35} | {result['message']}")
        
        # Performance insights
        print(f"\n⚡ PERFORMANCE INSIGHTS:")
        test_durations = [r["duration"] for r in self.test_results if r["duration"] > 0]
        if test_durations:
            avg_duration = sum(test_durations) / len(test_durations)
            max_duration = max(test_durations)
            min_duration = min(test_durations)
            
            print(f"├── Average Response Time: {avg_duration:.2f}s")
            print(f"├── Slowest Test: {max_duration:.2f}s")
            print(f"└── Fastest Test: {min_duration:.2f}s")
        
        # Save detailed report
        self.save_detailed_report()
        
        # Cleanup test data
        self.cleanup_test_data()
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Test suite passed with high success rate!")
        elif success_rate >= 75:
            print("✅ GOOD! Most tests passed successfully!")
        elif success_rate >= 50:
            print("⚠️  WARNING! Many tests failed - please review issues!")
        else:
            print("❌ CRITICAL! Most tests failed - server may have serious issues!")
        
        print("=" * 80)
    
    def save_detailed_report(self):
        """Save detailed test report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"notion_test_report_{timestamp}.json"
        
        report_data = {
            "test_summary": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r["success"]),
                "failed_tests": sum(1 for r in self.test_results if not r["success"]),
                "success_rate": (sum(1 for r in self.test_results if r["success"]) / len(self.test_results)) * 100,
                "server_url": self.base_url
            },
            "test_results": self.test_results,
            "category_breakdown": {
                category: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"])
                }
                for category, results in self.categories.items()
                if results
            },
            "created_test_pages": self.test_page_ids
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report file: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data (log test pages created)"""
        if self.test_page_ids:
            print(f"\n🧹 Test Data Cleanup:")
            print(f"├── {len(self.test_page_ids)} test pages were created during testing")
            print(f"├── Page IDs are saved in the detailed report for manual cleanup if needed")
            print(f"└── Note: Automatic page deletion not implemented (requires additional permissions)")
         
         
def main():
    """Main test runner"""
    
    # Check if server is running
    base_url = "http://localhost:8000"
    
    print("🔍 Checking if Notion MCP Server is running...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("❌ Server is not running or not accessible!")
        print(f"   Error: {str(e)}")
        print(f"\n💡 Please start the server first:")
        print(f"   python -m src.notion_mcp_server.api_serverV2")
        print(f"   or")
        print(f"   cd src/notion_mcp_server && python api_serverV2.py")
        return 1
    
    # Run comprehensive tests
    tester = ComprehensiveNotionTester(base_url)
    success = tester.run_comprehensive_test_suite()
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Test suite interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error in test suite: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1) 