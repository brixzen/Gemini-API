#!/usr/bin/env python3
"""
Debug script to check .env file loading
"""

import os
from pathlib import Path

print("=" * 60)
print("Environment Configuration Check")
print("=" * 60)
print()

# Check current directory
print(f"Current directory: {Path.cwd()}")
print()

# Check for .env file
env_file = Path.cwd() / ".env"
print(f"Looking for .env at: {env_file}")
print(f".env exists: {env_file.exists()}")
print()

if env_file.exists():
    print("Contents of .env file:")
    print("-" * 60)
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Mask sensitive values
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'PSID' in key or 'TOKEN' in key:
                        masked = value[:10] + '...' if len(value) > 10 else '***'
                        print(f"{key}={masked}")
                    else:
                        print(line)
    print("-" * 60)
    print()

# Try loading with dotenv
print("Testing python-dotenv:")
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv is installed")
    
    result = load_dotenv(env_file, override=True)
    print(f"load_dotenv() returned: {result}")
    print()
except ImportError:
    print("❌ python-dotenv is NOT installed")
    print("   Run: pip install python-dotenv")
    print()

# Check environment variables
print("Environment variables after loading:")
print("-" * 60)
psid = os.getenv("GEMINI_SECURE_1PSID", "")
psidts = os.getenv("GEMINI_SECURE_1PSIDTS", "")
cookies_json = os.getenv("GEMINI_COOKIES_JSON", "")

if psid:
    print(f"GEMINI_SECURE_1PSID: {psid[:10]}... (length: {len(psid)})")
else:
    print("GEMINI_SECURE_1PSID: NOT SET ❌")

if psidts:
    print(f"GEMINI_SECURE_1PSIDTS: {psidts[:10]}... (length: {len(psidts)})")
else:
    print("GEMINI_SECURE_1PSIDTS: NOT SET ❌")

if cookies_json:
    print(f"GEMINI_COOKIES_JSON: {cookies_json}")
else:
    print("GEMINI_COOKIES_JSON: NOT SET")

print("-" * 60)
print()

# Final verdict
if psid and psidts:
    print("✅ Gemini credentials are loaded!")
elif cookies_json:
    print("✅ Gemini cookies JSON path is set!")
else:
    print("❌ No Gemini credentials found!")
    print()
    print("Please check:")
    print("1. .env file exists in current directory")
    print("2. .env file contains GEMINI_SECURE_1PSID and GEMINI_SECURE_1PSIDTS")
    print("3. No quotes around values in .env file")
    print("4. No spaces around = sign")
    print()
    print("Example .env format:")
    print("GEMINI_SECURE_1PSID=g.a000abcdef123456...")
    print("GEMINI_SECURE_1PSIDTS=sidts-abcdef123456...")

print()
print("=" * 60)
