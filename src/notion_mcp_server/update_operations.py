"""
Update Operations for Notion API
Handles all content update functionality including templates and block operations
"""

from typing import List, Dict, Any
from notion_client import Client
from .notion_utils import NotionUtils


class UpdateOperations:
    """Handle all update operations for Notion content"""
    
    def __init__(self, notion_client: Client):
        self.notion = notion_client
    
    async def update_content_interactive(self):
        """Interactive content update using Notion API block operations"""
        print("\n🔄 UPDATE PAGE CONTENT")
        print("=" * 40)
        
        # Get page to update
        page_id = input("Enter page ID or name to update: ").strip()
        if not page_id:
            print("❌ Page ID/name required")
            return
        
        # If not a valid UUID, search for page
        if not NotionUtils.is_valid_uuid(page_id):
            try:
                search_results = self.notion.search(
                    query=page_id,
                    filter={"property": "object", "value": "page"}
                )
                
                if not search_results["results"]:
                    print(f"❌ No pages found matching '{page_id}'")
                    return
                
                # Show search results
                print(f"\n📋 Found {len(search_results['results'])} pages:")
                for i, page in enumerate(search_results["results"], 1):
                    title = NotionUtils.extract_title(page)
                    print(f"{i}. {title}")
                
                # Let user select
                try:
                    choice = int(input("\nSelect page number: ").strip()) - 1
                    if 0 <= choice < len(search_results["results"]):
                        page_id = search_results["results"][choice]["id"]
                        page_title = NotionUtils.extract_title(search_results["results"][choice])
                    else:
                        print("❌ Invalid selection")
                        return
                except ValueError:
                    print("❌ Invalid number")
                    return
                    
            except Exception as e:
                print(f"❌ Search error: {str(e)}")
                return
        else:
            # Get page title for valid UUID
            try:
                page = self.notion.pages.retrieve(page_id=page_id)
                page_title = NotionUtils.extract_title(page)
            except Exception as e:
                print(f"❌ Error retrieving page: {str(e)}")
                return
        
        try:
            print(f"\n📄 Updating page: {page_title}")
            
            # Show current content (first few blocks)
            print("\n📋 Current content (first 5 blocks):")
            try:
                blocks = self.notion.blocks.children.list(
                    block_id=page_id,
                    page_size=5
                )
                
                if blocks["results"]:
                    for i, block in enumerate(blocks["results"], 1):
                        block_type = block["type"]
                        content = NotionUtils.extract_block_text(block)
                        print(f"{i}. [{block_type}] {content[:100]}...")
                else:
                    print("   (No existing content)")
                    
            except Exception as e:
                print(f"⚠️  Could not read current content: {str(e)}")
            
            # Update options
            print("\n🔄 Update options:")
            print("1. Add new paragraph")
            print("2. Add new heading")
            print("3. Add new bullet point")
            print("4. Add new to-do item")
            print("5. Add template content")
            print("6. Add custom block")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                await self._add_paragraph_block(page_id)
            elif choice == "2":
                await self._add_heading_block(page_id)
            elif choice == "3":
                await self._add_bullet_block(page_id)
            elif choice == "4":
                await self._add_todo_block(page_id)
            elif choice == "5":
                await self._add_template_content(page_id, page_title)
            elif choice == "6":
                await self._add_custom_block(page_id)
            else:
                print("❌ Invalid option")
                
        except Exception as e:
            print(f"❌ Update error: {str(e)}")
    
    async def _add_paragraph_block(self, page_id: str):
        """Add a paragraph block to the page"""
        content = input("Enter paragraph text: ").strip()
        if not content:
            print("❌ Text required")
            return
        
        try:
            response = self.notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": content}
                                }
                            ]
                        }
                    }
                ]
            )
            print(f"✅ Added paragraph block successfully!")
            
        except Exception as e:
            print(f"❌ Error adding paragraph: {str(e)}")
    
    async def _add_heading_block(self, page_id: str):
        """Add a heading block to the page"""
        content = input("Enter heading text: ").strip()
        if not content:
            print("❌ Text required")
            return
        
        heading_level = input("Heading level (1-3, default 1): ").strip()
        if not heading_level:
            heading_level = "1"
        
        heading_types = {"1": "heading_1", "2": "heading_2", "3": "heading_3"}
        heading_type = heading_types.get(heading_level, "heading_1")
        
        try:
            response = self.notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": heading_type,
                        heading_type: {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": content}
                                }
                            ]
                        }
                    }
                ]
            )
            print(f"✅ Added {heading_type} block successfully!")
            
        except Exception as e:
            print(f"❌ Error adding heading: {str(e)}")
    
    async def _add_bullet_block(self, page_id: str):
        """Add a bulleted list item block to the page"""
        content = input("Enter bullet point text: ").strip()
        if not content:
            print("❌ Text required")
            return
        
        try:
            response = self.notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": content}
                                }
                            ]
                        }
                    }
                ]
            )
            print(f"✅ Added bullet point successfully!")
            
        except Exception as e:
            print(f"❌ Error adding bullet point: {str(e)}")
    
    async def _add_todo_block(self, page_id: str):
        """Add a to-do block to the page"""
        content = input("Enter to-do text: ").strip()
        if not content:
            print("❌ Text required")
            return
        
        try:
            response = self.notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": content}
                                }
                            ],
                            "checked": False
                        }
                    }
                ]
            )
            print(f"✅ Added to-do item successfully!")
            
        except Exception as e:
            print(f"❌ Error adding to-do: {str(e)}")
    
    async def _add_custom_block(self, page_id: str):
        """Add a custom block with user-defined type"""
        print("\n📝 Available block types:")
        print("• paragraph")
        print("• heading_1, heading_2, heading_3") 
        print("• bulleted_list_item")
        print("• numbered_list_item")
        print("• to_do")
        print("• quote")
        print("• callout")
        
        block_type = input("Enter block type: ").strip()
        content = input("Enter content: ").strip()
        
        if not block_type or not content:
            print("❌ Block type and content required")
            return
        
        # Build block based on type
        if block_type in ["paragraph", "quote", "callout"]:
            block_config = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content}
                    }
                ]
            }
        elif block_type in ["heading_1", "heading_2", "heading_3"]:
            block_config = {
                "rich_text": [
                    {
                        "type": "text", 
                        "text": {"content": content}
                    }
                ]
            }
        elif block_type in ["bulleted_list_item", "numbered_list_item"]:
            block_config = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content}
                    }
                ]
            }
        elif block_type == "to_do":
            block_config = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content}
                    }
                ],
                "checked": False
            }
        else:
            print(f"❌ Unsupported block type: {block_type}")
            return
        
        try:
            response = self.notion.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": block_type,
                        block_type: block_config
                    }
                ]
            )
            print(f"✅ Added {block_type} block successfully!")
            
        except Exception as e:
            print(f"❌ Error adding {block_type}: {str(e)}")
    
    async def _add_template_content(self, page_id: str, page_title: str):
        """Add template content based on page context"""
        title_lower = page_title.lower()
        
        print("\n📋 Template Content Options:")
        
        if any(keyword in title_lower for keyword in ['aws', 'amazon', 'cloud']):
            print("1. AWS Agent Implementation Guide")
            print("2. AWS Services Overview")
            print("3. AWS Integration Patterns")
            print("4. AWS Security Best Practices")
            
            choice = input("Select template (1-4): ").strip()
            
            if choice == "1":
                await self._add_aws_agent_template(page_id)
            elif choice == "2":
                await self._add_aws_services_template(page_id)
            elif choice == "3":
                await self._add_aws_integration_template(page_id)
            elif choice == "4":
                await self._add_aws_security_template(page_id)
            else:
                print("❌ Invalid template selection")
                
        elif any(keyword in title_lower for keyword in ['agent', 'ai']):
            print("1. AI Agent Architecture")
            print("2. Agent Workflow Design")
            print("3. Tool Integration Guide")
            
            choice = input("Select template (1-3): ").strip()
            
            if choice == "1":
                await self._add_ai_architecture_template(page_id)
            elif choice == "2":
                await self._add_workflow_template(page_id)
            elif choice == "3":
                await self._add_tool_integration_template(page_id)
            else:
                print("❌ Invalid template selection")
        else:
            await self._add_general_template(page_id)
    
    async def _add_aws_agent_template(self, page_id: str):
        """Add AWS Agent implementation template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS Agent Implementation Methods"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "This guide covers different methods to implement AI agents on AWS infrastructure."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "1. AWS Lambda + API Gateway"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Serverless agent deployment"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Pay-per-request pricing model"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Automatic scaling and high availability"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "2. ECS + Fargate"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Container-based agent deployment"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Long-running processes and persistent connections"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Better resource control and monitoring"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "3. EC2 + Auto Scaling"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Full control over infrastructure"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Custom configurations and optimizations"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Suitable for intensive workloads"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Key AWS Services for Agent Implementation"}}]
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon Bedrock - Managed foundation models"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS SageMaker - Custom model training and deployment"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon DynamoDB - Fast NoSQL database for agent state"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon S3 - Storage for files and model artifacts"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon CloudWatch - Monitoring and logging"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS Secrets Manager - Secure API key management"}}],
                    "checked": False
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ AWS Agent template added successfully!")
        except Exception as e:
            print(f"❌ Error adding AWS Agent template: {str(e)}")
    
    async def _add_aws_services_template(self, page_id: str):
        """Add AWS Services overview template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS Services Overview"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Key AWS services for building robust AI agents and applications."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Compute Services"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS Lambda - Serverless compute for event-driven applications"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon ECS - Container orchestration service"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon EC2 - Virtual servers in the cloud"}}]
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ AWS Services template added successfully!")
        except Exception as e:
            print(f"❌ Error adding AWS Services template: {str(e)}")
    
    async def _add_aws_integration_template(self, page_id: str):
        """Add AWS Integration patterns template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS Integration Patterns"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Common integration patterns for AWS-based applications."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Event-Driven Architecture"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Amazon EventBridge for event routing"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS SQS for message queuing"}}]
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ AWS Integration template added successfully!")
        except Exception as e:
            print(f"❌ Error adding AWS Integration template: {str(e)}")
    
    async def _add_aws_security_template(self, page_id: str):
        """Add AWS Security best practices template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "AWS Security Best Practices"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Security guidelines for AWS agent implementations."}}]
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Use IAM roles instead of access keys"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Enable CloudTrail for audit logging"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Use VPC for network isolation"}}],
                    "checked": False
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ AWS Security template added successfully!")
        except Exception as e:
            print(f"❌ Error adding AWS Security template: {str(e)}")
    
    async def _add_ai_architecture_template(self, page_id: str):
        """Add AI Architecture template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "AI Agent Architecture"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Core components of a robust AI agent system."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Core Components"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Language Model Engine"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Tool Integration Layer"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Memory Management System"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Workflow Orchestration"}}]
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ AI Architecture template added successfully!")
        except Exception as e:
            print(f"❌ Error adding AI Architecture template: {str(e)}")
    
    async def _add_workflow_template(self, page_id: str):
        """Add Workflow template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Agent Workflow Design"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Designing effective workflows for AI agents."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Workflow Steps"}}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Input Processing & Validation"}}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Intent Recognition & Planning"}}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Tool Selection & Execution"}}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Response Generation & Delivery"}}]
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ Workflow template added successfully!")
        except Exception as e:
            print(f"❌ Error adding Workflow template: {str(e)}")
    
    async def _add_tool_integration_template(self, page_id: str):
        """Add Tool Integration template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Tool Integration Guide"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Best practices for integrating external tools with AI agents."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Integration Patterns"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "REST API Integration"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Database Connections"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "File System Operations"}}]
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ Tool Integration template added successfully!")
        except Exception as e:
            print(f"❌ Error adding Tool Integration template: {str(e)}")
    
    async def _add_general_template(self, page_id: str):
        """Add General template"""
        template_blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Project Overview"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "A comprehensive overview of the project goals and implementation."}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Key Features"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Feature 1: Core functionality"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Feature 2: Enhanced capabilities"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Next Steps"}}]
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Define project requirements"}}],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": "Create implementation plan"}}],
                    "checked": False
                }
            }
        ]
        
        try:
            await self._append_blocks(page_id, template_blocks)
            print("✅ General template added successfully!")
        except Exception as e:
            print(f"❌ Error adding General template: {str(e)}")
    
    async def _append_blocks(self, page_id: str, blocks: List[dict]):
        """Helper method to append multiple blocks"""
        # Notion API has a limit on number of blocks per request
        # Split into chunks of 100 blocks
        chunk_size = 100
        
        for i in range(0, len(blocks), chunk_size):
            chunk = blocks[i:i + chunk_size]
            await self.notion.blocks.children.append(
                block_id=page_id,
                children=chunk
            ) 