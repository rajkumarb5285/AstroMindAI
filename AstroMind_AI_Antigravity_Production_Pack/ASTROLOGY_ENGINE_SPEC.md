# Vedic Astrology Engine Specification

## Configuration
Version and persist all calculation settings. Initial proposed defaults:
- Zodiac: sidereal
- Ayanamsa: Lahiri/Chitrapaksha
- D1/Rashi first
- Whole-sign houses for the initial interpretation model
- Explicit node mode: mean or true
- Vimshottari Dasha with documented year-length and boundary convention
- D9/Navamsa only after independent validation

These are product defaults, not universal rules across every Vedic tradition.

## Pipeline
1. Validate date, local time, IANA timezone, latitude and longitude.
2. If birth time is unknown, do not invent it. Mark time-dependent results unavailable or qualified.
3. Convert local civil time to UTC using historical timezone data.
4. Convert to the ephemeris time scale/Julian Day as required by the library.
5. Calculate planetary longitudes and Ascendant.
6. Apply configured ayanamsa consistently.
7. Normalize longitudes to [0, 360).
8. Derive sign, house, Nakshatra and pada.
9. Derive D9 and Dasha with documented algorithms.
10. Return structured facts, calculation metadata, and limitations.
11. Persist inputs/configuration/version and output for reproducibility.

## Required engine output metadata
- engine name/version
- configuration version
- Ayanamsa and node mode
- input timezone and normalized UTC instant
- latitude/longitude source and precision
- calculation timestamp
- warnings and uncertain inputs
- units and coordinate conventions

## Validation
- Golden reference chart set with source, expected values, tolerances and reviewer.
- Test longitude wraparound and sign boundaries.
- Test Nakshatra/pada boundaries.
- Test Ascendant and D9 boundaries.
- Test Vimshottari sequence and period boundaries.
- Test leap days, midnight, historical timezone offsets and missing birth time.
- Test engine upgrade diffs before accepting new versions.
- Never silently change configuration defaults.
- Do not call interpretations “accurate predictions”; separately evaluate numerical calculations and subjective interpretation quality.

## Licensing
Evaluate Swiss Ephemeris or alternatives with current licensing and distribution model. Obtain appropriate rights before commercial use. Record decision and evidence in `docs/licensing/`. Do not ship a production build until approved.
