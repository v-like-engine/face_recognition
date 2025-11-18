#!/bin/bash
# Quick start script for Face Recognition API

echo "================================================"
echo "  Face Recognition API - Quick Start"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads known_faces logs static

# Check if .env exists, if not create from example
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
    fi
fi

# Display camera test
echo ""
echo "Testing camera availability..."
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✓ Camera detected and accessible' if cap.isOpened() else '✗ Camera not found or not accessible'); cap.release()"

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Starting Face Recognition API..."
echo ""
echo "Access points:"
echo "  • Testing Stand: http://localhost:8000/testing-stand"
echo "  • API Docs:      http://localhost:8000/docs"
echo "  • Health Check:  http://localhost:8000/api/v1/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python main.py
