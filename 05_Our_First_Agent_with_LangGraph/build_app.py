#!/usr/bin/env python3
"""
Build script for the LangGraph Agent Chat Application
This script builds the React frontend and prepares the backend for deployment
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result

def main():
    print("🚀 Building LangGraph Agent Chat Application...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    backend_dir = project_root / "backend"
    
    print(f"Project root: {project_root}")
    print(f"Frontend directory: {frontend_dir}")
    print(f"Backend directory: {backend_dir}")
    
    # Check if Node.js is installed
    print("\n📦 Checking Node.js installation...")
    try:
        run_command("node --version")
        run_command("npm --version")
    except:
        print("❌ Node.js is not installed. Please install Node.js first.")
        sys.exit(1)
    
    # Install frontend dependencies
    print("\n📦 Installing frontend dependencies...")
    if not (frontend_dir / "node_modules").exists():
        run_command("npm install", cwd=frontend_dir)
    else:
        print("Frontend dependencies already installed.")
    
    # Build the React app
    print("\n🔨 Building React frontend...")
    run_command("npm run build", cwd=frontend_dir)
    
    # Check if build was successful
    build_dir = frontend_dir / "build"
    if not build_dir.exists():
        print("❌ Frontend build failed. Build directory not found.")
        sys.exit(1)
    
    print("✅ Frontend build completed successfully!")
    
    # Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    run_command("pip install -r requirements.txt", cwd=backend_dir)
    
    # Create environment file if it doesn't exist
    env_file = project_root / ".env"
    if not env_file.exists():
        print("\n📝 Creating .env file template...")
        env_content = """# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Key (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: LangSmith API Key (for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=langgraph-agent-chat
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template. Please update it with your API keys.")
    
    # Create start script
    print("\n📝 Creating start script...")
    start_script = project_root / "start_app.sh"
    start_content = """#!/bin/bash
# Start script for LangGraph Agent Chat Application

echo "🚀 Starting LangGraph Agent Chat Application..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one with your API keys."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start the FastAPI server
echo "🔧 Starting FastAPI backend..."
cd backend
python main.py
"""
    
    with open(start_script, 'w') as f:
        f.write(start_content)
    
    # Make start script executable
    os.chmod(start_script, 0o755)
    
    # Create deployment documentation
    print("\n📚 Creating deployment documentation...")
    deployment_doc = project_root / "DEPLOYMENT.md"
    deployment_content = """# LangGraph Agent Chat - Deployment Guide

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start the application:**
   ```bash
   ./start_app.sh
   ```

3. **Access the application:**
   - Open your browser and go to `http://localhost:8000`
   - The React frontend will be served by the FastAPI backend

## Manual Setup

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup (Development)
```bash
cd frontend
npm install
npm start
```

### Frontend Build (Production)
```bash
cd frontend
npm install
npm run build
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=langgraph-agent-chat
```

## Features

- 🤖 **LangGraph Agent Integration**: Full LangGraph agent with tools
- 🔍 **Web Search**: Tavily search integration
- 📚 **ArXiv Search**: Academic paper search
- 📄 **PDF Export**: Generate and download conversation PDFs
- 💬 **Interactive Chat**: Real-time chat interface
- 🎯 **Suggested Prompts**: Pre-defined prompts for easy testing
- 📱 **Responsive Design**: Works on desktop and mobile

## API Endpoints

- `GET /` - Serve React frontend
- `GET /api/suggested-prompts` - Get suggested prompts
- `POST /api/chat` - Chat with the agent
- `GET /api/health` - Health check

## Troubleshooting

1. **ModuleNotFoundError**: Make sure all dependencies are installed
2. **API Key Errors**: Check your .env file has correct API keys
3. **Frontend not loading**: Run `npm run build` in the frontend directory
4. **Port conflicts**: Change the port in backend/main.py if 8000 is occupied

## Development

For development, you can run the frontend and backend separately:

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

The frontend will proxy API requests to the backend automatically.
"""
    
    with open(deployment_doc, 'w') as f:
        f.write(deployment_content)
    
    print("\n✅ Build completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your API keys")
    print("2. Run: ./start_app.sh")
    print("3. Open: http://localhost:8000")
    print("\n📚 See DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main()
