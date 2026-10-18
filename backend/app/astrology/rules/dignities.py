from typing import Literal

DignityType = Literal[
    "exalted",
    "moolatrikona",
    "own_sign",
    "great_friend",
    "friend",
    "neutral",
    "enemy",
    "great_enemy",
    "debilitated",
]

# Classical Parashari Exaltation and Debilitation points (Degree within sign)
# Format: {planet_id: (exalt_sign_num, deep_exalt_deg, debil_sign_num, deep_debil_deg)}
EXALTATION_DEBILITATION = {
    "Sun": (1, 10.0, 7, 10.0),  # Aries 10° / Libra 10°
    "Moon": (2, 3.0, 8, 3.0),  # Taurus 3° / Scorpio 3°
    "Mars": (10, 28.0, 4, 28.0),  # Capricorn 28° / Cancer 28°
    "Mercury": (6, 15.0, 12, 15.0),  # Virgo 15° / Pisces 15°
    "Jupiter": (4, 5.0, 10, 5.0),  # Cancer 5° / Capricorn 5°
    "Venus": (12, 27.0, 6, 27.0),  # Pisces 27° / Virgo 27°
    "Saturn": (7, 20.0, 1, 20.0),  # Libra 20° / Aries 20°
    "Rahu": (2, 20.0, 8, 20.0),  # Taurus / Scorpio (Classical school)
    "Ketu": (8, 20.0, 2, 20.0),  # Scorpio / Taurus
}

# Own signs for each planet (Sign numbers 1 to 12)
OWN_SIGNS = {
    "Sun": [5],  # Leo
    "Moon": [4],  # Cancer
    "Mars": [1, 8],  # Aries, Scorpio
    "Mercury": [3, 6],  # Gemini, Virgo
    "Jupiter": [9, 12],  # Sagittarius, Pisces
    "Venus": [2, 7],  # Taurus, Libra
    "Saturn": [10, 11],  # Capricorn, Aquarius
    "Rahu": [11],  # Aquarius co-lord
    "Ketu": [8],  # Scorpio co-lord
}

# Moolatrikona definitions: (sign_number, start_deg, end_deg)
MOOLATRIKONA = {
    "Sun": (5, 0.0, 20.0),  # Leo 0° - 20°
    "Moon": (2, 3.0, 30.0),  # Taurus 3° - 30°
    "Mars": (1, 0.0, 12.0),  # Aries 0° - 12°
    "Mercury": (6, 15.0, 20.0),  # Virgo 15° - 20°
    "Jupiter": (9, 0.0, 10.0),  # Sagittarius 0° - 10°
    "Venus": (7, 0.0, 15.0),  # Libra 0° - 15°
    "Saturn": (11, 0.0, 20.0),  # Aquarius 0° - 20°
}

# Natural Relationships according to Brihat Parashara Hora Shastra
# Format: {planet: {"friends": [...], "neutrals": [...], "enemies": [...]}}
NATURAL_RELATIONSHIPS = {
    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "neutrals": ["Mercury"],
        "enemies": ["Venus", "Saturn", "Rahu", "Ketu"],
    },
    "Moon": {
        "friends": ["Sun", "Mercury"],
        "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"],
        "enemies": ["Rahu", "Ketu"],
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter"],
        "neutrals": ["Venus", "Saturn"],
        "enemies": ["Mercury", "Rahu", "Ketu"],
    },
    "Mercury": {
        "friends": ["Sun", "Venus"],
        "neutrals": ["Mars", "Jupiter", "Saturn"],
        "enemies": ["Moon"],
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "neutrals": ["Saturn"],
        "enemies": ["Mercury", "Venus"],
    },
    "Venus": {
        "friends": ["Mercury", "Saturn", "Rahu", "Ketu"],
        "neutrals": ["Mars", "Jupiter"],
        "enemies": ["Sun", "Moon"],
    },
    "Saturn": {
        "friends": ["Mercury", "Venus", "Rahu"],
        "neutrals": ["Jupiter"],
        "enemies": ["Sun", "Moon", "Mars"],
    },
    "Rahu": {
        "friends": ["Venus", "Saturn", "Mercury"],
        "neutrals": ["Jupiter"],
        "enemies": ["Sun", "Moon", "Mars"],
    },
    "Ketu": {
        "friends": ["Mars", "Venus", "Jupiter"],
        "neutrals": ["Mercury", "Saturn"],
        "enemies": ["Sun", "Moon"],
    },
}

SIGN_LORDS = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter",
}


def calculate_dignity(planet_id: str, sign_number: int, degree_in_sign: float) -> DignityType:
    """
    Deterministically evaluates the classical Parashari planetary dignity.
    Priority order:
    1. Exalted
    2. Debilitated
    3. Moolatrikona
    4. Own Sign
    5. Natural Friend / Neutral / Enemy based on Sign Lord
    """
    if planet_id not in EXALTATION_DEBILITATION:
        return "neutral"

    exalt_sign, _, debil_sign, _ = EXALTATION_DEBILITATION[planet_id]

    # 1. Check Exaltation
    if sign_number == exalt_sign:
        return "exalted"

    # 2. Check Debilitation
    if sign_number == debil_sign:
        return "debilitated"

    # 3. Check Moolatrikona
    if planet_id in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet_id]
        if sign_number == mt_sign and mt_start <= degree_in_sign <= mt_end:
            return "moolatrikona"

    # 4. Check Own Sign
    if planet_id in OWN_SIGNS and sign_number in OWN_SIGNS[planet_id]:
        return "own_sign"

    # 5. Relationship with Sign Lord
    sign_lord = SIGN_LORDS.get(sign_number)
    if not sign_lord or sign_lord == planet_id:
        return "own_sign"

    rel = NATURAL_RELATIONSHIPS.get(planet_id, {})
    if sign_lord in rel.get("friends", []):
        return "friend"
    elif sign_lord in rel.get("enemies", []):
        return "enemy"
    else:
        return "neutral"
