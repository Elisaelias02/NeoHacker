#!/usr/bin/env python3
"""
NeonSec Hacker Blog - Simple Production Entry Point
Minimal robust server for Kubernetes deployment
"""

import uvicorn
import os
import logging
import sys

# Configure minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", 8001))
        
        logger.info(f"Starting server on {host}:{port}")
        
        uvicorn.run(
            "server:app",
            host=host,
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)