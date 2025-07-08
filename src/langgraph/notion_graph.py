from typing import Dict, TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool, tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import the specialized Notion tools
from .notion_tools import notion_tools

# ----------------------------------------------------------------------------
# Notion Agent Subgraph
# ----------------------------------------------------------------------------

def create_notion_agent_graph():
    """
    Creates a specialized agent that can use a variety of Notion tools.
    """
    # Import ChatState from the main graph file
    from .graph import ChatState
    
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
# Notion Task Tool
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