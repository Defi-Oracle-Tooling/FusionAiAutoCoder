#!/bin/bash
# Script to set up the development environment for FusionAiAutoCoder

set -e

echo "Setting up development environment for FusionAiAutoCoder..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.template" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please update the .env file with your credentials."
fi

# Create logs directory
if [ ! -d "logs" ]; then
    echo "Creating logs directory..."
    mkdir -p logs
fi

echo "Setup complete! Activate the virtual environment with:"
echo "  source venv/bin/activate"