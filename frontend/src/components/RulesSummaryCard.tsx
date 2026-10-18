"use client";

import React, { useState, useEffect } from "react";
import {
  ChartRuleEvaluationResult,
  PlanetaryRuleAnalysis,
  ClassicalYoga,
  AspectResult,
} from "@/types/astrology";
import {
  BookOpen,
  Sparkles,
  Flame,
  Crown,
  Eye,
  ScrollText,
  Loader2,
} from "lucide-react";

interface RulesSummaryCardProps {
  chartId: string;
}

export function RulesSummaryCard({ chartId }: RulesSummaryCardProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [rules, setRules] = useState<ChartRuleEvaluationResult | null>(null);
  const [activeTab, setActiveTab] = useState<"yogas" | "dignities" | "aspects">("yogas");

  useEffect(() => {
    let isMounted = true;
    async function fetchRules() {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("astromind_token") || "test-token-usr_golden_001";
        const res = await fetch(`http://127.0.0.1:8000/api/v1/charts/${chartId}/rules`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          throw new Error(`Rules API returned ${res.status}`);
        }
        const data: ChartRuleEvaluationResult = await res.json();
        if (isMounted) {
          setRules(data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "Failed to load deterministic rules.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    if (chartId) {
      fetchRules();
    }
    return () => {
      isMounted = false;
    };
  }, [chartId]);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-surface-border text-center space-y-3">
        <Loader2 className="w-6 h-6 text-gold-400 animate-spin mx-auto" />
        <p className="text-xs font-mono text-slate-400">Evaluating Classical Parashari Rules...</p>
      </div>
    );
  }

  if (error || !rules) {
    return (
      <div className="glass-panel p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-xs text-rose-300">
        Unable to evaluate chart rules: {error || "No data"}
      </div>
    );
  }

  const combustPlanets = rules.planetary_analyses.filter((pa) => pa.combustion.is_combust);

  return (
    <div className="glass-panel rounded-2xl border border-surface-border overflow-hidden">
      {/* HEADER */}
      <div className="p-5 border-b border-surface-border/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface/50">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-gold-400" />
            <h3 className="font-serif text-lg font-bold text-white">
              Classical Vedic Rule Engine
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              {rules.rules_version}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Deterministic evaluations: <span className="text-emerald-400 font-semibold">{rules.summary.total_yogas_formed} Yogas</span>,{" "}
            <span className="text-gold-300 font-semibold">{rules.summary.exalted_count} Exalted</span>,{" "}
            <span className="text-amber-300 font-semibold">{rules.summary.combust_count} Combust</span>
          </p>
        </div>

        {/* TAB TOGGLES */}
        <div className="flex items-center gap-1 p-1 bg-surface-card rounded-xl border border-surface-border">
          <button
            onClick={() => setActiveTab("yogas")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === "yogas"
                ? "bg-gold-500/20 text-gold-300 border border-gold-500/40 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Yogas ({rules.yogas.length})
          </button>
          <button
            onClick={() => setActiveTab("dignities")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === "dignities"
                ? "bg-gold-500/20 text-gold-300 border border-gold-500/40 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Dignities
          </button>
          <button
            onClick={() => setActiveTab("aspects")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === "aspects"
                ? "bg-gold-500/20 text-gold-300 border border-gold-500/40 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Aspects ({rules.aspects.length})
          </button>
        </div>
      </div>

      {/* COMBUSTION BANNER IF ANY COMBUST */}
      {combustPlanets.length > 0 && (
        <div className="px-5 py-3 bg-amber-500/10 border-b border-amber-500/20 flex items-center gap-3 text-xs text-amber-200">
          <Flame className="w-4 h-4 text-amber-400 flex-shrink-0 animate-pulse" />
          <div>
            <span className="font-semibold text-amber-300">Combustion (Asta Graha) Detected: </span>
            {combustPlanets.map((c, i) => (
              <span key={c.planet_id}>
                {c.planet_id} ({c.combustion.angular_distance_deg}° from Sun, orb {c.combustion.orb_limit_deg}°)
                {i < combustPlanets.length - 1 ? ", " : ""}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* TAB CONTENT */}
      <div className="p-5">
        {/* YOGAS TAB */}
        {activeTab === "yogas" && (
          <div className="space-y-3">
            {rules.yogas.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No major classical yogas detected for this configuration.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {rules.yogas.map((yoga) => (
                  <div
                    key={yoga.yoga_id}
                    className="p-4 rounded-xl bg-surface/70 border border-surface-border hover:border-gold-500/40 transition-all space-y-2 group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-gold-400 flex-shrink-0 group-hover:rotate-12 transition-transform" />
                        <h4 className="font-serif text-sm font-bold text-white group-hover:text-gold-200 transition-colors">
                          {yoga.name}
                        </h4>
                      </div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-surface-card border border-surface-border text-slate-300">
                        {yoga.category}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      {yoga.description}
                    </p>

                    <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-surface-border/50 text-[11px] font-mono">
                      <div className="text-slate-400">
                        Grahas: <span className="text-sky-300 font-medium">{yoga.participating_planets.join(", ")}</span>
                        {yoga.houses_involved.length > 0 && (
                          <span className="ml-2 text-slate-400">
                            Houses: <span className="text-amber-300 font-medium">{yoga.houses_involved.join(", ")}</span>
                          </span>
                        )}
                      </div>
                      <span className="text-gold-400/90 flex items-center gap-1">
                        <ScrollText className="w-3 h-3" />
                        {yoga.classical_reference}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* DIGNITIES TAB */}
        {activeTab === "dignities" && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {rules.planetary_analyses.map((pa) => {
              const isHigh = pa.dignity === "exalted" || pa.dignity === "moolatrikona" || pa.dignity === "own_sign";
              const isLow = pa.dignity === "debilitated";
              return (
                <div
                  key={pa.planet_id}
                  className={`p-3 rounded-xl border transition-all ${
                    isHigh
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-200"
                      : isLow
                      ? "bg-rose-500/10 border-rose-500/30 text-rose-200"
                      : "bg-surface/60 border-surface-border text-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-serif font-bold text-white text-sm flex items-center gap-1.5">
                      {pa.planet_id}
                      {pa.dignity === "exalted" && <Crown className="w-3.5 h-3.5 text-gold-400" />}
                    </span>
                    <span className="text-[10px] font-mono font-semibold uppercase">
                      {pa.dignity.replace("_", " ")}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 font-mono">
                    Sign: {pa.sign} ({pa.degree_in_sign}°)
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    House {pa.house || "N/A"}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ASPECTS TAB */}
        {activeTab === "aspects" && (
          <div className="space-y-2">
            <p className="text-xs text-slate-400 mb-3">
              Full Parashari Graha Drishti: Special aspects evaluated for Mars (4th/8th), Jupiter (5th/9th), and Saturn (3rd/10th), alongside classical 7th-house mutual aspects.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {rules.aspects.map((asp, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-surface/60 border border-surface-border text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between font-serif font-bold text-white">
                    <span className="flex items-center gap-1">
                      <Eye className="w-3.5 h-3.5 text-sky-400" />
                      {asp.aspecting_planet}
                    </span>
                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                      {asp.aspect_type}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-300 font-mono">
                    House {asp.aspecting_house} &rarr; <span className="text-gold-300">House {asp.aspected_house}</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Aspected Grahas:{" "}
                    <span className="text-slate-200">
                      {asp.aspected_planets.length > 0 ? asp.aspected_planets.join(", ") : "Empty House"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
