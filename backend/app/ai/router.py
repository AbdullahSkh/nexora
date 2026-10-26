"""AI Assistant API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.ai.schemas import (
    ChatRequest,
    ChatResponse,
    GenerateCopyRequest,
    GenerateCopyResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.ai.service import AIService
from app.core.dependencies import get_current_user
from app.users.models import User

router = APIRouter()


def _svc(current_user: User = Depends(get_current_user)) -> AIService:
    return AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    svc: AIService = Depends(_svc),
):
    return await svc.chat(request)


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_content(
    request: SummarizeRequest,
    svc: AIService = Depends(_svc),
):
    return await svc.summarize(request)


@router.post("/generate-copy", response_model=GenerateCopyResponse)
async def generate_copy(
    request: GenerateCopyRequest,
    svc: AIService = Depends(_svc),
):
    return await svc.generate_copy(request)
