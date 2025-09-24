#!/bin/bash

echo "🚀 Starting Student Marketplace Admin Panel..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully!"

echo "🌐 Starting development server..."
echo "📍 Admin panel will be available at: http://localhost:3001"
echo "🔗 Backend API should be running at: http://localhost:8000"
echo ""
echo "📋 Demo Credentials:"
echo "   Email: admin@university.edu"
echo "   Password: admin123"
echo ""

npm run dev
