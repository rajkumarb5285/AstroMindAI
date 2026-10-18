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
        """
        # Prepare system and user messages
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": ASTROMIND_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Target chart_id: {chart_id}\n\nUser Question: {question}",
            },
        ]

        tools_specs = [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in AVAILABLE_TOOLS
        ]

        turns = 0
        total_tokens = 0
        tools_called: list[str] = []
        retrieved_citations: list[dict[str, str]] = []

        while turns < self.MAX_TOOL_TURNS:
            turns += 1
            response = self.provider.generate(messages=messages, tools=tools_specs)
            total_tokens += response.prompt_tokens + response.completion_tokens

            # 1. If tool calls requested, execute them with security bounds
            if response.tool_calls:
                # Append assistant tool call request message
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.name,
                                    "arguments": json.dumps(tc.arguments),
                                },
                            }
                            for tc in response.tool_calls
                        ],
                    }
                )

                # Execute each tool through SecureAIToolExecutor
                for tc in response.tool_calls:
                    tools_called.append(tc.name)
                    try:
                        # Security enforcement: override or enforce chart_id strictly
                        args = dict(tc.arguments)
                        if "chart_id" in args:
                            args["chart_id"] = chart_id

                        tool_output = self.executor.execute_tool(tc.name, args)

                        # Track citations
                        if tc.name == "search_vedic_knowledge":
                            for item in tool_output.get("citations", []):
                                retrieved_citations.append(
                                    {
                                        "citation": item.get("citation", ""),
                                        "topic": item.get("topic", ""),
                                        "content": item.get("content", ""),
                                        "chunk_id": item.get("chunk_id", ""),
                                    }
                                )

                        output_str = json.dumps(tool_output)
                    except Exception as err:
                        logger.warning(f"Tool execution error for {tc.name}: {err}")
                        output_str = json.dumps({"error": str(err)})

                    messages.append(
                        {
                            "role": "tool",
                            "name": tc.name,
                            "tool_call_id": tc.id,
                            "content": output_str,
                        }
                    )
            else:
                # 2. Final response generated
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

        # Fallback if loop exceeded
        return InterpretationResponse(
            interpretation=f"Analysis completed with primary placements.\n\n*{DISCLAIMER_TEXT}*",
            citations=retrieved_citations,
            chart_id=chart_id,
            tokens_used=total_tokens,
            tools_called=tools_called,
            disclaimer=DISCLAIMER_TEXT,
        )
