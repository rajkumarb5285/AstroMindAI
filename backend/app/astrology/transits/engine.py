from datetime import UTC, datetime
from typing import Any

from typing_extensions import TypedDict

from backend.app.astrology.adapter import SwissEphAdapter
from backend.app.astrology.schemas import ChartCalculationInput


class PlanetaryTransit(TypedDict):
    planet_id: str
    transit_sign_number: int
    transit_sign_name: str
    transit_degree: float
    is_retrograde: bool
    house_from_lagna: int
    house_from_moon: int
    classical_effect: str


class SadeSatiStatus(TypedDict):
    is_active: bool
    phase: str | None  # 'Phase 1: Rising (12th)', 'Phase 2: Peak (Janma)', 'Phase 3: Setting (2nd)'
    description: str


class GocharEvaluationResult(TypedDict):
    transit_timestamp: str
    natal_moon_sign: int
    natal_moon_sign_name: str
    natal_lagna_sign: int
    natal_lagna_sign_name: str
    sade_sati: SadeSatiStatus
    kantaka_shani: bool
    ashtama_shani: bool
    transits: list[PlanetaryTransit]
    summary_highlights: list[str]

ZODIAC_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


class TransitEngine:
    """
    Deterministic Gochar (Transit) Evaluation Engine.
    Computes exact astronomical planetary transits and projects them onto natal Moon and Ascendant.
    """

    @classmethod
    def evaluate_transits(
        cls,
        natal_chart_calc: dict[str, Any],
        transit_dt: datetime | None = None,
        ayanamsa: str = "lahiri",
    ) -> GocharEvaluationResult:
        """
        Evaluates current or target transit planetary positions against a natal chart.
        """
        if transit_dt is None:
            transit_dt = datetime.now(UTC)

        # 1. Identify Natal Moon and Natal Ascendant
        natal_planets = natal_chart_calc.get("planets", [])
        natal_moon = next((p for p in natal_planets if p.get("planet_id") == "Moon"), None)
        natal_moon_sign = natal_moon.get("sign_number", 1) if natal_moon else 1
        natal_lagna_sign = natal_chart_calc.get("ascendant_sign_number") or 1

        # 2. Compute Astronomical Transit Positions via Swiss Ephemeris
        adapter = SwissEphAdapter()
        inp = ChartCalculationInput(
            birth_date=transit_dt.strftime("%Y-%m-%d"),
            birth_time=transit_dt.strftime("%H:%M:%S"),
            timezone="UTC",
            latitude=28.6139,
            longitude=77.2090,
            ayanamsa=ayanamsa,
            node_mode="mean",
            calculation_type="transit",
            birth_time_confidence="exact",
        )
        transit_calc = adapter.calculate_chart(inp)

        transit_planets = transit_calc.planets
        transits_list: list[PlanetaryTransit] = []
        highlights: list[str] = []

        # Find Transit Saturn & Jupiter
        transit_saturn = next((p for p in transit_planets if p.planet_id == "Saturn"), None)
        sat_transit_sign = transit_saturn.sign_number if transit_saturn else 11

        # 3. Sade Sati & Shani Gochar Evaluation
        # Houses from Moon: ((sat_transit_sign - natal_moon_sign) % 12) + 1
        sat_from_moon = ((sat_transit_sign - natal_moon_sign) % 12) + 1
        sade_sati_active = False
        sade_sati_phase = None
        sade_sati_desc = "Saturn is not currently transiting the 12th, 1st, or 2nd house from your natal Moon."

        if sat_from_moon == 12:
            sade_sati_active = True
            sade_sati_phase = "Phase 1: Rising (12th from Moon)"
            sade_sati_desc = "Saturn transits the 12th house from natal Moon, marking the initiation of Sade Sati. Focus on restructuring expenditures, sleep cycles, and foreign connections."
            highlights.append("Sade Sati Phase 1 (Rising) active.")
        elif sat_from_moon == 1:
            sade_sati_active = True
            sade_sati_phase = "Phase 2: Peak (Janma Shani)"
            sade_sati_desc = "Saturn transits over natal Moon (Janma Shani), marking the peak phase of Sade Sati. Demands emotional discipline, patience, and rigorous karmic alignment."
            highlights.append("Sade Sati Phase 2 (Peak / Janma Shani) active.")
        elif sat_from_moon == 2:
            sade_sati_active = True
            sade_sati_phase = "Phase 3: Setting (2nd from Moon)"
            sade_sati_desc = "Saturn transits the 2nd house from natal Moon, concluding Sade Sati. Emphasis on stabilizing finances, family commitments, and speech."
            highlights.append("Sade Sati Phase 3 (Setting) active.")

        kantaka_shani = (sat_from_moon == 4)
        if kantaka_shani:
            highlights.append("Kantaka Shani (Saturn in 4th from Moon) active.")

        ashtama_shani = (sat_from_moon == 8)
        if ashtama_shani:
            highlights.append("Ashtama Shani (Saturn in 8th from Moon) active — exercise prudence in major decisions.")

        # 4. Map Each Transit Planet
        for tp in transit_planets:
            house_from_lagna = ((tp.sign_number - natal_lagna_sign) % 12) + 1
            house_from_moon = ((tp.sign_number - natal_moon_sign) % 12) + 1

            effect = f"Transiting {tp.sign_name} ({house_from_lagna}th from Lagna, {house_from_moon}th from Moon)."
            if tp.planet_id == "Jupiter":
                if house_from_moon in [2, 5, 7, 9, 11]:
                    effect += " Highly auspicious Guru Gochar fostering expansion, wisdom, and opportunities."
                    highlights.append(f"Benefic Jupiter Transit in {house_from_moon}th house from Moon.")
                else:
                    effect += " Transformative Jupiter Transit calling for inner introspection."

            transits_list.append({
                "planet_id": tp.planet_id,
                "transit_sign_number": tp.sign_number,
                "transit_sign_name": tp.sign_name,
                "transit_degree": round(tp.degree_in_sign, 2),
                "is_retrograde": tp.is_retrograde,
                "house_from_lagna": house_from_lagna,
                "house_from_moon": house_from_moon,
                "classical_effect": effect,
            })

        return {
            "transit_timestamp": transit_dt.isoformat(),
            "natal_moon_sign": natal_moon_sign,
            "natal_moon_sign_name": ZODIAC_NAMES[natal_moon_sign - 1],
            "natal_lagna_sign": natal_lagna_sign,
            "natal_lagna_sign_name": ZODIAC_NAMES[natal_lagna_sign - 1],
            "sade_sati": {
                "is_active": sade_sati_active,
                "phase": sade_sati_phase,
                "description": sade_sati_desc,
            },
            "kantaka_shani": kantaka_shani,
            "ashtama_shani": ashtama_shani,
            "transits": transits_list,
            "summary_highlights": highlights,
        }
