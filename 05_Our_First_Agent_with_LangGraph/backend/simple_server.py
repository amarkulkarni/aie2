#!/usr/bin/env python3
"""
Simple server that serves React app and handles API calls
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our agent setup
from agent_setup import get_agent

app = FastAPI(title="LangGraph PDF Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = get_agent()

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    response: str
    tool_calls: List[Dict[str, Any]] = []
    processing_steps: List[str] = []
    pdf_generated: bool = False
    pdf_data: Optional[str] = None
    pdf_filename: Optional[str] = None
    conversation_ended: bool = False

@app.get("/")
async def root():
    return FileResponse("simple.html")

@app.get("/api")
async def api_root():
    return {"message": "LangGraph PDF Agent API is running!"}

@app.post("/api/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    try:
        response_data = {
            "response": "",
            "tool_calls": [],
            "processing_steps": [],
            "pdf_generated": False,
            "pdf_data": None,
            "pdf_filename": None,
            "conversation_ended": False
        }
        
        # Create proper HumanMessage object
        from langchain_core.messages import HumanMessage
        human_message = HumanMessage(content=request.message)
        
        # Process the message through the agent
        async for chunk in agent.astream({
            "messages": [human_message],
            "pdf_generated": False
        }):
            # Check for agent response
            if "agent" in chunk and chunk["agent"].get("messages"):
                latest_message = chunk["agent"]["messages"][-1]
                if hasattr(latest_message, 'content') and latest_message.content:
                    response_data["response"] = latest_message.content
            
            # Check for tool calls
            elif "action" in chunk and chunk["action"].get("messages"):
                for msg in chunk["action"]["messages"]:
                    if hasattr(msg, 'name'):
                        tool_call = {
                            "tool": msg.name,
                            "input": getattr(msg, 'args', {}),
                            "output": msg.content
                        }
                        response_data["tool_calls"].append(tool_call)
                        response_data["processing_steps"].append(f"Used {msg.name} tool")
                        
                        # Check if PDF was generated
                        if msg.name == "pdf_export" and hasattr(msg, 'content'):
                            try:
                                import json
                                pdf_result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                                if pdf_result.get("success"):
                                    response_data["pdf_generated"] = True
                                    response_data["pdf_data"] = pdf_result.get("pdf_base64")
                                    response_data["pdf_filename"] = pdf_result.get("filename")
                                    response_data["conversation_ended"] = True
                            except:
                                pass
            
            # Check if PDF was generated in state
            elif "check_pdf" in chunk:
                if chunk["check_pdf"].get("pdf_generated"):
                    response_data["pdf_generated"] = True
                    response_data["conversation_ended"] = True
        
        return MessageResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/download-pdf/{filename}")
async def download_pdf(filename: str, pdf_data: str):
    """Download generated PDF file"""
    try:
        # Decode base64 PDF data
        pdf_bytes = base64.b64decode(pdf_data)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading PDF: {str(e)}")

# Serve static files directly
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files directly"""
    static_file = os.path.join("static", file_path)
    if os.path.exists(static_file):
        return FileResponse(static_file)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Catch-all route for React Router
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
