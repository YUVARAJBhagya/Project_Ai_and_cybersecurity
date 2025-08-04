#!/bin/bash

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A a4s_eval.celery_worker worker --loglevel=debug --concurrency=1 --hostname=worker@%h &

# Wait a moment for worker to start
sleep 10

# Check if worker started successfully using ps instead of pgrep
if ps aux | grep "celery.*worker" | grep -v grep > /dev/null; then
    echo "Celery worker started successfully"
    ps aux | grep "celery.*worker" | grep -v grep
else
    echo "ERROR: Celery worker failed to start"
    echo "Checking for any Celery processes:"
    ps aux | grep celery
fi

# Start FastAPI server
echo "Starting FastAPI server..."
uvicorn a4s_eval.main:app --host 0.0.0.0 --port 8001 