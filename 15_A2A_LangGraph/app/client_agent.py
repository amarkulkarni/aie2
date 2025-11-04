"""
Client Agent with LangGraph

This module implements a LangGraph-based client agent that can interact
with the remote A2A server. The client agent decides when to delegate
queries to the remote agent vs. answering directly.
"""

import logging
from typing import Annotated, List, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.a2a_tool import call_remote_agent, call_remote_agent_with_context


# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientAgentState(TypedDict):
    """State for the client agent graph."""
    messages: Annotated[List[BaseMessage], add_messages]
    using_remote_context: bool  # Track if we're in a multi-turn conversation


def create_client_agent_graph():
    """
    Creates a LangGraph for the client agent that can call the remote A2A server.
    
    The graph flow:
    1. Client agent decides if query needs remote agent or can answer directly
    2. If remote needed, calls A2A tool
    3. If not remote, answers directly
    4. Returns final response
    """
    
    # Initialize the LLM with tools
    tools = [call_remote_agent, call_remote_agent_with_context]
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )
    llm_with_tools = llm.bind_tools(tools)
    
    # System prompt for the client agent
    SYSTEM_PROMPT = """You are a helpful AI assistant that can answer questions directly or delegate to a remote specialized agent when needed.

The remote agent has access to:
- Web search (Tavily) for current information and news
- Academic paper search (ArXiv) for research papers
- Document retrieval (RAG) for specific document content

When to use the remote agent (call_remote_agent):
- Questions about current events, news, or recent information
- Requests for academic research papers or scientific information
- Questions that require searching through documents
- Complex queries that need multiple data sources

When to answer directly (no tool call):
- Simple factual questions you can answer from your training
- Math calculations
- General knowledge questions
- Explanations of concepts
- Greetings and casual conversation

For follow-up questions in the same conversation, use call_remote_agent_with_context to maintain context.

Be concise and helpful in your responses."""
    
    def client_agent_node(state: ClientAgentState) -> ClientAgentState:
        """
        The main client agent node that decides actions.
        """
        messages = state["messages"]
        
        # Add system prompt if this is the first message
        if len(messages) == 1 or not any(isinstance(m, HumanMessage) for m in messages[:-1]):
            messages_with_system = [HumanMessage(content=SYSTEM_PROMPT)] + messages
        else:
            messages_with_system = messages
        
        logger.info(f"Client agent processing: {messages[-1].content}")
        response = llm_with_tools.invoke(messages_with_system)
        
        return {"messages": [response]}
    
    def route_after_agent(
        state: ClientAgentState,
    ) -> Literal["tools", "end"]:
        """
        Router that decides if we need to call tools or end.
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, route to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_names = [tc['name'] for tc in last_message.tool_calls]
            if any('call_remote_agent' in name for name in tool_names):
                logger.info(f"🔧 Routing to tools (REMOTE A2A CALL): {tool_names}")
            else:
                logger.info(f"🔧 Routing to tools: {tool_names}")
            return "tools"
        
        # Otherwise, we're done
        logger.info("✅ Direct answer - Routing to END (no remote call)")
        return "end"
    
    def should_continue_after_tools(state: ClientAgentState) -> Literal["agent", "end"]:
        """
        After tools execute, decide if we need more agent processing.
        """
        # Always go back to agent to process tool results
        return "agent"
    
    # Build the graph
    workflow = StateGraph(ClientAgentState)
    
    # Add nodes
    workflow.add_node("agent", client_agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Add edges
    workflow.set_entry_point("agent")
    
    # Conditional edge from agent
    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tools": "tools",
            "end": END,
        }
    )
    
    # Edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


async def run_client_agent(query: str, conversation_history: List[BaseMessage] = None):
    """
    Run the client agent with a query.
    
    Args:
        query: The user's query
        conversation_history: Previous messages in the conversation
        
    Returns:
        The agent's response
    """
    graph = create_client_agent_graph()
    
    # Prepare initial state
    if conversation_history is None:
        conversation_history = []
    
    messages = conversation_history + [HumanMessage(content=query)]
    
    initial_state = {
        "messages": messages,
        "using_remote_context": len(conversation_history) > 0,
    }
    
    # Run the graph
    logger.info(f"Running client agent with query: {query}")
    final_state = await graph.ainvoke(initial_state)
    
    # Extract the final response
    final_message = final_state["messages"][-1]
    
    return final_message.content, final_state["messages"]


async def run_client_agent_streaming(query: str, conversation_history: List[BaseMessage] = None):
    """
    Run the client agent with streaming output.
    
    Args:
        query: The user's query
        conversation_history: Previous messages in the conversation
        
    Yields:
        State updates as they occur
    """
    graph = create_client_agent_graph()
    
    # Prepare initial state
    if conversation_history is None:
        conversation_history = []
    
    messages = conversation_history + [HumanMessage(content=query)]
    
    initial_state = {
        "messages": messages,
        "using_remote_context": len(conversation_history) > 0,
    }
    
    # Stream the graph execution
    logger.info(f"Running client agent (streaming) with query: {query}")
    async for state in graph.astream(initial_state):
        yield state

