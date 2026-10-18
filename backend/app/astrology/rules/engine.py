from typing import Any

from typing_extensions import TypedDict

from backend.app.astrology.rules.aspects import AspectResult, evaluate_planetary_aspects
from backend.app.astrology.rules.combustion import CombustionResult, check_combustion
from backend.app.astrology.rules.dignities import DignityType, calculate_dignity
from backend.app.astrology.rules.yogas import YogaResult, evaluate_classical_yogas


class PlanetaryRuleAnalysis(TypedDict):
    planet_id: str
    dignity: DignityType
    combustion: CombustionResult
    house: int | None
    sign: str
    degree_in_sign: float


class ChartRuleEvaluationResult(TypedDict):
    rules_version: str
    planetary_analyses: list[PlanetaryRuleAnalysis]
    aspects: list[AspectResult]
    yogas: list[YogaResult]
    summary: dict[str, Any]


class AstrologyRuleEngine:
    """
    Deterministic Vedic Interpretation Rule Engine.
    Evaluates planetary dignities, combustions, aspects, and yogas without any AI guessing.
    """

    RULES_VERSION = "vedic_rules_v1.0"

    @classmethod
    def evaluate(cls, calculation_result: dict[str, Any]) -> ChartRuleEvaluationResult:
        """
        Evaluates the full suite of classical rules on a verified chart calculation payload.
        """
        planets = calculation_result.get("planets", [])
        asc_sign_num = calculation_result.get("ascendant_sign_number") or 1

        # Extract Sun's longitude for combustion evaluations
        sun_planet = next((p for p in planets if p.get("planet_id") == "Sun"), None)
        sun_long = sun_planet.get("longitude", 0.0) if sun_planet else 0.0

        planet_house_map: dict[str, int] = {}
        planet_sign_map: dict[str, int] = {}
        planetary_analyses: list[PlanetaryRuleAnalysis] = []

        for p in planets:
            p_id = p.get("planet_id", "")
            sign_num = p.get("sign_number", 1)
            deg_in_sign = p.get("degree_in_sign", 0.0)
            p_long = p.get("longitude", 0.0)
            is_retro = p.get("is_retrograde", False)
            house = p.get("house_number")

            if house is not None:
                planet_house_map[p_id] = house
            planet_sign_map[p_id] = sign_num

            # 1. Dignity
            dignity = calculate_dignity(p_id, sign_num, deg_in_sign)

            # 2. Combustion
            comb = check_combustion(p_id, p_long, is_retro, sun_long)

            planetary_analyses.append(
                {
                    "planet_id": p_id,
                    "dignity": dignity,
                    "combustion": comb,
                    "house": house,
                    "sign": p.get("sign_name", ""),
                    "degree_in_sign": round(deg_in_sign, 2),
                }
            )

        # 3. Aspects (Parashari Graha Drishti)
        aspects = evaluate_planetary_aspects(planet_house_map)

        # 4. Yogas
        yogas = evaluate_classical_yogas(asc_sign_num, planet_house_map, planet_sign_map)

        # Summary statistics
        exalted_planets = [pa["planet_id"] for pa in planetary_analyses if pa["dignity"] == "exalted"]
        debilitated_planets = [pa["planet_id"] for pa in planetary_analyses if pa["dignity"] == "debilitated"]
        combust_planets = [pa["planet_id"] for pa in planetary_analyses if pa["combustion"]["is_combust"]]

        return {
            "rules_version": cls.RULES_VERSION,
            "planetary_analyses": planetary_analyses,
            "aspects": aspects,
            "yogas": yogas,
            "summary": {
                "exalted_count": len(exalted_planets),
                "exalted_planets": exalted_planets,
                "debilitated_count": len(debilitated_planets),
                "debilitated_planets": debilitated_planets,
                "combust_count": len(combust_planets),
                "combust_planets": combust_planets,
                "total_yogas_formed": len(yogas),
            },
        }
