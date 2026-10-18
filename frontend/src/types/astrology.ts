export interface BirthProfile {
  id: string;
  owner_id: string;
  name: string;
  birth_date: string;
  birth_time?: string | null;
  timezone: string;
  birthplace: string;
  latitude: number;
  longitude: number;
  birth_time_confidence: "exact" | "approximate" | "rectified" | "unknown";
  created_at?: string;
  updated_at?: string;
}

export interface PlanetaryPosition {
  planet_id: string;
  sanskrit_name: string;
  longitude: float;
  sign_number: number; // 1 to 12
  sign_name: string;
  sign_sanskrit: string;
  degree_in_sign: number; // 0.0 to 30.0
  nakshatra_index: number;
  nakshatra_name: string;
  nakshatra_ruler: string;
  pada: number; // 1 to 4
  house_number: number | null; // 1 to 12
  is_retrograde: boolean;
  speed: number;
}

type float = number;

export interface HousePosition {
  house_number: number;
  sign_number: number;
  sign_name: string;
  sign_sanskrit: string;
  occupying_planets: string[];
}

export interface D9Position {
  planet_id: string;
  d9_sign_number: number;
  d9_sign_name: string;
  d9_sign_sanskrit: string;
}

export interface VimshottariSubPeriod {
  lord: string;
  start_date: string;
  end_date: string;
  duration_years: number;
}

export interface VimshottariPeriod {
  lord: string;
  start_date: string;
  end_date: string;
  duration_years: number;
  sub_periods?: VimshottariSubPeriod[] | null;
}

export interface CalculationMetadata {
  engine: string;
  engine_version: string;
  config_version: string;
  ayanamsa: string;
  ayanamsa_value: number;
  node_mode: string;
  normalized_utc_instant: string;
  julian_day: number;
  calculation_timestamp: string;
  warnings: string[];
}

export interface ChartCalculationResult {
  metadata: CalculationMetadata;
  ascendant_longitude: number | null;
  ascendant_sign_number: number | null;
  ascendant_sign_name: string | null;
  ascendant_degree: number | null;
  ascendant_nakshatra: string | null;
  ascendant_pada: number | null;
  planets: PlanetaryPosition[];
  houses: HousePosition[];
  navamsa: D9Position[];
  vimshottari_dashas: VimshottariPeriod[];
  is_birth_time_qualified: boolean;
}

export interface ChartRecord {
  id: string;
  owner_id: string;
  birth_profile_id: string;
  calculation_type: string;
  ayanamsa: string;
  house_system: string;
  calculation_result: ChartCalculationResult;
  created_at: string;
}

export interface PlanetaryCombustionInfo {
  is_combust: boolean;
  angular_distance_deg: number;
  orb_limit_deg: number;
  classical_orb_reference: string;
}

export interface PlanetaryRuleAnalysis {
  planet_id: string;
  dignity: string;
  combustion: PlanetaryCombustionInfo;
  house: number | null;
  sign: string;
  degree_in_sign: number;
}

export interface AspectResult {
  aspecting_planet: string;
  aspect_type: string;
  aspecting_house: number;
  aspected_house: number;
  aspected_planets: string[];
  classical_source: string;
}

export interface ClassicalYoga {
  yoga_id: string;
  name: string;
  category: string;
  participating_planets: string[];
  houses_involved: number[];
  description: string;
  classical_reference: string;
}

export interface ChartRuleSummary {
  exalted_count: number;
  exalted_planets: string[];
  debilitated_count: number;
  debilitated_planets: string[];
  combust_count: number;
  combust_planets: string[];
  total_yogas_formed: number;
}

export interface ChartRuleEvaluationResult {
  rules_version: string;
  planetary_analyses: PlanetaryRuleAnalysis[];
  aspects: AspectResult[];
  yogas: ClassicalYoga[];
  summary: ChartRuleSummary;
}

export interface ToolExecutionRecord {
  tool_name: string;
  arguments: Record<string, any>;
  result_summary: string;
}

export interface InterpretationCitation {
  citation: string;
  topic?: string;
  content?: string;
  chunk_id?: string;
}

export interface InterpretationResponse {
  interpretation: string;
  citations: InterpretationCitation[];
  chart_id: string;
  tokens_used: number;
  tools_called: string[];
  disclaimer: string;
  question?: string;
}

export interface KootaScore {
  koota_name: string;
  max_points: number;
  points_obtained: number;
  description: string;
  status: "auspicious" | "neutral" | "dosha" | "cancelled";
  cancellation_reason?: string | null;
}

export interface CompatibilityResult {
  total_points: number;
  max_points: number;
  percentage: number;
  verdict: "Excellent" | "Good" | "Average" | "Inauspicious";
  kootas: KootaScore[];
  doshas: string[];
  cancellations: string[];
  bride_summary: {
    moon_sign: number;
    nakshatra_index: number;
    nakshatra_name: string;
    pada: number;
    gana: string;
    nadi: string;
    yoni: string;
    rashi_lord: string;
  };
  groom_summary: {
    moon_sign: number;
    nakshatra_index: number;
    nakshatra_name: string;
    pada: number;
    gana: string;
    nadi: string;
    yoni: string;
    rashi_lord: string;
  };
}

export interface PlanetaryTransit {
  planet_id: string;
  transit_sign_number: number;
  transit_sign_name: string;
  transit_degree: number;
  is_retrograde: boolean;
  house_from_lagna: number;
  house_from_moon: number;
  classical_effect: string;
}

export interface SadeSatiStatus {
  is_active: boolean;
  phase: string | null;
  description: string;
}

export interface GocharEvaluationResult {
  transit_timestamp: string;
  natal_moon_sign: number;
  natal_moon_sign_name: string;
  natal_lagna_sign: number;
  natal_lagna_sign_name: string;
  sade_sati: SadeSatiStatus;
  kantaka_shani: boolean;
  ashtama_shani: boolean;
  transits: PlanetaryTransit[];
  summary_highlights: string[];
}

export interface ReportJobResponse {
  report_id: string;
  chart_id: string;
  title: string;
  status: string;
  download_url: string;
}


