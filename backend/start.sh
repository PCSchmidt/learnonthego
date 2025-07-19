#!/bin/bash
echo "Starting LearnOnTheGo backend..."
echo "PORT environment variable: $PORT"
echo "Using port: ${PORT:-8000}"

# Start uvicorn with the correct port
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
