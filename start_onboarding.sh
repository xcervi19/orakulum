#!/bin/bash

# Orakulum Onboarding Startup Script
# Starts both the API server and a local web server for the frontend

echo "=============================================="
echo "🔮 ORAKULUM ONBOARDING"
echo "=============================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ✅ Created .env file"
    echo "   ⚠️  Please edit .env with your credentials before continuing"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Check if Python dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "   Installing dependencies..."
    pip install -r requirements.txt
fi

# Start API server in background
echo ""
echo "🚀 Starting API server..."
python3 api_onboarding.py &
API_PID=$!
echo "   API PID: $API_PID"
echo "   API running on http://localhost:5000"

# Wait for API to start
sleep 2

# Check if API is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "   ✅ API is healthy"
else
    echo "   ❌ API health check failed"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Start frontend server
echo ""
echo "🌐 Starting frontend server..."
echo "   Frontend running on http://localhost:8000"
echo ""
echo "=============================================="
echo "✅ Onboarding is ready!"
echo "=============================================="
echo ""
echo "📱 Open in browser: http://localhost:8000/onboarding_demo.html"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Trap Ctrl+C to kill all processes
trap "echo ''; echo 'Stopping servers...'; kill $API_PID 2>/dev/null; exit" INT

# Start frontend server (this will block)
python3 -m http.server 8000

# If we get here, user stopped the frontend server
kill $API_PID 2>/dev/null
echo "✅ Servers stopped"
