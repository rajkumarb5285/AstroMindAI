import abc
import json
import logging
from typing import Any

from backend.app.ai.prompts import DISCLAIMER_TEXT
from backend.app.core.config import settings
from pydantic import BaseModel

logger = logging.getLogger("astromind.ai")


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class LLMResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = []
    finish_reason: str = "stop"
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMProviderInterface(abc.ABC):
    @abc.abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """Generates completion or tool calls given structured messages and tool definitions."""
        pass


class MockLLMProvider(LLMProviderInterface):
    """
    Deterministic Mock LLM Provider for local development, CI testing, and evaluation.
    Provides verifiable, source-grounded answers without incurring API costs or requiring secrets.
    """

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        # Check if the last message is a tool response
        last_msg = messages[-1] if messages else {}

        # 1. If last message is a user message, determine what tools are needed
        if last_msg.get("role") == "user":
            user_content = str(last_msg.get("content", ""))

            # Extract chart_id if present in context or messages
            chart_id = "test-chart-id"
            for m in messages:
                txt = str(m.get("content", ""))
                if "chart_id:" in txt:
                    for part in txt.split():
                        if part.startswith("chart_id:"):
                            chart_id = part.replace("chart_id:", "").strip()

            # First turn: Call get_chart_facts and evaluate_astrology_rules
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_facts_1",
                        name="get_chart_facts",
                        arguments={"chart_id": chart_id},
                    ),
                    ToolCall(
                        id="call_rules_1",
                        name="evaluate_astrology_rules",
                        arguments={"chart_id": chart_id, "category": "all"},
                    ),
                    ToolCall(
                        id="call_search_1",
                        name="search_vedic_knowledge",
                        arguments={"query": user_content, "top_k": 3},
                    ),
                ],
                finish_reason="tool_calls",
                prompt_tokens=150,
                completion_tokens=45,
            )

        # 2. If tools have returned data, synthesize the final grounded interpretation
        tool_data: dict[str, Any] = {}
        citations_used: list[str] = []

        for m in messages:
            if m.get("role") == "tool":
                t_name = m.get("name")
                if isinstance(t_name, str):
                    try:
                        payload = json.loads(m.get("content", "{}"))
                        tool_data[t_name] = payload
                        if t_name == "search_vedic_knowledge":
                            for c in payload.get("citations", []):
                                citations_used.append(c.get("citation"))
                    except (json.JSONDecodeError, TypeError, KeyError) as e:
                        logger.debug("Failed to decode tool response in MockLLMProvider: %s", e)

        facts = tool_data.get("get_chart_facts", {})
        rules = tool_data.get("evaluate_astrology_rules", {})
        asc = facts.get("ascendant", {})
        asc_sign = asc.get("sign", "Aries")
        planets = facts.get("planets", [])
        yogas = rules.get("yogas", [])

        # Build grounded response
        yoga_summary = (
            f"Classical Yogas Identified: {', '.join([y['name'] for y in yogas])}."
            if yogas
            else "No prominent classical yogas detected in primary angular placements."
        )

        citation_line = (
            f"Scriptural Citations: {', '.join(citations_used[:2])}."
            if citations_used
            else "Scriptural Citations: Brihat Parashara Hora Shastra, Chapter 11; Phaladeepika, Chapter 6."
        )

        planets_summary = ", ".join([f"{p['planet']} in {p['sign']} (House {p['house']})" for p in planets[:4]])

        final_text = (
            f"### Vedic Chart Analysis\n\n"
            f"**Verified Astronomical Placements:**\n"
            f"- **Ascendant (Lagna):** {asc_sign} ({asc.get('degree', 0.0)}°)\n"
            f"- **Key Planetary Placements:** {planets_summary}\n\n"
            f"**Classical Interpretations & Yogas:**\n"
            f"{yoga_summary}\n\n"
            f"**Scriptural References:**\n"
            f"{citation_line}\n\n"
            f"**Synthesis:**\n"
            f"The native's chart shows an analytical orientation with emphasis on ethical dharma and purposeful action. "
            f"Planetary significations should be integrated into conscious personal development.\n\n"
            f"*{DISCLAIMER_TEXT}*"
        )

        return LLMResponse(
            content=final_text,
            tool_calls=[],
            finish_reason="stop",
            prompt_tokens=320,
            completion_tokens=210,
        )


class OpenAICompatibleProvider(LLMProviderInterface):
    """
    OpenAI-compatible API Provider supporting Groq, OpenAI, and other standard endpoints
    with strict timeouts, structured tool calling, and error containment.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        base_url: str = "https://api.groq.com/openai/v1",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": settings.LLM_MAX_OUTPUT_TOKENS,
            "temperature": 0.2,  # Low temperature for factual consistency
        }

        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    },
                }
                for t in tools
            ]

        try:
            endpoint = f"{self.base_url}/chat/completions"
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(endpoint, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()

            choice = data["choices"][0]["message"]
            raw_tool_calls = choice.get("tool_calls", [])
            parsed_tools = []
            for tc in raw_tool_calls:
                fn = tc.get("function", {})
                args = json.loads(fn.get("arguments", "{}"))
                parsed_tools.append(ToolCall(id=tc["id"], name=fn["name"], arguments=args))

            return LLMResponse(
                content=choice.get("content"),
                tool_calls=parsed_tools,
                finish_reason=data["choices"][0].get("finish_reason", "stop"),
                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
            )
        except Exception as e:
            logger.error(f"LLM API completion error: {e}")
            raise RuntimeError(f"AI Provider execution failed: {e}") from e


def get_llm_provider() -> LLMProviderInterface:
    """Factory returning the active LLM provider (Groq, OpenAI, or Mock)."""
    import os
    import sys

    # In test environment / pytest execution, always use the deterministic MockLLMProvider
    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("TESTING") == "1" or settings.APP_ENV == "test":
        return MockLLMProvider()

    api_key = settings.LLM_API_KEY
    if not api_key or api_key in ("dummy-key-for-dev", "PLACEHOLDER_LLM_KEY"):
        return MockLLMProvider()

    if settings.LLM_PROVIDER == "groq" or api_key.startswith("gsk_"):
        return OpenAICompatibleProvider(
            api_key=api_key,
            model=settings.LLM_MODEL or "openai/gpt-oss-120b",
            base_url=settings.GROQ_API_BASE,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

    return OpenAICompatibleProvider(
        api_key=api_key,
        model=settings.LLM_MODEL or "gpt-4o-mini",
        base_url="https://api.openai.com/v1",
        timeout=settings.LLM_TIMEOUT_SECONDS,
    )
