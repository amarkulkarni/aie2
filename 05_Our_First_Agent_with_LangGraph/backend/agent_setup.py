import os
from typing import Annotated, Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

# Initialize the model (with error handling)
def get_model():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        api_key=api_key
    )

# Initialize tools (with error handling)
def get_search_tool():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    return TavilySearchResults(api_key=api_key)

def get_arxiv_tool():
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper())

# Wikipedia tool - no API key needed!
@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for information about a topic. 
    Use this for general knowledge, definitions, and encyclopedic information.
    Perfect for getting background information, historical context, or definitions."""
    try:
        import urllib.parse
        
        # Set proper headers for Wikipedia API
        headers = {
            'User-Agent': 'LangGraph-Agent/1.0 (https://github.com/langchain-ai/langgraph; contact@example.com)'
        }
        
        # First, search for the topic to get the correct page title
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': 1
        }
        
        search_response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            if search_data.get('query', {}).get('search'):
                # Get the exact page title from search results
                page_title = search_data['query']['search'][0]['title']
                
                # URL encode the page title properly
                encoded_title = urllib.parse.quote(page_title.replace(' ', '_'), safe='')
                
                # Now get the summary using the correct page title
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
                summary_response = requests.get(summary_url, headers=headers, timeout=10)
                
                if summary_response.status_code == 200:
                    data = summary_response.json()
                    return f"### Wikipedia: {data['title']}\n\n{data['extract']}\n\n**Source:** {data['content_urls']['desktop']['page']}"
                else:
                    return ""  # Return empty string instead of error message
            else:
                return ""  # Return empty string instead of error message
        else:
            return ""  # Return empty string instead of error message
            
    except Exception as e:
        return ""  # Return empty string instead of error message

# Tool belt - now with Wikipedia! (lazy initialization)
def get_tool_belt():
    return [get_search_tool(), get_arxiv_tool(), wikipedia_search]

def get_model_with_tools():
    return get_model().bind_tools(get_tool_belt())

def should_continue(state):
    """Determine whether to continue or end"""
    last_message = state["messages"][-1]

    # Check for tool calls (only on AIMessage, not ToolMessage)
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "action"

    return END


def call_model(state):
    """Call the model"""
    response = get_model_with_tools().invoke(state["messages"])
    return {"messages": [response]}

def call_tools(state):
    """Call the tools"""
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls
    
    tool_messages = []
    tool_belt = get_tool_belt()  # Get tools lazily
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Handle tools
        tool_found = False
        for tool in tool_belt:
            # Check if it's a LangChain tool (has name attribute)
            if hasattr(tool, 'name') and tool.name == tool_name:
                try:
                    result = tool.invoke(tool_args)
                    tool_messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))
                    tool_found = True
                    break
                except Exception as e:
                    tool_messages.append(ToolMessage(
                        content=f"Error calling tool '{tool_name}': {str(e)}",
                        tool_call_id=tool_call["id"]
                    ))
                    tool_found = True
                    break
            # Check if it's a custom @tool decorated function
            elif hasattr(tool, '__name__') and tool.__name__ == tool_name:
                try:
                    result = tool.invoke(tool_args)
                    tool_messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    ))
                    tool_found = True
                    break
                except Exception as e:
                    tool_messages.append(ToolMessage(
                        content=f"Error calling tool '{tool_name}': {str(e)}",
                        tool_call_id=tool_call["id"]
                    ))
                    tool_found = True
                    break
        
        if not tool_found:
            tool_messages.append(ToolMessage(
                content=f"Tool '{tool_name}' not found",
                tool_call_id=tool_call["id"]
            ))
    
    return {"messages": tool_messages}

def create_agent():
    """Create and return the LangGraph agent"""
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tools)
    
    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "action": "action",
            END: END
        }
    )
    workflow.add_edge("action", "agent")
    
    # Compile the graph
    app = workflow.compile()
    return app
