#!/usr/bin/env python3
"""
Omnara Webhook Server for Render.com deployment
"""
import os
import json
import hmac
import hashlib
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Omnara Webhook Server", version="1.0.0")

# Add CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://omnara.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key from environment or default
API_KEY = os.environ.get("OMNARA_API_KEY", "B7hVKeNKPcVIL0lk")

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "service": "Omnara Webhook Server",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook",
            "agents": "/api/agents"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/webhook")
async def webhook_handler(request: Request, x_api_key: str = Header(None)):
    """Handle incoming webhooks"""
    # Verify API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        payload = await request.json()
        action = payload.get("action", "unknown")
        data = payload.get("data", {})
        
        logger.info(f"Webhook received: action={action}")
        
        # Process different webhook actions
        if action == "create_agent":
            return await create_agent(data)
        elif action == "deploy":
            return await handle_deploy(data)
        elif action == "code_review":
            return await handle_code_review(data)
        else:
            return {"status": "success", "message": f"Action '{action}' received"}
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents")
async def create_agent(data: dict = None):
    """Create a new agent instance"""
    if not data:
        data = {}
    
    agent_id = f"agent_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "status": "success",
        "agent_id": agent_id,
        "message": "Agent created successfully",
        "config": data
    }

@app.get("/api/agents")
async def list_agents():
    """List all agent instances"""
    return {
        "status": "success",
        "agents": [
            {"id": "agent_1", "status": "running", "created": "2024-01-01"},
            {"id": "agent_2", "status": "stopped", "created": "2024-01-02"}
        ]
    }

async def handle_deploy(data: dict):
    """Handle deployment webhook"""
    environment = data.get("environment", "production")
    version = data.get("version", "latest")
    
    logger.info(f"Deploying version {version} to {environment}")
    
    return {
        "status": "success",
        "message": f"Deployment initiated",
        "environment": environment,
        "version": version
    }

async def handle_code_review(data: dict):
    """Handle code review webhook"""
    repository = data.get("repository", "unknown")
    branch = data.get("branch", "main")
    
    logger.info(f"Code review for {repository}:{branch}")
    
    return {
        "status": "success",
        "message": "Code review initiated",
        "repository": repository,
        "branch": branch
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)