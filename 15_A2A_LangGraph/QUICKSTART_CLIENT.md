# 🚀 Quick Start Guide - Client Agent

This guide will get you up and running with the client agent in under 5 minutes!

## Prerequisites

- ✅ Python environment set up
- ✅ Dependencies installed (`uv sync` or from `quickstart.sh`)
- ✅ `.env` file with `OPENAI_API_KEY`

## Step-by-Step

### 1️⃣ Verify Setup (Optional)

```bash
uv run python verify_client_setup.py
```

Expected output:
```
✅ VERIFICATION PASSED

Next steps:
1. Start the A2A server: uv run python -m app
2. Run the client agent: uv run python app/run_client_agent.py
```

---

### 2️⃣ Start the A2A Server

Open **Terminal 1**:

```bash
uv run python -m app
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://localhost:10000
```

✅ Leave this running!

---

### 3️⃣ Run the Client Agent

Open **Terminal 2**:

#### Option A: Interactive Mode (Recommended)

```bash
uv run python app/run_client_agent.py
```

Try these queries:
```
You: What is 2 + 2?
Agent: 4

You: Find recent papers on transformers
Agent: [Fetches from ArXiv via A2A]

You: What are the key findings?
Agent: [Uses context from previous query]

You: reset
[Clears conversation]

You: quit
[Exit]
```

#### Option B: Demo Mode (Automated)

```bash
uv run python app/run_client_agent.py --demo
```

Runs 4 automated demo queries.

#### Option C: Test Suite

```bash
uv run python app/test_client_agent.py
```

Runs 6 comprehensive tests.

---

## 🎯 What to Expect

### Direct Answers (No Remote Call)
- Math: "Calculate 157 * 23"
- Facts: "What is the capital of France?"
- Knowledge: "Explain transformers"

Response time: ~1 second

### Remote Agent Calls (A2A Protocol)
- Web: "Latest AI news in 2025"
- Papers: "Find papers on vision transformers"
- Documents: "What do the documents say about X?"

Response time: 10-60 seconds (includes helpfulness evaluation)

### Multi-Turn with Context
- Query 1: "Find papers on X"
- Query 2: "Summarize the findings"

Context automatically maintained!

---

## 🐛 Troubleshooting

### Server Not Running
```
Error: Connection refused
```

**Fix**: Start server in Terminal 1:
```bash
uv run python -m app
```

### Timeout Errors
```
Error: Timeout waiting for response
```

**Expected**: Remote queries can take 30-60 seconds due to:
- Tool execution (web search, ArXiv)
- Helpfulness evaluation loop (up to 10 iterations)

This is normal! ⏰

### Missing API Key
```
Error: OPENAI_API_KEY not set
```

**Fix**: Create `.env` file:
```bash
OPENAI_API_KEY=your_key_here
```

---

## 📊 Architecture Recap

```
Your Terminal (Client Agent)
         ↓
   A2A Protocol
         ↓
Server (localhost:10000)
         ↓
  Tools: Tavily, ArXiv, RAG
         ↓
   LLM Response + Helpfulness Check
         ↓
   Back to Client
```

---

## 📚 Next Steps

- Read full documentation: `CLIENT_AGENT_README.md`
- Review implementation: `ACTIVITY_1_SUMMARY.md`
- Explore code: `app/client_agent.py`, `app/a2a_tool.py`
- Record demo video for submission!

---

## 🎬 Quick Demo for Video

```bash
# Terminal 1
uv run python -m app

# Terminal 2
uv run python app/run_client_agent.py

# Type these queries:
# 1. What is 2 + 2?
# 2. Find recent papers on vision transformers
# 3. What are the key findings?
```

Then show the code in `app/client_agent.py`!

---

**That's it! You're ready to go! 🎉**


