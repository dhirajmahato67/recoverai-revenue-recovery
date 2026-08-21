"""OpenAI-compatible AI Provider implementation."""

import asyncio
import json
import time
import urllib.request
import urllib.error
from typing import Any
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.services.ai.providers.base import AIProvider, AIProviderResult

logger = get_logger("app.services.ai.openai")


class OpenAIProvider(AIProvider):
    """OpenAI HTTP provider using chat completions API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 15.0,
    ):
        super().__init__(model=model, timeout_seconds=timeout_seconds)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        context: dict[str, Any],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIProviderResult:
        """Call OpenAI chat completion endpoint asynchronously."""
        if not self.api_key:
            raise AppException(
                status_code=503,
                error_code="AI_PROVIDER_UNCONFIGURED",
                message="OpenAI API key is missing or empty.",
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Verified Investigation Telemetry Context:\n```json\n{json.dumps(context, indent=2)}\n```\n\nUser Question:\n{user_prompt}",
            },
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "RecoverAI-Copilot/1.0",
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        t0 = time.perf_counter()
        try:
            loop = asyncio.get_running_loop()

            def _send() -> bytes:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    return resp.read()

            raw_bytes = await loop.run_in_executor(None, _send)
            latency_ms = int((time.perf_counter() - t0) * 1000)

            data = json.loads(raw_bytes.decode("utf-8"))
            choice = data.get("choices", [{}])[0]
            message_content = choice.get("message", {}).get("content", "")
            usage = data.get("usage", {})

            return AIProviderResult(
                text=message_content,
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency_ms,
                token_usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                raw_payload=data,
            )

        except urllib.error.HTTPError as exc:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            logger.error(f"OpenAI API HTTP error: {exc.code} {exc.reason}")
            raise AppException(
                status_code=502,
                error_code="AI_PROVIDER_ERROR",
                message=f"OpenAI API returned HTTP {exc.code}: {exc.reason}",
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            logger.error(f"OpenAI API connection/timeout error after {latency_ms}ms: {exc}")
            raise AppException(
                status_code=504,
                error_code="AI_PROVIDER_TIMEOUT",
                message=f"AI provider timed out after {self.timeout_seconds}s.",
            ) from exc
        except Exception as exc:
            logger.error(f"Unexpected error communicating with OpenAI: {exc}")
            raise AppException(
                status_code=500,
                error_code="AI_INTERNAL_ERROR",
                message="Unexpected error during AI completion generation.",
            ) from exc
