"""Pydantic schemas for AI Assistant module."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_module: Optional[str] = None  # e.g. "crm", "projects", "finance", "general"


class ChatResponse(BaseModel):
    reply: str
    model_used: str


class SummarizeRequest(BaseModel):
    content: str
    max_words: Optional[int] = 150


class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str] = []


class GenerateCopyRequest(BaseModel):
    topic: str
    copy_type: str = "email"  # "email", "task_description", "announcement"
    tone: str = "professional"  # "professional", "casual", "urgent"


class GenerateCopyResponse(BaseModel):
    generated_text: str
