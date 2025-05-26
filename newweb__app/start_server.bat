@echo off
chcp 65001 > nul
echo ============================================
echo Starting Tag Management System...
echo ============================================

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Some dependencies may not have been installed correctly
)

REM Start the Flask application
echo Starting Flask application...
python app.py

REM Keep the window open if there's an error
if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%
    pause
) 