import os
import uuid
import json
from typing import Dict, Any
from traceback import format_exc
from openai import OpenAI
# External LangGraph symbols are now consumed inside the dedicated graph builder
# module located at `src/graph.py`, so we no longer need to import them here.
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage
from langsmith import Client
from langsmith.run_trees import RunTree

# Import existing utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.sql_manager import SQLManager
from utils.user_manager import UserManager
from utils.chat_history_manager import ChatHistoryManager
from utils.search_manager import SearchManager
from utils.prepare_system_prompt import prepare_system_prompt_for_agentic_chatbot_v2
from utils.utils import Utils
from utils.vector_db_manager import VectorDBManager

from agent_state import AgentState
from config import config
from .graph import ChatState, create_chat_graph

# Initialize LangSmith client
langsmith_client = Client(**config.get_langsmith_config())

# `ChatState` now lives in `graph.py` and is imported above.

class AgenticChatbot:
    """
    LangGraph-based chatbot that handles conversational flow, manages user data, 
    and executes function calls using OpenAI's API.
    """

    def __init__(self):
        """
        Initializes the AgenticChatbot instance.
        Sets up OpenAI client, configuration settings, and database managers.
        """
        openai_config = config.get_openai_config()
        self.client = OpenAI(api_key=openai_config["api_key"])
        self.chat_model = openai_config["chat_model"]
        self.summary_model = openai_config["summary_model"]
        self.temperature = openai_config["temperature"]
        
        # Get chat configuration
        chat_config = config.get_chat_config()
        self.max_history_pairs = chat_config["max_history_pairs"]
        self.max_tokens = chat_config["max_tokens"]
        self.max_function_calls = chat_config["max_function_calls"]
        
        # Initialize utilities and managers
        db_config = config.get_db_config()
        self.utils = Utils()
        self.sql_manager = SQLManager(db_config["db_path"])
        self.user_manager = UserManager(self.sql_manager)
        self.vector_db_manager = VectorDBManager(config)
        self.search_manager = SearchManager(
            self.sql_manager, 
            self.utils, 
            self.client, 
            self.summary_model, 
            chat_config["max_characters"]
        )
        
        # Agent functions for OpenAI function calling
        self.agent_functions = [
            self.utils.jsonschema(self.user_manager.add_user_info_to_database),
            self.utils.jsonschema(self.vector_db_manager.search_vector_db)
        ]

        # Initialize memory checkpointing
        self.memory = MemorySaver()

        # Build the LangGraph using the shared factory
        self.graph = create_chat_graph(
            memory=self.memory,
            initialize_fn=self._initialize_conversation,
            agent_fn=self._generate_response,
            finalize_fn=self._finalize_response,
            tools=self.agent_functions,
        )

    # The `_create_graph` helper has been relocated to `src/graph.py`.

    def _initialize_conversation(self, state: ChatState) -> Dict[str, Any]:
        """
        Initialize the conversation state with user and session data.
        """
        session_id = str(uuid.uuid4())
        chat_history_manager = ChatHistoryManager(
            self.sql_manager, self.user_manager.user_id, session_id, 
            self.client, self.summary_model, self.max_tokens
        )
        
        return {
            "messages": [state["messages"][0]],  # Keep the initial user message
            "session_id": session_id,
            "user_id": self.user_manager.user_id,
            "function_call_count": 0,
            "function_call_state": None,
            "function_call_result": None,
            "function_name": None,
            "function_args": None,
            "chat_state": "thinking",
            "error_message": None,
            "function_call_result_section": ""
        }

    def _generate_response(self, state: ChatState) -> Dict[str, Any]:
        """
        Generate response using OpenAI API with function calling capabilities.
        """
        try:
            # Get chat history manager
            chat_history_manager = ChatHistoryManager(
                self.sql_manager, state["user_id"], state["session_id"], 
                self.client, self.summary_model, self.max_tokens
            )
            
            # Prepare system prompt
            system_prompt = prepare_system_prompt_for_agentic_chatbot_v2(
                self.user_manager.user_info,
                chat_history_manager.get_latest_summary(),
                chat_history_manager.chat_history,
                state["function_call_result_section"]
            )

            print("\n\n==========================================")
            print(f"System prompt: {system_prompt}")
            print(f"\nChat state: {state['chat_state']}")

            # Check function call limits
            if state["function_call_count"] >= self.max_function_calls:
                function_call_result_section = (
                    "# Function Call Limit Reached.\n"
                    "Please conclude the conversation with the user based on the available information."
                )
                system_prompt = prepare_system_prompt_for_agentic_chatbot_v2(
                    self.user_manager.user_info,
                    chat_history_manager.get_latest_summary(),
                    chat_history_manager.chat_history,
                    function_call_result_section
                )

            # Generate response
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": state["messages"][0].content}
                ],
                functions=self.agent_functions,
                function_call="auto",
                temperature=self.temperature
            )

            # Handle response
            if response.choices[0].message.content:
                state["messages"].append(AIMessage(content=response.choices[0].message.content))
                return {
                    "messages": state["messages"],
                    "chat_state": "finished",
                    "system_prompt": system_prompt
                }
            elif response.choices[0].message.function_call:
                function_name = response.choices[0].message.function_call.name
                function_args = json.loads(response.choices[0].message.function_call.arguments)
                
                print(f"Function name requested by LLM: {function_name}")
                print(f"Function arguments: {function_args}")
                
                return {
                    "messages": state["messages"],
                    "function_name": function_name,
                    "function_args": function_args,
                    "chat_state": "function_call",
                    "system_prompt": system_prompt
                }
            else:
                return {
                    "messages": state["messages"],
                    "error_message": "No valid assistant response from the chatbot. Please try again.",
                    "chat_state": "finished"
                }

        except Exception as e:
            return {
                "messages": state["messages"],
                "error_message": f"Error: {str(e)}\n{format_exc()}",
                "chat_state": "finished"
            }

    def _execute_function(self, state: ChatState) -> Dict[str, Any]:
        """
        Execute the requested function call.
        """
        try:
            function_name = state["function_name"]
            function_args = state["function_args"]
            
            # Execute function
            if function_name == "search_vector_db":
                function_call_state, function_call_result = self.vector_db_manager.search_vector_db(**function_args)
            elif function_name == "add_user_info_to_database":
                function_call_state, function_call_result = self.user_manager.add_user_info_to_database(function_args)
            else:
                function_call_state = "Function call failed."
                function_call_result = f"Unknown function: {function_name}"

            # Prepare function call result section
            if function_call_state == "Function call successful.":
                function_call_result_section = (
                    f"## Function Call Executed\n\n"
                    f"- The assistant just called the function `{function_name}` in response to the user's most recent message.\n"
                    f"- Arguments provided:\n"
                    + "".join([f"  - {k}: {v}\n" for k, v in function_args.items()])
                    + f"- Outcome: ✅ {function_call_state}\n\n"
                    "Please proceed with the conversation using the new context.\n\n"
                    + f"{function_call_result}"
                )
                print("************************************")
                print(function_call_result)
                print("************************************")
                
                # Refresh user info if needed
                if function_name == "add_user_info_to_database":
                    self.user_manager.refresh_user_info()
                    
            else:
                function_call_result_section = (
                    f"## Function Call Attempted\n\n"
                    f"- The assistant attempted to call `{function_name}` with the following arguments:\n"
                    + "".join([f"  - {k}: {v}\n" for k, v in function_args.items()])
                    + f"- Outcome: ❌ {function_call_state} - {function_call_result}\n\n"
                    "Please assist the user based on this result."
                )

            return {
                "function_call_state": function_call_state,
                "function_call_result": function_call_result,
                "function_call_result_section": function_call_result_section,
                "function_call_count": state["function_call_count"] + 1
            }

        except Exception as e:
            return {
                "function_call_state": "Function call failed.",
                "function_call_result": f"Error executing function: {str(e)}\n{format_exc()}",
                "function_call_count": state["function_call_count"] + 1
            }

    def _finalize_response(self, state: ChatState) -> Dict[str, Any]:
        """
        Finalize the conversation by updating chat history and vector database.
        """
        try:
            # Handle fallback if no response and function call limit reached
            last_message = state["messages"][-1] if state["messages"] else None
            if (not isinstance(last_message, AIMessage) and 
                state["function_call_count"] >= self.max_function_calls):
                print("Triggering the fallback model...")
                fallback_response = self.client.chat.completions.create(
                    model=self.chat_model,
                    messages=[
                        {"role": "system", "content": state["system_prompt"]},
                        {"role": "user", "content": state["messages"][0].content}
                    ],
                    temperature=self.temperature
                )
                assistant_message = AIMessage(content=fallback_response.choices[0].message.content)
                state["messages"].append(assistant_message)

            # Get the final response
            last_message = state["messages"][-1]
            assistant_response = last_message.content if isinstance(last_message, AIMessage) else ""

            # Update chat history
            chat_history_manager = ChatHistoryManager(
                self.sql_manager, state["user_id"], state["session_id"], 
                self.client, self.summary_model, self.max_tokens
            )
            
            chat_history_manager.add_to_history(
                state["messages"][0].content, assistant_response, self.max_history_pairs
            )
            chat_history_manager.update_chat_summary(self.max_history_pairs)

            # Update vector database
            msg_pair = f"user: {state['messages'][0].content}, assistant: {assistant_response}"
            self.vector_db_manager.update_vector_db(msg_pair)
            self.vector_db_manager.refresh_vector_db_client()

            return {
                "messages": state["messages"],
                "chat_state": "finished"
            }

        except Exception as e:
            return {
                "error_message": f"Error finalizing response: {str(e)}\n{format_exc()}",
                "chat_state": "finished"
            }

    def _should_call_function(self, state: ChatState) -> str:
        """
        Determine if a function call should be made.
        """
        if state["chat_state"] == "function_call":
            return "function_call"
        else:
            return "finalize"

    def _should_continue_conversation(self, state: ChatState) -> str:
        """
        Determine if the conversation should continue or be finalized.
        """
        if (state["function_call_state"] == "Function call successful." and 
            state["function_call_count"] < self.max_function_calls):
            return "continue"
        else:
            return "finalize"

    def chat(self, user_message: str) -> str:
        """
        Process a user message through the LangGraph workflow.
        
        Args:
            user_message: The message from the user
            
        Returns:
            str: The chatbot's response
        """
        try:
            # Initialize state with user message
            state = {
                "messages": [HumanMessage(content=user_message)]
            }
            
            # Configure thread tracking
            config = {
                "configurable": {
                    "thread_id": str(uuid.uuid4())
                }
            }
            
            # Run the graph with thread tracking
            final_state = self.graph.invoke(state, config=config)
            
            if final_state.get("error_message"):
                return f"Error: {final_state['error_message']}"
            
            # Get the last AI message from the conversation
            last_message = final_state["messages"][-1]
            return last_message.content if isinstance(last_message, AIMessage) else "No response generated"
            
        except Exception as e:
            error_msg = f"Error in chat processing: {str(e)}\n{format_exc()}"
            print(error_msg)
            return f"An error occurred: {str(e)}" 