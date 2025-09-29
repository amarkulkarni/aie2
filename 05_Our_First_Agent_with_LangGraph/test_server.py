#!/usr/bin/env python3
"""
Simple test server to verify static file serving works
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("backend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

