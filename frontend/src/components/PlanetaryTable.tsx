"use client";

import React from "react";
import { ChartCalculationResult } from "@/types/astrology";
import { Orbit } from "lucide-react";

interface PlanetaryTableProps {
  calculation: ChartCalculationResult;
}

function formatDMS(deg: number): string {
  const d = Math.floor(deg);
  const mDec = (deg - d) * 60;
  const m = Math.floor(mDec);
  const s = Math.round((mDec - m) * 60);
  return `${d}° ${m.toString().padStart(2, "0")}' ${s.toString().padStart(2, "0")}"`;
}

export function PlanetaryTable({ calculation }: PlanetaryTableProps) {
  const { planets } = calculation;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border/60 pb-3">
        <h3 className="font-serif text-lg font-bold text-white flex items-center gap-2">
          <Orbit className="w-5 h-5 text-gold-400" />
          Planetary Positions & Longitudes (D1 Rashi)
        </h3>
        <span className="text-xs font-mono text-slate-400">
          Ayanamsa: {calculation.metadata.ayanamsa} ({formatDMS(calculation.metadata.ayanamsa_value)})
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-surface-border text-slate-400 uppercase tracking-wider text-[11px]">
              <th className="py-2.5 px-3">Graha / Body</th>
              <th className="py-2.5 px-3">Rashi (Sign)</th>
              <th className="py-2.5 px-3">Deg in Sign</th>
              <th className="py-2.5 px-3">Total Longitude</th>
              <th className="py-2.5 px-3">Nakshatra (Pada)</th>
              <th className="py-2.5 px-3">Bhava (House)</th>
              <th className="py-2.5 px-3">Motion</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/40 text-slate-200">
            {/* Ascendant Row */}
            {calculation.ascendant_longitude !== null && (
              <tr className="bg-sky-950/20 hover:bg-sky-950/40 transition-colors">
                <td className="py-3 px-3 font-semibold text-sky-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-sky-400" />
                  Ascendant (Lagna)
                </td>
                <td className="py-3 px-3 font-sans font-medium text-white">
                  {calculation.ascendant_sign_name}
                </td>
                <td className="py-3 px-3 text-gold-300 font-semibold">
                  {formatDMS(calculation.ascendant_degree ?? 0)}
                </td>
                <td className="py-3 px-3 text-slate-400">
                  {formatDMS(calculation.ascendant_longitude)}
                </td>
                <td className="py-3 px-3 text-slate-300">
                  {calculation.ascendant_nakshatra} (Pada {calculation.ascendant_pada})
                </td>
                <td className="py-3 px-3 font-semibold text-white">House 1</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 text-[10px]">
                    Direct
                  </span>
                </td>
              </tr>
            )}

            {/* Planets Rows */}
            {planets.map((p) => (
              <tr
                key={p.planet_id}
                className="hover:bg-surface-card/60 transition-colors"
              >
                <td className="py-3 px-3 font-sans font-medium text-white flex items-center gap-1.5">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      p.is_retrograde ? "bg-rose-400" : "bg-gold-400"
                    }`}
                  />
                  {p.planet_id}
                  <span className="text-[10px] text-slate-400 font-serif">({p.sanskrit_name})</span>
                </td>
                <td className="py-3 px-3 font-sans text-slate-300">
                  {p.sign_name}
                  <span className="text-[10px] text-slate-500 ml-1 font-mono">
                    ({p.sign_sanskrit})
                  </span>
                </td>
                <td className="py-3 px-3 text-gold-400">
                  {formatDMS(p.degree_in_sign)}
                </td>
                <td className="py-3 px-3 text-slate-400">
                  {formatDMS(p.longitude)}
                </td>
                <td className="py-3 px-3 text-slate-300">
                  {p.nakshatra_name} (Pada {p.pada})
                </td>
                <td className="py-3 px-3 font-semibold text-slate-200">
                  {p.house_number ? `House ${p.house_number}` : "N/A (Unknown Time)"}
                </td>
                <td className="py-3 px-3">
                  {p.is_retrograde ? (
                    <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-bold">
                      Retrograde [R]
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                      Direct
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
