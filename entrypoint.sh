#!/bin/bash
set -e

if [ "$RUN_MODE" = "test" ]; then
    echo "Running tests..."
    export PYTHONPATH=./app:./tests
    python -m pytest "$@"
else
    echo "Starting development server..."
    export PYTHONPATH=./app
    exec uvicorn main:http_api_app --host 0.0.0.0 --port 7086 "$@"
fi 
