#!/bin/bash
# Run script for Gemini-OpenClaw Gateway
# Automatically activates virtual environment and starts the server

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./install.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your Gemini cookies"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run the server
echo "Starting Gemini-OpenClaw Gateway..."
echo ""
python api_server.py "$@"
