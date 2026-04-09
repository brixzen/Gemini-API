#!/bin/bash
# Test if server can start without errors

echo "Testing server startup..."
echo ""

cd "$(dirname "$0")"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ No venv found. Run ./install.sh first"
    exit 1
fi

# Test imports
echo ""
echo "Testing imports..."
python3 -c "
from models import ResponseRequest, ChatCompletionRequest
from handlers import OpenAIAdapter
print('✅ All imports successful!')
" || {
    echo "❌ Import test failed"
    exit 1
}

# Test server can be imported
echo ""
echo "Testing server module..."
python3 -c "
import api_server
print('✅ Server module loads successfully!')
" || {
    echo "❌ Server module failed to load"
    exit 1
}

echo ""
echo "=" * 60
echo "✅ All tests passed! Server should start correctly."
echo "=" * 60
echo ""
echo "To start the server:"
echo "  python api_server.py"
