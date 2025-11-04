# 🎥 5-Minute Loom Video Script

## ⏱️ Total Time: 5 Minutes

---

## 🎬 Introduction (20 seconds)

"Hi! I'm presenting my Session 16 assignment on Production RAG and Guardrails. I built a production-ready LLM system with caching, LangGraph agents, and security guardrails. Let me walk you through the key implementations."

---

## ⚡ Activity #1: Cache Performance Testing (1 minute)

**[SHOW: Cell 24]**

"First, Activity #1 tested cache performance at multiple levels.

**Results:**
- Embedding cache: **15x faster** on second call
- LLM cache: instant responses for repeated queries
- Production impact: 50-80% latency reduction at scale

**Key insight:** Caching is critical for production - dramatically reduces API costs and improves user experience. Main challenges are cache invalidation, memory management, and cold starts."

---

## 🤖 LangGraph Agents (45 seconds)

**[SHOW: Cell 28]**

"I implemented a LangGraph agent with GPT-4-mini that uses multiple tools:
- RAG system for document retrieval
- Tavily for web search
- Arxiv for academic papers

The agent intelligently selects tools and executes them in parallel for efficient responses."

**[SHOW: Cell 31 - Answer]**

"Simple agents are fast but lack quality control. Helpfulness agents add self-correction but cost 2-3x more. The key is choosing the right trade-off for your use case."

---

## 🛡️ Activity #3: Production-Safe Agent with Guardrails (2 minutes)

**[SHOW: Cell 46 - Architecture diagram]**

"Activity #3 was building a production-safe agent with security guardrails. The architecture flows like this:

```
User Input → Input Guards → Agent → Tools → Output Guards → Response
```

**Input Guards:**
- ✅ Topic Restriction - Keeps queries on-topic
- ✅ PII Detection - Identifies sensitive data
- ✅ Profanity Filter

**Output Guards:**
- ✅ PII Redaction - Removes sensitive info
- ✅ Content Moderation

**[SHOW: Cells 45-47 - Testing]**

I installed 3 out of 4 guards successfully. The jailbreak guard requires PyTorch 2.4+, which Intel Macs don't support, so I made it optional with graceful fallback.

**Testing Suite:**
I created 20 comprehensive tests across 5 categories:
- ✅ 4 legitimate queries - all passed
- 🛡️ 4 off-topic queries - correctly blocked
- 🚨 4 jailbreak attempts - blocked
- 🔐 4 PII tests - detected and redacted
- ⚠️ 4 edge cases - handled gracefully

**Results:** Guards work correctly with only 10-30% latency overhead - acceptable for production security."

---

## 💡 Key Challenges Overcome (45 seconds)

"Three main challenges:

1. **PyTorch compatibility** - Intel Mac doesn't support 2.4+, so I constrained to 2.2.2
2. **Module caching** - Jupyter cached old imports, solved with module reload cell
3. **Guard availability** - Made jailbreak detection optional, 3/4 guards still provide strong protection

All implemented with proper error handling and fallbacks for production reliability."

---

## 📚 Key Learnings & Wrap-up (30 seconds)

"Three key takeaways:

1. **Caching is essential** - 15-300x speedup and massive cost savings
2. **Defense in depth** - Multiple guard layers catch different attack vectors
3. **Production trade-offs** - Balance security, performance, and cost

All requirements completed:
✅ Production RAG with caching
✅ LangGraph agent integration  
✅ Comprehensive security guardrails
✅ Extensive adversarial testing

Thanks for watching!"

---

## 📋 5-Minute Timeline

| Time | Section | What to Show |
|------|---------|--------------|
| 0:00-0:20 | Intro | Notebook overview |
| 0:20-1:20 | Activity #1 Cache | Cell 24 with results |
| 1:20-2:05 | Agents & Q2 | Cells 28, 31 |
| 2:05-4:05 | Activity #3 Guardrails | Cells 45-47, architecture |
| 4:05-4:50 | Challenges | Explain solutions |
| 4:50-5:00 | Wrap-up | Summary checklist |

---

## 🎯 Quick Cheat Sheet

### Must-Show Cells:
- **Cell 24** - Cache performance (1 min)
- **Cell 28** - Agent testing (20s)
- **Cell 31** - Architecture answer (20s)
- **Cell 46** - Architecture diagram (30s)
- **Cell 45-47** - Guardrails testing (1 min)

### Key Numbers to Mention:
- **15-300x** cache speedup
- **3/4 guards** installed
- **20 tests** comprehensive
- **10-30%** latency overhead

### Key Phrases:
- "Production-ready with caching and guardrails"
- "Defense in depth with multiple layers"
- "Graceful fallbacks for missing components"

---

## 📱 Social Media Post (Short Version)

```
Completed Session 16: Production RAG & Guardrails! 🚀

✅ Multi-layer caching (15x speedup)
✅ LangGraph agent integration
✅ Security guardrails (3/4 guards)
✅ 20 adversarial tests

Key learning: Production systems need caching 
for performance + guardrails for safety.

#AIEngineering #LLM #Production @AIMakerspace

[Video] [GitHub]
```

---

## ✅ Pre-Recording Checklist

- [ ] Jupyter Lab open with notebook
- [ ] Cells 24, 28, 31, 45-47 ready to show
- [ ] This script visible on second monitor
- [ ] Microphone tested
- [ ] Screen sharing working
- [ ] Speak clearly and confidently

---

## 🎬 Recording Tips

1. **Pace yourself** - Don't rush, but stay on time
2. **Show outputs** - Briefly pause on results
3. **Be confident** - You did great work!
4. **Smile** - Enthusiasm shows through voice
5. **Stick to script** - 5 minutes goes fast

**You've got this! 🎯**

