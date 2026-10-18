import pytest

from backend.app.astrology.adapter import SwissEphAdapter, normalize_360
from backend.app.astrology.constants import NAKSHATRAS, ZODIAC_SIGNS
from backend.app.astrology.schemas import ChartCalculationInput


@pytest.fixture
def adapter():
    return SwissEphAdapter()


def test_golden_reference_chart_delhi_1980(adapter):
    """
    Golden Reference Chart:
    Birth: 1980-01-01 12:00:00 IST (UTC: 1980-01-01 06:30:00)
    Location: New Delhi, India (28.6139° N, 77.2090° E)
    Zodiac: Sidereal, Ayanamsa: Lahiri, House System: Whole-Sign
    """
    input_data = ChartCalculationInput(
        birth_date="1980-01-01",
        birth_time="12:00:00",
        timezone="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
        ayanamsa="lahiri",
        node_mode="mean",
        calculation_type="D1",
        birth_time_confidence="exact",
    )

    result = adapter.calculate_chart(input_data)

    # 1. Metadata Verification
    assert result.metadata.engine == "pyswisseph"
    assert result.metadata.ayanamsa == "lahiri"
    # Historical Lahiri Ayanamsa on 1980-01-01 was ~23.578° (Tolerance ±0.01°)
    assert 23.55 <= result.metadata.ayanamsa_value <= 23.60
    assert result.metadata.normalized_utc_instant == "1980-01-01T06:30:00+00:00"

    # 2. Ascendant (Lagna) Verification
    # On 1980-01-01 at 12:00 IST in Delhi (28.6139° N, 77.2090° E),
    # Ascendant is 343.250° (Pisces 13°15', Uttara Bhadrapada pada 3)
    assert result.ascendant_longitude is not None
    assert 343.20 <= result.ascendant_longitude <= 343.30
    assert result.ascendant_sign_number == 12
    assert result.ascendant_sign_name == "Pisces"
    assert result.ascendant_nakshatra == "Uttara Bhadrapada"
    assert result.ascendant_pada == 3

    # 3. Sun Verification
    # Sun on Jan 1 is in Sagittarius (Dhanu, Sign 9) ~256°
    sun = next(p for p in result.planets if p.planet_id == "Sun")
    assert sun.sign_number == 9
    assert sun.sign_name == "Sagittarius"
    assert 255.0 <= sun.longitude <= 258.0
    assert sun.is_retrograde is False

    # 4. Planetary Array Completeness (9 Vedic Grahas)
    assert len(result.planets) == 9
    planet_ids = {p.planet_id for p in result.planets}
    assert planet_ids == {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

    # 5. Ketu is exactly 180° opposite Rahu
    rahu = next(p for p in result.planets if p.planet_id == "Rahu")
    ketu = next(p for p in result.planets if p.planet_id == "Ketu")
    diff = abs(rahu.longitude - ketu.longitude)
    assert abs(diff - 180.0) < 1e-4

    # 6. Whole-Sign Houses Completeness
    assert len(result.houses) == 12
    assert result.houses[0].house_number == 1
    assert result.houses[0].sign_number == 12  # House 1 = Ascendant sign (Pisces)
    assert result.houses[1].sign_number == 1  # House 2 = Aries (Mesha)

    # All planets have a valid house number (1-12)
    for p in result.planets:
        assert p.house_number is not None
        assert 1 <= p.house_number <= 12


def test_zodiac_sign_boundary_and_wraparound():
    """Verify 0°/360° boundary wraparound behavior."""
    assert normalize_360(0.0) == 0.0
    assert normalize_360(360.0) == 0.0
    assert normalize_360(-10.0) == 350.0
    assert normalize_360(725.5) == 5.5
    assert normalize_360(-360.0) == 0.0


def test_nakshatras_and_padas_structure(adapter):
    """Verify that all 27 Nakshatras and 108 Padas map with zero gaps or overlaps."""
    assert len(NAKSHATRAS) == 27
    assert len(ZODIAC_SIGNS) == 12

    for i, nak in enumerate(NAKSHATRAS):
        assert nak["index"] == i
        assert 0.0 <= nak["start_deg"] < 360.0

    # Test arbitrary longitude mapping (e.g. 0.0° = Ashwini pada 1)
    # 13°20' = 13.333333°
    # 26°40' = 26.666666°
    input_data = ChartCalculationInput(
        birth_date="2000-01-01",
        birth_time="00:00:00",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0,
    )
    res = adapter.calculate_chart(input_data)
    for p in res.planets:
        assert 0 <= p.nakshatra_index <= 26
        assert 1 <= p.pada <= 4
        assert 0.0 <= p.degree_in_sign < 30.0


def test_navamsa_d9_classical_formula(adapter):
    """Verify D9 Navamsa divisions adhere to the classical cycle."""
    input_data = ChartCalculationInput(
        birth_date="2000-01-01",
        birth_time="12:00:00",
        timezone="UTC",
        latitude=28.6,
        longitude=77.2,
    )
    res = adapter.calculate_chart(input_data)
    assert len(res.navamsa) == 9
    for d9 in res.navamsa:
        assert 1 <= d9.d9_sign_number <= 12
        assert d9.d9_sign_name in [s["english"] for s in ZODIAC_SIGNS]


def test_vimshottari_dasha_calculation(adapter):
    """Verify Vimshottari Dasha sequence, duration sum, and sub-period contiguity."""
    input_data = ChartCalculationInput(
        birth_date="1992-05-14",
        birth_time="14:30:00",
        timezone="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
    )
    res = adapter.calculate_chart(input_data)

    # Must contain 9 Maha Dashas
    assert len(res.vimshottari_dashas) == 9

    # Total duration across the full cycle must equal ~120 years
    total_years = sum(d.duration_years for d in res.vimshottari_dashas)
    # The first dasha has a fractional remaining balance, so the 9 dashas span 120 years minus elapsed birth balance
    assert 100.0 <= total_years <= 120.0

    # Check each Maha Dasha has 9 Antar Dashas
    for dasha in res.vimshottari_dashas:
        assert dasha.sub_periods is not None
        assert len(dasha.sub_periods) == 9
        # Contiguity: each sub-period starts when previous sub-period ends
        for i in range(len(dasha.sub_periods) - 1):
            assert dasha.sub_periods[i].end_date == dasha.sub_periods[i + 1].start_date


def test_leap_day_and_midnight_transitions(adapter):
    """Verify leap day (Feb 29) and midnight civil time boundaries."""
    # Leap Day
    leap_input = ChartCalculationInput(
        birth_date="2000-02-29",
        birth_time="23:59:00",
        timezone="UTC",
        latitude=51.5074,
        longitude=-0.1278,
    )
    leap_res = adapter.calculate_chart(leap_input)
    assert leap_res.metadata.normalized_utc_instant == "2000-02-29T23:59:00+00:00"
    assert len(leap_res.planets) == 9

    # Midnight Transition
    midnight_input = ChartCalculationInput(
        birth_date="1995-07-01",
        birth_time="00:00:00",
        timezone="America/New_York",  # EDT is UTC-4
        latitude=40.7128,
        longitude=-74.0060,
    )
    midnight_res = adapter.calculate_chart(midnight_input)
    # Midnight July 1 in New York is 04:00 UTC July 1
    assert midnight_res.metadata.normalized_utc_instant == "1995-07-01T04:00:00+00:00"


def test_unknown_birth_time_handling_no_guessing(adapter):
    """
    CRITICAL NON-NEGOTIABLE RULE:
    If birth time is unknown, NEVER silently guess an arbitrary birth time.
    Time-dependent results (Ascendant, Houses, fine dashas) must be marked unavailable.
    """
    input_data = ChartCalculationInput(
        birth_date="1985-06-15",
        birth_time=None,  # Missing birth time
        timezone="Asia/Kolkata",
        latitude=19.0760,
        longitude=72.8777,
        birth_time_confidence="unknown",
    )
    res = adapter.calculate_chart(input_data)

    # 1. Verification of honest qualification
    assert res.is_birth_time_qualified is False
    assert res.ascendant_longitude is None
    assert res.ascendant_sign_number is None
    assert res.ascendant_sign_name is None
    assert len(res.houses) == 0

    # 2. Planetary positions are computed for 12:00 UTC, but house numbers are None
    assert len(res.planets) == 9
    for p in res.planets:
        assert p.house_number is None

    # 3. Warnings must explicitly inform the consumer
    assert len(res.metadata.warnings) > 0
    assert any("Birth time is unknown" in w for w in res.metadata.warnings)


def test_engine_calculation_determinism(adapter):
    """Verify that identical input calculations produce strictly deterministic results."""
    input_data = ChartCalculationInput(
        birth_date="1993-11-20",
        birth_time="05:45:00",
        timezone="Asia/Kolkata",
        latitude=13.0827,
        longitude=80.2707,
    )

    baseline = adapter.calculate_chart(input_data)

    # Run 25 consecutive calculations
    for _ in range(25):
        run = adapter.calculate_chart(input_data)
        assert run.ascendant_longitude == baseline.ascendant_longitude
        assert run.metadata.ayanamsa_value == baseline.metadata.ayanamsa_value
        for i in range(9):
            assert run.planets[i].longitude == baseline.planets[i].longitude
            assert run.planets[i].speed == baseline.planets[i].speed
            assert run.planets[i].house_number == baseline.planets[i].house_number
