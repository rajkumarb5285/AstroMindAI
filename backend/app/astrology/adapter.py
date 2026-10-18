import zoneinfo
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

import swisseph as swe

from backend.app.astrology.constants import (
    DAYS_PER_YEAR,
    NAKSHATRAS,
    PLANETS,
    VIMSHOTTARI_DURATIONS,
    ZODIAC_SIGNS,
)
from backend.app.astrology.schemas import (
    CalculationMetadata,
    ChartCalculationInput,
    ChartCalculationResult,
    D9Position,
    HousePosition,
    PlanetaryPosition,
    VimshottariPeriod,
    VimshottariSubPeriod,
)


def normalize_360(deg: float) -> float:
    """Normalize angle strictly to [0.0, 360.0)."""
    val = deg % 360.0
    return val + 360.0 if val < 0.0 else val


class AstrologyEngineAdapter(ABC):
    """Abstract interface defining the Vedic astrology calculation contract."""

    @abstractmethod
    def calculate_chart(self, input_data: ChartCalculationInput) -> ChartCalculationResult:
        pass


class SwissEphAdapter(AstrologyEngineAdapter):
    """
    Deterministic Vedic astrology calculations powered by the Swiss Ephemeris.
    Strictly isolated behind domain contracts; produces reproducible, verified mathematical placements.
    """

    ENGINE_NAME = "pyswisseph"
    ENGINE_VERSION = "2.10.3.2"
    CONFIG_VERSION = "vedic-v1"

    def __init__(self):
        # Configure Lahiri / Chitrapaksha Ayanamsa as the standard Vedic baseline
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def _parse_utc_instant(self, input_data: ChartCalculationInput) -> tuple[datetime, float, bool, list[str]]:
        """
        Convert local civil time to a normalized UTC instant and Julian Day.
        Honors historical daylight saving transitions via zoneinfo.
        """
        warnings = []
        is_exact = True

        try:
            tz = zoneinfo.ZoneInfo(input_data.timezone)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC")
            warnings.append(f"Invalid timezone '{input_data.timezone}', defaulted to UTC.")

        if not input_data.birth_time or input_data.birth_time_confidence == "unknown":
            is_exact = False
            warnings.append(
                "Birth time is unknown or unverified. Ascendant, Whole-Sign houses, "
                "and precise Dasha boundaries are marked unavailable. Planetary positions evaluated at 12:00 UTC."
            )
            # Default to 12:00:00 UTC for planetary longitudes
            date_parts = [int(p) for p in input_data.birth_date.split("-")]
            utc_dt = datetime(date_parts[0], date_parts[1], date_parts[2], 12, 0, 0, tzinfo=UTC)
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 12.0)
            return utc_dt, jd, is_exact, warnings

        # Exact civil time provided
        date_parts = [int(p) for p in input_data.birth_date.split("-")]
        time_parts = [int(p) for p in input_data.birth_time.split(":")]
        second = time_parts[2] if len(time_parts) > 2 else 0

        local_dt = datetime(
            date_parts[0],
            date_parts[1],
            date_parts[2],
            time_parts[0],
            time_parts[1],
            second,
            tzinfo=tz,
        )
        utc_dt = local_dt.astimezone(UTC)
        hour_fraction = (
            utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0) + (utc_dt.microsecond / 3600000000.0)
        )
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_fraction)

        return utc_dt, jd, is_exact, warnings

    def calculate_chart(self, input_data: ChartCalculationInput) -> ChartCalculationResult:
        utc_dt, jd, is_exact, warnings = self._parse_utc_instant(input_data)

        # Set configured Ayanamsa
        if input_data.ayanamsa.lower() in ("lahiri", "chitrapaksha"):
            swe.set_sid_mode(swe.SIDM_LAHIRI)
        else:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            warnings.append(f"Unsupported ayanamsa '{input_data.ayanamsa}', fell back to Lahiri.")

        ayanamsa_val = swe.get_ayanamsa_ut(jd)
        node_mode = input_data.node_mode.lower()

        # 1. Calculate Planetary Positions
        planets_result: list[PlanetaryPosition] = []
        moon_longitude = 0.0

        for p_def in PLANETS:
            p_id = p_def["id"]
            sanskrit = p_def["sanskrit"]

            if p_id == "Rahu":
                node_id = swe.MEAN_NODE if node_mode == "mean" else swe.TRUE_NODE
                res, _ = swe.calc_ut(jd, node_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                lon = normalize_360(res[0])
                speed = res[3]
                is_retro = True  # Nodes are always retro in Vedic convention
            elif p_id == "Ketu":
                # Ketu is exactly 180° opposite Rahu
                rahu_node_id = swe.MEAN_NODE if node_mode == "mean" else swe.TRUE_NODE
                res, _ = swe.calc_ut(jd, rahu_node_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                lon = normalize_360(res[0] + 180.0)
                speed = res[3]
                is_retro = True
            else:
                swe_id = p_def["swe_id"]
                if swe_id is None:
                    continue
                res, _ = swe.calc_ut(jd, swe_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                lon = normalize_360(res[0])
                speed = res[3]
                is_retro = speed < 0.0

            if p_id == "Moon":
                moon_longitude = lon

            # Sign determination (1 = Mesha ... 12 = Meena)
            sign_num = int(lon // 30.0) + 1
            deg_in_sign = lon % 30.0
            sign_info = ZODIAC_SIGNS[sign_num - 1]

            # Nakshatra determination (0 to 26) & Pada (1 to 4)
            nak_span = 360.0 / 27.0  # 13°20'
            nak_idx = int(lon // nak_span)
            nak_idx = min(nak_idx, 26)
            nak_info = NAKSHATRAS[nak_idx]
            pada = int((lon % nak_span) // (nak_span / 4.0)) + 1
            pada = min(max(pada, 1), 4)

            planets_result.append(
                PlanetaryPosition(
                    planet_id=p_id,
                    sanskrit_name=sanskrit,
                    longitude=round(lon, 6),
                    sign_number=sign_num,
                    sign_name=sign_info["english"],
                    sign_sanskrit=sign_info["sanskrit"],
                    degree_in_sign=round(deg_in_sign, 6),
                    nakshatra_index=nak_idx,
                    nakshatra_name=nak_info["name"],
                    nakshatra_ruler=nak_info["ruler"],
                    pada=pada,
                    house_number=None,  # Assigned after Ascendant calculation
                    is_retrograde=is_retro,
                    speed=round(speed, 6),
                )
            )

        # 2. Calculate Ascendant (Lagna) and Whole-Sign Houses
        asc_lon = None
        asc_sign_num = None
        asc_sign_name = None
        asc_deg = None
        asc_nak = None
        asc_pada = None
        houses_result: list[HousePosition] = []

        if is_exact:
            cusps, ascmc = swe.houses_ex(jd, input_data.latitude, input_data.longitude, b"W", swe.FLG_SIDEREAL)
            asc_lon = normalize_360(ascmc[0])
            asc_sign_num = int(asc_lon // 30.0) + 1
            asc_deg = asc_lon % 30.0
            sign_info = ZODIAC_SIGNS[asc_sign_num - 1]
            asc_sign_name = sign_info["english"]

            nak_span = 360.0 / 27.0
            nak_idx = min(int(asc_lon // nak_span), 26)
            asc_nak = NAKSHATRAS[nak_idx]["name"]
            asc_pada = min(max(int((asc_lon % nak_span) // (nak_span / 4.0)) + 1, 1), 4)

            # Assign Whole-Sign Houses (House 1 = Ascendant sign, House 2 = Next sign, ...)
            for h in range(1, 13):
                h_sign_num = ((asc_sign_num - 1 + (h - 1)) % 12) + 1
                h_sign_info = ZODIAC_SIGNS[h_sign_num - 1]
                occupying = [p.planet_id for p in planets_result if p.sign_number == h_sign_num]

                houses_result.append(
                    HousePosition(
                        house_number=h,
                        sign_number=h_sign_num,
                        sign_name=h_sign_info["english"],
                        sign_sanskrit=h_sign_info["sanskrit"],
                        occupying_planets=occupying,
                    )
                )

            # Update house_number on each planet
            for p in planets_result:
                p.house_number = ((p.sign_number - asc_sign_num) % 12) + 1

        # 3. Calculate D9 Navamsa Chart
        navamsa_result: list[D9Position] = []
        d9_pada_span = 360.0 / 108.0  # 3°20'
        for p in planets_result:
            d9_sign_num = (int(p.longitude // d9_pada_span) % 12) + 1
            d9_sign_info = ZODIAC_SIGNS[d9_sign_num - 1]
            navamsa_result.append(
                D9Position(
                    planet_id=p.planet_id,
                    d9_sign_number=d9_sign_num,
                    d9_sign_name=d9_sign_info["english"],
                    d9_sign_sanskrit=d9_sign_info["sanskrit"],
                )
            )

        # 4. Calculate Vimshottari Dasha Engine (120-year cycle)
        dashas_result: list[VimshottariPeriod] = []
        nak_span = 360.0 / 27.0
        moon_nak_idx = min(int(moon_longitude // nak_span), 26)
        birth_nak = NAKSHATRAS[moon_nak_idx]
        first_lord = birth_nak["ruler"]

        # Find starting index in standard Vimshottari sequence
        start_idx = 0
        for i, d in enumerate(VIMSHOTTARI_DURATIONS):
            if d["lord"] == first_lord:
                start_idx = i
                break

        # Fractional balance of first Dasha remaining at birth
        deg_into_nak = moon_longitude % nak_span
        fraction_spent = deg_into_nak / nak_span
        fraction_remaining = max(0.0, min(1.0 - fraction_spent, 1.0))

        current_start_dt = utc_dt
        for step in range(9):
            d_idx = (start_idx + step) % 9
            d_info = VIMSHOTTARI_DURATIONS[d_idx]
            lord_name = d_info["lord"]
            full_years = d_info["years"]

            duration_years = full_years * fraction_remaining if step == 0 else full_years

            # Advance date using 365.25 days per solar year
            duration_days = duration_years * DAYS_PER_YEAR
            current_end_dt = current_start_dt + timedelta(days=duration_days)

            # Compute Antar-Dashas (9 sub-periods)
            sub_periods: list[VimshottariSubPeriod] = []
            sub_start_dt = current_start_dt
            for sub_step in range(9):
                sub_lord_idx = (d_idx + sub_step) % 9
                sub_lord_info = VIMSHOTTARI_DURATIONS[sub_lord_idx]
                sub_lord_name = sub_lord_info["lord"]

                # Formula: Antar duration = (Maha duration * Sub Lord full duration) / 120.0
                sub_years = (duration_years * sub_lord_info["years"]) / 120.0
                sub_days = sub_years * DAYS_PER_YEAR
                sub_end_dt = sub_start_dt + timedelta(days=sub_days)

                sub_periods.append(
                    VimshottariSubPeriod(
                        lord=sub_lord_name,
                        start_date=sub_start_dt.strftime("%Y-%m-%d"),
                        end_date=sub_end_dt.strftime("%Y-%m-%d"),
                        duration_years=round(sub_years, 4),
                    )
                )
                sub_start_dt = sub_end_dt

            dashas_result.append(
                VimshottariPeriod(
                    lord=lord_name,
                    start_date=current_start_dt.strftime("%Y-%m-%d"),
                    end_date=current_end_dt.strftime("%Y-%m-%d"),
                    duration_years=round(duration_years, 4),
                    sub_periods=sub_periods,
                )
            )
            current_start_dt = current_end_dt

        metadata = CalculationMetadata(
            engine=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION,
            config_version=self.CONFIG_VERSION,
            ayanamsa="lahiri",
            ayanamsa_value=round(ayanamsa_val, 6),
            node_mode=node_mode,
            normalized_utc_instant=utc_dt.isoformat(),
            julian_day=round(jd, 6),
            calculation_timestamp=datetime.now(UTC).isoformat(),
            warnings=warnings,
        )

        return ChartCalculationResult(
            metadata=metadata,
            ascendant_longitude=round(asc_lon, 6) if asc_lon is not None else None,
            ascendant_sign_number=asc_sign_num,
            ascendant_sign_name=asc_sign_name,
            ascendant_degree=round(asc_deg, 6) if asc_deg is not None else None,
            ascendant_nakshatra=asc_nak,
            ascendant_pada=asc_pada,
            planets=planets_result,
            houses=houses_result,
            navamsa=navamsa_result,
            vimshottari_dashas=dashas_result,
            is_birth_time_qualified=is_exact,
        )
