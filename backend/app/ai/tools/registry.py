from typing import Any

from backend.app.astrology.rules.engine import AstrologyRuleEngine
from backend.app.core.auth import UserContext
from backend.app.knowledge.store import global_knowledge_store
from backend.app.repositories.scoped import ChartRepository
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
    is_read_only: bool = True
    requires_auth: bool = True


# Tool Schemas
class GetChartFactsInput(BaseModel):
    chart_id: str = Field(..., description="UUID of the verified natal chart calculation.")


class EvaluateRulesInput(BaseModel):
    chart_id: str = Field(..., description="UUID of the verified natal chart calculation.")
    category: str = Field("all", description="Rule category: 'all', 'dignities', 'yogas', 'aspects', 'combustion'.")


class SearchKnowledgeInput(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, description="Classical astrological query string.")
    top_k: int = Field(3, ge=1, le=5, description="Number of source passages to retrieve.")


# Tools Registry Specifications for LLM Function Calling
AVAILABLE_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="get_chart_facts",
        description="Retrieves verified planetary positions, Ascendant, houses, and dashas for an authorized chart. Never guess chart data.",
        parameters=GetChartFactsInput.model_json_schema(),
    ),
    ToolDefinition(
        name="evaluate_astrology_rules",
        description="Deterministically evaluates classical Parashari rules including planetary dignities (exaltation/debilitation), combustion, aspects (Drishti), and auspicious yogas.",
        parameters=EvaluateRulesInput.model_json_schema(),
    ),
    ToolDefinition(
        name="search_vedic_knowledge",
        description="Searches allowlisted classical Vedic texts (Brihat Parashara Hora Shastra, Phaladeepika, Saravali) for authentic interpretive principles and citations.",
        parameters=SearchKnowledgeInput.model_json_schema(),
    ),
]


class SecureAIToolExecutor:
    """
    Executes typed AI tools under strict server-side owner authorization.
    Identity and permissions are derived strictly from UserContext, never from LLM arguments.
    """

    def __init__(self, db: Session, user_context: UserContext):
        self.db = db
        self.user_context = user_context
        self.chart_repo = ChartRepository(db)

    def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatches tool execution with validation and object-level authorization."""
        if tool_name == "get_chart_facts":
            return self._get_chart_facts(arguments)
        elif tool_name == "evaluate_astrology_rules":
            return self._evaluate_astrology_rules(arguments)
        elif tool_name == "search_vedic_knowledge":
            return self._search_vedic_knowledge(arguments)
        else:
            raise ValueError(f"Unknown or unauthorized tool '{tool_name}'.")

    def _get_chart_facts(self, args: dict[str, Any]) -> dict[str, Any]:
        validated = GetChartFactsInput.model_validate(args)
        chart = self.chart_repo.get_by_id(
            chart_id=validated.chart_id,
            owner_id=self.user_context.user_id,
        )
        if not chart:
            raise PermissionError(f"Access denied: Chart '{validated.chart_id}' not found or belongs to another user.")

        from backend.app.api.v1.charts import reconstruct_chart_calculation_result

        calc = reconstruct_chart_calculation_result(chart).model_dump()
        return {
            "chart_id": chart.id,
            "owner_id": chart.owner_id,
            "ayanamsa": chart.ayanamsa,
            "ascendant": {
                "sign": calc.get("ascendant_sign_name"),
                "degree": calc.get("ascendant_degree"),
                "nakshatra": calc.get("ascendant_nakshatra"),
                "pada": calc.get("ascendant_pada"),
            },
            "planets": [
                {
                    "planet": p.get("planet_id"),
                    "sign": p.get("sign_name"),
                    "degree": round(p.get("degree_in_sign", 0.0), 2),
                    "nakshatra": p.get("nakshatra_name"),
                    "pada": p.get("pada"),
                    "house": p.get("house_number"),
                    "is_retrograde": p.get("is_retrograde"),
                }
                for p in calc.get("planets", [])
            ],
            "current_dashas": [
                {
                    "lord": d.get("lord"),
                    "start": d.get("start_date"),
                    "end": d.get("end_date"),
                    "duration_years": d.get("duration_years"),
                }
                for d in calc.get("vimshottari_dashas", [])
            ],
        }

    def _evaluate_astrology_rules(self, args: dict[str, Any]) -> dict[str, Any]:
        validated = EvaluateRulesInput.model_validate(args)
        chart = self.chart_repo.get_by_id(
            chart_id=validated.chart_id,
            owner_id=self.user_context.user_id,
        )
        if not chart:
            raise PermissionError(f"Access denied: Chart '{validated.chart_id}' not found or belongs to another user.")

        from backend.app.api.v1.charts import reconstruct_chart_calculation_result

        calc_result = reconstruct_chart_calculation_result(chart).model_dump()
        eval_result = AstrologyRuleEngine.evaluate(calc_result)
        return {
            "chart_id": chart.id,
            "rules_version": eval_result["rules_version"],
            "planetary_analyses": eval_result["planetary_analyses"],
            "yogas": eval_result["yogas"],
            "aspects": eval_result["aspects"],
            "summary": eval_result["summary"],
        }

    def _search_vedic_knowledge(self, args: dict[str, Any]) -> dict[str, Any]:
        validated = SearchKnowledgeInput.model_validate(args)
        results = global_knowledge_store.search(validated.query, top_k=validated.top_k)
        return {
            "query": validated.query,
            "results_count": len(results),
            "citations": [
                {
                    "chunk_id": r["chunk_id"],
                    "citation": r["citation_label"],
                    "topic": r["topic"],
                    "content": r["content"],
                }
                for r in results
            ],
        }
