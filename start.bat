@echo off
REM Quick start script for Face Recognition API (Windows)

echo ================================================
echo   Face Recognition API - Quick Start
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "uploads\" mkdir uploads
if not exist "known_faces\" mkdir known_faces
if not exist "logs\" mkdir logs
if not exist "static\" mkdir static

REM Check if .env exists, if not create from example
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env file from .env.example...
        copy .env.example .env
    )
)

REM Display camera test
echo.
echo Testing camera availability...
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera detected and accessible' if cap.isOpened() else 'Camera not found or not accessible'); cap.release()"

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Starting Face Recognition API...
echo.
echo Access points:
echo   - Testing Stand: http://localhost:8000/testing-stand
echo   - API Docs:      http://localhost:8000/docs
echo   - Health Check:  http://localhost:8000/api/v1/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python main.py
