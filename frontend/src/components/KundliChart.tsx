"use client";

import React, { useState } from "react";
import { ChartCalculationResult } from "@/types/astrology";
import { Compass, Sparkles } from "lucide-react";

interface KundliChartProps {
  calculation: ChartCalculationResult;
  title?: string;
}

const SIGN_NAMES_SHORT = [
  "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
  "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"
];

// Graha short codes and styling
const GRAHA_ABBR: Record<string, string> = {
  Sun: "Su",
  Moon: "Mo",
  Mars: "Ma",
  Mercury: "Me",
  Jupiter: "Ju",
  Venus: "Ve",
  Saturn: "Sa",
  Rahu: "Ra",
  Ketu: "Ke",
  Ascendant: "Asc",
};

export function KundliChart({ calculation, title = "Vedic Kundli (Birth Chart)" }: KundliChartProps) {
  const [chartStyle, setChartStyle] = useState<"north" | "south">("north");
  const [chartType, setChartType] = useState<"D1" | "D9">("D1");

  const ascSignId = calculation.ascendant_sign_number || 1; // 1 to 12

  // Map planets to houses based on chart type (D1 vs D9)
  const houseOccupants: Record<number, Array<{ name: string; isRetro: boolean; deg?: number }>> = {
    1: [{ name: "Asc", isRetro: false, deg: calculation.ascendant_degree ?? undefined }],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
    11: [],
    12: [],
  };

  if (chartType === "D1") {
    calculation.planets.forEach((p) => {
      const h = p.house_number;
      if (h && h >= 1 && h <= 12) {
        houseOccupants[h].push({
          name: GRAHA_ABBR[p.planet_id] || p.planet_id.slice(0, 2),
          isRetro: p.is_retrograde,
          deg: p.degree_in_sign,
        });
      }
    });
  } else {
    // D9 Navamsa chart
    // Find D9 Ascendant sign if ascendant longitude is available
    const ascLong = calculation.ascendant_longitude || 0;
    const navamsaIndex = Math.floor((ascLong % 30) / (30 / 9)); // 0..8
    const ascSignZero = Math.floor(ascLong / 30); // 0..11
    let d9AscSignId = 1;
    if ([0, 4, 8].includes(ascSignZero)) d9AscSignId = 1 + navamsaIndex;
    else if ([1, 5, 9].includes(ascSignZero)) d9AscSignId = ((10 + navamsaIndex - 1) % 12) + 1;
    else if ([2, 6, 10].includes(ascSignZero)) d9AscSignId = ((7 + navamsaIndex - 1) % 12) + 1;
    else d9AscSignId = ((4 + navamsaIndex - 1) % 12) + 1;

    houseOccupants[1] = [{ name: "Asc", isRetro: false }];
    calculation.navamsa.forEach((d9) => {
      const houseNum = ((d9.d9_sign_number - d9AscSignId + 12) % 12) + 1;
      const isRetro = calculation.planets.find((p) => p.planet_id === d9.planet_id)?.is_retrograde ?? false;
      houseOccupants[houseNum].push({
        name: GRAHA_ABBR[d9.planet_id] || d9.planet_id.slice(0, 2),
        isRetro,
      });
    });
  }

  const getHouseSignNumber = (h: number): number => {
    return ((ascSignId - 1 + (h - 1)) % 12) + 1;
  };

  const houseCoordinates: Record<number, { rashiX: number; rashiY: number; planetX: number; planetY: number }> = {
    1: { rashiX: 200, rashiY: 70, planetX: 200, planetY: 110 },
    2: { rashiX: 110, rashiY: 35, planetX: 95, planetY: 65 },
    3: { rashiX: 35, rashiY: 105, planetX: 65, planetY: 95 },
    4: { rashiX: 95, rashiY: 165, planetX: 100, planetY: 205 },
    5: { rashiX: 35, rashiY: 295, planetX: 65, planetY: 305 },
    6: { rashiX: 110, rashiY: 365, planetX: 95, planetY: 335 },
    7: { rashiX: 200, rashiY: 330, planetX: 200, planetY: 290 },
    8: { rashiX: 290, rashiY: 365, planetX: 305, planetY: 335 },
    9: { rashiX: 365, rashiY: 295, planetX: 335, planetY: 305 },
    10: { rashiX: 305, rashiY: 165, planetX: 300, planetY: 205 },
    11: { rashiX: 365, rashiY: 105, planetX: 335, planetY: 95 },
    12: { rashiX: 290, rashiY: 35, planetX: 305, planetY: 65 },
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-5">
      {/* Chart Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-surface-border/60 pb-4">
        <div>
          <h3 className="font-serif text-lg font-bold text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-gold-400" />
            {title}
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Lahiri Ayanamsa &bull; Whole-Sign Bhavas &bull;{" "}
            <span className="text-gold-400 font-medium">
              Ascendant: {calculation.ascendant_sign_name || "Surya Lagna"} ({calculation.ascendant_degree?.toFixed(2) || "0.00"}°)
            </span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* D1 / D9 Tabs */}
          <div className="inline-flex rounded-lg bg-surface-card p-1 border border-surface-border text-xs">
            <button
              onClick={() => setChartType("D1")}
              className={`px-3 py-1 rounded-md font-medium transition-all ${
                chartType === "D1"
                  ? "bg-gold-500 text-slate-950 font-semibold shadow-sm"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              D1 Rashi
            </button>
            <button
              onClick={() => setChartType("D9")}
              className={`px-3 py-1 rounded-md font-medium transition-all ${
                chartType === "D9"
                  ? "bg-gold-500 text-slate-950 font-semibold shadow-sm"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              D9 Navamsa
            </button>
          </div>

          {/* North / South Style Toggle */}
          <div className="inline-flex rounded-lg bg-surface-card p-1 border border-surface-border text-xs">
            <button
              onClick={() => setChartStyle("north")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                chartStyle === "north"
                  ? "bg-cosmic-primary text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Diamond
            </button>
            <button
              onClick={() => setChartStyle("south")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                chartStyle === "south"
                  ? "bg-cosmic-primary text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Grid
            </button>
          </div>
        </div>
      </div>

      {/* CHART RENDERING CANVAS */}
      <div className="flex justify-center items-center py-2">
        {chartStyle === "north" ? (
          /* NORTH INDIAN DIAMOND SVG */
          <div className="relative w-full max-w-[420px] aspect-square">
            <svg
              viewBox="0 0 400 400"
              className="w-full h-full drop-shadow-2xl select-none"
            >
              <defs>
                <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#0B0E1E" />
                  <stop offset="100%" stopColor="#0F142A" />
                </linearGradient>
              </defs>

              <rect x="0" y="0" width="400" height="400" fill="url(#bgGrad)" rx="16" />

              <rect
                x="4"
                y="4"
                width="392"
                height="392"
                fill="none"
                stroke="#EAB308"
                strokeWidth="2.5"
                strokeOpacity="0.8"
                rx="14"
              />

              <line x1="4" y1="4" x2="396" y2="396" stroke="#CA8A04" strokeWidth="1.5" strokeOpacity="0.7" />
              <line x1="4" y1="396" x2="396" y2="4" stroke="#CA8A04" strokeWidth="1.5" strokeOpacity="0.7" />

              <polygon
                points="200,4 396,200 200,396 4,200"
                fill="none"
                stroke="#EAB308"
                strokeWidth="2"
                strokeOpacity="0.8"
              />

              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
                const pos = houseCoordinates[houseNum];
                const signNum = getHouseSignNumber(houseNum);
                const planets = houseOccupants[houseNum] || [];

                return (
                  <g key={`house-${houseNum}`}>
                    <text
                      x={pos.rashiX}
                      y={pos.rashiY}
                      fill="#FACC15"
                      fontSize="12"
                      fontWeight="bold"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontFamily="var(--font-cinzel), serif"
                      className="opacity-90"
                    >
                      {signNum}
                    </text>

                    <text
                      x={pos.planetX}
                      y={pos.planetY}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="select-none"
                    >
                      {planets.map((p, idx) => {
                        const isAsc = p.name === "Asc";
                        return (
                          <tspan
                            key={`${p.name}-${idx}`}
                            x={pos.planetX}
                            dy={idx === 0 ? 0 : 14}
                            fontSize={isAsc ? "11" : "10"}
                            fontWeight={isAsc ? "bold" : "600"}
                            fill={isAsc ? "#38BDF8" : p.isRetro ? "#F43F5E" : "#F8FAFC"}
                            fontFamily="monospace"
                          >
                            {p.name}
                            {p.isRetro ? "®" : ""}
                            {p.deg !== undefined ? ` ${Math.floor(p.deg)}°` : ""}
                          </tspan>
                        );
                      })}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        ) : (
          /* SOUTH INDIAN 4x4 GRID */
          <div className="w-full max-w-[420px] aspect-square grid grid-cols-4 grid-rows-4 gap-1 p-2 bg-surface-card rounded-2xl border border-gold-500/40">
            {[
              { signId: 12, name: "Pisces", row: 0, col: 0 },
              { signId: 1, name: "Aries", row: 0, col: 1 },
              { signId: 2, name: "Taurus", row: 0, col: 2 },
              { signId: 3, name: "Gemini", row: 0, col: 3 },
              { signId: 11, name: "Aquarius", row: 1, col: 0 },
              { signId: 4, name: "Cancer", row: 1, col: 3 },
              { signId: 10, name: "Capricorn", row: 2, col: 0 },
              { signId: 5, name: "Leo", row: 2, col: 3 },
              { signId: 9, name: "Sagittarius", row: 3, col: 0 },
              { signId: 8, name: "Scorpio", row: 3, col: 1 },
              { signId: 7, name: "Libra", row: 3, col: 2 },
              { signId: 6, name: "Virgo", row: 3, col: 3 },
            ].map((box) => {
              const houseNum = ((box.signId - ascSignId + 12) % 12) + 1;
              const planets = houseOccupants[houseNum] || [];
              const isLagnaBox = box.signId === ascSignId;

              return (
                <div
                  key={box.signId}
                  style={{ gridRow: box.row + 1, gridColumn: box.col + 1 }}
                  className={`relative p-1.5 rounded-lg border text-xs flex flex-col justify-between ${
                    isLagnaBox
                      ? "border-sky-400 bg-sky-950/30"
                      : "border-surface-border bg-surface/80"
                  }`}
                >
                  <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                    <span>{SIGN_NAMES_SHORT[box.signId - 1]}</span>
                    {isLagnaBox && <span className="text-sky-400 font-bold">ASC</span>}
                  </div>

                  <div className="flex flex-wrap gap-1 items-center justify-center my-auto">
                    {planets
                      .filter((p) => p.name !== "Asc")
                      .map((p, pIdx) => (
                        <span
                          key={`${p.name}-${pIdx}`}
                          className={`text-[10px] font-mono px-1 rounded ${
                            p.isRetro ? "text-rose-400 font-bold" : "text-slate-200"
                          }`}
                        >
                          {p.name}
                          {p.isRetro ? "®" : ""}
                        </span>
                      ))}
                  </div>

                  <div className="text-[9px] text-right text-gold-400/80 font-mono">
                    H{houseNum}
                  </div>
                </div>
              );
            })}

            <div
              style={{ gridRow: "2 / span 2", gridColumn: "2 / span 2" }}
              className="flex flex-col items-center justify-center text-center p-3 rounded-xl bg-surface/50 border border-gold-500/20"
            >
              <Sparkles className="w-5 h-5 text-gold-400 mb-1" />
              <span className="font-serif text-sm font-bold text-white tracking-wider">
                ASTROMIND
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {chartType} &bull; Whole Sign
              </span>
              <span className="text-[9px] text-gold-300 font-mono mt-1">
                Lagna: {calculation.ascendant_sign_name || "Mesha"}
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 border-t border-surface-border/50">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 inline-block" />
            <span className="text-slate-300">Asc / Lagna</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="text-rose-400 font-bold font-mono">®</span>
            <span className="text-slate-300">Retrograde Graha</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="text-gold-400 font-bold font-mono">1-12</span>
            <span className="text-slate-300">Rashi Signs (1=Aries)</span>
          </span>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          Engine: Swiss Ephemeris v{calculation.metadata.engine_version}
        </div>
      </div>
    </div>
  );
}
