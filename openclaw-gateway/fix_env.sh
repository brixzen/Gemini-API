#!/bin/bash
# Script to fix .env configuration

echo "============================================================"
echo "Fixing .env Configuration"
echo "============================================================"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    echo ""
    echo "Current contents:"
    echo "------------------------------------------------------------"
    cat .env
    echo "------------------------------------------------------------"
    echo ""
else
    echo "❌ .env file does NOT exist"
    echo ""
fi

# Find cookies.json
COOKIES_PATH=""
if [ -f "cookies.json" ]; then
    COOKIES_PATH="$(pwd)/cookies.json"
elif [ -f "../cookies.json" ]; then
    COOKIES_PATH="$(cd .. && pwd)/cookies.json"
fi

if [ -n "$COOKIES_PATH" ]; then
    echo "✅ Found cookies.json at: $COOKIES_PATH"
    echo ""
    
    # Create or update .env
    if [ -f ".env" ]; then
        # Check if GEMINI_COOKIES_JSON already exists
        if grep -q "GEMINI_COOKIES_JSON" .env; then
            echo "Updating existing GEMINI_COOKIES_JSON in .env..."
            # Use sed to update the line (macOS and Linux compatible)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s|^GEMINI_COOKIES_JSON=.*|GEMINI_COOKIES_JSON=$COOKIES_PATH|" .env
            else
                sed -i "s|^GEMINI_COOKIES_JSON=.*|GEMINI_COOKIES_JSON=$COOKIES_PATH|" .env
            fi
        else
            echo "Adding GEMINI_COOKIES_JSON to .env..."
            echo "" >> .env
            echo "# Gemini Cookies JSON file" >> .env
            echo "GEMINI_COOKIES_JSON=$COOKIES_PATH" >> .env
        fi
    else
        echo "Creating new .env file..."
        cat > .env << EOF
# Gemini Authentication
# Option 1: Use cookies.json file
GEMINI_COOKIES_JSON=$COOKIES_PATH

# Option 2: Use individual cookies (comment out GEMINI_COOKIES_JSON above and uncomment below)
# GEMINI_SECURE_1PSID=your_cookie_value
# GEMINI_SECURE_1PSIDTS=your_cookie_value

# Server Configuration
API_HOST=0.0.0.0
API_PORT=18080
LOG_LEVEL=INFO
EOF
    fi
    
    echo "✅ .env file updated!"
    echo ""
    echo "New .env contents:"
    echo "------------------------------------------------------------"
    cat .env
    echo "------------------------------------------------------------"
    echo ""
else
    echo "❌ Could not find cookies.json file"
    echo ""
    echo "Please create cookies.json with your Gemini cookies:"
    echo '{'
    echo '  "__Secure-1PSID": "your_cookie_value",'
    echo '  "__Secure-1PSIDTS": "your_cookie_value"'
    echo '}'
    echo ""
fi

echo "============================================================"
echo "Next Steps:"
echo "============================================================"
echo "1. Verify .env file: cat .env"
echo "2. Test configuration: python check_cookies.py"
echo "3. Run server: python api_server.py"
echo ""
