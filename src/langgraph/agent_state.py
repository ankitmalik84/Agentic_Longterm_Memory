from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """
    State schema for the LangGraph agent.
    Tracks conversation flow, function calls, and user data.
    """
    # Current user message
    user_message: str
    
    # Chat history and conversation context
    chat_history: List[Dict[str, str]]
    previous_summary: str
    
    # Function call tracking
    function_call_count: int
    function_call_state: Optional[str]
    function_call_result: Optional[str]
    function_name: Optional[str]
    function_args: Optional[Dict[str, Any]]
    
    # Response generation
    assistant_response: Optional[str]
    
    # Flow control
    chat_state: str  # "thinking", "function_call", "finished"
    
    # User and session context
    user_id: str
    session_id: str
    
    # Error handling
    error_message: Optional[str]
    
    # System prompt context
    system_prompt: Optional[str]
    function_call_result_section: str 