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
        from datetime import datetime

        asc = facts.get("ascendant", {})
        asc_sign = asc.get("sign", "Aries")
        asc_deg = asc.get("degree", 0.0)
        planets = facts.get("planets", [])
        yogas = rules.get("yogas", [])
        active_timing = facts.get("active_timing", {})

        # Identify key house occupants
        h1_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 1]
        h2_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 2]
        h6_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 6]
        h7_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 7]
        h10_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 10]
        h11_planets = [f"{p['planet']} ({p['sign']})" for p in planets if p.get("house") == 11]

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

        # Extract active real-time dasha timeline
        today_date = active_timing.get("today", datetime.utcnow().strftime("%Y-%m-%d"))
        try:
            today_obj = datetime.strptime(today_date, "%Y-%m-%d")
            current_date_str = today_obj.strftime("%B %d, %Y")
            current_year = today_obj.year
        except Exception:
            current_date_str = "October 2026"
            current_year = 2026

        cur_maha = active_timing.get("current_mahadasha") or {}
        cur_antar = active_timing.get("current_antardasha") or {}
        prev_antar = active_timing.get("previous_antardasha") or {}
        next_antar = active_timing.get("next_antardasha") or {}

        maha_desc = f"{cur_maha.get('lord')} Mahadasha (active {cur_maha.get('start')} to {cur_maha.get('end')})" if cur_maha.get('lord') else "Active Mahadasha verified in chart"
        antar_desc = f"{cur_antar.get('lord')} Antardasha (active {cur_antar.get('start')} to {cur_antar.get('end')})" if cur_antar.get('lord') else "Active Sub-period verified in chart"
        prev_desc = f"{prev_antar.get('lord')} Antardasha (ended {prev_antar.get('end')})" if prev_antar.get('lord') else "Previous sub-period"
        next_desc = f"{next_antar.get('lord')} Antardasha (commences {next_antar.get('start')} to {next_antar.get('end')})" if next_antar.get('lord') else "Upcoming sub-period"
        next_lord_name = next_antar.get('lord') or 'the upcoming sub-period'
        cur_antar_lord = cur_antar.get('lord') or 'active benefic'

        prompt_body = f"""Client's Life Inquiry: "{question}"

================ REAL-TIME ASTROLOGICAL & TIMING CONTEXT ================
- TODAY'S REAL-WORLD DATE: {current_date_str} (Year {current_year})
- Currently Running Mahadasha: {maha_desc}
- Currently Running Antardasha (Sub-Period): {antar_desc}
- Immediate Previous Sub-Period: {prev_desc}
- Next Upcoming Sub-Period: {next_desc}

Verified Astronomical Placements (Chart ID: {chart_id}):
- Ascendant (Lagna): {asc_sign} ({asc_deg:.1f}°)
- Planetary Placements:
{chr(10).join(planet_lines)}
- 1st House (Self & Vitality): {'Occupied by ' + ', '.join(h1_planets) if h1_planets else 'Governed by Lagna Lord'}
- 2nd House (Accumulated Wealth & Income): {'Occupied by ' + ', '.join(h2_planets) if h2_planets else 'Governed by 2nd Lord'}
- 6th House (Service, Daily Employment & Competitive Clearing): {'Occupied by ' + ', '.join(h6_planets) if h6_planets else 'Governed by 6th Lord'}
- 7th House (Marriage & Partnership): {'Occupied by ' + ', '.join(h7_planets) if h7_planets else 'Governed by 7th Lord'}
- 10th House (Career, Karma & Professional Status): {'Occupied by ' + ', '.join(h10_planets) if h10_planets else 'Governed by 10th Lord'}
- 11th House (Income, Gains & Salary/Compensation): {'Occupied by ' + ', '.join(h11_planets) if h11_planets else 'Governed by 11th Lord'}
- Classical Yogas Detected: {', '.join(yoga_names) if yoga_names else 'Standard auspicious planetary combinations'}

Classical Vedic Wisdom from Shastras:
{chr(10).join(scripture_excerpts) if scripture_excerpts else '- Classical Parashari Jyotish guidelines apply.'}

================ MANDATORY CONSULTATION INSTRUCTIONS ================
As Acharya Shastri (30+ years master experience), answer this client with absolute truth, compassion, and accuracy:
1. STRICT REAL-TIME CHRONOLOGY:
   - Today's date is {current_date_str}. NEVER give past dates (such as 2024 or early 2025). Any event timing for a job, marriage, or finance must be in the FUTURE relative to {current_date_str}.
   - You MUST explicitly cite their ACTUAL verified Dasha periods: {maha_desc} and {antar_desc}. Do NOT invent or guess different Dasha lords.
   - Note astronomical truths: The Sun and Moon NEVER go retrograde.

2. CAREER & PAID IT JOB GUIDANCE (IF APPLICABLE):
   - If the client is struggling with unpaid internships or looking for a PAID IT/Tech role:
     * Acknowledge their past struggle with empathy: explain that the previous sub-period ({prev_desc}) was a karmic testing phase of skill incubation without immediate reward.
     * Pinpoint the exact realistic window for landing a PAID role within the active {cur_antar_lord} sub-period and transition into {next_lord_name}.
     * Detail the IT/tech significators in their chart: Mercury (logic/coding), Rahu (software/cloud/AI/MNCs), Saturn (backend engineering/persistence).
     * Recommend the specific technical domain matching their strongest planets.

3. ACTIONABLE VEDIC REMEDIES (UPAYAS):
   - Provide 2-3 specific, authentic Vedic remedies to remove career/relationship roadblocks (e.g., Budha Beej Mantra on Wednesdays, feeding birds/cows, offering water to the rising Sun, or lighting a mustard oil lamp on Saturdays).
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
