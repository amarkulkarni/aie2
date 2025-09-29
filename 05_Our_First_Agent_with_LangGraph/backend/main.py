from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from agent_setup import create_agent

def format_agent_response(content):
    """Format agent response for better readability"""
    if not content:
        return content
    
    # If content is a list of search results, format them nicely
    if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
        formatted = "## 🔍 Search Results\n\n"
        for i, result in enumerate(content, 1):
            title = result.get('title', 'No Title')
            url = result.get('url', '')
            content_text = result.get('content', '')
            score = result.get('score', 0)
            
            formatted += f"### {i}. {title}\n"
            if url:
                formatted += f"**Source:** {url}\n\n"
            if content_text:
                # Truncate content if too long
                if len(content_text) > 500:
                    content_text = content_text[:500] + "..."
                formatted += f"{content_text}\n\n"
            formatted += "---\n\n"
        return formatted
    
    # If content is a string, try to format it
    if isinstance(content, str):
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Format headings
            if line.startswith('**') and line.endswith('**') and len(line) > 4:
                formatted_lines.append(f"## {line.replace('**', '')}")
            # Format subheadings
            elif line.startswith('###'):
                formatted_lines.append(f"### {line.replace('###', '').strip()}")
            # Format list items
            elif line.startswith('- ') or line.startswith('• '):
                formatted_lines.append(f"- {line[2:]}")
            # Format numbered lists
            elif re.match(r'^\d+\.\s+', line):
                formatted_lines.append(line)
            # Regular paragraphs
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    return str(content)

app = FastAPI(title="LangGraph Agent API", version="1.0.0")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = None

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    tools_used: List[str] = []
    conversation_ended: bool = False

class SuggestedPrompts(BaseModel):
    prompts: List[str]

# Suggested prompts for the UI
SUGGESTED_PROMPTS = [
    "What are the latest trends in AI?",
    "Explain how machine learning works",
    "What is the difference between supervised and unsupervised learning?",
    "Tell me about neural networks",
    "What are the applications of deep learning?",
    "How does natural language processing work?",
    "What is computer vision?",
    "Explain reinforcement learning",
    "What are the challenges in AI?",
    "How can I get started with AI development?"
]

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        agent = create_agent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        raise

@app.get("/")
async def root():
    """Serve the React app"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"message": "Frontend not built. Run 'npm run build' in the frontend directory."}

@app.get("/api/suggested-prompts")
async def get_suggested_prompts():
    """Get suggested prompts for the UI"""
    return SuggestedPrompts(prompts=SUGGESTED_PROMPTS)

@app.post("/api/chat", response_model=AgentResponse)
async def chat_with_agent(chat_message: ChatMessage):
    """Chat with the LangGraph agent"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Prepare the input for the agent
        input_data = {
            "messages": [{"role": "user", "content": chat_message.message}]
        }
        
        # Run the agent
        result = await agent.ainvoke(input_data)
        
        # Extract response and tools used
        response_text = ""
        tools_used = []
        conversation_ended = False
        
        # Process the agent's response
        if "messages" in result:
            for message in result["messages"]:
                # Check for tool usage
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tools_used.append(tool_call.get('name', 'Unknown Tool'))
                
                # Format the content for display
                if hasattr(message, 'content') and message.content:
                    formatted_content = format_agent_response(message.content)
                    response_text += formatted_content + "\n"
        
        return AgentResponse(
            response=response_text.strip(),
            tools_used=tools_used,
            conversation_ended=conversation_ended
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent_initialized": agent is not None}

# Mount static files (React build)
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "build", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Catch-all route for React Router
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all other routes"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"message": "Frontend not built. Run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
