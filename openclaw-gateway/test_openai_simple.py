#!/usr/bin/env python3
"""Simple OpenAI API tests without external dependencies"""

import requests
import json

BASE_URL = "http://localhost:18080/v1"

def test_models():
    """Test /v1/models endpoint"""
    print("✅ Testing /v1/models...")
    response = requests.get(f"{BASE_URL}/models")
    assert response.status_code == 200, f"Failed: {response.status_code}"
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    print(f"   Found {len(data['data'])} models")

def test_simple_chat():
    """Test simple chat completion"""
    print("✅ Testing /v1/chat/completions (simple)...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [
                {"role": "user", "content": "Say 'Hello World' and nothing else"}
            ]
        }
    )
    assert response.status_code == 200, f"Failed: {response.status_code} - {response.text}"
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    content = data["choices"][0]["message"]["content"]
    print(f"   Response: {content[:100]}")

def test_system_message():
    """Test with system message"""
    print("✅ Testing with system message...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [
                {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
                {"role": "user", "content": "Hello"}
            ]
        }
    )
    assert response.status_code == 200, f"Failed: {response.status_code}"
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"   Response: {content[:100]}")

def test_streaming():
    """Test streaming"""
    print("✅ Testing streaming...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [{"role": "user", "content": "Count from 1 to 3"}],
            "stream": True
        },
        stream=True
    )
    assert response.status_code == 200, f"Failed: {response.status_code}"
    
    chunks = 0
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = line_str[6:]
                if data != '[DONE]':
                    chunks += 1
    
    print(f"   Received {chunks} chunks")
    assert chunks > 0, "No chunks received"

def test_legacy_completion():
    """Test legacy completions endpoint"""
    print("✅ Testing /v1/completions (legacy)...")
    response = requests.post(
        f"{BASE_URL}/completions",
        json={
            "model": "gemini-3-flash",
            "prompt": "Say hello",
            "max_tokens": 50
        }
    )
    assert response.status_code == 200, f"Failed: {response.status_code}"
    data = response.json()
    assert "choices" in data
    print(f"   Response: {data['choices'][0]['text'][:100]}")

def test_temperature():
    """Test with temperature parameter"""
    print("✅ Testing with temperature...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [{"role": "user", "content": "Say hi"}],
            "temperature": 0.5
        }
    )
    assert response.status_code == 200, f"Failed: {response.status_code}"
    print("   Temperature parameter accepted")

if __name__ == "__main__":
    print("=" * 60)
    print("OpenAI API Simple Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_models,
        test_simple_chat,
        test_system_message,
        test_streaming,
        test_legacy_completion,
        test_temperature
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
        exit(1)
