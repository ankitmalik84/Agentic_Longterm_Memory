from typing import Dict, TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool, tool
# Add SystemMessage to the imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import the specialized Notion tools
from .notion_tools import notion_tools

# ----------------------------------------------------------------------------
# Shared ChatState
# ----------------------------------------------------------------------------

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    # This is a new field to pass the original user's request to the subgraph
    original_request: str

# ----------------------------------------------------------------------------
# Notion Agent Subgraph
# ----------------------------------------------------------------------------

def create_notion_agent_graph():
    """
    Creates a specialized agent that can use a variety of Notion tools.
    """
    notion_llm = ChatOpenAI(model="gpt-4o", temperature=0.3).bind_tools(notion_tools)
    
    def notion_agent(state: ChatState):
        """Invokes the Notion LLM to generate tool calls based on the user's request."""
        # The HumanMessage here is crafted to be specific to the Notion agent's task
        prompt = f"You are a specialized Notion assistant. Based on the user's request, select the best Notion tool to use. User's request: {state['original_request']}"
        response = notion_llm.invoke([HumanMessage(content=prompt)])
        return {"messages": [response]}

    def notion_router(state: ChatState) -> str:
        """Routes to the tool node if the agent decides to use a tool."""
        if isinstance(state["messages"][-1], AIMessage) and state["messages"][-1].tool_calls:
            return "tools"
        return "end"

    workflow = StateGraph(ChatState)
    workflow.add_node("agent", notion_agent)
    workflow.add_node("tools", ToolNode(notion_tools))
    
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", notion_router, {
        "tools": "tools",
        "end": "end" # Explicitly define the end route
    })
    # After using a tool, the result is implicitly passed back to the graph's output
    workflow.add_edge("tools", END)
    
    return workflow.compile()

# ----------------------------------------------------------------------------
# Main Orchestrator Graph
# ----------------------------------------------------------------------------

@tool
def notion_task(user_query: str):
    """
    Use this tool for any and all requests related to Notion,
    such as creating, reading, or searching pages.
    The user query will be forwarded to a specialized Notion agent.
    """
    # This tool is a placeholder. Its only job is to be called by the main agent
    # so the orchestrator knows to route to the Notion subgraph.
    # The actual logic is handled by the subgraph itself.
    return f"Forwarding request to Notion agent: {user_query}"

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
