"""OpenAI-compatible request/response models"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """OpenAI chat message format"""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="Optional name of the participant")
    
    class Config:
        # Allow arbitrary types for content flexibility
        arbitrary_types_allowed = True


class ChatCompletionRequest(BaseModel):
    """OpenAI chat completion request"""
    model: str = Field(..., description="Model to use")
    messages: List[Union[ChatMessage, Dict[str, Any]]] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(1.0, ge=0, le=2, description="Sampling temperature")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="Nucleus sampling")
    n: Optional[int] = Field(1, description="Number of completions")
    stream: Optional[bool] = Field(False, description="Stream responses")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2)
    logit_bias: Optional[Dict[str, float]] = Field(None)
    user: Optional[str] = Field(None, description="User identifier")
    
    class Config:
        # Allow extra fields and arbitrary types
        extra = "allow"
        arbitrary_types_allowed = True


class ChatCompletionChoice(BaseModel):
    """OpenAI chat completion choice"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionUsage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """OpenAI chat completion response"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[ChatCompletionUsage] = None


class ChatCompletionChunk(BaseModel):
    """OpenAI streaming chunk"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


class CompletionRequest(BaseModel):
    """OpenAI completion request (legacy)"""
    model: str
    prompt: Union[str, List[str]]
    temperature: Optional[float] = Field(1.0, ge=0, le=2)
    max_tokens: Optional[int] = Field(16)
    top_p: Optional[float] = Field(1.0, ge=0, le=1)
    n: Optional[int] = Field(1)
    stream: Optional[bool] = Field(False)
    logprobs: Optional[int] = Field(None)
    echo: Optional[bool] = Field(False)
    stop: Optional[Union[str, List[str]]] = Field(None)
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2)
    user: Optional[str] = Field(None)


class ModelInfo(BaseModel):
    """OpenAI model information"""
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """OpenAI model list response"""
    object: str = "list"
    data: List[ModelInfo]


class ErrorResponse(BaseModel):
    """OpenAI error response"""
    error: Dict[str, Any]
