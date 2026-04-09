#!/usr/bin/env python3
"""
Gemini-OpenClaw Gateway API Server
OpenClaw-compatible HTTP API endpoint for Google Gemini with full multimodal support
"""

import sys
import json
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add parent directory to path for gemini_webapi imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gemini_webapi import GeminiClient, logger, set_log_level
from gemini_webapi.exceptions import AuthError, GeminiError
from gemini_webapi.constants import Model

# Handle both direct execution and module import
try:
    from .config import config
    from .models import ResponseRequest
    from .models.openai_models import (
        ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice,
        ChatCompletionChunk, ChatCompletionUsage, CompletionRequest, ModelList, ModelInfo
    )
    from .handlers import InputProcessor, ModelRouter, SessionManager, OutputHandler
    from .handlers.openai_adapter import OpenAIAdapter
except ImportError:
    # Add current directory to path for absolute imports
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from config import config
    from models import ResponseRequest
    from models.openai_models import (
        ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice,
        ChatCompletionChunk, ChatCompletionUsage, CompletionRequest, ModelList, ModelInfo
    )
    from handlers import InputProcessor, ModelRouter, SessionManager, OutputHandler
    from handlers.openai_adapter import OpenAIAdapter


# ============================================================================
# Gemini Client Manager
# ============================================================================

class GeminiClientManager:
    """Manages Gemini client instances per agent"""
    
    def __init__(self):
        self.clients: Dict[str, GeminiClient] = {}
        self.session_manager = SessionManager()
    
    async def get_client(self, agent_id: str = "main") -> GeminiClient:
        """Get or create a Gemini client for an agent"""
        if agent_id in self.clients:
            return self.clients[agent_id]
        
        # Load cookies
        psid = config.GEMINI_SECURE_1PSID
        psidts = config.GEMINI_SECURE_1PSIDTS
        
        if config.GEMINI_COOKIES_JSON and Path(config.GEMINI_COOKIES_JSON).exists():
            try:
                cookies_data = json.loads(Path(config.GEMINI_COOKIES_JSON).read_text())
                
                # Handle browser export format (array of cookie objects)
                if isinstance(cookies_data, list):
                    cookies = {c.get("name"): c.get("value") for c in cookies_data if isinstance(c, dict)}
                    psid = cookies.get("__Secure-1PSID") or psid
                    psidts = cookies.get("__Secure-1PSIDTS") or psidts
                # Handle dict formats
                elif isinstance(cookies_data, dict):
                    cookies = cookies_data.get("cookies", cookies_data)
                    psid = cookies.get("__Secure-1PSID") or psid
                    psidts = cookies.get("__Secure-1PSIDTS") or psidts
            except Exception as e:
                logger.warning(f"Failed to load cookies from JSON: {e}")
        
        if not psid:
            raise HTTPException(
                status_code=401,
                detail="Missing Gemini credentials. Set GEMINI_SECURE_1PSID or GEMINI_COOKIES_JSON"
            )
        
        # Create client
        client = GeminiClient(
            secure_1psid=psid,
            secure_1psidts=psidts or "",
        )
        
        try:
            await client.init(
                timeout=config.REQUEST_TIMEOUT,
                auto_refresh=True,
                verbose=(config.LOG_LEVEL == "DEBUG")
            )
            self.clients[agent_id] = client
            logger.info(f"Initialized Gemini client for agent: {agent_id}")
            return client
        except AuthError as e:
            raise HTTPException(status_code=401, detail=f"Gemini auth failed: {e}")
    
    async def cleanup(self):
        """Close all clients"""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()


# ============================================================================
# FastAPI Application
# ============================================================================

# Global manager instance
manager = GeminiClientManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    log_level = config.LOG_LEVEL
    set_log_level(log_level)
    logger.info("Gemini-OpenClaw Gateway starting...")
    
    yield
    
    # Shutdown
    await manager.cleanup()
    logger.info("Gemini-OpenClaw Gateway stopped")


app = FastAPI(
    title="Gemini-OpenClaw Gateway",
    description="OpenClaw-compatible API endpoint for Google Gemini with multimodal support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Authentication Middleware
# ============================================================================

async def verify_bearer_token(authorization: Optional[str] = Header(None)):
    """Verify bearer token if configured"""
    if config.API_BEARER_TOKEN:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization[7:]  # Remove "Bearer " prefix
        if token != config.API_BEARER_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid bearer token")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "gemini-openclaw-gateway",
        "version": "1.0.0"
    }


@app.get("/v1/models")
async def list_models(
    authorization: Optional[str] = Header(None),
    x_openclaw_agent_id: str = Header("main", alias="x-openclaw-agent-id")
):
    """List available models (OpenAI-compatible)"""
    await verify_bearer_token(authorization)
    
    try:
        client = await manager.get_client(x_openclaw_agent_id)
        
        # Get models from Gemini
        gemini_models = client.list_models()
        
        model_list = []
        created_timestamp = int(datetime.now().timestamp())
        
        # Add all supported models
        for model_name in ModelRouter.get_all_models():
            model_list.append(ModelInfo(
                id=model_name,
                created=created_timestamp,
                owned_by="google-gemini"
            ))
        
        # Add dynamic models from Gemini if available
        if gemini_models:
            for m in gemini_models:
                if m.is_available:
                    model_list.append(ModelInfo(
                        id=m.model_name or m.display_name,
                        created=created_timestamp,
                        owned_by="google-gemini"
                    ))
        
        return ModelList(data=model_list)
    
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None),
    x_openclaw_agent_id: str = Header("main", alias="x-openclaw-agent-id")
):
    """
    OpenAI-compatible chat completions endpoint
    
    Fully compatible with OpenAI's Chat Completions API.
    Supports:
    - Multi-turn conversations via messages array
    - System/user/assistant roles
    - Streaming responses
    - Multi-modal inputs (text + images)
    - Temperature and other parameters
    """
    await verify_bearer_token(authorization)
    
    try:
        # Get Gemini client
        client = await manager.get_client(x_openclaw_agent_id)
        
        # Route to correct model
        gemini_model = ModelRouter.get_model(request.model)
        
        # Generate response ID
        response_id = f"chatcmpl-{uuid.uuid4().hex[:16]}"
        created_timestamp = int(datetime.now().timestamp())
        
        # Convert OpenAI request to internal format
        internal_request = OpenAIAdapter.openai_to_internal(request)
        
        # Process inputs (downloads URLs, decodes base64, saves to temp files)
        input_processor = InputProcessor()
        prompt, files = await input_processor.process_request(internal_request)
        
        logger.debug(f"Prompt length: {len(prompt) if prompt else 0}")
        logger.debug(f"Files count: {len(files)}")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Empty prompt")
        
        # Handle streaming
        if request.stream:
            async def stream_generator():
                try:
                    stream = client.generate_content_stream(
                        prompt,
                        files=files,
                        model=gemini_model
                    )
                    
                    chunk_index = 0
                    async for chunk in stream:
                        if chunk and hasattr(chunk, 'text') and chunk.text:
                            # Create OpenAI-format chunk
                            chunk_data = ChatCompletionChunk(
                                id=response_id,
                                created=created_timestamp,
                                model=request.model,
                                choices=[{
                                    "index": 0,
                                    "delta": {"role": "assistant", "content": chunk.text},
                                    "finish_reason": None
                                }]
                            )
                            yield f"data: {chunk_data.model_dump_json()}\n\n"
                            chunk_index += 1
                    
                    # Send final chunk
                    final_chunk = ChatCompletionChunk(
                        id=response_id,
                        created=created_timestamp,
                        model=request.model,
                        choices=[{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }]
                    )
                    yield f"data: {final_chunk.model_dump_json()}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    error_data = {"error": {"message": str(e), "type": "server_error"}}
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Non-streaming response
        response = await client.generate_content(prompt, files=files, model=gemini_model)
        
        if not response or not hasattr(response, 'text'):
            raise HTTPException(status_code=500, detail="Empty response from Gemini")
        
        # Extract thinking if present
        thinking, response_text = OpenAIAdapter.extract_thinking_and_response(response.text)
        
        # Build OpenAI response
        completion_response = ChatCompletionResponse(
            id=response_id,
            created=created_timestamp,
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=OpenAIAdapter.internal_to_openai_message(response_text),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=len(prompt.split()),  # Rough estimate
                completion_tokens=len(response_text.split()),
                total_tokens=len(prompt.split()) + len(response_text.split())
            )
        )
        
        return completion_response
        
    except AuthError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except GeminiError as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in chat completions: {error_msg}")
        
        # Provide more helpful error messages
        if "403" in error_msg or "forbidden" in error_msg.lower():
            raise HTTPException(
                status_code=400, 
                detail=f"Image URL access denied (HTTP 403). The image host may be blocking requests. Try using a different image URL or base64 encoding: {error_msg}"
            )
        elif "404" in error_msg:
            raise HTTPException(status_code=400, detail=f"Image not found (HTTP 404): {error_msg}")
        elif "downloading" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Failed to download image: {error_msg}")
        else:
            raise HTTPException(status_code=500, detail=error_msg)


@app.post("/v1/completions")
async def completions(
    request: CompletionRequest,
    authorization: Optional[str] = Header(None),
    x_openclaw_agent_id: str = Header("main", alias="x-openclaw-agent-id")
):
    """
    OpenAI-compatible completions endpoint (legacy)
    
    Supports the legacy completion format with prompt parameter.
    For new applications, use /v1/chat/completions instead.
    """
    await verify_bearer_token(authorization)
    
    try:
        # Convert to chat format
        prompt_text = request.prompt if isinstance(request.prompt, str) else "\n".join(request.prompt)
        
        # Create a simple chat request with proper ChatMessage objects
        chat_request = ChatCompletionRequest(
            model=request.model,
            messages=[ChatMessage(role="user", content=prompt_text)],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            stream=request.stream,
            stop=request.stop,
            user=request.user
        )
        
        # Use chat completions endpoint
        response = await chat_completions(chat_request, authorization, x_openclaw_agent_id)
        
        # Convert response format if needed
        if isinstance(response, ChatCompletionResponse):
            # Convert to legacy completion format
            return {
                "id": response.id,
                "object": "text_completion",
                "created": response.created,
                "model": response.model,
                "choices": [{
                    "text": choice.message.content,
                    "index": choice.index,
                    "finish_reason": choice.finish_reason
                } for choice in response.choices],
                "usage": response.usage.model_dump() if response.usage else None
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in completions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/responses")
async def create_response(
    request: ResponseRequest,
    authorization: Optional[str] = Header(None),
    x_openclaw_agent_id: str = Header("main", alias="x-openclaw-agent-id")
):
    """
    Generate a response from Gemini (OpenClaw-compatible)
    
    Supports:
    - Text input
    - Image input (URL or base64)
    - File input (PDF, documents via base64)
    - Streaming via SSE
    - Session continuity via previous_response_id
    - All 9 Gemini model variants
    """
    await verify_bearer_token(authorization)
    
    input_processor = InputProcessor()
    
    try:
        # Get Gemini client
        client = await manager.get_client(x_openclaw_agent_id)
        
        # Process inputs
        prompt, files = await input_processor.process_request(request)
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Empty prompt")
        
        # Route to correct model
        gemini_model = ModelRouter.get_model(request.model)
        
        # Generate response ID
        response_id = f"resp_{uuid.uuid4().hex[:16]}"
        
        # Check for session continuity
        chat_session = await manager.session_manager.get_or_create_chat_session(
            client=client,
            user_id=request.user,
            previous_response_id=request.previous_response_id,
            model=gemini_model
        )
        
        # Handle streaming
        if request.stream:
            async def stream_generator():
                try:
                    if chat_session:
                        # Continue existing conversation
                        stream = chat_session.send_message_stream(prompt, files=files)
                    else:
                        # New conversation
                        stream = client.generate_content_stream(
                            prompt,
                            files=files,
                            model=gemini_model
                        )
                    
                    # Stream with output handler
                    async for sse_event in OutputHandler.stream_response(
                        stream,
                        request.model,
                        response_id
                    ):
                        yield sse_event
                
                finally:
                    # Cleanup temp files
                    input_processor.cleanup()
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream"
            )
        
        # Non-streaming response
        if chat_session:
            # Continue existing conversation
            gemini_output = await chat_session.send_message(prompt, files=files)
        else:
            # New conversation
            gemini_output = await client.generate_content(
                prompt,
                files=files,
                model=gemini_model
            )
        
        # Store session for continuity
        manager.session_manager.store_response(
            response_id=response_id,
            metadata=gemini_output.metadata,
            user_id=request.user,
            model=gemini_model
        )
        
        # Format response
        response = OutputHandler.format_response(
            gemini_output,
            request.model,
            response_id
        )
        
        return response
    
    except GeminiError as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Always cleanup temp files
        input_processor.cleanup()


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini-OpenClaw Gateway")
    parser.add_argument("--host", default=config.API_HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=config.API_PORT, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default=config.LOG_LEVEL.lower(), help="Log level")
    
    args = parser.parse_args()
    
    # Set log level
    set_log_level(args.log_level.upper())
    
    logger.info(f"Starting Gemini-OpenClaw Gateway on {args.host}:{args.port}")
    
    # Run uvicorn with the app instance directly (not as a string)
    uvicorn.run(
        app,  # Pass app instance directly instead of string
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
