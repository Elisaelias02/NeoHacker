#!/bin/bash
# NeonSec Blog Production Startup Script

set -e

echo "🚀 Starting NeonSec Hacker Blog..."

# Set production environment
export ENV=production

# Create uploads directory if it doesn't exist
mkdir -p /app/uploads/{images,pdfs}

# Log environment info
echo "Environment: $ENV"
echo "MongoDB URI: ${MONGODB_URI:0:20}..."
echo "Backend URL: $BACKEND_URL"
echo "Upload Path: $UPLOAD_PATH"

# Start the FastAPI server
echo "Starting FastAPI server..."
cd /app/backend
python main.py