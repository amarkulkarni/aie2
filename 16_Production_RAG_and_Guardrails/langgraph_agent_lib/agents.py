"""LangGraph agent integration with production features."""

from typing import Dict, Any, List, Optional
import os

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_core.tools import tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

from .models import get_openai_model
from .rag import ProductionRAGChain

# Guardrails imports - optional
try:
    from .guardrails import (
        GuardrailsState,
        create_guardrails_guard,
        create_guardrails_node
    )
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    GuardrailsState = None


class AgentState(TypedDict):
    """State schema for agent graphs."""
    messages: Annotated[List[BaseMessage], add_messages]


def create_rag_tool(rag_chain: ProductionRAGChain):
    """Create a RAG tool from a ProductionRAGChain."""
    
    @tool
    def retrieve_information(query: str) -> str:
        """Use Retrieval Augmented Generation to retrieve information from the student loan documents."""
        try:
            result = rag_chain.invoke(query)
            return result.content if hasattr(result, 'content') else str(result)
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
    
    return retrieve_information


def get_default_tools(rag_chain: Optional[ProductionRAGChain] = None) -> List:
    """Get default tools for the agent.
    
    Args:
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        List of tools
    """
    tools = []
    
    # Add Tavily search if API key is available
    if os.getenv("TAVILY_API_KEY"):
        tools.append(TavilySearchResults(max_results=5))
    
    # Add Arxiv tool
    tools.append(ArxivQueryRun())
    
    # Add RAG tool if provided
    if rag_chain:
        tools.append(create_rag_tool(rag_chain))
    
    return tools


def create_langgraph_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None
):
    """Create a simple LangGraph agent.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        Compiled LangGraph agent
    """
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)
    
    def call_model(state: AgentState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState):
        """Route to tools if the last message has tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        return END
    
    # Build graph
    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)
    
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"action": "action", END: END})
    graph.add_edge("action", "agent")
    
    return graph.compile()


def create_guardrails_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None,
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None,
    enable_input_guards: bool = True,
    enable_output_guards: bool = True,
    strict_mode: bool = True
):
    """Create a LangGraph agent with Guardrails validation.
    
    This agent includes input and output validation nodes that ensure
    safe, on-topic, and compliant interactions.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        valid_topics: List of valid topics to allow
        invalid_topics: List of invalid topics to block
        enable_input_guards: Enable input validation (jailbreak, topic, PII)
        enable_output_guards: Enable output validation (content moderation)
        strict_mode: If True, raises exceptions on validation failure
        
    Returns:
        Compiled LangGraph agent with guardrails
        
    Raises:
        RuntimeError: If guardrails are not available
    """
    if not GUARDRAILS_AVAILABLE:
        raise RuntimeError(
            "Guardrails not available. Install guards with:\n"
            "uv run guardrails hub install hub://tryolabs/restricttotopic\n"
            "uv run guardrails hub install hub://guardrails/detect_jailbreak\n"
            "uv run guardrails hub install hub://guardrails/profanity_free\n"
            "uv run guardrails hub install hub://guardrails/guardrails_pii"
        )
    
    # Set up tools
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Create guards
    input_guard = None
    output_guard = None
    
    if enable_input_guards:
        input_guard = create_guardrails_guard(
            valid_topics=valid_topics,
            invalid_topics=invalid_topics,
            enable_jailbreak_detection=True,
            enable_pii_protection=True,
            enable_profanity_check=False,  # Don't check user input for profanity
        )
    
    if enable_output_guards:
        output_guard = create_guardrails_guard(
            valid_topics=None,  # Don't restrict topics in output
            invalid_topics=None,
            enable_jailbreak_detection=False,
            enable_pii_protection=True,  # Redact PII in output
            enable_profanity_check=True,  # Check output for profanity
        )
    
    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)
    
    # Create guardrails validation node
    validate_node = create_guardrails_node(
        input_guard=input_guard,
        output_guard=output_guard,
        strict_mode=strict_mode
    )
    
    def validate_input_node(state: GuardrailsState) -> Dict[str, Any]:
        """Validate user input before processing."""
        return validate_node(state)
    
    def call_model(state: GuardrailsState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def validate_output_node(state: GuardrailsState) -> Dict[str, Any]:
        """Validate agent output before returning."""
        return validate_node(state)
    
    def should_continue(state: GuardrailsState):
        """Route based on tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        return "validate_output"
    
    def should_end(state: GuardrailsState):
        """Check if validation passed."""
        validation_results = state.get("validation_results", [])
        
        # If no validation results or all passed, end
        if not validation_results or all(r.get("passed", True) for r in validation_results):
            return END
        
        # If in strict mode and validation failed, END (exception will be raised)
        # If not in strict mode, still return the response
        return END
    
    # Build graph with guardrails
    graph = StateGraph(GuardrailsState)
    tool_node = ToolNode(tools)
    
    # Add nodes
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.add_node("validate_output", validate_output_node)
    
    # Set up flow
    graph.set_entry_point("validate_input")
    graph.add_edge("validate_input", "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"action": "action", "validate_output": "validate_output"}
    )
    graph.add_edge("action", "agent")
    graph.add_conditional_edges("validate_output", should_end, {END: END})
    
    return graph.compile()
