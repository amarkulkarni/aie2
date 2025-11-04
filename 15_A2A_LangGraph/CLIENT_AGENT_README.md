# 🤖 Client Agent for A2A Protocol - Activity #1

This directory contains the implementation of **Activity #1**: A LangGraph-based client agent that communicates with the A2A server.

## 📋 Overview

The client agent is an intelligent system that can:
- ✅ Answer simple questions directly from its own knowledge
- ✅ Delegate complex queries to the remote A2A server
- ✅ Maintain conversation context across multiple turns
- ✅ Make intelligent decisions about when to use remote capabilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 User Query                          │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           Client Agent (LangGraph)                  │
│  ┌───────────────────────────────────────────────┐ │
│  │  Decision: Direct Answer or Call Remote?     │ │
│  └───────────┬───────────────────────┬───────────┘ │
│              │                       │             │
│      ┌───────▼────────┐     ┌───────▼──────────┐  │
│      │ Direct Answer  │     │  A2A Tool Call   │  │
│      │  (Local LLM)   │     │  (Remote Agent)  │  │
│      └───────┬────────┘     └───────┬──────────┘  │
│              │                       │             │
│              └───────────┬───────────┘             │
│                          │                         │
└──────────────────────────┼─────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Response   │
                    └──────────────┘
```

## 📁 New Files Created

### 1. `app/a2a_tool.py`
**Purpose**: LangChain tool wrapper for A2A client calls

**Key Components**:
- `A2AToolWrapper`: Manages A2A client state and context
- `call_remote_agent`: Tool for single queries to remote agent
- `call_remote_agent_with_context`: Tool for multi-turn conversations
- Context management for conversation continuity

**Features**:
- Automatic agent card fetching
- Error handling and logging
- Context preservation for multi-turn dialogues
- Resource cleanup

### 2. `app/client_agent.py`
**Purpose**: LangGraph implementation of the client agent

**Key Components**:
- `ClientAgentState`: State management with message history
- `create_client_agent_graph()`: Builds the LangGraph workflow
- `client_agent_node`: Main decision-making node
- Routing logic for tool calls vs. direct answers

**Graph Structure**:
```
START → agent → router
         ↑         ↓
         │      tools
         └────────┘
         
         router → END (if no tools needed)
```

**Intelligence**:
The client agent uses a detailed system prompt to decide when to:
- Answer directly (simple questions, math, general knowledge)
- Call remote agent (current events, research papers, documents)
- Use context (follow-up questions)

### 3. `app/run_client_agent.py`
**Purpose**: Interactive CLI for testing the client agent

**Modes**:
1. **Interactive Mode** (default): Chat interface
2. **Demo Mode** (`--demo` flag): Automated test queries

**Features**:
- Colored terminal output for better readability
- Conversation history management
- Commands: `reset`, `quit`, `exit`
- Real-time streaming of agent responses

### 4. `app/test_client_agent.py`
**Purpose**: Comprehensive test suite for the client agent

**Test Scenarios**:
1. ✅ Direct answers (no remote call needed)
2. ✅ Web search delegation
3. ✅ Academic paper search
4. ✅ Multi-turn conversations with context
5. ✅ Math calculations
6. ✅ General knowledge questions

## 🚀 Usage

### Prerequisites

1. **Start the A2A Server** (Terminal 1):
```bash
uv run python -m app
```

The server will run at `http://localhost:10000`

### Running the Client Agent

#### Interactive Mode (Terminal 2):
```bash
uv run python app/run_client_agent.py
```

Example session:
```
You: What is 2 + 2?
Agent: 4

You: Find recent papers on vision transformers
Agent: [Calls remote agent, returns papers]

You: Summarize the key findings
Agent: [Uses context from previous query]

You: reset
[Conversation reset]

You: quit
[Exit]
```

#### Demo Mode:
```bash
uv run python app/run_client_agent.py --demo
```

Runs automated demo queries showcasing different capabilities.

#### Test Suite:
```bash
uv run python app/test_client_agent.py
```

Runs comprehensive tests with detailed output.

## 🎯 How It Works

### Decision Making Process

The client agent evaluates each query using this logic:

**Use Remote Agent When:**
- Query asks about current events or news
- User requests academic research papers
- Question requires document retrieval
- Complex queries needing multiple data sources

**Answer Directly When:**
- Simple factual questions from training data
- Math calculations
- General knowledge explanations
- Greetings and casual conversation

### Example Queries

| Query Type | Example | Expected Behavior |
|------------|---------|-------------------|
| **Direct** | "What is the capital of France?" | Answer directly: "Paris" |
| **Remote** | "Latest AI developments in 2025" | Call remote agent → Web search |
| **Remote** | "Find papers on transformers" | Call remote agent → ArXiv search |
| **Context** | "Summarize the key findings" | Use remote agent with context |
| **Math** | "Calculate 157 * 23" | Answer directly: "3611" |

## 🔍 Technical Deep Dive

### A2A Tool Integration

The `A2AToolWrapper` class manages:
```python
# Initialize once, reuse across calls
wrapper = A2AToolWrapper(base_url="http://localhost:10000")
await wrapper.initialize()  # Fetches agent card

# Make calls with automatic context management
response = await wrapper.call_remote_agent(query, use_existing_context=True)
```

### LangGraph Flow

```python
1. User sends query
2. Agent node processes with LLM + tools
3. Router checks for tool calls
   - If tool calls → Execute tools → Back to agent
   - If no tools → END
4. Return final response
```

### State Management

```python
class ClientAgentState(TypedDict):
    messages: List[BaseMessage]        # Full conversation
    using_remote_context: bool         # Multi-turn tracking
```

## 🐛 Troubleshooting

### Common Issues

**Error: Connection refused**
- Make sure A2A server is running: `uv run python -m app`
- Check server is on port 10000

**Error: Timeout**
- Remote agent queries can take 10-60 seconds
- This is normal for queries requiring web search or helpfulness evaluation

**Tool not being called**
- Check the query - may be simple enough for direct answer
- Try more specific queries like "Find recent papers on X"

**Context not maintained**
- Context is automatically managed
- Use `reset` command to start fresh conversation

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LANGCHAIN_VERBOSE=true
```

## 📊 Performance Notes

- **Direct answers**: < 1 second
- **Remote agent calls**: 5-60 seconds (includes helpfulness evaluation)
- **Multi-turn queries**: Similar to single queries, context adds minimal overhead

## 🎓 Key Learnings

### 1. **Agent-to-Agent Communication**
The A2A protocol enables seamless agent communication with:
- Standardized message format
- Context preservation
- Status tracking
- Error handling

### 2. **Intelligent Delegation**
The client agent demonstrates:
- When to use specialized capabilities
- How to maintain conversation context
- Resource optimization (don't call remote if not needed)

### 3. **Graph-Based Architecture**
LangGraph provides:
- Clear separation of concerns
- Flexible routing logic
- Easy debugging and visualization
- State management

## 🔮 Future Enhancements

Potential improvements:
- [ ] Add caching for repeated queries
- [ ] Implement streaming responses
- [ ] Support for multiple remote agents
- [ ] Add persona-based behavior (Advanced Build)
- [ ] Metrics and analytics dashboard
- [ ] Retry logic with exponential backoff

## 🎬 Video Demo Script

For your Loom video, demonstrate:

1. **Start the A2A server**
   ```bash
   uv run python -m app
   ```

2. **Run the interactive client**
   ```bash
   uv run python app/run_client_agent.py
   ```

3. **Show direct answer**
   - Query: "What is 2 + 2?"
   - Point out: No remote agent call

4. **Show remote delegation**
   - Query: "Find recent papers on vision transformers"
   - Point out: Tool call to remote agent
   - Show the response with papers

5. **Show multi-turn context**
   - Query: "What are the key findings?"
   - Point out: Uses previous context

6. **Explain architecture**
   - Show the code structure
   - Explain decision-making logic
   - Discuss A2A protocol benefits

7. **Run test suite** (optional)
   ```bash
   uv run python app/test_client_agent.py
   ```

## 📚 Related Documentation

- Main README: `../README.md`
- App Documentation: `app/README.md`
- A2A Protocol: [A2A Spec](https://github.com/anthropics/anthropic-cookbook/tree/main/a2a)

---

**Activity #1 Complete! ✅**

This implementation demonstrates a working LangGraph client agent that intelligently uses the A2A protocol to communicate with your server agent.


