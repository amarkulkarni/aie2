"""
A2A Tool Wrapper

This module provides a LangChain tool that wraps the A2A client,
allowing a client agent to call the remote A2A server as a tool.
"""

import logging
from typing import Optional
from uuid import uuid4

import httpx
from langchain_core.tools import tool

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AToolWrapper:
    """Wrapper class to maintain A2A client state and context."""
    
    def __init__(self, base_url: str = "http://localhost:10000"):
        self.base_url = base_url
        self.httpx_client = None
        self.client = None
        self.context_id: Optional[str] = None
        self.task_id: Optional[str] = None
        
    async def initialize(self):
        """Initialize the A2A client by fetching the agent card."""
        if self.client is not None:
            return  # Already initialized
            
        self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        
        try:
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.base_url,
            )
            
            logger.info(f"Fetching agent card from {self.base_url}")
            agent_card = await resolver.get_agent_card()
            logger.info(f"Successfully connected to agent: {agent_card.name}")
            
            self.client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=agent_card
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize A2A client: {e}")
            raise
    
    async def call_remote_agent(
        self, 
        query: str, 
        use_existing_context: bool = False
    ) -> str:
        """
        Call the remote A2A agent with a query.
        
        Args:
            query: The question or request to send to the remote agent
            use_existing_context: Whether to continue previous conversation
            
        Returns:
            The response from the remote agent
        """
        await self.initialize()
        
        message_payload = {
            'message': {
                'role': 'user',
                'parts': [{'kind': 'text', 'text': query}],
                'message_id': uuid4().hex,
            }
        }
        
        # Add context for multi-turn conversations
        if use_existing_context and self.context_id and self.task_id:
            message_payload['message']['context_id'] = self.context_id
            message_payload['message']['task_id'] = self.task_id
        
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**message_payload)
        )
        
        try:
            logger.info(f"📡 REMOTE CALL: Sending query to remote A2A agent: {query}")
            response = await self.client.send_message(request)
            
            # Store context for multi-turn conversations
            if response.root and response.root.result:
                self.task_id = response.root.result.id
                self.context_id = response.root.result.context_id
                
                # Extract the response text
                if response.root.result.message and response.root.result.message.parts:
                    response_text = ""
                    for part in response.root.result.message.parts:
                        if hasattr(part.root, 'text'):
                            response_text += part.root.text
                    
                    logger.info(f"✅ REMOTE RESPONSE: Received response from remote A2A agent")
                    return response_text
            
            return "No response received from remote agent"
            
        except Exception as e:
            logger.error(f"Error calling remote agent: {e}")
            return f"Error communicating with remote agent: {str(e)}"
    
    async def reset_context(self):
        """Reset the conversation context for a new conversation."""
        self.context_id = None
        self.task_id = None
        logger.info("Context reset for new conversation")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.httpx_client:
            await self.httpx_client.aclose()


# Global instance for the tool
_a2a_wrapper = A2AToolWrapper()


@tool
async def call_remote_agent(query: str) -> str:
    """
    Call a remote AI agent that has access to web search (Tavily), 
    academic paper search (ArXiv), and document retrieval (RAG).
    
    Use this tool when you need:
    - Current web information or news
    - Academic research papers
    - Information from specific documents
    - Complex queries requiring multiple data sources
    
    Args:
        query: The question or request to send to the remote agent
        
    Returns:
        The response from the remote agent with relevant information
    """
    return await _a2a_wrapper.call_remote_agent(query, use_existing_context=False)


@tool
async def call_remote_agent_with_context(query: str) -> str:
    """
    Continue a conversation with the remote AI agent using previous context.
    
    Use this for follow-up questions that relate to previous queries.
    
    Args:
        query: The follow-up question or request
        
    Returns:
        The response from the remote agent considering previous context
    """
    return await _a2a_wrapper.call_remote_agent(query, use_existing_context=True)


async def reset_remote_context():
    """Reset the conversation context with the remote agent."""
    await _a2a_wrapper.reset_context()


async def cleanup_a2a_client():
    """Cleanup A2A client resources."""
    await _a2a_wrapper.cleanup()


