#!/bin/bash
# Setup script for Conflux Community Member Tracker

set -e

echo "🚀 Setting up Conflux Community Member Tracker..."
echo ""

# Check Python version
echo "📦 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
echo "✅ Data directory created"
echo ""

echo "✅ Setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the dashboard: streamlit run app.py"
echo "  3. Click 'Collect Data Now' to gather initial data"
echo ""
echo "For automated collection:"
echo "  - Push to GitHub and enable Actions"
echo "  - See README.md for detailed instructions"
echo ""
