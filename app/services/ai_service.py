import asyncio
import logging
from typing import Any, Dict

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, api_key: str):
        self.model = None
        self.model_name = "gemini-2.0-flash"
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=2048,
                    top_p=0.95,
                    top_k=40,
                ),
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, RuntimeError, Exception)),
        reraise=True,
    )
    async def query(self, prompt: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Gọi Gemini có retry + timeout.
        SDK Gemini sync nên dùng asyncio.to_thread để không block event loop.
        """
        if self.model is None:
            raise ValueError("GEMINI_API_KEY is not configured")

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model.generate_content, prompt),
                timeout=timeout_seconds,
            )
            text = getattr(response, "text", "") or ""
            finish_reason = None
            if getattr(response, "candidates", None):
                finish_reason = getattr(response.candidates[0], "finish_reason", None)

            return {
                "text": text.strip(),
                "model": self.model_name,
                "finish_reason": str(finish_reason) if finish_reason is not None else None,
            }
        except asyncio.TimeoutError as e:
            logger.error("Gemini API timeout after %s seconds", timeout_seconds)
            raise TimeoutError(f"Gemini timeout after {timeout_seconds} seconds") from e
        except Exception as e:
            logger.exception("Gemini API error: %s", e)
            raise


gemini_service = GeminiService(api_key=settings.GEMINI_API_KEY)
