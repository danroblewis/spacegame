#!/bin/bash

echo "🚀 Installing SpaceTraders GUI..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

cd ..

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Create a .env file with your SpaceTraders credentials:"
echo "   SPACETRADERS_TOKEN=your_token_here"
echo "   SPACETRADERS_CALLSIGN=your_callsign_here"
echo ""
echo "2. Run the application:"
echo "   ./start.sh"
echo ""
echo "3. Open your browser to:"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000"
