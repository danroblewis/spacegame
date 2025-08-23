#!/bin/bash

echo "🎭 Starting Jeremy Roast API Server... 🎭"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if requirements are installed
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please make sure you're in the correct directory."
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🚀 Starting server..."
echo "🌐 Server will be available at: http://localhost:8000"
echo "📚 API docs will be at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py
