from typing_extensions import TypedDict


class CombustionResult(TypedDict):
    is_combust: bool
    angular_distance_deg: float
    combustion_orb_deg: float


# Classical combustion limits (degrees from Sun)
# Format: (direct_orb_deg, retrograde_orb_deg)
COMBUSTION_ORBS = {
    "Moon": (12.0, 12.0),
    "Mars": (17.0, 17.0),
    "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0),
    "Venus": (10.0, 8.0),
    "Saturn": (15.0, 15.0),
}


def calculate_angular_separation(long1: float, long2: float) -> float:
    """Calculate the shortest angular separation between two ecliptic longitudes (0 to 180°)."""
    diff = abs(long1 - long2) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


def check_combustion(
    planet_id: str,
    planet_longitude: float,
    is_retrograde: bool,
    sun_longitude: float,
) -> CombustionResult:
    """
    Deterministically determines if a planet is in combustion (Asta) with the Sun.
    Sun, Rahu, and Ketu are not subject to combustion.
    """
    if planet_id in ("Sun", "Rahu", "Ketu"):
        return {
            "is_combust": False,
            "angular_distance_deg": 0.0,
            "combustion_orb_deg": 0.0,
        }

    orbs = COMBUSTION_ORBS.get(planet_id)
    if not orbs:
        return {
            "is_combust": False,
            "angular_distance_deg": 0.0,
            "combustion_orb_deg": 0.0,
        }

    direct_orb, retro_orb = orbs
    effective_orb = retro_orb if is_retrograde else direct_orb

    separation = calculate_angular_separation(planet_longitude, sun_longitude)
    is_combust = separation <= effective_orb

    return {
        "is_combust": is_combust,
        "angular_distance_deg": round(separation, 4),
        "combustion_orb_deg": effective_orb,
    }
