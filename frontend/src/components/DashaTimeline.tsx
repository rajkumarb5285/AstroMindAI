"use client";

import React, { useState } from "react";
import { VimshottariPeriod } from "@/types/astrology";
import { Clock, ChevronDown, ChevronRight, CheckCircle2, Calendar } from "lucide-react";

interface DashaTimelineProps {
  dashas: VimshottariPeriod[];
}

export function DashaTimeline({ dashas }: DashaTimelineProps) {
  const [expandedPlanet, setExpandedPlanet] = useState<string | null>(null);

  const today = new Date().toISOString().split("T")[0];

  const toggleExpand = (lord: string) => {
    setExpandedPlanet(expandedPlanet === lord ? null : lord);
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border/60 pb-3">
        <div>
          <h3 className="font-serif text-lg font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-gold-400" />
            Vimshottari Dasha System (120-Year Cycle)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Calculated from natal Moon nakshatra longitude using standard 365.25 days/year.
          </p>
        </div>
        <div className="text-xs font-mono px-2.5 py-1 rounded bg-surface-card border border-surface-border text-slate-300">
          Today: {today}
        </div>
      </div>

      <div className="space-y-2.5">
        {dashas.map((dasha) => {
          const isActive = today >= dasha.start_date && today <= dasha.end_date;
          const isPast = today > dasha.end_date;
          const isExpanded = expandedPlanet === dasha.lord;

          return (
            <div
              key={dasha.lord}
              className={`rounded-xl border transition-all ${
                isActive
                  ? "border-gold-500/50 bg-gold-950/20 shadow-md shadow-gold-500/5"
                  : isPast
                  ? "border-surface-border/40 bg-surface/40 opacity-75"
                  : "border-surface-border bg-surface/80 hover:border-surface-border/80"
              }`}
            >
              {/* Maha Dasha Header Row */}
              <div
                onClick={() => toggleExpand(dasha.lord)}
                className="p-3.5 flex items-center justify-between cursor-pointer select-none"
              >
                <div className="flex items-center gap-3">
                  <button className="text-slate-400 hover:text-white">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gold-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    )}
                  </button>

                  <div>
                    <span className="font-serif font-bold text-sm text-white">
                      {dasha.lord} Maha Dasha
                    </span>
                    <span className="text-xs text-slate-400 ml-2 font-mono">
                      ({dasha.duration_years.toFixed(1)} Years)
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-xs font-mono text-slate-300 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>{dasha.start_date}</span>
                    <span className="text-slate-600">&rarr;</span>
                    <span>{dasha.end_date}</span>
                  </div>

                  {isActive && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-gold-500 text-slate-950 flex items-center gap-1 shadow-sm">
                      <CheckCircle2 className="w-3 h-3" />
                      ACTIVE
                    </span>
                  )}
                  {isPast && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-card text-slate-500">
                      Completed
                    </span>
                  )}
                </div>
              </div>

              {/* Antar Dasha Sub-periods (Expanded View) */}
              {isExpanded && dasha.sub_periods && (
                <div className="px-6 pb-4 pt-1 border-t border-surface-border/50 bg-surface-card/40 rounded-b-xl">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block mb-2">
                    Antar Dashas (Sub-Periods of {dasha.lord})
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {dasha.sub_periods.map((sub) => {
                      const isSubActive = today >= sub.start_date && today <= sub.end_date;
                      return (
                        <div
                          key={sub.lord}
                          className={`p-2.5 rounded-lg border text-xs font-mono ${
                            isSubActive
                              ? "border-gold-400 bg-gold-950/40 text-gold-200 font-semibold"
                              : "border-surface-border/60 bg-surface/60 text-slate-300"
                          }`}
                        >
                          <div className="flex justify-between items-center mb-1">
                            <span>
                              {dasha.lord}-{sub.lord}
                            </span>
                            {isSubActive && (
                              <span className="text-[9px] px-1.5 py-0.2 rounded bg-gold-500 text-slate-950 font-bold">
                                CURRENT
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-400 flex justify-between">
                            <span>{sub.start_date}</span>
                            <span>{sub.end_date}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
