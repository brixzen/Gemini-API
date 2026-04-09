"""Adapter to convert between OpenAI and Gemini formats"""

import base64
import re
import io
from typing import List, Tuple, Optional, Dict, Any, Union
from pathlib import Path

try:
    from ..models.openai_models import ChatMessage, ChatCompletionRequest
    from ..models.requests import ResponseRequest, MessageItem, InputImageItem, InputFileItem, ImageSource
except ImportError:
    import sys
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from models.openai_models import ChatMessage, ChatCompletionRequest
    from models.requests import ResponseRequest, MessageItem, InputImageItem, InputFileItem, ImageSource


class OpenAIAdapter:
    """Convert between OpenAI and internal formats"""
    
    @staticmethod
    def messages_to_prompt(messages: List[Any]) -> Tuple[str, List[Any]]:
        """
        Convert OpenAI messages to Gemini prompt format
        
        Args:
            messages: List of ChatMessage objects or dicts
        
        Returns:
            Tuple of (text_prompt, files_list)
        """
        prompt_parts = []
        files = []
        
        for msg in messages:
            # Convert dict to ChatMessage-like object if needed
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                name = msg.get("name")
            else:
                role = msg.role
                content = msg.content
                name = msg.name if hasattr(msg, "name") else None
            role_prefix = ""
            if role == "system":
                role_prefix = "System: "
            elif role == "user":
                role_prefix = "User: "
            elif role == "assistant":
                role_prefix = "Assistant: "
            
            # Handle content - can be string or list of content parts
            if isinstance(content, str):
                prompt_parts.append(f"{role_prefix}{content}")
            elif isinstance(content, list):
                # Multi-modal content (text + images)
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            prompt_parts.append(f"{role_prefix}{part.get('text', '')}")
                        elif part.get("type") == "image_url":
                            image_url = part.get("image_url", {})
                            url = image_url.get("url", "") if isinstance(image_url, dict) else image_url
                            
                            # Handle base64 images
                            if url.startswith("data:image"):
                                # Extract base64 data
                                match = re.match(r"data:image/([^;]+);base64,(.+)", url)
                                if match:
                                    mime_type = match.group(1)
                                    base64_data = match.group(2)
                                    files.append({
                                        "mime_type": f"image/{mime_type}",
                                        "data": base64_data
                                    })
                            else:
                                # Regular URL
                                files.append(url)
        
        # Combine all prompt parts
        prompt = "\n\n".join(prompt_parts)
        
        return prompt, files
    
    @staticmethod
    def openai_to_gemini_files(request: ChatCompletionRequest) -> Tuple[str, List[Union[str, io.BytesIO]]]:
        """
        Convert OpenAI ChatCompletionRequest directly to Gemini format
        
        Returns:
            Tuple of (prompt_text, files_for_gemini)
            where files_for_gemini can be URLs (str) or BytesIO objects
        """
        # Convert messages to prompt
        prompt, files = OpenAIAdapter.messages_to_prompt(request.messages)
        
        print(f"[DEBUG] Extracted prompt: {prompt[:100] if prompt else 'None'}...")
        print(f"[DEBUG] Extracted files count: {len(files)}")
        
        # Convert files to Gemini format
        gemini_files = []
        for i, f in enumerate(files):
            if isinstance(f, str):
                # URL - pass directly to Gemini client (it will download with auth)
                print(f"[DEBUG] File {i}: URL - {f[:50]}...")
                gemini_files.append(f)
            elif isinstance(f, dict):
                # Base64 - decode and pass as BytesIO
                print(f"[DEBUG] File {i}: Base64 - mime={f.get('mime_type')}, data_len={len(f.get('data', ''))}")
                try:
                    image_bytes = base64.b64decode(f["data"])
                    gemini_files.append(io.BytesIO(image_bytes))
                    print(f"[DEBUG] File {i}: Decoded to {len(image_bytes)} bytes")
                except Exception as e:
                    print(f"[DEBUG] File {i}: Failed to decode - {e}")
        
        print(f"[DEBUG] Created {len(gemini_files)} Gemini files")
        return prompt, gemini_files
    
    @staticmethod
    def openai_to_internal(request: ChatCompletionRequest) -> ResponseRequest:
        """Convert OpenAI ChatCompletionRequest to internal ResponseRequest"""
        
        # Convert messages to prompt
        prompt, files = OpenAIAdapter.messages_to_prompt(request.messages)
        
        print(f"[DEBUG] Extracted prompt: {prompt[:100] if prompt else 'None'}...")
        print(f"[DEBUG] Extracted files count: {len(files)}")
        for i, f in enumerate(files):
            if isinstance(f, str):
                print(f"[DEBUG] File {i}: URL - {f[:50]}...")
            elif isinstance(f, dict):
                print(f"[DEBUG] File {i}: Base64 - mime={f.get('mime_type')}, data_len={len(f.get('data', ''))}")
        
        # Build input list
        input_items = []
        
        # Add text
        if prompt:
            input_items.append(MessageItem(type="message", role="user", content=prompt))
        
        # Add files
        for file in files:
            if isinstance(file, str):
                # URL - create InputImageItem
                input_items.append(InputImageItem(
                    source=ImageSource(type="url", url=file)
                ))
            elif isinstance(file, dict):
                # Base64 image - create InputImageItem
                input_items.append(InputImageItem(
                    source=ImageSource(
                        type="base64",
                        data=file["data"],
                        media_type=file.get("mime_type", "image/jpeg")
                    )
                ))
        
        print(f"[DEBUG] Created {len(input_items)} input items")
        
        # Create internal request
        return ResponseRequest(
            model=request.model,
            input=input_items if len(input_items) > 1 else prompt,
            stream=request.stream or False,
            user=request.user,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
    
    @staticmethod
    def internal_to_openai_message(text: str, role: str = "assistant") -> ChatMessage:
        """Convert internal response text to OpenAI message"""
        return ChatMessage(role=role, content=text)
    
    @staticmethod
    def extract_thinking_and_response(text: str) -> Tuple[Optional[str], str]:
        """
        Extract thinking process and final response from Gemini output
        
        Returns:
            Tuple of (thinking_text, response_text)
        """
        # Look for thinking markers
        thinking_pattern = r"<thinking>(.*?)</thinking>"
        match = re.search(thinking_pattern, text, re.DOTALL)
        
        if match:
            thinking = match.group(1).strip()
            response = re.sub(thinking_pattern, "", text, flags=re.DOTALL).strip()
            return thinking, response
        
        return None, text
    
    @staticmethod
    def format_multimodal_content(text: str, images: List[str] = None) -> List[Dict[str, Any]]:
        """Format multimodal content for OpenAI response"""
        content = []
        
        if text:
            content.append({"type": "text", "text": text})
        
        if images:
            for img_url in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img_url}
                })
        
        return content if len(content) > 1 else text
