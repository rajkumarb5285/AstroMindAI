from pydantic import BaseModel, Field


class ChartCalculationInput(BaseModel):
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Local civil birth date (YYYY-MM-DD)")
    birth_time: str | None = Field(
        None, pattern=r"^\d{2}:\d{2}(:\d{2})?$", description="Local civil birth time (HH:MM:SS)"
    )
    timezone: str = Field(..., description="IANA timezone e.g. 'Asia/Kolkata', 'America/New_York'")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Geographic latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Geographic longitude")
    ayanamsa: str = Field("lahiri", description="Ayanamsa system: 'lahiri' / 'chitrapaksha'")
    node_mode: str = Field("mean", description="Lunar node calculation: 'mean' or 'true'")
    calculation_type: str = Field("D1", description="Chart type: 'D1', 'D9', 'transit'")
    birth_time_confidence: str = Field("exact", description="'exact', 'approximate', or 'unknown'")


class PlanetaryPosition(BaseModel):
    planet_id: str
    sanskrit_name: str
    longitude: float
    sign_number: int  # 1 (Mesha) to 12 (Meena)
    sign_name: str
    sign_sanskrit: str
    degree_in_sign: float  # 0.0 to 30.0
    nakshatra_index: int  # 0 to 26
    nakshatra_name: str
    nakshatra_ruler: str
    pada: int  # 1 to 4
    house_number: int | None  # 1 to 12 in Whole-Sign system (None if birth time unknown)
    is_retrograde: bool
    speed: float


class HousePosition(BaseModel):
    house_number: int  # 1 to 12
    sign_number: int  # 1 to 12
    sign_name: str
    sign_sanskrit: str
    occupying_planets: list[str]


class D9Position(BaseModel):
    planet_id: str
    d9_sign_number: int
    d9_sign_name: str
    d9_sign_sanskrit: str


class VimshottariSubPeriod(BaseModel):
    lord: str
    start_date: str
    end_date: str
    duration_years: float


class VimshottariPeriod(BaseModel):
    lord: str
    start_date: str
    end_date: str
    duration_years: float
    sub_periods: list[VimshottariSubPeriod] | None = None


class CalculationMetadata(BaseModel):
    engine: str
    engine_version: str
    config_version: str
    ayanamsa: str
    ayanamsa_value: float
    node_mode: str
    normalized_utc_instant: str
    julian_day: float
    calculation_timestamp: str
    warnings: list[str] = []


class ChartCalculationResult(BaseModel):
    metadata: CalculationMetadata
    ascendant_longitude: float | None
    ascendant_sign_number: int | None
    ascendant_sign_name: str | None
    ascendant_degree: float | None
    ascendant_nakshatra: str | None
    ascendant_pada: int | None
    planets: list[PlanetaryPosition]
    houses: list[HousePosition]
    navamsa: list[D9Position]
    vimshottari_dashas: list[VimshottariPeriod]
    is_birth_time_qualified: bool  # True if birth time was known/exact, False if qualified
