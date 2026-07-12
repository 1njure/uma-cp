@echo off
title Umamusume Completionist Planner
echo =============================================
echo 🏇 Umamusume Completionist Planner Launcher
echo =============================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: python is not installed or not in PATH.
    echo Please install Python 3.10+ to run this application.
    pause
    exit /b 1
)

:: Create virtual environment if it does not exist
if not exist .venv (
    echo 📦 Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo 📥 Installing dependencies from requirements.txt...
    .venv\Scripts\pip install --upgrade pip
    .venv\Scripts\pip install -r requirements.txt
) else (
    echo 🔄 Checking dependencies...
    .venv\Scripts\pip install -r requirements.txt --quiet
)

echo 🚀 Starting Streamlit application...
.venv\Scripts\streamlit run app.py
pause
