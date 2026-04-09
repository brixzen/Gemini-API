#!/bin/bash
# Show .env file contents

echo "============================================================"
echo "Checking .env File"
echo "============================================================"
echo ""

if [ -f ".env" ]; then
    echo "✅ .env file exists at: $(pwd)/.env"
    echo ""
    echo "Contents:"
    echo "------------------------------------------------------------"
    cat .env
    echo "------------------------------------------------------------"
    echo ""
    echo "File size: $(wc -c < .env) bytes"
    echo "Line count: $(wc -l < .env) lines"
else
    echo "❌ .env file does NOT exist at: $(pwd)/.env"
    echo ""
    echo "Creating .env file with cookies.json path..."
    
    if [ -f "cookies.json" ]; then
        cat > .env << EOF
# Gemini Authentication
GEMINI_COOKIES_JSON=$(pwd)/cookies.json

# Server Configuration
API_HOST=0.0.0.0
API_PORT=18789
LOG_LEVEL=INFO
EOF
        echo "✅ Created .env file"
        echo ""
        echo "Contents:"
        echo "------------------------------------------------------------"
        cat .env
        echo "------------------------------------------------------------"
    else
        echo "❌ cookies.json not found, cannot create .env"
    fi
fi

echo ""
echo "============================================================"
