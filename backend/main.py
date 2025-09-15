#!/usr/bin/env python3
"""
NeonSec Hacker Blog - Production Entry Point
Optimized for Kubernetes deployment with proper health checks and error handling
"""

import uvicorn
import os
import sys
import logging
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

def test_imports():
    """Test all imports before starting server"""
    try:
        logger.info("Testing imports...")
        from server import app
        logger.info("✅ All imports successful")
        return app
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Failed to import server module")
        sys.exit(1)

async def test_health_endpoint(app):
    """Test health endpoint before starting server"""
    try:
        logger.info("Testing health endpoint...")
        from server import db
        
        # Test database connection
        await db.command("ping")
        logger.info("✅ Database connection successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def main():
    try:
        # Test imports first
        app = test_imports()
        
        # Production configuration
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", 8001))
        
        logger.info(f"🚀 Starting NeonSec API server on {host}:{port}")
        logger.info(f"Environment: {os.environ.get('ENV', 'development')}")
        logger.info(f"MongoDB URL: {os.environ.get('MONGO_URL', 'Not set')[:50]}...")
        logger.info(f"DB Name: {os.environ.get('DB_NAME', 'Not set')}")
        
        # Test health endpoint in background
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            health_ok = loop.run_until_complete(test_health_endpoint(app))
            loop.close()
            
            if not health_ok:
                logger.warning("⚠️  Health check failed, but starting server anyway")
        except Exception as e:
            logger.warning(f"⚠️  Could not test health endpoint: {e}")
        
        # Run with production-ready settings
        uvicorn.run(
            app,  # Pass app directly instead of string
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False,
            loop="asyncio"
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Fatal error starting server: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()