import os
import uuid
import json
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from traceback import format_exc
from utils.sql_manager import SQLManager
from utils.user_manager import UserManager
from utils.chat_history_manager import ChatHistoryManager
from utils.search_manager import SearchManager
# from utils.prepare_system_prompt import prepare_system_prompt_for_agentic_chatbot_v2
from utils.prepare_system_prompt import prepare_system_prompt_for_agentic_chatbot_v4
from utils.utils import Utils
from utils.config import Config
from utils.vector_db_manager import VectorDBManager

# Import Notion ServerV2 components
from notion_client import Client
from notion_mcp_server.core_operations import CoreOperations
from notion_mcp_server.analytics_operations import AnalyticsOperations
from notion_mcp_server.bulk_operations import BulkOperations
from notion_mcp_server.update_operations import UpdateOperations
from notion_mcp_server.notion_utils import NotionUtils

load_dotenv()


class Chatbot:
    """
    Chatbot class that handles conversational flow, manages user data, and executes function calls using OpenAI's API.
    """

    def __init__(self):
        """
        Initializes the Chatbot instance.

        Sets up OpenAI client, configuration settings, session ID, and database managers.
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cfg = Config()
        self.chat_model = self.cfg.chat_model
        self.summary_model = self.cfg.summary_model
        self.temperature = self.cfg.temperature
        self.max_history_pairs = self.cfg.max_history_pairs

        self.session_id = str(uuid.uuid4())
        self.utils = Utils()
        self.sql_manager = SQLManager(self.cfg.db_path)
        self.user_manager = UserManager(self.sql_manager)
        self.chat_history_manager = ChatHistoryManager(
            self.sql_manager, self.user_manager.user_id, self.session_id, self.client, self.summary_model, self.cfg.max_tokens)

        self.vector_db_manager = VectorDBManager(self.cfg)

        self.search_manager = SearchManager(
            self.sql_manager, self.utils, self.client, self.summary_model, self.cfg.max_characters)
        
        # Initialize Notion ServerV2 components
        self.notion_token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
        if self.notion_token:
            self.notion_client = Client(auth=self.notion_token)
            self.notion_core = CoreOperations(self.notion_client)
            self.notion_analytics = AnalyticsOperations(self.notion_client)
            self.notion_bulk = BulkOperations(self.notion_client)
            self.notion_update = UpdateOperations(self.notion_client)
            print("✅ Notion ServerV2 initialized successfully!")
        else:
            print("⚠️  Notion token not found. Notion functionality will be disabled.")
            self.notion_client = None
        
        # Setup agent functions with Notion tools
        self.agent_functions = [
            self.utils.jsonschema(self.user_manager.add_user_info_to_database),
            self.utils.jsonschema(self.vector_db_manager.search_vector_db)
        ]
        
        # Add Notion function schemas if available
        if self.notion_client:
            self.agent_functions.extend([
                # Core Operations
                self.utils.jsonschema(self.notion_search_content),
                self.utils.jsonschema(self.notion_read_page),
                self.utils.jsonschema(self.notion_create_page),
                self.utils.jsonschema(self.notion_list_pages),
                self.utils.jsonschema(self.notion_list_databases),
                
                # Content Addition Helper
                self.utils.jsonschema(self.notion_add_structured_content),
                self.utils.jsonschema(self.notion_add_smart_content),
                
                # Analytics Operations
                self.utils.jsonschema(self.notion_workspace_analytics),
                self.utils.jsonschema(self.notion_content_analytics),
                self.utils.jsonschema(self.notion_activity_analytics),
                
                # Update Operations
                self.utils.jsonschema(self.notion_add_paragraph),
                self.utils.jsonschema(self.notion_add_heading),
                self.utils.jsonschema(self.notion_add_bullet_point),
                self.utils.jsonschema(self.notion_add_todo),
                self.utils.jsonschema(self.notion_add_multiple_todos),
                
                # Bulk Operations
                self.utils.jsonschema(self.notion_bulk_create_pages),
                self.utils.jsonschema(self.notion_bulk_list_pages),
                self.utils.jsonschema(self.notion_bulk_analyze_pages),
            ])
        
        
    def execute_function_call(self, function_name: str, function_args: dict) -> tuple[str, str]:
        """
        Executes the requested function based on the function name and arguments.

        Args:
            function_name (str): The name of the function to execute.
            function_args (dict): The arguments required for the function.

        Returns:
            tuple[str, str]: A tuple containing the function state and result.
        """
        try:
            # Vector DB and User Management Functions
            if function_name == "search_vector_db":
                return self.vector_db_manager.search_vector_db(**function_args)
            elif function_name == "add_user_info_to_database":
                return self.user_manager.add_user_info_to_database(function_args)
            
            # Notion Core Operations
            elif function_name == "notion_search_content":
                result = self.notion_search_content(**function_args)
                
                # Add chaining context for content addition tasks
                if result[0] == "Function call successful.":
                    # Check if this looks like a content addition request
                    search_term = function_args.get("search_term", "").lower()
                    if any(keyword in search_term for keyword in ["education", "notes", "project", "page"]):
                        chaining_hint = "\n\n💡 NEXT STEP: If you need to add content to this page, use functions like notion_add_paragraph, notion_add_heading, notion_add_bullet_point, or notion_add_todo with the page title or ID found above."
                        return result[0], result[1] + chaining_hint
                
                return result
            elif function_name == "notion_read_page":
                return self.notion_read_page(**function_args)
            elif function_name == "notion_create_page":
                return self.notion_create_page(**function_args)
            elif function_name == "notion_list_pages":
                return self.notion_list_pages(**function_args)
            elif function_name == "notion_list_databases":
                return self.notion_list_databases(**function_args)
            
            # Content Addition Helper
            elif function_name == "notion_add_structured_content":
                return self.notion_add_structured_content(**function_args)
            elif function_name == "notion_add_smart_content":
                return self.notion_add_smart_content(**function_args)
            
            # Notion Analytics Operations
            elif function_name == "notion_workspace_analytics":
                return self.notion_workspace_analytics(**function_args)
            elif function_name == "notion_content_analytics":
                return self.notion_content_analytics(**function_args)
            elif function_name == "notion_activity_analytics":
                return self.notion_activity_analytics(**function_args)
            
            # Notion Update Operations
            elif function_name == "notion_add_paragraph":
                return self.notion_add_paragraph(**function_args)
            elif function_name == "notion_add_heading":
                return self.notion_add_heading(**function_args)
            elif function_name == "notion_add_bullet_point":
                return self.notion_add_bullet_point(**function_args)
            elif function_name == "notion_add_todo":
                return self.notion_add_todo(**function_args)
            elif function_name == "notion_add_multiple_todos":
                return self.notion_add_multiple_todos(**function_args)
            
            # Notion Bulk Operations
            elif function_name == "notion_bulk_create_pages":
                return self.notion_bulk_create_pages(**function_args)
            elif function_name == "notion_bulk_list_pages":
                return self.notion_bulk_list_pages(**function_args)
            elif function_name == "notion_bulk_analyze_pages":
                return self.notion_bulk_analyze_pages(**function_args)
            
            # Unknown function
            else:
                return "Function call failed.", f"Unknown function: {function_name}"
                
        except Exception as e:
            return "Function call failed.", f"Error executing {function_name}: {str(e)}"

    def chat(self, user_message: str) -> str:
        """
        Handles a conversation with the user, manages chat history, and executes function calls if needed.

        Args:
            user_message (str): The message from the user.

        Returns:
            str: The chatbot's response or an error message.
        """
        function_call_result_section = ""
        function_call_state = None
        chat_state = "thinking"
        function_call_count = 0
        self.chat_history = self.chat_history_manager.chat_history
        # function_call_prompt = f"""## Based on the last user's message you called the following functions:\n"""
        self.previous_summary = self.chat_history_manager.get_latest_summary()
        while chat_state != "finished":
            try:
                if function_call_state == "Function call successful.":
                    # Enhanced chaining for content addition tasks - CHECK FIRST
                    chaining_guidance = ""
                    is_chaining_task = False
                    
                    # Check for various chaining scenarios
                    if function_name == "notion_search_content" and any(keyword in user_message.lower() for keyword in ["add content", "add to", "create content", "add paragraph", "add heading", "add bullet", "add todo", "add aws", "add structured", "create sections", "multiple", "several", "tasks", "items", "todo list"]):
                        chat_state = "thinking"  # Continue the conversation for content addition
                        is_chaining_task = True
                        chaining_guidance = "\n\n🔄 CONTENT ADDITION TASK DETECTED: You found the page, now proceed to add the requested content using the appropriate notion_add_* functions."
                    
                    elif function_name == "notion_search_content" and any(keyword in user_message.lower() for keyword in ["read content", "read page", "read and add", "same type", "similar content", "copy content"]):
                        chat_state = "thinking"  # Continue for read-and-add operations
                        is_chaining_task = True
                        chaining_guidance = "\n\n🔄 READ-AND-ADD TASK DETECTED: You found the target page, now continue with reading the source content and adding it to the target page."
                    
                    elif function_name == "notion_read_page" and any(keyword in user_message.lower() for keyword in ["add to", "update", "modify", "append"]):
                        chat_state = "thinking"  # Continue for page updates
                        is_chaining_task = True
                        chaining_guidance = "\n\n🔄 PAGE UPDATE TASK DETECTED: You read the page, now proceed to add or update the content as requested."
                    
                    elif function_name == "notion_create_page" and any(keyword in user_message.lower() for keyword in ["add content", "with sections", "with bullet", "with todo"]):
                        chat_state = "thinking"  # Continue for adding content to new page
                        is_chaining_task = True
                        chaining_guidance = "\n\n🔄 NEW PAGE CONTENT TASK DETECTED: You created the page, now add the requested content to it."
                    
                    # Special case: Multi-step operations involving reading from one page and adding to another
                    elif any(pattern in user_message.lower() for pattern in ["read content from", "read page", "read and add", "same type of content", "similar content", "copy from"]):
                        chat_state = "thinking"  # Continue for complex multi-step operations
                        is_chaining_task = True
                        chaining_guidance = "\n\n🔄 MULTI-STEP OPERATION DETECTED: Continue with the full workflow - read source content, then add to target page."
                    
                    else:
                        # Only set to finished if it's NOT a chaining task
                        chat_state = "finished"
                    
                    if function_name == "add_user_info_to_database":
                        self.user_manager.refresh_user_info()
                    
                    function_call_result_section = (
                        f"## Function Call Executed\n\n"
                        f"- The assistant just called the function `{function_name}` in response to the user's most recent message.\n"
                        f"- Arguments provided:\n"
                        + "".join([f"  - {k}: {v}\n" for k,
                                   v in function_args.items()])
                        + f"- Outcome: ✅ {function_call_state}\n\n"
                        "Please proceed with the conversation using the new context.\n\n"
                        + f"{function_call_result}"
                        + chaining_guidance
                    )
                    print("************************************")
                    print(function_call_result)
                    if is_chaining_task:
                        print(f"🔄 CHAINING DETECTED: {function_name} -> continuing conversation")
                        print(f"📝 User message keywords: {user_message.lower()}")
                        print(f"🎯 Chat state: {chat_state}")
                    else:
                        print(f"✅ TASK COMPLETED: {function_name} -> finishing conversation")
                    print("************************************")
                elif function_call_state == "Function call failed.":
                    function_call_result_section = (
                        f"## Function Call Attempted\n\n"
                        f"- The assistant attempted to call `{function_name}` with the following arguments:\n"
                        + "".join([f"  - {k}: {v}\n" for k,
                                   v in function_args.items()])
                        + f"- Outcome: ❌ {function_call_state} - {function_call_result}\n\n"
                        "Please assist the user based on this result."
                    )

                if function_call_count >= self.cfg.max_function_calls:
                    function_call_result_section = f"""  # Function Call Limit Reached.\n
                    Please conclude the conversation with the user based on the available information."""
                system_prompt = prepare_system_prompt_for_agentic_chatbot_v4(self.user_manager.user_info,
                                                                             self.previous_summary,
                                                                             self.chat_history,
                                                                             function_call_result_section)
                print("\n\n==========================================")
                print(f"System prompt: {system_prompt}")

                print("\n\nchat_State:", chat_state)
                response = self.client.chat.completions.create(
                    model=self.chat_model,
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": user_message}],
                    functions=self.agent_functions,
                    function_call="auto",
                    temperature=self.cfg.temperature
                )

                if response.choices[0].message.content:
                    assistant_response = response.choices[0].message.content
                    self.chat_history_manager.add_to_history(
                        user_message, assistant_response, self.max_history_pairs
                    )
                    self.chat_history_manager.update_chat_summary(
                        self.max_history_pairs
                    )
                    chat_state = "finished"
                    msg_pair = f"user: {user_message}, assistant: {assistant_response}"
                    self.vector_db_manager.update_vector_db(
                        msg_pair)
                    function_call_state = None
                    self.vector_db_manager.refresh_vector_db_client()
                    return assistant_response

                elif response.choices[0].message.function_call:
                    if function_call_count >= self.cfg.max_function_calls or chat_state == "finished":
                        print("Trigerring the fallback model...")
                        fallback_response = self.client.chat.completions.create(
                            model=self.chat_model,
                            messages=[{"role": "system", "content": system_prompt},
                                      {"role": "user", "content": user_message}],
                            temperature=self.cfg.temperature
                        )
                        assistant_response = fallback_response.choices[0].message.content
                        self.chat_history_manager.add_to_history(
                            user_message, assistant_response, self.max_history_pairs
                        )
                        msg_pair = f"user: {user_message}, assistant: {assistant_response}"
                        self.vector_db_manager.update_vector_db(
                            msg_pair)
                        function_call_state = None
                        self.vector_db_manager.refresh_vector_db_client()
                        return assistant_response

                    function_call_count += 1
                    function_name = response.choices[0].message.function_call.name
                    function_args = json.loads(
                        response.choices[0].message.function_call.arguments)
                    print("Function name that was requested by the LLM:",
                          function_name)
                    print("Function arguments:", function_args)
                    function_call_state, function_call_result = self.execute_function_call(
                        function_name, function_args)
                # Neither function call nor message content (edge case)
                else:
                    return "Warning: No valid assistant response from the chatbot. Please try again."

            except Exception as e:
                return f"Error: {str(e)}\n{format_exc()}"

    # ==================== CONTENT ADDITION HELPER ====================
    
    def notion_add_structured_content(self, page_identifier: str, content_type: str = "paragraph", content: str = "", title: str = "", sections: list = None) -> tuple[str, str]:
        """
        Add structured content to a Notion page with intelligent content handling.
        
        Args:
            page_identifier (str): Page ID or title
            content_type (str): Type of content ("paragraph", "heading", "bullet", "todo", "structured")
            content (str): Content to add (for simple types)
            title (str): Title for structured content (optional)
            sections (list): List of sections for structured content [{"title": "Section Title", "content": "Section content"}]
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # First, find the page
            if not NotionUtils.is_valid_uuid(page_identifier):
                results = self.notion_client.search(
                    query=page_identifier,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_identifier}'"
                
                page = results["results"][0]
                page_id = page["id"]
                page_title = NotionUtils.extract_title(page)
            else:
                page_id = page_identifier
                page_title = page_identifier
            
            # Handle different content types
            if content_type == "structured":
                results = []
                
                # If no sections provided, require user to provide content
                if not sections:
                    if content.strip():
                        # Use the user's actual content as a single section
                        sections = [{"title": title or "Content", "content": content}]
                    else:
                        return "Function call failed.", "No content or sections provided for structured content."
                
                # Add main title if provided
                if title:
                    heading_result = self.notion_add_heading(page_id, title, 1)
                    results.append(heading_result[1])
                
                # Add sections
                for section in sections:
                    section_title = section.get("title", "")
                    section_content = section.get("content", "")
                    
                    if section_title:
                        heading_result = self.notion_add_heading(page_id, section_title, 2)
                        results.append(heading_result[1])
                    
                    if section_content:
                        para_result = self.notion_add_paragraph(page_id, section_content)
                        results.append(para_result[1])
                
                return "Function call successful.", f"✅ Added structured content to '{page_title}'. Added {len(results)} content blocks."
            
            elif content_type == "paragraph":
                return self.notion_add_paragraph(page_id, content)
            elif content_type == "heading":
                return self.notion_add_heading(page_id, content)
            elif content_type == "bullet":
                return self.notion_add_bullet_point(page_id, content)
            elif content_type == "todo":
                return self.notion_add_todo(page_id, content)
            else:
                return "Function call failed.", f"Unknown content type: {content_type}"
                
        except Exception as e:
            return "Function call failed.", f"Error adding structured content: {str(e)}"
    
    def notion_add_smart_content(self, page_identifier: str, user_request: str) -> tuple[str, str]:
        """
        Intelligently add content to a Notion page based on the user's actual request.
        
        Args:
            page_identifier (str): Page ID or title
            user_request (str): The user's natural language request (contains the actual content)
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            user_request_lower = user_request.lower()
            
            # Detect if user wants multiple todos/bullet points
            multiple_indicators = ["multiple", "several", "many", "list of", "tasks", "items", "todos", "todo list", "bullet points"]
            wants_multiple = any(indicator in user_request_lower for indicator in multiple_indicators)
            
            # Detect if user wants todos specifically
            todo_indicators = ["todo", "to-do", "task", "tasks", "checklist"]
            wants_todos = any(indicator in user_request_lower for indicator in todo_indicators)
            
           
            # Extract the actual content from the user's request
            # Remove command words to get the pure content
            content_indicators = ["add", "create", "write", "put", "insert", "content", "about", "on", "to"]
            page_indicators = ["page", "in", "to my", "on my"]
            
            # Split the request into words
            words = user_request.split()
            
            # Try to find where the actual content starts
            content_start_idx = 0
            for i, word in enumerate(words):
                if any(indicator in word.lower() for indicator in content_indicators):
                    content_start_idx = i + 1
                    break
            
            # Extract content (everything after command words)
            if content_start_idx < len(words):
                content_words = words[content_start_idx:]
                # Remove page references from content
                filtered_content = []
                skip_next = False
                for word in content_words:
                    if skip_next:
                        skip_next = False
                        continue
                    if any(indicator in word.lower() for indicator in page_indicators):
                        skip_next = True
                        continue
                    if word.lower() not in ["page", "my", "to", "on", "in"]:
                        filtered_content.append(word)
                
                actual_content = " ".join(filtered_content)
            else:
                actual_content = user_request
            
            # If no meaningful content extracted, use the full request
            if not actual_content.strip() or len(actual_content.strip()) < 10:
                actual_content = user_request
            
            # Check if user wants multiple items and parse them
            if wants_multiple or wants_todos:
                # Try to parse multiple items from the content
                items = []
                
                # Split by common delimiters
                for delimiter in ['\n', '- ', '• ', '* ', ';', ',']:
                    if delimiter in actual_content:
                        items = [item.strip() for item in actual_content.split(delimiter) if item.strip()]
                        break
                
                # If no delimiters found but multiple words, suggest common items
                if not items and len(actual_content.split()) > 3:
                    # If it's a vague request, ask for specifics
                    if any(vague in actual_content.lower() for vague in ["tasks", "items", "things", "stuff"]):
                        return "Function call failed.", f"Please specify the exact items you want to add. For example: 'Task 1, Task 2, Task 3' or provide a list with line breaks."
                    else:
                        items = [actual_content]  # Treat as single item
                
                if items and len(items) > 1:
                    if wants_todos:
                        return self.notion_add_multiple_todos(page_identifier, items)
                    else:
                        # Add as multiple bullet points
                        results = []
                        for item in items:
                            result = self.notion_add_bullet_point(page_identifier, item.strip())
                            results.append(result[1])
                        return "Function call successful.", f"✅ Added {len(results)} bullet points to the page."
                elif items and len(items) == 1:
                    if wants_todos:
                        return self.notion_add_todo(page_identifier, items[0])
                    else:
                        return self.notion_add_bullet_point(page_identifier, items[0])
            
            # Determine the best way to add the content based on its structure
            if len(actual_content) > 500:  # Long content - break into sections
                # Try to split into natural sections
                sections = []
                
                # Split by double newlines first
                paragraphs = actual_content.split('\n\n')
                if len(paragraphs) > 1:
                    for para in paragraphs:
                        if para.strip():
                            sections.append(para.strip())
                else:
                    # Split by sentences if too long
                    sentences = actual_content.split('. ')
                    if len(sentences) > 3:
                        # Group sentences into paragraphs
                        current_section = []
                        for sentence in sentences:
                            current_section.append(sentence.strip())
                            if len(' '.join(current_section)) > 300:
                                sections.append('. '.join(current_section) + '.')
                                current_section = []
                        if current_section:
                            sections.append('. '.join(current_section) + '.')
                    else:
                        sections = [actual_content]
                
                # Add each section as a separate paragraph
                results = []
                for section in sections:
                    if section.strip():
                        result = self.notion_add_paragraph(page_identifier, section.strip())
                        results.append(result[1])
                
                return "Function call successful.", f"✅ Added {len(results)} sections of content to the page."
            
            else:
                # Short content - add as single paragraph
                return self.notion_add_paragraph(page_identifier, actual_content)
                
        except Exception as e:
            return "Function call failed.", f"Error adding smart content: {str(e)}"
    
    # ==================== NOTION OPERATIONS ====================
    
    def notion_search_content(self, search_term: str) -> tuple[str, str]:
        """
        Search for content in Notion workspace.
        
        Args:
            search_term (str): The term to search for in pages and databases
            
        Returns:
            tuple[str, str]: Function state and search results
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Search all content
            all_results = self.notion_client.search(query=search_term)
            pages = [r for r in all_results.get("results", []) if r["object"] == "page"]
            databases = [r for r in all_results.get("results", []) if r["object"] == "database"]
            
            # Format results
            result_text = f"🔍 Search Results for '{search_term}':\n"
            result_text += f"📄 Pages: {len(pages)}\n"
            result_text += f"🗄️ Databases: {len(databases)}\n\n"
            
            if pages:
                result_text += "📄 Pages Found:\n"
                for i, page in enumerate(pages[:5], 1):
                    title = NotionUtils.extract_title(page)
                    result_text += f"{i}. {title}\n"
                    result_text += f"   🆔 {page['id']}\n"
                    result_text += f"   📅 {page['last_edited_time']}\n\n"
            
            if databases:
                result_text += "🗄️ Databases Found:\n"
                for i, db in enumerate(databases[:3], 1):
                    title = NotionUtils.extract_database_title(db)
                    result_text += f"{i}. {title}\n"
                    result_text += f"   🆔 {db['id']}\n\n"
            
            if not pages and not databases:
                result_text += f"❌ No results found for '{search_term}'"
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Search error: {str(e)}"
    
    def notion_read_page(self, page_identifier: str) -> tuple[str, str]:
        """
        Read content from a Notion page.
        
        Args:
            page_identifier (str): Page ID or title to read
            
        Returns:
            tuple[str, str]: Function state and page content
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Check if identifier is a page ID or title
            if NotionUtils.is_valid_uuid(page_identifier):
                page_id = page_identifier
                page = self.notion_client.pages.retrieve(page_id)
            else:
                # Search for page by title
                results = self.notion_client.search(
                    query=page_identifier,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_identifier}'"
                
                page = results["results"][0]
                page_id = page["id"]
                page = self.notion_client.pages.retrieve(page_id)
            
            # Extract page info
            title = NotionUtils.extract_title(page)
            created_time = page["created_time"]
            last_edited = page["last_edited_time"]
            
            # Get page content (blocks)
            blocks = self.notion_client.blocks.children.list(page_id)
            
            # Format content
            result_text = f"📄 Page: {title}\n"
            result_text += f"📅 Created: {created_time}\n"
            result_text += f"✏️ Last edited: {last_edited}\n"
            result_text += f"🆔 ID: {page_id}\n\n"
            result_text += "📝 Content:\n"
            result_text += "-" * 50 + "\n"
            
            if not blocks.get("results"):
                result_text += "(This page has no content)\n"
            else:
                for block in blocks["results"]:
                    block_type = block["type"]
                    content = NotionUtils.extract_block_text(block)
                    result_text += f"[{block_type}] {content}\n"
            
            result_text += "-" * 50
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error reading page: {str(e)}"
    
    def notion_create_page(self, title: str, content: str = "", parent_id: str = None) -> tuple[str, str]:
        """
        Create a new Notion page.
        
        Args:
            title (str): Title of the new page
            content (str, optional): Initial content for the page
            parent_id (str, optional): Parent page ID
            
        Returns:
            tuple[str, str]: Function state and page creation result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get a suitable parent if not provided
            if not parent_id:
                parent_id = NotionUtils.get_suitable_parent_sync(self.notion_client)
                if not parent_id:
                    return "Function call failed.", "No suitable parent page found. Please specify a parent_id."
            
            # Create page data
            page_data = {
                "parent": {"page_id": parent_id},
                "properties": {"title": {"title": [{"text": {"content": title}}]}}
            }
            
            # Add content if provided
            if content:
                page_data["children"] = [{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": content}}]}
                }]
            
            page = self.notion_client.pages.create(**page_data)
            
            result_text = f"✅ Page created successfully!\n"
            result_text += f"📄 Title: {title}\n"
            result_text += f"🆔 ID: {page['id']}\n"
            result_text += f"🔗 URL: {page['url']}\n"
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error creating page: {str(e)}"
    
    def notion_list_pages(self, limit: int = 10) -> tuple[str, str]:
        """
        List all pages in the Notion workspace.
        
        Args:
            limit (int): Maximum number of pages to return
            
        Returns:
            tuple[str, str]: Function state and pages list
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            pages = self.notion_client.search(filter={"property": "object", "value": "page"})
            
            result_text = f"📋 Pages in Workspace ({len(pages['results'])} total):\n\n"
            
            for i, page in enumerate(pages["results"][:limit], 1):
                title = NotionUtils.extract_title(page)
                result_text += f"{i}. {title}\n"
                result_text += f"   🆔 {page['id']}\n"
                result_text += f"   📅 {page['last_edited_time']}\n\n"
            
            if len(pages["results"]) > limit:
                result_text += f"... and {len(pages['results']) - limit} more pages"
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error listing pages: {str(e)}"
    
    def notion_list_databases(self, limit: int = 10) -> tuple[str, str]:
        """
        List all databases in the Notion workspace.
        
        Args:
            limit (int): Maximum number of databases to return
            
        Returns:
            tuple[str, str]: Function state and databases list
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            databases = self.notion_client.search(filter={"property": "object", "value": "database"})
            
            result_text = f"🗄️ Databases in Workspace ({len(databases['results'])} total):\n\n"
            
            for i, db in enumerate(databases["results"][:limit], 1):
                title = NotionUtils.extract_database_title(db)
                result_text += f"{i}. {title}\n"
                result_text += f"   🆔 {db['id']}\n\n"
            
            if len(databases["results"]) > limit:
                result_text += f"... and {len(databases['results']) - limit} more databases"
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error listing databases: {str(e)}"
    
    def notion_workspace_analytics(self) -> tuple[str, str]:
        """
        Get comprehensive workspace analytics.
        
        Returns:
            tuple[str, str]: Function state and analytics results
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get data using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a temporary analytics instance
            analytics = AnalyticsOperations(self.notion_client)
            
            # Capture the output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Run analytics
            loop.run_until_complete(analytics.run_workspace_analytics())
            
            # Restore stdout and get result
            sys.stdout = old_stdout
            result_text = captured_output.getvalue()
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error running workspace analytics: {str(e)}"
    
    def notion_content_analytics(self) -> tuple[str, str]:
        """
        Get content structure analytics.
        
        Returns:
            tuple[str, str]: Function state and analytics results
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get data using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a temporary analytics instance
            analytics = AnalyticsOperations(self.notion_client)
            
            # Capture the output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Run analytics
            loop.run_until_complete(analytics.run_content_analytics())
            
            # Restore stdout and get result
            sys.stdout = old_stdout
            result_text = captured_output.getvalue()
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error running content analytics: {str(e)}"
    
    def notion_activity_analytics(self) -> tuple[str, str]:
        """
        Get activity pattern analytics.
        
        Returns:
            tuple[str, str]: Function state and analytics results
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get data using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a temporary analytics instance
            analytics = AnalyticsOperations(self.notion_client)
            
            # Capture the output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Run analytics
            loop.run_until_complete(analytics.run_activity_analytics())
            
            # Restore stdout and get result
            sys.stdout = old_stdout
            result_text = captured_output.getvalue()
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error running activity analytics: {str(e)}"
    
    def notion_add_paragraph(self, page_id: str, content: str) -> tuple[str, str]:
        """
        Add a paragraph block to a Notion page.
        
        Args:
            page_id (str): Page ID (UUID) or page title to add content to
            content (str): Text content for the paragraph
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Check if page_id is a valid UUID, if not search for page by title
            if not NotionUtils.is_valid_uuid(page_id):
                # Search for page by title
                results = self.notion_client.search(
                    query=page_id,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_id}'"
                
                # Use the first matching page
                page = results["results"][0]
                page_id = page["id"]
                page_title = NotionUtils.extract_title(page)
                print(f"✅ Found page: {page_title} ({page_id})")
            
            # Handle content length - Notion API limit is 2000 characters per paragraph
            MAX_PARAGRAPH_LENGTH = 2000
            
            if len(content) <= MAX_PARAGRAPH_LENGTH:
                # Single paragraph
                response = self.notion_client.blocks.children.append(
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
                return "Function call successful.", f"✅ Added paragraph to page {page_id}"
            else:
                # Split into multiple paragraphs
                paragraphs = []
                remaining_content = content
                
                while remaining_content:
                    # Find a good breaking point (prefer sentence endings)
                    if len(remaining_content) <= MAX_PARAGRAPH_LENGTH:
                        # Last chunk
                        chunk = remaining_content
                        remaining_content = ""
                    else:
                        # Find the best break point within the limit
                        chunk = remaining_content[:MAX_PARAGRAPH_LENGTH]
                        
                        # Try to break at sentence endings
                        last_sentence = max(
                            chunk.rfind('. '),
                            chunk.rfind('! '),
                            chunk.rfind('? '),
                            chunk.rfind('\n')
                        )
                        
                        if last_sentence > MAX_PARAGRAPH_LENGTH * 0.7:  # Don't break too early
                            chunk = remaining_content[:last_sentence + 1]
                            remaining_content = remaining_content[last_sentence + 1:].strip()
                        else:
                            # Break at word boundary
                            last_space = chunk.rfind(' ')
                            if last_space > MAX_PARAGRAPH_LENGTH * 0.8:
                                chunk = remaining_content[:last_space]
                                remaining_content = remaining_content[last_space:].strip()
                            else:
                                # Hard break (rare case)
                                remaining_content = remaining_content[MAX_PARAGRAPH_LENGTH:]
                    
                    paragraphs.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": chunk.strip()}
                                }
                            ]
                        }
                    })
                
                # Add all paragraphs
                response = self.notion_client.blocks.children.append(
                    block_id=page_id,
                    children=paragraphs
                )
                
                return "Function call successful.", f"✅ Added {len(paragraphs)} paragraphs to page {page_id} (content was split due to length limit)"
            
        except Exception as e:
            return "Function call failed.", f"Error adding paragraph: {str(e)}"
    
    def notion_add_heading(self, page_id: str, content: str, level: int = 1) -> tuple[str, str]:
        """
        Add a heading block to a Notion page.
        
        Args:
            page_id (str): Page ID (UUID) or page title to add content to
            content (str): Text content for the heading
            level (int): Heading level (1-3)
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Check if page_id is a valid UUID, if not search for page by title
            if not NotionUtils.is_valid_uuid(page_id):
                # Search for page by title
                results = self.notion_client.search(
                    query=page_id,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_id}'"
                
                # Use the first matching page
                page = results["results"][0]
                page_id = page["id"]
                page_title = NotionUtils.extract_title(page)
                print(f"✅ Found page: {page_title} ({page_id})")
            
            heading_types = {1: "heading_1", 2: "heading_2", 3: "heading_3"}
            heading_type = heading_types.get(level, "heading_1")
            
            # Handle content length - Notion API limit is 2000 characters per block
            MAX_BLOCK_LENGTH = 2000
            
            if len(content) > MAX_BLOCK_LENGTH:
                # Truncate with warning for headings (headings should be short anyway)
                content = content[:MAX_BLOCK_LENGTH-3] + "..."
                truncated_warning = " (truncated due to length limit)"
            else:
                truncated_warning = ""
            
            response = self.notion_client.blocks.children.append(
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
            
            return "Function call successful.", f"✅ Added {heading_type} to page {page_id}{truncated_warning}"
            
        except Exception as e:
            return "Function call failed.", f"Error adding heading: {str(e)}"
    
    def notion_add_bullet_point(self, page_id: str, content: str) -> tuple[str, str]:
        """
        Add a bullet point block to a Notion page.
        
        Args:
            page_id (str): Page ID (UUID) or page title to add content to
            content (str): Text content for the bullet point
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Check if page_id is a valid UUID, if not search for page by title
            if not NotionUtils.is_valid_uuid(page_id):
                # Search for page by title
                results = self.notion_client.search(
                    query=page_id,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_id}'"
                
                # Use the first matching page
                page = results["results"][0]
                page_id = page["id"]
                page_title = NotionUtils.extract_title(page)
                print(f"✅ Found page: {page_title} ({page_id})")
            
            # Handle content length - Notion API limit is 2000 characters per block
            MAX_BLOCK_LENGTH = 2000
            
            if len(content) > MAX_BLOCK_LENGTH:
                # For bullet points, split into multiple bullet points
                bullet_points = []
                remaining_content = content
                
                while remaining_content:
                    if len(remaining_content) <= MAX_BLOCK_LENGTH:
                        chunk = remaining_content
                        remaining_content = ""
                    else:
                        # Find good break point
                        chunk = remaining_content[:MAX_BLOCK_LENGTH]
                        last_sentence = max(
                            chunk.rfind('. '),
                            chunk.rfind('! '),
                            chunk.rfind('? '),
                            chunk.rfind('\n')
                        )
                        
                        if last_sentence > MAX_BLOCK_LENGTH * 0.7:
                            chunk = remaining_content[:last_sentence + 1]
                            remaining_content = remaining_content[last_sentence + 1:].strip()
                        else:
                            last_space = chunk.rfind(' ')
                            if last_space > MAX_BLOCK_LENGTH * 0.8:
                                chunk = remaining_content[:last_space]
                                remaining_content = remaining_content[last_space:].strip()
                            else:
                                remaining_content = remaining_content[MAX_BLOCK_LENGTH:]
                    
                    bullet_points.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": chunk.strip()}
                                }
                            ]
                        }
                    })
                
                response = self.notion_client.blocks.children.append(
                    block_id=page_id,
                    children=bullet_points
                )
                
                return "Function call successful.", f"✅ Added {len(bullet_points)} bullet points to page {page_id} (content was split due to length limit)"
            else:
                # Single bullet point
                response = self.notion_client.blocks.children.append(
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
                
                return "Function call successful.", f"✅ Added bullet point to page {page_id}"
            
        except Exception as e:
            return "Function call failed.", f"Error adding bullet point: {str(e)}"
    
    def notion_add_todo(self, page_id: str, content: str, checked: bool = False) -> tuple[str, str]:
        """
        Add a to-do block to a Notion page.
        
        Args:
            page_id (str): Page ID (UUID) or page title to add content to
            content (str): Text content for the to-do item
            checked (bool): Whether the to-do is checked
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Check if page_id is a valid UUID, if not search for page by title
            if not NotionUtils.is_valid_uuid(page_id):
                # Search for page by title
                results = self.notion_client.search(
                    query=page_id,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_id}'"
                
                # Use the first matching page
                page = results["results"][0]
                page_id = page["id"]
                page_title = NotionUtils.extract_title(page)
                print(f"✅ Found page: {page_title} ({page_id})")
            
            # Handle content length - Notion API limit is 2000 characters per block
            MAX_BLOCK_LENGTH = 2000
            
            if len(content) > MAX_BLOCK_LENGTH:
                # For to-do items, split into multiple to-do items
                todo_items = []
                remaining_content = content
                
                while remaining_content:
                    if len(remaining_content) <= MAX_BLOCK_LENGTH:
                        chunk = remaining_content
                        remaining_content = ""
                    else:
                        # Find good break point
                        chunk = remaining_content[:MAX_BLOCK_LENGTH]
                        last_sentence = max(
                            chunk.rfind('. '),
                            chunk.rfind('! '),
                            chunk.rfind('? '),
                            chunk.rfind('\n')
                        )
                        
                        if last_sentence > MAX_BLOCK_LENGTH * 0.7:
                            chunk = remaining_content[:last_sentence + 1]
                            remaining_content = remaining_content[last_sentence + 1:].strip()
                        else:
                            last_space = chunk.rfind(' ')
                            if last_space > MAX_BLOCK_LENGTH * 0.8:
                                chunk = remaining_content[:last_space]
                                remaining_content = remaining_content[last_space:].strip()
                            else:
                                remaining_content = remaining_content[MAX_BLOCK_LENGTH:]
                    
                    todo_items.append({
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": chunk.strip()}
                                }
                            ],
                            "checked": checked
                        }
                    })
                
                response = self.notion_client.blocks.children.append(
                    block_id=page_id,
                    children=todo_items
                )
                
                return "Function call successful.", f"✅ Added {len(todo_items)} to-do items to page {page_id} (content was split due to length limit)"
            else:
                # Single to-do item
                response = self.notion_client.blocks.children.append(
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
                                "checked": checked
                            }
                        }
                    ]
                )
                
                return "Function call successful.", f"✅ Added to-do item to page {page_id}"
            
        except Exception as e:
            return "Function call failed.", f"Error adding to-do: {str(e)}"
    
    def notion_add_multiple_todos(self, page_id: str, todo_items: list, checked: bool = False) -> tuple[str, str]:
        """
        Add multiple to-do items to a Notion page at once.
        
        Args:
            page_id (str): Page ID (UUID) or page title to add content to
            todo_items (list): List of todo item texts
            checked (bool): Whether the to-do items are checked
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Check if page_id is a valid UUID, if not search for page by title
            if not NotionUtils.is_valid_uuid(page_id):
                results = self.notion_client.search(
                    query=page_id,
                    filter={"property": "object", "value": "page"}
                )
                
                if not results.get("results"):
                    return "Function call failed.", f"No page found with title '{page_id}'"
                
                page = results["results"][0]
                page_id = page["id"]
                page_title = NotionUtils.extract_title(page)
                print(f"✅ Found page: {page_title} ({page_id})")
            
            # Prepare all todo blocks
            todo_blocks = []
            for item in todo_items:
                if item.strip():  # Only add non-empty items
                    # Handle content length for each item
                    MAX_BLOCK_LENGTH = 2000
                    
                    if len(item) > MAX_BLOCK_LENGTH:
                        # Split long items into multiple todos
                        chunks = []
                        remaining = item
                        
                        while remaining:
                            if len(remaining) <= MAX_BLOCK_LENGTH:
                                chunks.append(remaining)
                                break
                            else:
                                # Find good break point
                                chunk = remaining[:MAX_BLOCK_LENGTH]
                                last_sentence = max(
                                    chunk.rfind('. '),
                                    chunk.rfind('! '),
                                    chunk.rfind('? '),
                                    chunk.rfind('\n')
                                )
                                
                                if last_sentence > MAX_BLOCK_LENGTH * 0.7:
                                    chunk = remaining[:last_sentence + 1]
                                    remaining = remaining[last_sentence + 1:].strip()
                                else:
                                    last_space = chunk.rfind(' ')
                                    if last_space > MAX_BLOCK_LENGTH * 0.8:
                                        chunk = remaining[:last_space]
                                        remaining = remaining[last_space:].strip()
                                    else:
                                        remaining = remaining[MAX_BLOCK_LENGTH:]
                                
                                chunks.append(chunk.strip())
                        
                        # Add each chunk as separate todo
                        for chunk in chunks:
                            todo_blocks.append({
                                "object": "block",
                                "type": "to_do",
                                "to_do": {
                                    "rich_text": [
                                        {
                                            "type": "text",
                                            "text": {"content": chunk}
                                        }
                                    ],
                                    "checked": checked
                                }
                            })
                    else:
                        # Single todo item
                        todo_blocks.append({
                            "object": "block",
                            "type": "to_do",
                            "to_do": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": item.strip()}
                                    }
                                ],
                                "checked": checked
                            }
                        })
            
            if not todo_blocks:
                return "Function call failed.", "No valid todo items provided"
            
            # Add all todos at once
            response = self.notion_client.blocks.children.append(
                block_id=page_id,
                children=todo_blocks
            )
            
            return "Function call successful.", f"✅ Added {len(todo_blocks)} to-do items to page {page_id}"
            
        except Exception as e:
            return "Function call failed.", f"Error adding multiple todos: {str(e)}"
    
    def notion_bulk_create_pages(self, pages_data: list) -> tuple[str, str]:
        """
        Create multiple pages in bulk.
        
        Args:
            pages_data (list): List of page data dictionaries with 'title' and optional 'content'
            
        Returns:
            tuple[str, str]: Function state and result
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get data using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a temporary bulk operations instance
            bulk_ops = BulkOperations(self.notion_client)
            
            # Run bulk creation
            result = loop.run_until_complete(bulk_ops.bulk_create_pages(pages_data))
            
            result_text = f"🔄 Bulk Page Creation Results:\n"
            result_text += f"✅ Created: {len(result['created'])} pages\n"
            result_text += f"❌ Failed: {len(result['failed'])} pages\n\n"
            
            if result['created']:
                result_text += "Created Pages:\n"
                for page in result['created']:
                    result_text += f"  • {page['title']} (ID: {page['id']})\n"
            
            if result['failed']:
                result_text += "\nFailed Pages:\n"
                for failure in result['failed']:
                    result_text += f"  • {failure['data']['title']}: {failure['error']}\n"
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error creating pages in bulk: {str(e)}"
    
    def notion_bulk_list_pages(self) -> tuple[str, str]:
        """
        List all pages with detailed information.
        
        Returns:
            tuple[str, str]: Function state and pages list
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get data using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a temporary bulk operations instance
            bulk_ops = BulkOperations(self.notion_client)
            
            # Capture the output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Run bulk listing
            loop.run_until_complete(bulk_ops.bulk_list_pages())
            
            # Restore stdout and get result
            sys.stdout = old_stdout
            result_text = captured_output.getvalue()
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error listing pages in bulk: {str(e)}"
    
    def notion_bulk_analyze_pages(self, search_query: str) -> tuple[str, str]:
        """
        Analyze pages matching a search query.
        
        Args:
            search_query (str): Search query to find pages to analyze
            
        Returns:
            tuple[str, str]: Function state and analysis results
        """
        if not self.notion_client:
            return "Function call failed.", "Notion client not initialized. Please check your NOTION_TOKEN."
        
        try:
            # Get data using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create a temporary bulk operations instance
            bulk_ops = BulkOperations(self.notion_client)
            
            # Capture the output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Run bulk analysis
            loop.run_until_complete(bulk_ops.bulk_analyze_pages())
            
            # Restore stdout and get result
            sys.stdout = old_stdout
            result_text = captured_output.getvalue()
            
            return "Function call successful.", result_text
            
        except Exception as e:
            return "Function call failed.", f"Error analyzing pages in bulk: {str(e)}"
