"""
Quick verification script to check client agent setup.
This doesn't require the A2A server to be running.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from app.client_agent import create_client_agent_graph

# Load environment variables
load_dotenv()

async def test_graph_creation():
    """Test that the graph can be created successfully."""
    print("Testing client agent graph creation...")
    
    try:
        graph = create_client_agent_graph()
        print("✅ Graph created successfully!")
        
        # Test a simple query that should be answered directly
        print("\nTesting with a simple math query (should answer directly)...")
        initial_state = {
            "messages": [HumanMessage(content="What is 2 + 2?")],
            "using_remote_context": False,
        }
        
        # This should work without calling the remote agent
        result = await graph.ainvoke(initial_state)
        
        final_message = result["messages"][-1]
        print(f"\n✅ Query processed successfully!")
        print(f"Response: {final_message.content}")
        
        # Check if it used tools (it shouldn't for this simple question)
        tool_calls = getattr(final_message, 'tool_calls', [])
        if tool_calls:
            print(f"\n⚠️  Warning: Agent made tool calls for a simple question: {tool_calls}")
        else:
            print("\n✅ Agent answered directly without tool calls (as expected)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*70)
    print("Client Agent Setup Verification")
    print("="*70)
    print("\nThis test verifies the client agent can be initialized")
    print("and handle simple queries without the A2A server.\n")
    
    success = await test_graph_creation()
    
    print("\n" + "="*70)
    if success:
        print("✅ VERIFICATION PASSED")
        print("\nNext steps:")
        print("1. Start the A2A server: uv run python -m app")
        print("2. Run the client agent: uv run python app/run_client_agent.py")
        print("3. Or run tests: uv run python app/test_client_agent.py")
    else:
        print("❌ VERIFICATION FAILED")
        print("\nPlease check the error messages above.")
    print("="*70 + "\n")

if __name__ == '__main__':
    asyncio.run(main())

