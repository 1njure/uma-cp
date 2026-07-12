#!/bin/bash
set -e

# Change directory to the script's directory
cd "$(dirname "$0")"

echo "============================================="
echo "🏇 Umamusume Completionist Planner Launcher"
echo "============================================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH."
    echo "Please install Python 3.10+ to run this application."
    exit 1
fi

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
    
    echo "📥 Installing dependencies from requirements.txt..."
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
else
    # Quick check/sync of dependencies
    echo "🔄 Checking dependencies..."
    .venv/bin/pip install -r requirements.txt --quiet
fi

echo "🚀 Starting Streamlit application..."
.venv/bin/streamlit run app.py
