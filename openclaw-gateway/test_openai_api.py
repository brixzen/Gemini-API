#!/usr/bin/env python3
"""Test OpenAI API compatibility"""

import requests
import json

BASE_URL = "http://localhost:18080/v1"

def test_models():
    """Test /v1/models endpoint"""
    print("Testing /v1/models...")
    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_chat_completion():
    """Test /v1/chat/completions endpoint"""
    print("Testing /v1/chat/completions...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in 5 words or less."}
            ]
        }
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_chat_streaming():
    """Test streaming chat completions"""
    print("Testing streaming...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [{"role": "user", "content": "Count from 1 to 5"}],
            "stream": True
        },
        stream=True
    )
    print(f"Status: {response.status_code}")
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = line_str[6:]
                if data != '[DONE]':
                    try:
                        chunk = json.loads(data)
                        if chunk['choices'][0]['delta'].get('content'):
                            print(chunk['choices'][0]['delta']['content'], end='', flush=True)
                    except:
                        pass
    print("\n")

def test_chat_with_image():
    """Test chat with image URL"""
    print("Testing chat with image...")
    # Use a more reliable image URL (GitHub raw content)
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image? Describe it briefly."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://raw.githubusercontent.com/googlesamples/mediapipe/main/examples/object_detection/android/app/src/main/assets/cat.jpg"
                        }
                    }
                ]
            }]
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['choices'][0]['message']['content'][:200]}...")
    else:
        print(f"Error: {response.text}")
        print("Note: Image URL tests may fail due to network restrictions or URL access issues.")
    print()

def test_legacy_completion():
    """Test legacy /v1/completions endpoint"""
    print("Testing /v1/completions (legacy)...")
    response = requests.post(
        f"{BASE_URL}/completions",
        json={
            "model": "gemini-3-flash",
            "prompt": "Say hello in 5 words",
            "max_tokens": 50
        }
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("OpenAI API Compatibility Tests")
    print("=" * 60)
    print()
    
    try:
        test_models()
        test_chat_completion()
        test_chat_streaming()
        
        # Skip image URL test by default (often fails due to network restrictions)
        print("⚠️  Skipping image URL test (use test_image_base64.py instead)")
        print()
        # test_chat_with_image()
        
        test_legacy_completion()
        
        print("=" * 60)
        print("✅ Core tests completed!")
        print("=" * 60)
        print()
        print("💡 To test images, run: python test_image_base64.py")
    except Exception as e:
        print(f"❌ Error: {e}")
