@echo off
echo 🚀 Starting Student Marketplace Admin Panel...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully!

echo 🌐 Starting development server...
echo 📍 Admin panel will be available at: http://localhost:3001
echo 🔗 Backend API should be running at: http://localhost:8000
echo.
echo 📋 Demo Credentials:
echo    Email: admin@university.edu
echo    Password: admin123
echo.

npm run dev
