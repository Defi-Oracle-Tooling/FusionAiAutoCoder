#!/bin/bash
set -e

# Initialize environment
echo "Initializing FusionAiAutoCoder environment..."

# Setup log directory
mkdir -p /app/logs

# Check if running in development mode
if [ "$1" = "dev" ]; then
    echo "Starting in development mode..."
    # Start code-server if available
    if command -v code-server &> /dev/null; then
        echo "Starting VS Code server..."
        exec code-server --bind-addr 0.0.0.0:8000 --auth none /app
    else
        echo "VS Code server not installed. Run with INSTALL_CODE_SERVER=true build argument."
        exit 1
    fi
fi

# Check if running tests
if [ "$1" = "test" ]; then
    echo "Running tests..."
    exec pytest /app/tests "$@"
fi

# Check if running API server specifically
if [ "$1" = "api" ]; then
    echo "Starting API server..."
    shift
    exec python -m uvicorn src.api:app --host 0.0.0.0 --port "${PORT:-8080}" "$@"
fi

# Check for initialization tasks
if [ "$1" = "init" ]; then
    echo "Running initialization tasks..."
    # Add any initialization tasks here
    exit 0
fi

# Check for help command
if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "FusionAiAutoCoder Docker Container"
    echo "Usage: docker run [docker-options] fusionaicoder:[tag] [command]"
    echo ""
    echo "Commands:"
    echo "  dev             Start in development mode with VS Code server"
    echo "  test            Run tests"
    echo "  api             Start the API server"
    echo "  init            Run initialization tasks"
    echo "  help            Show this help message"
    echo ""
    echo "If no command is provided, the container starts the API server by default."
    exit 0
fi

# Setup environment variables for GPU if available
if [ -f /proc/driver/nvidia/version ]; then
    echo "NVIDIA GPU detected"
    export ENABLE_GPU_ACCELERATION=true
else
    echo "No NVIDIA GPU detected"
    export ENABLE_GPU_ACCELERATION=false
fi

# Default: execute the command passed to docker
if [ "$1" ]; then
    exec "$@"
else
    echo "Starting API server in production mode..."
    exec python -m uvicorn src.api:app --host 0.0.0.0 --port "${PORT:-8080}"
fi