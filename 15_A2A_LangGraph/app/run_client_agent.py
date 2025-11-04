"""
Interactive Client Agent Runner

This script provides an interactive interface to test the client agent
that uses the A2A protocol to communicate with the remote server.
"""

import asyncio
import logging
import sys
from typing import List

from langchain_core.messages import BaseMessage

from app.client_agent import run_client_agent
from app.a2a_tool import cleanup_a2a_client, reset_remote_context


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


async def interactive_session():
    """
    Run an interactive session with the client agent.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🤖 Client Agent Interactive Session{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}This client agent can:")
    print(f"  • Answer simple questions directly")
    print(f"  • Delegate complex queries to the remote A2A server")
    print(f"  • Maintain conversation context across turns{Colors.ENDC}\n")
    
    print(f"{Colors.YELLOW}Commands:")
    print(f"  • Type your question and press Enter")
    print(f"  • Type 'reset' to start a new conversation")
    print(f"  • Type 'quit' or 'exit' to end the session{Colors.ENDC}\n")
    
    print(f"{Colors.GREEN}{'─'*70}{Colors.ENDC}\n")
    
    conversation_history: List[BaseMessage] = []
    
    try:
        while True:
            # Get user input
            user_input = input(f"{Colors.BOLD}{Colors.BLUE}You: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.ENDC}\n")
                break
            
            if user_input.lower() == 'reset':
                conversation_history = []
                await reset_remote_context()
                print(f"{Colors.YELLOW}🔄 Conversation reset. Starting fresh!{Colors.ENDC}\n")
                continue
            
            # Process the query
            print(f"\n{Colors.CYAN}🤔 Processing...{Colors.ENDC}\n")
            
            try:
                response, updated_history = await run_client_agent(
                    user_input,
                    conversation_history
                )
                
                # Update conversation history
                conversation_history = updated_history
                
                # Check if remote agent was called by looking at the message history
                remote_call_made = False
                for msg in updated_history:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            if 'call_remote_agent' in tool_call.get('name', ''):
                                remote_call_made = True
                                break
                
                # Display how the query was handled
                if remote_call_made:
                    print(f"{Colors.YELLOW}📡 Remote A2A Agent Called{Colors.ENDC}")
                else:
                    print(f"{Colors.BLUE}💡 Direct Answer (No Remote Call){Colors.ENDC}")
                
                # Display response
                print(f"\n{Colors.BOLD}{Colors.GREEN}Agent: {Colors.ENDC}{response}\n")
                print(f"{Colors.GREEN}{'─'*70}{Colors.ENDC}\n")
                
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {str(e)}{Colors.ENDC}\n")
                logger.error(f"Error processing query: {e}", exc_info=True)
    
    finally:
        # Cleanup
        await cleanup_a2a_client()


async def run_demo_queries():
    """
    Run a set of demo queries to showcase the client agent capabilities.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🎬 Client Agent Demo - Automated Queries{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    demo_queries = [
        {
            "category": "Simple Question (Direct Answer)",
            "query": "What is 2 + 2?",
            "description": "Should be answered directly without calling remote agent"
        },
        {
            "category": "Current Events (Remote Agent)",
            "query": "What are the latest developments in artificial intelligence in 2025?",
            "description": "Should call remote agent for web search"
        },
        {
            "category": "Academic Research (Remote Agent)",
            "query": "Find recent papers on transformer architectures",
            "description": "Should call remote agent for ArXiv search"
        },
        {
            "category": "Follow-up Question (Context)",
            "query": "Can you summarize the key findings from those papers?",
            "description": "Should use context from previous query"
        },
    ]
    
    conversation_history: List[BaseMessage] = []
    
    try:
        for i, demo in enumerate(demo_queries, 1):
            print(f"{Colors.HEADER}{Colors.BOLD}Demo Query {i}/{len(demo_queries)}{Colors.ENDC}")
            print(f"{Colors.CYAN}Category: {demo['category']}{Colors.ENDC}")
            print(f"{Colors.YELLOW}Expected: {demo['description']}{Colors.ENDC}\n")
            
            print(f"{Colors.BOLD}{Colors.BLUE}Query: {demo['query']}{Colors.ENDC}\n")
            
            print(f"{Colors.CYAN}🤔 Processing...{Colors.ENDC}\n")
            
            try:
                response, updated_history = await run_client_agent(
                    demo['query'],
                    conversation_history
                )
                
                # Update conversation history for context in next queries
                conversation_history = updated_history
                
                # Check if remote agent was called
                remote_call_made = False
                for msg in updated_history:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            if 'call_remote_agent' in tool_call.get('name', ''):
                                remote_call_made = True
                                break
                
                # Display how the query was handled
                if remote_call_made:
                    print(f"{Colors.YELLOW}📡 Remote A2A Agent Called{Colors.ENDC}")
                else:
                    print(f"{Colors.BLUE}💡 Direct Answer (No Remote Call){Colors.ENDC}")
                
                # Display response
                print(f"\n{Colors.BOLD}{Colors.GREEN}Response:{Colors.ENDC}")
                print(f"{response}\n")
                print(f"{Colors.GREEN}{'─'*70}{Colors.ENDC}\n")
                
                # Pause between queries
                if i < len(demo_queries):
                    await asyncio.sleep(2)
                
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {str(e)}{Colors.ENDC}\n")
                logger.error(f"Error in demo query: {e}", exc_info=True)
    
    finally:
        # Cleanup
        await cleanup_a2a_client()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Demo Complete!{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


async def main():
    """Main entry point."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Client Agent for A2A Protocol{Colors.ENDC}\n")
    
    # Check if demo mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        await run_demo_queries()
    else:
        await interactive_session()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Session interrupted. Goodbye!{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {str(e)}{Colors.ENDC}\n")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


