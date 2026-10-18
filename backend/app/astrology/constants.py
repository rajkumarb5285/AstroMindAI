# ==============================================================================
# AstroMind AI - Vedic Astrology Constants & Standard Definitions
# ==============================================================================

from typing_extensions import TypedDict


class SignInfo(TypedDict):
    number: int
    sanskrit: str
    english: str
    ruler: str
    element: str


class NakshatraInfo(TypedDict):
    index: int
    name: str
    ruler: str
    start_deg: float


class PlanetDef(TypedDict):
    id: str
    sanskrit: str
    swe_id: int | None


class DashaDuration(TypedDict):
    lord: str
    years: float


# 12 Vedic Rashi (Zodiac Signs)
ZODIAC_SIGNS: list[SignInfo] = [
    {"number": 1, "sanskrit": "Mesha", "english": "Aries", "ruler": "Mars", "element": "Fire"},
    {"number": 2, "sanskrit": "Vrishabha", "english": "Taurus", "ruler": "Venus", "element": "Earth"},
    {"number": 3, "sanskrit": "Mithuna", "english": "Gemini", "ruler": "Mercury", "element": "Air"},
    {"number": 4, "sanskrit": "Karka", "english": "Cancer", "ruler": "Moon", "element": "Water"},
    {"number": 5, "sanskrit": "Simha", "english": "Leo", "ruler": "Sun", "element": "Fire"},
    {"number": 6, "sanskrit": "Kanya", "english": "Virgo", "ruler": "Mercury", "element": "Earth"},
    {"number": 7, "sanskrit": "Tula", "english": "Libra", "ruler": "Venus", "element": "Air"},
    {"number": 8, "sanskrit": "Vrishchika", "english": "Scorpio", "ruler": "Mars", "element": "Water"},
    {"number": 9, "sanskrit": "Dhanu", "english": "Sagittarius", "ruler": "Jupiter", "element": "Fire"},
    {"number": 10, "sanskrit": "Makara", "english": "Capricorn", "ruler": "Saturn", "element": "Earth"},
    {"number": 11, "sanskrit": "Kumbha", "english": "Aquarius", "ruler": "Saturn", "element": "Air"},
    {"number": 12, "sanskrit": "Meena", "english": "Pisces", "ruler": "Jupiter", "element": "Water"},
]

# 27 Nakshatras (Lunar Mansions) - 13°20' (13.333333°) span each
NAKSHATRAS: list[NakshatraInfo] = [
    {"index": 0, "name": "Ashwini", "ruler": "Ketu", "start_deg": 0.0},
    {"index": 1, "name": "Bharani", "ruler": "Venus", "start_deg": 13.333333333333334},
    {"index": 2, "name": "Krittika", "ruler": "Sun", "start_deg": 26.666666666666668},
    {"index": 3, "name": "Rohini", "ruler": "Moon", "start_deg": 40.0},
    {"index": 4, "name": "Mrigashira", "ruler": "Mars", "start_deg": 53.333333333333336},
    {"index": 5, "name": "Ardra", "ruler": "Rahu", "start_deg": 66.66666666666667},
    {"index": 6, "name": "Punarvasu", "ruler": "Jupiter", "start_deg": 80.0},
    {"index": 7, "name": "Pushya", "ruler": "Saturn", "start_deg": 93.33333333333333},
    {"index": 8, "name": "Ashlesha", "ruler": "Mercury", "start_deg": 106.66666666666667},
    {"index": 9, "name": "Magha", "ruler": "Ketu", "start_deg": 120.0},
    {"index": 10, "name": "Purva Phalguni", "ruler": "Venus", "start_deg": 133.33333333333334},
    {"index": 11, "name": "Uttara Phalguni", "ruler": "Sun", "start_deg": 146.66666666666666},
    {"index": 12, "name": "Hasta", "ruler": "Moon", "start_deg": 160.0},
    {"index": 13, "name": "Chitra", "ruler": "Mars", "start_deg": 173.33333333333334},
    {"index": 14, "name": "Swati", "ruler": "Rahu", "start_deg": 186.66666666666666},
    {"index": 15, "name": "Vishakha", "ruler": "Jupiter", "start_deg": 200.0},
    {"index": 16, "name": "Anuradha", "ruler": "Saturn", "start_deg": 213.33333333333334},
    {"index": 17, "name": "Jyeshtha", "ruler": "Mercury", "start_deg": 226.66666666666666},
    {"index": 18, "name": "Mula", "ruler": "Ketu", "start_deg": 240.0},
    {"index": 19, "name": "Purva Ashadha", "ruler": "Venus", "start_deg": 253.33333333333334},
    {"index": 20, "name": "Uttara Ashadha", "ruler": "Sun", "start_deg": 266.6666666666667},
    {"index": 21, "name": "Shravana", "ruler": "Moon", "start_deg": 280.0},
    {"index": 22, "name": "Dhanishta", "ruler": "Mars", "start_deg": 293.3333333333333},
    {"index": 23, "name": "Shatabhisha", "ruler": "Rahu", "start_deg": 306.6666666666667},
    {"index": 24, "name": "Purva Bhadrapada", "ruler": "Jupiter", "start_deg": 320.0},
    {"index": 25, "name": "Uttara Bhadrapada", "ruler": "Saturn", "start_deg": 333.3333333333333},
    {"index": 26, "name": "Revati", "ruler": "Mercury", "start_deg": 346.6666666666667},
]

# 9 Vedic Grahas (Celestial Bodies)
PLANETS: list[PlanetDef] = [
    {"id": "Sun", "sanskrit": "Surya", "swe_id": 0},
    {"id": "Moon", "sanskrit": "Chandra", "swe_id": 1},
    {"id": "Mars", "sanskrit": "Mangala", "swe_id": 4},
    {"id": "Mercury", "sanskrit": "Budha", "swe_id": 2},
    {"id": "Jupiter", "sanskrit": "Guru", "swe_id": 5},
    {"id": "Venus", "sanskrit": "Shukra", "swe_id": 3},
    {"id": "Saturn", "sanskrit": "Shani", "swe_id": 6},
    {"id": "Rahu", "sanskrit": "Rahu", "swe_id": 10},  # Mean/True Lunar Node
    {"id": "Ketu", "sanskrit": "Ketu", "swe_id": None},  # Derived 180° opposite Rahu
]

# Vimshottari Dasha Order & Standard Durations (Total 120 solar years)
VIMSHOTTARI_DURATIONS: list[DashaDuration] = [
    {"lord": "Ketu", "years": 7.0},
    {"lord": "Venus", "years": 20.0},
    {"lord": "Sun", "years": 6.0},
    {"lord": "Moon", "years": 10.0},
    {"lord": "Mars", "years": 7.0},
    {"lord": "Rahu", "years": 18.0},
    {"lord": "Jupiter", "years": 16.0},
    {"lord": "Saturn", "years": 19.0},
    {"lord": "Mercury", "years": 17.0},
]

DAYS_PER_YEAR = 365.25  # Standard tropical solar year length for dasha boundaries
