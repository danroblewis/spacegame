#!/bin/bash

# Simple SpaceTraders GUI Development Script
# Starts server, monitors for changes, restarts when code updates

echo "🚀 Starting SpaceTraders GUI development mode..."

# Pull latest code from main branch
echo "📥 Pulling latest code from main branch..."
git pull origin main

# Check if .env exists, create demo if not
if [ ! -f .env ]; then
    echo "📝 Creating demo .env file..."
    echo "SPACETRADERS_TOKEN=demo_token_for_testing" > .env
    echo "SPACETRADERS_CALLSIGN=DEMO_AGENT" >> .env
fi

# Function to start server
start_server() {
    echo "🔧 Starting server..."
    
    # Start backend
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Server started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
}

# Function to stop server
stop_server() {
    echo "🛑 Stopping server..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
}

# Function to restart server
restart_server() {
    echo "🔄 Restarting server..."
    stop_server
    sleep 2
    start_server
}

# Cleanup on exit
trap 'echo "🛑 Shutting down..."; stop_server; exit' INT TERM

# Start server initially
start_server

echo "🔍 Monitoring for code changes... (Press Ctrl+C to stop)"
echo ""

# Main loop - check for git changes every 30 seconds
while true; do
    sleep 30
    
    # Fetch latest changes
    git fetch origin main >/dev/null 2>&1
    
    # Check if there are new commits
    if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
        echo "📥 Code changes detected! Pulling and restarting..."
        git pull origin main
        restart_server
        echo "✅ Server restarted with latest code!"
    fi
done
