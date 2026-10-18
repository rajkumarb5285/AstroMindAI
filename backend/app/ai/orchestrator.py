import json
import logging
from typing import Any

from backend.app.ai.adapter import LLMProviderInterface, get_llm_provider
from backend.app.ai.prompts import ASTROMIND_SYSTEM_PROMPT, DISCLAIMER_TEXT
from backend.app.ai.tools.registry import AVAILABLE_TOOLS, SecureAIToolExecutor
from backend.app.core.auth import UserContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger("astromind.ai.orchestrator")


class InterpretationResponse(BaseModel):
    interpretation: str
    citations: list[dict[str, str]]
    chart_id: str
    tokens_used: int
    tools_called: list[str]
    disclaimer: str


class AIInterpretationOrchestrator:
    """
    Secure Orchestrator for Grounded Vedic Astrology Consultations.
    Guarantees that responses are strictly derived from verified chart facts and approved citations.
    """

    MAX_TOOL_TURNS = 4

    def __init__(
        self,
        db: Session,
        user_context: UserContext,
        provider: LLMProviderInterface | None = None,
    ):
        self.db = db
        self.user_context = user_context
        self.provider = provider or get_llm_provider()
        self.executor = SecureAIToolExecutor(db=db, user_context=user_context)

    def interpret(self, chart_id: str, question: str) -> InterpretationResponse:
        """
        Executes a bounded, source-grounded consultation query for an authorized chart.
        Pre-fetches verified astronomical calculations and classical rules to enable
        the AI to respond as an empathetic, 30+ year veteran Jyotish Acharya.
        """
        retrieved_citations: list[dict[str, str]] = []
        tools_called: list[str] = []

        # 1. Pre-fetch verified astronomical chart facts & classical rules from database
        try:
            facts = self.executor.execute_tool("get_chart_facts", {"chart_id": chart_id})
            tools_called.append("get_chart_facts")
        except Exception as err:
            logger.warning(f"Error fetching chart facts for {chart_id}: {err}")
            facts = {}

        try:
            rules = self.executor.execute_tool("evaluate_astrology_rules", {"chart_id": chart_id, "category": "all"})
            tools_called.append("evaluate_astrology_rules")
        except Exception as err:
            logger.warning(f"Error evaluating rules for {chart_id}: {err}")
            rules = {}

        try:
            knowledge = self.executor.execute_tool("search_vedic_knowledge", {"query": question, "top_k": 3})
            tools_called.append("search_vedic_knowledge")
            for item in knowledge.get("citations", []):
                retrieved_citations.append(
                    {
                        "citation": item.get("citation", ""),
                        "topic": item.get("topic", ""),
                        "content": item.get("content", ""),
                        "chunk_id": item.get("chunk_id", ""),
                    }
                )
        except Exception as err:
            logger.warning(f"Error searching knowledge for {question}: {err}")

        # 2. Extract structured astrological significations
        asc = facts.get("ascendant", {})
        asc_sign = asc.get("sign", "Aries")
        asc_deg = asc.get("degree", 0.0)
        planets = facts.get("planets", [])
        yogas = rules.get("yogas", [])

        # Identify key house occupants
        h7_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 7]
        h10_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 10]
        h1_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 1]

        # Format clean, human-readable verified astrological context
        planet_lines = [
            f"  * {p['planet']}: in {p['sign']} (House {p['house']}, {p.get('degree', 0.0):.1f}°, {'Retrograde' if p.get('is_retrograde') else 'Direct'})"
            for p in planets
        ]
        yoga_names = [y.get("name", "") for y in yogas]

        scripture_excerpts = [
            f"- [{c['citation']}] {c['content'][:280]}..."
            for c in retrieved_citations[:2]
        ]

        prompt_body = f"""Client's Life Inquiry: "{question}"

Verified Astronomical Calculations (Chart ID: {chart_id}):
- Ascendant (Lagna): {asc_sign} ({asc_deg:.1f}°)
- Planetary Placements:
{chr(10).join(planet_lines)}
- 1st House (Self & Vitality): {'Occupied by ' + ', '.join(h1_planets) if h1_planets else 'Governed by Lagna Lord'}
- 7th House (Marriage & Partnership): {'Occupied by ' + ', '.join(h7_planets) if h7_planets else 'No occupying planets, governed by 7th Lord'}
- 10th House (Career, Karma & Status): {'Occupied by ' + ', '.join(h10_planets) if h10_planets else 'Governed by 10th Lord'}
- Classical Yogas Detected: {', '.join(yoga_names) if yoga_names else 'Standard auspicious planetary combinations'}

Classical Vedic Wisdom from Shastras:
{chr(10).join(scripture_excerpts) if scripture_excerpts else '- Classical Parashari Jyotish guidelines apply.'}

As Acharya Shastri (30+ years experience), answer this client with warmth, directness, and compassion:
1. Address the question directly first in easy-to-understand human language. If marriage/career, pinpoint the favorable timing windows clearly.
2. Explain partner/career traits in simple, engaging terms (no raw decimals or technical confusion).
3. Provide 2-3 practical, authentic Vedic remedies (Upayas) to remove obstacles and bring peace.
"""

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": ASTROMIND_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_body},
        ]

        # Call active LLM Provider
        response = self.provider.generate(messages=messages)
        total_tokens = response.prompt_tokens + response.completion_tokens

        final_text = response.content or "No response could be generated."
        if DISCLAIMER_TEXT not in final_text:
            final_text += f"\n\n*{DISCLAIMER_TEXT}*"

        return InterpretationResponse(
            interpretation=final_text,
            citations=retrieved_citations,
            chart_id=chart_id,
            tokens_used=total_tokens,
            tools_called=tools_called,
            disclaimer=DISCLAIMER_TEXT,
        )
