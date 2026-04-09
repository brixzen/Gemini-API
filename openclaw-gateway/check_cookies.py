#!/usr/bin/env python3
"""
Check cookies.json configuration
"""

import os
import json
from pathlib import Path

# Load .env file first
try:
    from dotenv import load_dotenv
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print(f"📄 Loaded .env from: {env_file}")
    else:
        print(f"⚠️  No .env file found at: {env_file}")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")

print("=" * 60)
print("Cookies Configuration Check")
print("=" * 60)
print()

# Check environment variables
print("Environment Variables:")
print("-" * 60)
psid = os.getenv("GEMINI_SECURE_1PSID", "")
psidts = os.getenv("GEMINI_SECURE_1PSIDTS", "")
cookies_json = os.getenv("GEMINI_COOKIES_JSON", "")

if psid:
    print(f"✅ GEMINI_SECURE_1PSID: {psid[:15]}... (length: {len(psid)})")
else:
    print("❌ GEMINI_SECURE_1PSID: NOT SET")

if psidts:
    print(f"✅ GEMINI_SECURE_1PSIDTS: {psidts[:15]}... (length: {len(psidts)})")
else:
    print("❌ GEMINI_SECURE_1PSIDTS: NOT SET")

if cookies_json:
    print(f"✅ GEMINI_COOKIES_JSON: {cookies_json}")
else:
    print("❌ GEMINI_COOKIES_JSON: NOT SET")

print("-" * 60)
print()

# Check for cookies.json file
print("Looking for cookies.json file:")
print("-" * 60)

possible_locations = [
    Path.cwd() / "cookies.json",
    Path.cwd() / ".." / "cookies.json",
    Path.home() / "Gemini-API" / "cookies.json",
    Path.home() / "Gemini-API" / "openclaw-gateway" / "cookies.json",
]

found_files = []
for location in possible_locations:
    if location.exists():
        print(f"✅ Found: {location}")
        found_files.append(location)
    else:
        print(f"❌ Not found: {location}")

print("-" * 60)
print()

# If cookies.json path is set, check if it exists and is valid
if cookies_json:
    cookies_path = Path(cookies_json)
    print(f"Checking configured cookies.json path:")
    print(f"Path: {cookies_path}")
    print(f"Exists: {cookies_path.exists()}")
    print(f"Is file: {cookies_path.is_file() if cookies_path.exists() else 'N/A'}")
    print()
    
    if cookies_path.exists():
        try:
            with open(cookies_path, 'r') as f:
                cookies_data = json.load(f)
            
            print("✅ cookies.json is valid JSON")
            print(f"Keys in file: {list(cookies_data.keys())}")
            
            # Check for required cookies
            required_cookies = ["__Secure-1PSID", "__Secure-1PSIDTS"]
            for cookie in required_cookies:
                if cookie in cookies_data:
                    value = cookies_data[cookie]
                    print(f"✅ {cookie}: {value[:15]}... (length: {len(value)})")
                else:
                    print(f"❌ {cookie}: MISSING")
        except json.JSONDecodeError as e:
            print(f"❌ cookies.json is NOT valid JSON: {e}")
        except Exception as e:
            print(f"❌ Error reading cookies.json: {e}")
    else:
        print("❌ Configured cookies.json file does not exist!")
    print()

# Recommendations
print("=" * 60)
print("Recommendations:")
print("=" * 60)

if psid and psidts:
    print("✅ You have GEMINI_SECURE_1PSID and GEMINI_SECURE_1PSIDTS set")
    print("   The server should work with these credentials")
elif cookies_json and Path(cookies_json).exists():
    print("✅ You have GEMINI_COOKIES_JSON set and file exists")
    print("   The server should work with this cookies file")
elif found_files:
    print("⚠️  Found cookies.json file(s) but GEMINI_COOKIES_JSON not set")
    print()
    print("Add this to your .env file:")
    for f in found_files:
        print(f"GEMINI_COOKIES_JSON={f.absolute()}")
    print()
else:
    print("❌ No credentials found!")
    print()
    print("Option 1: Set individual cookies in .env:")
    print("GEMINI_SECURE_1PSID=your_cookie_value")
    print("GEMINI_SECURE_1PSIDTS=your_cookie_value")
    print()
    print("Option 2: Set cookies.json path in .env:")
    print("GEMINI_COOKIES_JSON=/full/path/to/cookies.json")

print()
print("=" * 60)
