# OpenAI API Compatibility

The Gemini-OpenClaw Gateway provides full OpenAI API compatibility, allowing you to use it as a drop-in replacement for OpenAI's API with any compatible client library.

## Supported Endpoints

### ✅ Chat Completions
```
POST /v1/chat/completions
```

Full support for OpenAI's chat completions API including:
- Multi-turn conversations
- System/user/assistant roles
- Streaming responses
- Multi-modal inputs (text + images)
- Temperature and sampling parameters

### ✅ Completions (Legacy)
```
POST /v1/completions
```

Legacy text completion endpoint for backward compatibility.

### ✅ Models List
```
GET /v1/models
```

List all available Gemini models in OpenAI format.

## Quick Start

### Using OpenAI Python SDK

```python
from openai import OpenAI

# Point to your gateway
client = OpenAI(
    base_url="http://localhost:18080/v1",
    api_key="your-api-key"  # Optional if you set API_BEARER_TOKEN
)

# Chat completion
response = client.chat.completions.create(
    model="gemini-3-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

### Streaming

```python
stream = client.chat.completions.create(
    model="gemini-3-flash",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Multi-modal (Images)

```python
response = client.chat.completions.create(
    model="gemini-3-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ]
)
```

### Base64 Images

```python
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="gemini-3-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)
```

## Using with LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:18080/v1",
    api_key="your-api-key",
    model="gemini-3-flash"
)

response = llm.invoke("What is the meaning of life?")
print(response.content)
```

## Using with LlamaIndex

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    api_base="http://localhost:18080/v1",
    api_key="your-api-key",
    model="gemini-3-flash"
)

response = llm.complete("Explain quantum computing")
print(response.text)
```

## Using with curl

### Simple Chat

```bash
curl -X POST http://localhost:18080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### Streaming

```bash
curl -N -X POST http://localhost:18080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "stream": true
  }'
```

### With Image

```bash
curl -X POST http://localhost:18080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/image.jpg"
          }
        }
      ]
    }]
  }'
```

## Request Format

### Chat Completions

```json
{
  "model": "gemini-3-flash",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 1.0,
  "top_p": 1.0,
  "max_tokens": null,
  "stream": false,
  "stop": null,
  "user": "user-123"
}
```

### Supported Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | string | Model to use | Required |
| `messages` | array | Conversation messages | Required |
| `temperature` | float | Sampling temperature (0-2) | 1.0 |
| `top_p` | float | Nucleus sampling (0-1) | 1.0 |
| `max_tokens` | int | Max tokens to generate | null |
| `stream` | boolean | Enable streaming | false |
| `stop` | string/array | Stop sequences | null |
| `user` | string | User identifier | null |

## Response Format

### Non-streaming

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gemini-3-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### Streaming

Each chunk:
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "gemini-3-flash",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "Hello"
      },
      "finish_reason": null
    }
  ]
}
```

Final chunk:
```
data: [DONE]
```

## Available Models

Use these model names with the OpenAI API:

| Model Name | Description |
|------------|-------------|
| `gemini-3-flash` | Fast, efficient model |
| `gemini-3-pro` | Balanced performance |
| `gemini-3-flash-thinking` | Enhanced reasoning |
| `gemini-3-flash-plus` | Plus tier flash |
| `gemini-3-pro-plus` | Plus tier pro |
| `gemini-3-flash-thinking-plus` | Plus tier thinking |
| `gemini-3-flash-advanced` | Advanced tier flash |
| `gemini-3-pro-advanced` | Advanced tier pro |
| `gemini-3-flash-thinking-advanced` | Advanced tier thinking |

## Error Handling

Errors follow OpenAI format:

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

## Environment Variables

```bash
# Optional: Set bearer token for authentication
API_BEARER_TOKEN=your_secret_token

# Gateway configuration
API_HOST=0.0.0.0
API_PORT=18080
```

## Differences from OpenAI

### Supported Features
✅ Chat completions with messages array  
✅ Streaming responses  
✅ Multi-modal inputs (text + images)  
✅ Temperature and top_p parameters  
✅ System/user/assistant roles  
✅ Base64 image support  

### Not Supported
❌ Function calling (coming soon)  
❌ Tool use (coming soon)  
❌ Fine-tuned models  
❌ Embeddings endpoint  
❌ Audio/TTS endpoints  

## Testing

```bash
# Test connection
curl http://localhost:18080/health

# List models
curl http://localhost:18080/v1/models

# Simple chat
curl -X POST http://localhost:18080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Integration Examples

### OpenClaw

```yaml
# config.yaml
api_endpoint: http://localhost:18080/v1/chat/completions
model: gemini-3-flash
api_key: your-api-key
```

### Continue.dev

```json
{
  "models": [{
    "title": "Gemini Flash",
    "provider": "openai",
    "model": "gemini-3-flash",
    "apiBase": "http://localhost:18080/v1",
    "apiKey": "your-api-key"
  }]
}
```

### Cursor

```json
{
  "openaiBaseUrl": "http://localhost:18080/v1",
  "openaiApiKey": "your-api-key",
  "model": "gemini-3-flash"
}
```

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [EXAMPLES.md](EXAMPLES.md) for more examples
- Open an issue on GitHub
