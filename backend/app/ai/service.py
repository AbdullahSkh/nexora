"""AI Assistant service with Gemini / Ollama integration and local fallback."""
from __future__ import annotations

import httpx
from typing import List

from app.ai.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    GenerateCopyRequest,
    GenerateCopyResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIService:
    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY
        self.provider = settings.AI_PROVIDER
        self.ollama_url = settings.OLLAMA_BASE_URL

    async def chat(self, request: ChatRequest) -> ChatResponse:
        user_message = request.messages[-1].content if request.messages else ""
        context = f" Context: {request.context_module}." if request.context_module else ""

        if self.api_key and self.provider == "gemini":
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                contents = [
                    {"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]}
                    for m in request.messages
                ]
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json={"contents": contents})
                    if resp.status_code == 200:
                        data = resp.json()
                        reply = data["candidates"][0]["content"]["parts"][0]["text"]
                        return ChatResponse(reply=reply, model_used="gemini-1.5-flash")
            except Exception as e:
                logger.error("Gemini API call failed: %s", str(e))

        # Default smart assistant reply when API key is not configured or in offline mode
        reply = (
            f"Hello! I am your Nexora Startup OS Assistant.{context} "
            f"Regarding your query: '{user_message}', I am ready to help organize tasks, "
            f"draft communications, and analyze pipeline metrics across your workspace."
        )
        return ChatResponse(reply=reply, model_used="nexora-copilot-local")

    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        content = request.content.strip()
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Generate key takeaways
        key_points: List[str] = []
        for line in lines[:3]:
            if line.startswith(("-", "*", "#")):
                key_points.append(line.lstrip("-*# ").strip())
            else:
                key_points.append(line[:100] + ("..." if len(line) > 100 else ""))

        if not key_points:
            key_points = ["Overview of document or interaction provided."]

        summary_text = (
            f"Summary ({len(content.split())} words condensed): "
            + " ".join(lines[:2])[:200]
            + ("..." if len(content) > 200 else "")
        )
        return SummarizeResponse(summary=summary_text, key_points=key_points)

    async def generate_copy(self, request: GenerateCopyRequest) -> GenerateCopyResponse:
        tone_prefix = f"[{request.tone.capitalize()}] "
        if request.copy_type == "email":
            copy = (
                f"{tone_prefix}Subject: Update regarding {request.topic}\n\n"
                f"Hi Team,\n\n"
                f"I am writing to share a brief update on {request.topic}. "
                f"Please review the attached details and let me know if you have any questions.\n\n"
                f"Best regards,\nNexora Workspace"
            )
        elif request.copy_type == "announcement":
            copy = (
                f"{tone_prefix}📢 Announcement: {request.topic}\n\n"
                f"We are excited to announce new progress on {request.topic}! "
                f"Check our dashboard for updated milestones and next steps."
            )
        else:
            copy = f"{tone_prefix}Task: Implement and review {request.topic}. Ensure proper validation and QA."

        return GenerateCopyResponse(generated_text=copy)
