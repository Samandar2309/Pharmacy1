#!/bin/bash
# Dorixona Frontend - Quick Start Script

echo "🚀 DORIXONA FRONTEND - QUICK START"
echo "=================================="
echo ""

# Check if running in correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Run this script from frontend_test directory"
    echo "   cd d:\Dorixona\frontend_test"
    exit 1
fi

echo "✅ Directory check passed"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install from https://nodejs.org"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Start dev server
echo "🌐 Starting Vite dev server..."
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔗 Backend: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
