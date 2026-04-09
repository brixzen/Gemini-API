#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

print("Testing imports...")
print()

try:
    print("1. Testing gemini_webapi imports...")
    from gemini_webapi import GeminiClient, logger, set_log_level
    from gemini_webapi.exceptions import AuthError, GeminiError
    from gemini_webapi.constants import Model
    print("   ✅ gemini_webapi imports successful")
except ImportError as e:
    print(f"   ❌ gemini_webapi import failed: {e}")
    sys.exit(1)

try:
    print("2. Testing config import...")
    from config import config
    print("   ✅ config import successful")
except ImportError as e:
    print(f"   ❌ config import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing models imports...")
    from models import ResponseRequest
    print("   ✅ models import successful")
except ImportError as e:
    print(f"   ❌ models import failed: {e}")
    sys.exit(1)

try:
    print("4. Testing handlers imports...")
    from handlers import InputProcessor, ModelRouter, SessionManager, OutputHandler
    print("   ✅ handlers import successful")
except ImportError as e:
    print(f"   ❌ handlers import failed: {e}")
    sys.exit(1)

try:
    print("5. Testing FastAPI imports...")
    from fastapi import FastAPI
    import uvicorn
    print("   ✅ FastAPI imports successful")
except ImportError as e:
    print(f"   ❌ FastAPI import failed: {e}")
    sys.exit(1)

print()
print("=" * 50)
print("✅ All imports successful!")
print("=" * 50)
print()
print("You can now run the server:")
print("  python api_server.py")
print()
