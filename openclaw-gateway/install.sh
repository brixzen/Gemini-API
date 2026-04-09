#!/bin/bash
# Installation script for Gemini-OpenClaw Gateway

set -e

echo "========================================="
echo "Gemini-OpenClaw Gateway Installation"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ Error: Python 3.10 or higher is required"
    echo "   Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
else
    echo "✅ Virtual environment already exists"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install parent project dependencies
echo "Installing parent Gemini-API dependencies..."
if [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
    echo "✅ Parent dependencies installed"
else
    echo "⚠️  Warning: Parent requirements.txt not found, skipping..."
fi
echo ""

# Install gateway dependencies
echo "Installing gateway dependencies..."
pip install -r requirements.txt
echo "✅ Gateway dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Gemini cookies:"
    echo "   - GEMINI_SECURE_1PSID"
    echo "   - GEMINI_SECURE_1PSIDTS"
    echo ""
    echo "   Get these from gemini.google.com (F12 > Network > Cookie)"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Create temp directory
echo "Creating temp directory..."
mkdir -p /tmp/gemini-gateway
echo "✅ Temp directory created"
echo ""

echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini cookies:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the server:"
echo "   python api_server.py"
echo ""
echo "4. Test the server:"
echo "   curl http://localhost:18789/health"
echo ""
echo "For more information, see:"
echo "- QUICKSTART.md - Quick start guide"
echo "- README.md - Full documentation"
echo "- EXAMPLES.md - Usage examples"
echo ""
echo "💡 Tip: To deactivate the virtual environment later, run: deactivate"
echo ""
