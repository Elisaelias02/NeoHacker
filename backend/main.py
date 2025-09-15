#!/usr/bin/env python3
"""
NeonSec Hacker Blog - Production Entry Point
Optimized for Kubernetes deployment with proper health checks
"""

import uvicorn
import os
import logging
from server import app

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Production configuration
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8001))
    
    logger.info(f"Starting NeonSec API server on {host}:{port}")
    logger.info(f"Environment: {os.environ.get('ENV', 'development')}")
    
    # Run with production-ready settings
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        workers=1,  # Single worker for container deployment
        log_level="info",
        access_log=True,
        reload=False,
        loop="asyncio"
    )