# Ephemeris Licensing Audit & Policy

**Project:** AstroMind AI  
**Component:** Deterministic Vedic Calculation Engine (`pyswisseph` / `libswe`)  
**Status:** In Development / Evaluation Phase  
**Review Date:** 2026-10-18  

---

## 1. Executive Summary

AstroMind AI uses the Swiss Ephemeris (`libswe` via Python bindings `pyswisseph`) for high-precision geocentric planetary longitudes, Lahiri (Chitrapaksha) ayanamsa, Ascendant calculation, and lunar node positions.

The Swiss Ephemeris is published by **Astrodienst AG (Zurich, Switzerland)** under a **dual-licensing model**:
1. **GNU Affero General Public License (AGPL) v3**: Available for open-source projects where the entire software interacting with the library across a network is published under the GNU AGPL v3.
2. **Astrodienst Commercial License**: Available for proprietary and commercial software applications without requiring open-sourcing the proprietary application code.

---

## 2. Legal Analysis & Architectural Isolation

### 2.1 AGPL v3 Scope & Network Trigger (Section 13)
Under AGPL v3, if a program is modified or incorporated into a network service, users interacting with it remotely through a computer network must be provided access to the Corresponding Source of the program.

### 2.2 Architectural Mitigation: The Adapter Pattern
To avoid tight coupling and ensure legal safety:
1. All astrology calculations are strictly isolated behind the `AstrologyEngineAdapter` abstraction.
2. The core FastAPI business logic, authentication system, database models, and AI orchestration communicate with the calculation engine **only** through typed data transfer objects (`ChartCalculationInput` and `ChartCalculationResult`).
3. No internal ephemeris C-pointers or proprietary library types cross the domain boundary.

---

## 3. Commercial Release Pre-Requisites

Before AstroMind AI proceeds to broad public commercial operations or monetized offerings:
1. **Commercial License Procurement:** An official commercial license must be purchased from Astrodienst AG for the server-side deployment of Swiss Ephemeris.
   - Contact: `financial@astro.com` / `https://www.astro.com/swisseph/swephprice_e.htm`
2. **Alternative Engines:** The `AstrologyEngineAdapter` interface permits swapping the calculation provider to alternatives (such as NASA JPL DE440 ephemeris data via Skyfield/SPICE, or custom astronomical code) without changing any frontend, database, or API code.
3. **Open Source Development:** During local development and testing under Phase 3, `pyswisseph` is operated under AGPL compliance for evaluation and validation against golden reference charts.

---

## 4. Acceptance Gate
Commercial release **MUST REMAIN BLOCKED** until:
- [ ] Astrodienst commercial license agreement executed, OR
- [ ] Alternative open-licensed engine adapter verified, OR
- [ ] Full service published under GNU AGPL v3.
