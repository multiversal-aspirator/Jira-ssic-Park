import json
import re
import httpx
from langchain_openai import ChatOpenAI
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_logged_once = False


def parse_llm_json(content: str) -> dict:
    """Parse JSON from LLM output, stripping markdown code fences if present."""
    text = content.strip()
    # Strip ```json ... ``` or ``` ... ```
    match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def get_chat_model() -> ChatOpenAI:
    """Create a ChatOpenAI instance using centralized settings.

    Supports OpenAI, OpenRouter, and any OpenAI-compatible endpoint
    via OPENAI_BASE_URL configuration.

    Raises ValueError if OPENAI_API_KEY is not configured.
    """
    global _logged_once
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured")

    kwargs = {
        "model": settings.LLM_MODEL,
        "temperature": settings.LLM_TEMPERATURE,
        "api_key": settings.OPENAI_API_KEY,
    }

    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
        # Use custom httpx client to handle corporate proxy/SSL issues
        kwargs["http_client"] = httpx.Client(verify=False)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

    if not _logged_once:
        base_url_display = settings.OPENAI_BASE_URL or "default (OpenAI)"
        logger.info(
            f"[LLMService] Provider: {settings.LLM_PROVIDER} | "
            f"Model: {settings.LLM_MODEL} | "
            f"Base URL: {base_url_display}"
        )
        _logged_once = True

    return ChatOpenAI(**kwargs)
