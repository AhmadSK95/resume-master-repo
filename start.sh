#!/bin/bash

echo "🤖 Starting AI Resume Matcher..."
echo ""

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend not set up. Run ./setup.sh first!"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Run ./setup.sh first!"
    exit 1
fi

# Start backend in background
echo "🐍 Starting backend on port 5001..."
./start_backend.sh > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 3

# Check if backend started
if ! curl -s http://localhost:5001/api/health > /dev/null; then
    echo "❌ Backend failed to start. Check backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "✅ Backend running"

# Start frontend in background
echo ""
echo "⚛️  Starting frontend on port 3001..."
./start_frontend.sh > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
sleep 5

echo ""
echo "=========================================="
echo "✅ Application Started Successfully!"
echo "=========================================="
echo ""
echo "📊 Backend:  http://localhost:5001"
echo "🌐 Frontend: http://localhost:3001"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Keep script running and handle Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for both processes
wait
