#!/bin/bash
# Quick test script for basic functionality

BASE_URL="http://localhost:18080"

echo "Testing Gemini-OpenClaw Gateway"
echo "================================"
echo ""

# Test 1: Health check
echo "1. Health Check"
curl -s $BASE_URL/health | jq '.'
echo ""

# Test 2: List models
echo "2. List Models"
curl -s $BASE_URL/v1/models | jq '.data[0:3]'
echo ""

# Test 3: Simple chat (no images)
echo "3. Simple Chat Completion"
curl -s -X POST $BASE_URL/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [
      {"role": "user", "content": "Say hello in exactly 3 words"}
    ]
  }' | jq '.'
echo ""

# Test 4: With system message
echo "4. Chat with System Message"
curl -s -X POST $BASE_URL/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is 2+2?"}
    ]
  }' | jq '.choices[0].message.content'
echo ""

echo "================================"
echo "Tests complete!"
