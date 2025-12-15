#!/usr/bin/env python3
"""
Entry point for running the Property AI Agent API server.
"""

import uvicorn
from ap_agent_api.infrastructure.api.main import app

def main():
    """Run the FastAPI server."""
    uvicorn.run(
        "ap_agent_api.infrastructure.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info"
    )

if __name__ == "__main__":
    main()