from typing_extensions import TypedDict


class AspectResult(TypedDict):
    source_planet: str
    from_house: int
    aspected_houses: list[int]
    aspected_planets: list[str]


# Classical Parashari full aspects (relative house offset, 1-indexed count)
# e.g. 7th house aspect means (from_house + 6) % 12
PARASHARI_ASPECT_OFFSETS = {
    "Sun": [7],
    "Moon": [7],
    "Mercury": [7],
    "Venus": [7],
    "Mars": [4, 7, 8],  # 4th, 7th, 8th special aspects
    "Jupiter": [5, 7, 9],  # 5th, 7th, 9th special aspects (Trikona)
    "Saturn": [3, 7, 10],  # 3rd, 7th, 10th special aspects
    "Rahu": [5, 7, 9],  # 5th, 7th, 9th aspects
    "Ketu": [5, 7, 9],  # 5th, 7th, 9th aspects
}


def calculate_aspected_house(from_house: int, aspect_offset: int) -> int:
    """Calculates the target 1-based house number for a given Parashari aspect offset."""
    # e.g. from H1, 7th aspect = (1 + 7 - 1 - 1) % 12 + 1 = 7
    return ((from_house - 1 + (aspect_offset - 1)) % 12) + 1


def evaluate_planetary_aspects(
    planet_house_map: dict[str, int],
) -> list[AspectResult]:
    """
    Evaluates full Parashari aspects for all planets in the chart.
    planet_house_map: {planet_id: house_number (1..12)}
    """
    results: list[AspectResult] = []

    # Invert mapping: house_number -> list of occupying planets
    house_occupants: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for planet, house in planet_house_map.items():
        if 1 <= house <= 12:
            house_occupants[house].append(planet)

    for planet, from_house in planet_house_map.items():
        offsets = PARASHARI_ASPECT_OFFSETS.get(planet, [7])
        target_houses: list[int] = []
        target_planets: list[str] = []

        for offset in offsets:
            target_h = calculate_aspected_house(from_house, offset)
            target_houses.append(target_h)
            # Find planets sitting in target house
            occupants = house_occupants.get(target_h, [])
            for occ in occupants:
                if occ != planet:
                    target_planets.append(occ)

        results.append(
            {
                "source_planet": planet,
                "from_house": from_house,
                "aspected_houses": target_houses,
                "aspected_planets": target_planets,
            }
        )

    return results
