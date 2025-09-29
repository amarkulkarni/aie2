#!/bin/bash
# Start script for LangGraph Agent Chat Application

echo "🚀 Starting LangGraph Agent Chat Application..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one with your API keys."
    echo "You can copy env_example.txt to .env and update it with your keys."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start the FastAPI server
echo "🔧 Starting FastAPI backend..."
cd backend
python main.py
