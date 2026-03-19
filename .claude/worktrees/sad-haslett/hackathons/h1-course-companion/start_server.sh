#!/bin/bash
# Startup script for Course Companion API

echo "Starting Course Companion API..."

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Start the API server
echo "Starting API server on http://localhost:8000"
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload