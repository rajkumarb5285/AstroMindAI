from backend.app.astrology.rules.aspects import calculate_aspected_house, evaluate_planetary_aspects
from backend.app.astrology.rules.combustion import check_combustion
from backend.app.astrology.rules.dignities import calculate_dignity
from backend.app.astrology.rules.engine import AstrologyRuleEngine
from backend.app.astrology.rules.yogas import evaluate_classical_yogas


def test_planetary_dignity_exaltation_and_debilitation():
    # Sun exalted in Aries (sign 1), debilitated in Libra (sign 7)
    assert calculate_dignity("Sun", sign_number=1, degree_in_sign=10.0) == "exalted"
    assert calculate_dignity("Sun", sign_number=7, degree_in_sign=10.0) == "debilitated"

    # Moon exalted in Taurus (sign 2), debilitated in Scorpio (sign 8)
    assert calculate_dignity("Moon", sign_number=2, degree_in_sign=3.0) == "exalted"
    assert calculate_dignity("Moon", sign_number=8, degree_in_sign=3.0) == "debilitated"

    # Jupiter exalted in Cancer (sign 4), debilitated in Capricorn (sign 10)
    assert calculate_dignity("Jupiter", sign_number=4, degree_in_sign=5.0) == "exalted"
    assert calculate_dignity("Jupiter", sign_number=10, degree_in_sign=5.0) == "debilitated"

    # Venus exalted in Pisces (sign 12), debilitated in Virgo (sign 6)
    assert calculate_dignity("Venus", sign_number=12, degree_in_sign=27.0) == "exalted"
    assert calculate_dignity("Venus", sign_number=6, degree_in_sign=27.0) == "debilitated"

    # Saturn exalted in Libra (sign 7), debilitated in Aries (sign 1)
    assert calculate_dignity("Saturn", sign_number=7, degree_in_sign=20.0) == "exalted"
    assert calculate_dignity("Saturn", sign_number=1, degree_in_sign=20.0) == "debilitated"


def test_moolatrikona_vs_own_sign():
    # Sun in Leo (sign 5): 0° to 20° is Moolatrikona, 20° to 30° is Own Sign
    assert calculate_dignity("Sun", sign_number=5, degree_in_sign=10.0) == "moolatrikona"
    assert calculate_dignity("Sun", sign_number=5, degree_in_sign=25.0) == "own_sign"

    # Jupiter in Sagittarius (sign 9): 0° to 10° is Moolatrikona, 10° to 30° is Own Sign
    assert calculate_dignity("Jupiter", sign_number=9, degree_in_sign=5.0) == "moolatrikona"
    assert calculate_dignity("Jupiter", sign_number=9, degree_in_sign=18.0) == "own_sign"


def test_combustion_calculations():
    sun_long = 120.0  # Sun at 120° (Leo 0°)

    # Moon within 12° -> Combust
    moon_combust = check_combustion("Moon", planet_longitude=126.0, is_retrograde=False, sun_longitude=sun_long)
    assert moon_combust["is_combust"] is True
    assert moon_combust["angular_distance_deg"] == 6.0

    # Moon at 135° (15° away) -> Direct, Not Combust
    moon_free = check_combustion("Moon", planet_longitude=135.0, is_retrograde=False, sun_longitude=sun_long)
    assert moon_free["is_combust"] is False

    # Jupiter within 11° -> Combust
    jupiter_combust = check_combustion("Jupiter", planet_longitude=128.0, is_retrograde=False, sun_longitude=sun_long)
    assert jupiter_combust["is_combust"] is True

    # Sun itself or Rahu/Ketu cannot be combust
    assert check_combustion("Sun", 120.0, False, 120.0)["is_combust"] is False
    assert check_combustion("Rahu", 120.0, False, 120.0)["is_combust"] is False


def test_parashari_aspects_graha_drishti():
    # Helper to calculate aspect house
    assert calculate_aspected_house(from_house=1, aspect_offset=7) == 7
    assert calculate_aspected_house(from_house=10, aspect_offset=7) == 4
    assert calculate_aspected_house(from_house=1, aspect_offset=4) == 4
    assert calculate_aspected_house(from_house=1, aspect_offset=8) == 8

    # Mars in H1 aspects 4, 7, 8
    # Jupiter in H4 aspects 8, 10, 12 (5th, 7th, 9th from H4)
    planet_house_map = {
        "Mars": 1,
        "Jupiter": 4,
        "Saturn": 7,
    }
    aspects = evaluate_planetary_aspects(planet_house_map)

    mars_aspect = next(a for a in aspects if a["source_planet"] == "Mars")
    assert mars_aspect["aspected_houses"] == [4, 7, 8]
    assert "Jupiter" in mars_aspect["aspected_planets"]  # Jupiter is in H4
    assert "Saturn" in mars_aspect["aspected_planets"]  # Saturn is in H7

    saturn_aspect = next(a for a in aspects if a["source_planet"] == "Saturn")
    # Saturn in H7 aspects H9 (3rd), H1 (7th), H4 (10th)
    assert saturn_aspect["aspected_houses"] == [9, 1, 4]
    assert "Mars" in saturn_aspect["aspected_planets"]  # Mars is in H1


def test_classical_yogas():
    # 1. Gaja Kesari: Jupiter in H4, Moon in H1 (Kendra from Moon)
    yogas_gk = evaluate_classical_yogas(
        ascendant_sign=1,
        planet_house_map={"Moon": 1, "Jupiter": 4},
        planet_sign_map={"Moon": 1, "Jupiter": 4},
    )
    assert any(y["yoga_id"] == "gaja_kesari_yoga" for y in yogas_gk)

    # 2. Budhaditya Yoga: Sun and Mercury in H10
    yogas_ba = evaluate_classical_yogas(
        ascendant_sign=1,
        planet_house_map={"Sun": 10, "Mercury": 10},
        planet_sign_map={"Sun": 10, "Mercury": 10},
    )
    assert any(y["yoga_id"] == "budhaditya_yoga" for y in yogas_ba)

    # 3. Hamsa Yoga (Pancha Mahapurusha): Jupiter in H1 in Sagittarius (sign 9)
    yogas_hamsa = evaluate_classical_yogas(
        ascendant_sign=9,  # Sagittarius Lagna
        planet_house_map={"Jupiter": 1},
        planet_sign_map={"Jupiter": 9},  # Own sign in H1
    )
    assert any(y["name"] == "Hamsa Yoga" for y in yogas_hamsa)

    # 4. Viparita Raja Yoga (Harsha Yoga): 6th lord in 8th house
    # Aries Lagna (sign 1): 6th house is Virgo (sign 6, Lord: Mercury)
    # If Mercury is placed in H8:
    yogas_vry = evaluate_classical_yogas(
        ascendant_sign=1,
        planet_house_map={"Mercury": 8},
        planet_sign_map={"Mercury": 8},
    )
    assert any("Harsha Yoga" in y["name"] for y in yogas_vry)


def test_full_astrology_rule_engine():
    calc_mock = {
        "ascendant_sign_number": 1,
        "ascendant_sign_name": "Aries",
        "planets": [
            {
                "planet_id": "Sun",
                "sign_number": 1,
                "sign_name": "Aries",
                "degree_in_sign": 10.0,
                "longitude": 10.0,
                "is_retrograde": False,
                "house_number": 1,
            },
            {
                "planet_id": "Mercury",
                "sign_number": 1,
                "sign_name": "Aries",
                "degree_in_sign": 14.0,
                "longitude": 14.0,
                "is_retrograde": False,
                "house_number": 1,
            },
            {
                "planet_id": "Moon",
                "sign_number": 2,
                "sign_name": "Taurus",
                "degree_in_sign": 3.0,
                "longitude": 33.0,
                "is_retrograde": False,
                "house_number": 2,
            },
        ],
    }
    result = AstrologyRuleEngine.evaluate(calc_mock)
    assert result["rules_version"] == "vedic_rules_v1.0"
    assert result["summary"]["exalted_count"] == 2  # Sun (Aries) and Moon (Taurus)
    assert any(y["yoga_id"] == "budhaditya_yoga" for y in result["yogas"])
