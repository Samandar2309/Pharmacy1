@echo off
REM Dorixona Frontend - Quick Start Script (Windows)

echo.
echo ========================================
echo DORIXONA FRONTEND - QUICK START (WINDOWS)
echo ========================================
echo.

REM Check if running in correct directory
if not exist "package.json" (
    echo Error: Run this script from frontend_test directory
    echo   cd d:\Dorixona\frontend_test
    pause
    exit /b 1
)

echo OK Directory check passed
echo.

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo OK Node.js found: %NODE_VERSION%
echo.

REM Install dependencies
echo Installing dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo Error: npm install failed
    pause
    exit /b 1
)

echo OK Dependencies installed
echo.

REM Start dev server
echo Starting Vite dev server...
echo.
echo Mobile: http://localhost:3000
echo Backend: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev
