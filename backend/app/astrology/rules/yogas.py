from typing_extensions import TypedDict

from backend.app.astrology.rules.dignities import EXALTATION_DEBILITATION, OWN_SIGNS, SIGN_LORDS


class YogaResult(TypedDict):
    yoga_id: str
    name: str
    category: str  # "Raja", "Dhana", "Mahapurusha", "Auspicious", "Viparita"
    participating_planets: list[str]
    houses_involved: list[int]
    description: str
    classical_reference: str


def evaluate_classical_yogas(
    ascendant_sign: int,
    planet_house_map: dict[str, int],
    planet_sign_map: dict[str, int],
) -> list[YogaResult]:
    """
    Deterministically evaluates classical Parashari yogas.
    ascendant_sign: sign number 1..12
    planet_house_map: {planet_id: house_number (1..12)}
    planet_sign_map: {planet_id: sign_number (1..12)}
    """
    yogas: list[YogaResult] = []

    # 1. Budhaditya Yoga: Sun and Mercury in same house
    sun_h = planet_house_map.get("Sun")
    mercury_h = planet_house_map.get("Mercury")
    if sun_h and mercury_h and sun_h == mercury_h:
        yogas.append(
            {
                "yoga_id": "budhaditya_yoga",
                "name": "Budhaditya Yoga",
                "category": "Auspicious",
                "participating_planets": ["Sun", "Mercury"],
                "houses_involved": [sun_h],
                "description": "Conjunction of the Sun (soul/vitality) and Mercury (buddhi/intellect) confers sharp analytical skill, eloquence, and reputation.",
                "classical_reference": "Brihat Parashara Hora Shastra, Ch. 35",
            }
        )

    # 2. Gaja Kesari Yoga: Jupiter in Kendra (1, 4, 7, 10) from Moon
    moon_h = planet_house_map.get("Moon")
    jupiter_h = planet_house_map.get("Jupiter")
    if moon_h and jupiter_h:
        # Distance from Moon to Jupiter (1-based counting)
        dist_from_moon = ((jupiter_h - moon_h + 12) % 12) + 1
        if dist_from_moon in (1, 4, 7, 10):
            yogas.append(
                {
                    "yoga_id": "gaja_kesari_yoga",
                    "name": "Gaja Kesari Yoga",
                    "category": "Auspicious",
                    "participating_planets": ["Jupiter", "Moon"],
                    "houses_involved": [moon_h, jupiter_h],
                    "description": "Jupiter in an angular house from the Moon creates the lion-elephant combination, conferring wisdom, virtues, enduring reputation, and moral strength.",
                    "classical_reference": "Phaladeepika, Ch. 6, Verse 26",
                }
            )

    # 3. Pancha Mahapurusha Yogas (Mars, Mercury, Jupiter, Venus, Saturn in Kendra and in Own/Exaltation sign)
    mahapurusha_specs = [
        ("Mars", "Ruchaka Yoga", "Leadership, courage, technical prowess, and physical vitality"),
        ("Mercury", "Bhadra Yoga", "Scholarly excellence, sharp intellect, and high communicative authority"),
        ("Jupiter", "Hamsa Yoga", "Nobility, spiritual knowledge, righteousness, and profound social honor"),
        ("Venus", "Malavya Yoga", "Aesthetic brilliance, refined grace, material prosperity, and marital joy"),
        ("Saturn", "Sasa Yoga", "Patience, mastery of masses, enduring administrative capability, and steadfastness"),
    ]

    for planet, y_name, desc in mahapurusha_specs:
        h = planet_house_map.get(planet)
        s = planet_sign_map.get(planet)
        if h and s and h in (1, 4, 7, 10):
            is_own = s in OWN_SIGNS.get(planet, [])
            is_exalt = s == EXALTATION_DEBILITATION.get(planet, (None,))[0]
            if is_own or is_exalt:
                yogas.append(
                    {
                        "yoga_id": f"{planet.lower()}_mahapurusha",
                        "name": y_name,
                        "category": "Mahapurusha",
                        "participating_planets": [planet],
                        "houses_involved": [h],
                        "description": f"Formed by {planet} placed in an angular house (Kendra {h}) in its {'exalted' if is_exalt else 'own'} sign. {desc}.",
                        "classical_reference": "Brihat Parashara Hora Shastra, Ch. 75",
                    }
                )

    # Map house numbers (1..12) to their ruling signs and Lords
    house_lord_map: dict[int, str] = {}
    for h in range(1, 13):
        sign_of_house = ((ascendant_sign - 1 + (h - 1)) % 12) + 1
        house_lord_map[h] = SIGN_LORDS[sign_of_house]

    # 4. Viparita Raja Yogas (Lords of 6, 8, 12 in 6, 8, 12)
    viparita_specs = [
        (
            6,
            "Harsha Yoga",
            "Lord of 6th house in a Dusthana (6, 8, 12), granting triumph over adversaries and sound resilience",
        ),
        (
            8,
            "Sarala Yoga",
            "Lord of 8th house in a Dusthana (6, 8, 12), giving fearlessness, scholarly insight, and longevity",
        ),
        (
            12,
            "Vimala Yoga",
            "Lord of 12th house in a Dusthana (6, 8, 12), ensuring virtuous expenditures, independence, and inner contentment",
        ),
    ]

    for dusthana_h, v_name, desc in viparita_specs:
        lord = house_lord_map[dusthana_h]
        lord_placed_h = planet_house_map.get(lord)
        if lord_placed_h and lord_placed_h in (6, 8, 12):
            yogas.append(
                {
                    "yoga_id": f"viparita_{lord.lower()}_{dusthana_h}",
                    "name": f"Viparita Raja Yoga ({v_name})",
                    "category": "Viparita",
                    "participating_planets": [lord],
                    "houses_involved": [dusthana_h, lord_placed_h],
                    "description": f"{desc}. The lord of house {dusthana_h} ({lord}) occupies house {lord_placed_h}.",
                    "classical_reference": "Phaladeepika, Ch. 6, Verses 58-69",
                }
            )

    # 5. Kendra-Trikona Raja Yoga (Kendra lords 1, 4, 7, 10 and Trikona lords 1, 5, 9 conjunct)
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]

    conjunction_houses: dict[int, list[str]] = {}
    for p, h in planet_house_map.items():
        if 1 <= h <= 12:
            conjunction_houses.setdefault(h, []).append(p)

    for h, planets in conjunction_houses.items():
        if len(planets) >= 2:
            kendra_lords_here = {p for p in planets if any(house_lord_map[kh] == p for kh in kendra_houses)}
            trikona_lords_here = {p for p in planets if any(house_lord_map[th] == p for th in trikona_houses)}

            # Distinct planets representing Kendra and Trikona
            valid_pairs = kendra_lords_here & trikona_lords_here
            combined = kendra_lords_here | trikona_lords_here
            if len(combined) >= 2 and (kendra_lords_here - trikona_lords_here or len(valid_pairs) >= 2):
                yogas.append(
                    {
                        "yoga_id": f"raja_yoga_h{h}",
                        "name": f"Dharma-Karmadhipati Raja Yoga (House {h})",
                        "category": "Raja",
                        "participating_planets": sorted(combined),
                        "houses_involved": [h],
                        "description": f"Conjunction of Kendra and Trikona lords in house {h} creates a powerful auspicious foundation for leadership, dharmic achievement, and social eminence.",
                        "classical_reference": "Brihat Parashara Hora Shastra, Ch. 34",
                    }
                )
                break  # Record strongest combination once

    return yogas
