#!/usr/bin/env python3
"""Test OpenAI API with base64 image (most reliable method)"""

import requests
import json
import base64
import io
from PIL import Image

BASE_URL = "http://localhost:18080/v1"

def create_test_image():
    """Create a simple test image in memory"""
    # Create a simple 100x100 red square
    img = Image.new('RGB', (100, 100), color='red')
    
    # Add some text or pattern to make it interesting
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill='blue')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64

def test_image_base64():
    """Test with base64 encoded image"""
    print("Creating test image...")
    
    try:
        img_base64 = create_test_image()
        print(f"✅ Created test image ({len(img_base64)} bytes base64)")
    except ImportError:
        print("⚠️  PIL not installed. Using placeholder.")
        print("   Install with: pip install pillow")
        # Create a minimal valid JPEG header for testing
        img_base64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
    
    print("\nTesting /v1/chat/completions with base64 image...")
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image briefly. What colors do you see?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }]
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print(f"✅ Success!")
        print(f"Response: {content}")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    return True

def test_simple_url():
    """Test with a simple, reliable public image URL"""
    print("\nTesting with public image URL...")
    
    # Use a real, accessible image URL
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": "gemini-3-flash",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image? Describe it briefly."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://brixzen.com/assets/front/images/slider-bg.jpg"
                        }
                    }
                ]
            }]
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print(f"✅ Success!")
        print(f"Response: {content[:200]}")
        return True
    else:
        print(f"⚠️  URL test failed (this is common): {response.text[:200]}")
        print("   Recommendation: Use base64 encoding for images")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("OpenAI API Image Test")
    print("=" * 70)
    print()
    
    # Test base64 (most reliable)
    base64_success = test_image_base64()
    
    print("\n" + "=" * 70)
    
    # Test URL (may fail due to network restrictions)
    url_success = test_simple_url()
    
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"Base64 image: {'✅ PASSED' if base64_success else '❌ FAILED'}")
    print(f"URL image:    {'✅ PASSED' if url_success else '⚠️  FAILED (expected)'}")
    print()
    print("💡 Recommendation: Always use base64 encoding for images")
    print("   It's more reliable and avoids URL access issues.")
    print()
