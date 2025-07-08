from typing import Dict, TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool, tool
# Add SystemMessage to the imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import the Notion-related components from the separate file
from .notion_graph import create_notion_agent_graph, notion_task

# ----------------------------------------------------------------------------
# Shared ChatState
# ----------------------------------------------------------------------------

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    # This is a new field to pass the original user's request to the subgraph
    original_request: str

# ----------------------------------------------------------------------------
# Main Orchestrator Graph
# ----------------------------------------------------------------------------

def create_orchestrator_graph(general_tools: List[BaseTool] = []):
    """
    Builds and compiles a master LangGraph that acts as an orchestrator,
    routing tasks to a general tool executor or the specialized Notion agent.
    """
    orchestrator_llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    
    # The orchestrator is aware of general tools and the high-level Notion tool
    all_tools = general_tools + [notion_task]
    orchestrator_llm = orchestrator_llm.bind_tools(all_tools)

    notion_agent_graph = create_notion_agent_graph()

    def orchestrator_agent(state: ChatState):
        """Invokes the main LLM to decide which tool to use, guided by a system prompt."""
        
        # This system prompt gives the orchestrator explicit instructions on how to route tasks.
        system_prompt = (
            "You are a master orchestrator. Your primary job is to analyze the user's request "
            "and route it to the appropriate tool or agent. "
            "If the request is about Notion (e.g., creating, searching, or reading pages), "
            "you must use the 'notion_task' tool. For other tasks that require a specific function, "
            "like checking the weather, use the general-purpose tools available. "
            "If the user asks a general question or makes a conversational remark, "
            "provide a direct, helpful response without using any tools."
        )
        
        # Prepend the system prompt to the message history
        messages_with_system_prompt = [SystemMessage(content=system_prompt)] + state["messages"]
        
        response = orchestrator_llm.invoke(messages_with_system_prompt)
        return {"messages": [response]}

    def router(state: ChatState):
        """Routes to the correct node based on the tool called by the orchestrator."""
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            if last_message.tool_calls[0]['name'] == "notion_task":
                # Pass the original user request to the subgraph
                original_user_message = next((msg.content for msg in reversed(state['messages']) if isinstance(msg, HumanMessage)), None)
                state['original_request'] = original_user_message
                return "notion_agent"
            return "tools"
        return "end"

    workflow = StateGraph(ChatState)
    
    workflow.add_node("orchestrator", orchestrator_agent)
    workflow.add_node("tools", ToolNode(general_tools))
    workflow.add_node("notion_agent", notion_agent_graph)

    workflow.set_entry_point("orchestrator")
    
    workflow.add_conditional_edges("orchestrator", router, {
        "tools": "tools",
        "notion_agent": "notion_agent",
        "end": END
    })

    workflow.add_edge("tools", "orchestrator")
    # After the Notion agent finishes, its result is passed back to the orchestrator
    workflow.add_edge("notion_agent", "orchestrator")

    return workflow.compile()
