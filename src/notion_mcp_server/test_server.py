#!/usr/bin/env python3
"""
Comprehensive Test Suite for Notion MCP Server V2
Tests all endpoints and functionality with proper error handling and reporting.
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_mcp_server.config import get_config, print_config
from notion_mcp_server.api_serverV2 import app

# Load environment variables
load_dotenv()


class NotionServerTester:
    """Comprehensive test suite for Notion MCP Server V2"""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.config = get_config()
        self.test_results = []
        self.test_page_ids = []  # Store created page IDs for cleanup
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().isoformat()
        
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": timestamp,
            "data": data
        }
        
        self.test_results.append(result)
        print(f"{status} | {test_name} | {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.make_request("GET", "/health")
        
        success = response.get("success", False) and response.get("status") == "healthy"
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        self.log_test("Health Check", success, message)
        return success
    
    def test_search_functionality(self):
        """Test search endpoint"""
        test_data = {
            "query": "aws",
            "page_size": 10
        }
        
        response = self.make_request("POST", "/api/search", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        # Check if we have data
        if success and response.get("data"):
            data = response["data"]
            pages_count = len(data.get("pages", []))
            databases_count = len(data.get("databases", []))
            message += f" | Found {pages_count} pages, {databases_count} databases"
        
        self.log_test("Search Functionality", success, message)
        return success
    
    def test_page_creation(self):
        """Test page creation endpoint"""
        test_data = {
            "title": f"Test Page {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": "This is a test page created by the automated test suite."
        }
        
        response = self.make_request("POST", "/api/page/create", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        # Store page ID for cleanup
        if success and response.get("data", {}).get("id"):
            page_id = response["data"]["id"]
            self.test_page_ids.append(page_id)
            message += f" | Page ID: {page_id[:8]}..."
        
        self.log_test("Page Creation", success, message)
        return success, response.get("data", {}).get("id")
    
    def test_page_reading(self, page_id: str):
        """Test page reading endpoint"""
        if not page_id:
            self.log_test("Page Reading", False, "No page ID provided")
            return False
        
        test_data = {
            "identifier": page_id
        }
        
        response = self.make_request("POST", "/api/page/read", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        # Check content
        if success and response.get("data"):
            data = response["data"]
            title = data.get("title", "")
            content_length = len(data.get("content", ""))
            block_count = data.get("block_count", 0)
            message += f" | '{title}' | {content_length} chars | {block_count} blocks"
        
        self.log_test("Page Reading", success, message)
        return success
    
    def test_content_addition(self, page_id: str):
        """Test content addition endpoint"""
        if not page_id:
            self.log_test("Content Addition", False, "No page ID provided")
            return False
        
        test_data = {
            "page_id": page_id,
            "content_type": "paragraph",
            "content": "This paragraph was added by the automated test suite."
        }
        
        response = self.make_request("POST", "/api/page/add-content", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        self.log_test("Content Addition", success, message)
        return success
    
    def test_bulk_content_addition(self, page_id: str):
        """Test bulk content addition endpoint"""
        if not page_id:
            self.log_test("Bulk Content Addition", False, "No page ID provided")
            return False
        
        test_data = {
            "page_id": page_id,
            "items": [
                {
                    "content_type": "heading_2",
                    "content": "Test Section"
                },
                {
                    "content_type": "paragraph",
                    "content": "This is a test paragraph in the bulk addition."
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "First bullet point"
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "Second bullet point"
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "Second bullet point"
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "Second bullet point"
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "Second bullet point"
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "Second bullet point"
                },
                {
                    "content_type": "bulleted_list_item",
                    "content": "Second bullet point"
                },
                {
                    "content_type": "to_do",
                    "content": "Complete the test suite",
                    "checked": False
                }
            ]
        }
        
        response = self.make_request("POST", "/api/page/bulk-add-content", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        if success and response.get("data"):
            items_added = response["data"].get("items_added", 0)
            message += f" | Added {items_added} items"
        
        self.log_test("Bulk Content Addition", success, message)
        return success
    
    def test_analytics(self):
        """Test analytics endpoint"""
        test_data = {
            "type": "workspace"
        }
        
        response = self.make_request("POST", "/api/analytics", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        # Check analytics data
        if success and response.get("data"):
            data = response["data"]
            total_pages = data.get("total_pages", 0)
            total_databases = data.get("total_databases", 0)
            recent_activity = data.get("recent_activity_7_days", 0)
            message += f" | {total_pages} pages, {total_databases} databases, {recent_activity} recent"
        
        self.log_test("Analytics", success, message)
        return success
    
    def test_bulk_operations(self):
        """Test bulk operations endpoint"""
        test_data = {
            "operation": "list_pages"
        }
        
        response = self.make_request("POST", "/api/bulk", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        # Check bulk data
        if success and response.get("data"):
            data = response["data"]
            total = data.get("total", 0)
            message += f" | Retrieved {total} pages"
        
        self.log_test("Bulk Operations", success, message)
        return success
    
    def test_agent_query_integration(self):
        """Test agent query endpoint"""
        test_data = {
            "action": "search",
            "params": {
                "query": "aws",
                "page_size": 5
            }
        }
        
        response = self.make_request("POST", "/api/agent/query", test_data)
        
        success = response.get("success", False)
        message = response.get("message", "") if success else response.get("error", "Failed")
        
        self.log_test("Agent Query Integration", success, message)
        return success
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Notion MCP Server Tests")
        print("=" * 60)
        
        # Print configuration
        print_config()
        
        print("\n📋 Running Tests...")
        print("-" * 40)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Health check failed. Server may not be running.")
            return False
        
        # Test 2: Search
        self.test_search_functionality()
        
        # Test 3: Page Creation
        success, page_id = self.test_page_creation()
        
        # Test 4: Page Reading (requires page from Test 3)
        if page_id:
            self.test_page_reading(page_id)
            
            # Test 5: Content Addition (requires page from Test 3)
            self.test_content_addition(page_id)
            
            # Test 6: Bulk Content Addition (requires page from Test 3)
            self.test_bulk_content_addition(page_id)
        
        # Test 7: Analytics
        self.test_analytics()
        
        # Test 8: Bulk Operations
        self.test_bulk_operations()
        
        # Test 9: Agent Query Integration
        self.test_agent_query_integration()
        
        # Generate test report
        self.generate_test_report()
        
        return True
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test_name']}: {result['message']}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test_name']}: {result['message']}")
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("=" * 60)
        
        # Cleanup
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Clean up test data (pages created during testing)"""
        if self.test_page_ids:
            print(f"\n🧹 Cleaning up {len(self.test_page_ids)} test pages...")
            # Note: Actual cleanup would require implementing a delete endpoint
            # For now, we just log the pages that were created
            print("📋 Test pages created (may need manual cleanup):")
            for page_id in self.test_page_ids:
                print(f"  • {page_id}")


def main():
    """Main test runner"""
    
    # Check if server is running
    base_url = "http://localhost:8000"
    
    print("🔍 Checking if server is running...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the server first:")
        print("   python -m notion_mcp_server.api_serverV2")
        return 1
    
    # Run tests
    tester = NotionServerTester(base_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 