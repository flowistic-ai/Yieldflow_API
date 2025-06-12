#!/bin/bash

# Production startup script for Render

echo "🚀 Starting Yieldflow API production deployment..."

# Set production environment
export PYTHONPATH="${PYTHONPATH}:${PWD}"
export ENVIRONMENT="production"

# Create logs directory if it doesn't exist
mkdir -p logs

# Initialize database tables (if needed)
echo "📦 Initializing database..."
python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
print('✅ Database initialized successfully')
"

# Start the server with uvicorn (production-ready)
echo "🌐 Starting Yieldflow API server on port ${PORT:-10000}..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-10000} \
    --workers ${WORKERS:-1} \
    --log-level info \
    --access-log \
    --no-use-colors 