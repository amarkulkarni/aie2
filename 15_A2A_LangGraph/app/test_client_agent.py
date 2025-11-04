"""
Test Client Agent

This script tests the client agent with various scenarios to demonstrate
its ability to make intelligent decisions about when to use the A2A server.
"""

import asyncio
import logging

from app.client_agent import run_client_agent
from app.a2a_tool import cleanup_a2a_client, reset_remote_context


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_direct_answer():
    """Test that simple questions are answered directly."""
    print("\n" + "="*70)
    print("TEST 1: Direct Answer (No Remote Agent)")
    print("="*70)
    
    query = "What is the capital of France?"
    print(f"\nQuery: {query}")
    print("Expected: Direct answer without calling remote agent\n")
    
    response, _ = await run_client_agent(query)
    print(f"Response: {response}\n")
    
    await reset_remote_context()


async def test_web_search():
    """Test delegation to remote agent for web search."""
    print("\n" + "="*70)
    print("TEST 2: Web Search via Remote Agent")
    print("="*70)
    
    query = "What are the latest AI developments in 2025?"
    print(f"\nQuery: {query}")
    print("Expected: Should call remote agent for web search\n")
    
    response, _ = await run_client_agent(query)
    print(f"Response: {response}\n")
    
    await reset_remote_context()


async def test_arxiv_search():
    """Test delegation to remote agent for academic paper search."""
    print("\n" + "="*70)
    print("TEST 3: Academic Paper Search via Remote Agent")
    print("="*70)
    
    query = "Find recent papers on multimodal large language models"
    print(f"\nQuery: {query}")
    print("Expected: Should call remote agent for ArXiv search\n")
    
    response, _ = await run_client_agent(query)
    print(f"Response: {response}\n")
    
    await reset_remote_context()


async def test_multi_turn_conversation():
    """Test multi-turn conversation with context."""
    print("\n" + "="*70)
    print("TEST 4: Multi-Turn Conversation with Context")
    print("="*70)
    
    # First query
    query1 = "Find papers on vision transformers"
    print(f"\nQuery 1: {query1}")
    print("Expected: Should call remote agent for ArXiv search\n")
    
    response1, history = await run_client_agent(query1)
    print(f"Response 1: {response1}\n")
    
    # Follow-up query with context
    query2 = "What are the key innovations in those papers?"
    print(f"\nQuery 2: {query2}")
    print("Expected: Should use context from previous query\n")
    
    response2, history = await run_client_agent(query2, history)
    print(f"Response 2: {response2}\n")
    
    await reset_remote_context()


async def test_math_calculation():
    """Test that math questions are answered directly."""
    print("\n" + "="*70)
    print("TEST 5: Math Calculation (Direct Answer)")
    print("="*70)
    
    query = "Calculate 157 * 23"
    print(f"\nQuery: {query}")
    print("Expected: Direct calculation without remote agent\n")
    
    response, _ = await run_client_agent(query)
    print(f"Response: {response}\n")
    
    await reset_remote_context()


async def test_general_knowledge():
    """Test general knowledge question."""
    print("\n" + "="*70)
    print("TEST 6: General Knowledge (Direct Answer)")
    print("="*70)
    
    query = "Explain what a transformer model is in machine learning"
    print(f"\nQuery: {query}")
    print("Expected: Direct explanation from training knowledge\n")
    
    response, _ = await run_client_agent(query)
    print(f"Response: {response}\n")
    
    await reset_remote_context()


async def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "="*70)
    print("🧪 RUNNING CLIENT AGENT TEST SUITE")
    print("="*70)
    print("\nNote: Make sure the A2A server is running at http://localhost:10000")
    print("Start it with: uv run python -m app\n")
    
    input("Press Enter to start tests...")
    
    try:
        # Test 1: Direct answer
        await test_direct_answer()
        await asyncio.sleep(1)
        
        # Test 2: Web search
        await test_web_search()
        await asyncio.sleep(1)
        
        # Test 3: ArXiv search
        await test_arxiv_search()
        await asyncio.sleep(1)
        
        # Test 4: Multi-turn conversation
        await test_multi_turn_conversation()
        await asyncio.sleep(1)
        
        # Test 5: Math calculation
        await test_math_calculation()
        await asyncio.sleep(1)
        
        # Test 6: General knowledge
        await test_general_knowledge()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
    
    finally:
        await cleanup_a2a_client()


async def main():
    """Main entry point."""
    await run_all_tests()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        logger.error(f"Fatal error: {e}", exc_info=True)


