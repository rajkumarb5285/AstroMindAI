"use client";

import React, { useState, useEffect } from "react";
import { GocharEvaluationResult, PlanetaryTransit } from "@/types/astrology";
import {
  Compass,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  RotateCw,
  Orbit,
  Loader2,
  Calendar,
} from "lucide-react";

interface GocharTransitCardProps {
  chartId: string;
}

import { getApiUrl } from "@/lib/api";

export function GocharTransitCard({ chartId }: GocharTransitCardProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<GocharEvaluationResult | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function fetchTransits() {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("astromind_token") || "test-token-usr_golden_001";
        const res = await fetch(getApiUrl(`/api/v1/charts/${chartId}/transits`), {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          throw new Error(`Transits API returned ${res.status}`);
        }
        const json: GocharEvaluationResult = await res.json();
        if (isMounted) {
          setData(json);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "Failed to load planetary transits.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    if (chartId) {
      fetchTransits();
    }
    return () => {
      isMounted = false;
    };
  }, [chartId]);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-surface-border text-center space-y-3">
        <Loader2 className="w-6 h-6 text-sky-400 animate-spin mx-auto" />
        <p className="text-xs font-mono text-slate-400">Computing Real-Time Astronomical Transits...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-xs text-rose-300">
        Unable to load Gochar transits: {error || "No data"}
      </div>
    );
  }

  const { sade_sati, kantaka_shani, ashtama_shani, transits, summary_highlights } = data;

  return (
    <div className="glass-panel rounded-2xl border border-surface-border overflow-hidden">
      {/* HEADER */}
      <div className="p-5 border-b border-surface-border/80 bg-surface/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Orbit className="w-4 h-4 text-sky-400" />
            <h3 className="font-serif text-lg font-bold text-white">
              Gochar (Planetary Transits)
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-sky-500/15 text-sky-400 border border-sky-500/30">
              Swiss Ephemeris Geocentric
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time planetary projections mapped against Natal Moon (
            <span className="text-white font-semibold">{data.natal_moon_sign_name}</span>) & Lagna (
            <span className="text-white font-semibold">{data.natal_lagna_sign_name}</span>).
          </p>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400 bg-surface-card px-3 py-1.5 rounded-xl border border-surface-border">
          <Calendar className="w-3.5 h-3.5 text-gold-400" />
          <span>{new Date(data.transit_timestamp).toLocaleDateString()}</span>
        </div>
      </div>

      {/* SADE SATI & SHANI GOCHAR BANNER */}
      <div className="p-5 border-b border-surface-border/50">
        <div
          className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-start justify-between gap-4 ${
            sade_sati.is_active
              ? "bg-amber-500/10 border-amber-500/30 text-amber-200"
              : "bg-emerald-500/10 border-emerald-500/30 text-emerald-200"
          }`}
        >
          <div className="flex items-start gap-3">
            {sade_sati.is_active ? (
              <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5 animate-pulse" />
            ) : (
              <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-serif text-sm font-bold">
                  {sade_sati.is_active ? `Sade Sati Active (${sade_sati.phase})` : "Sade Sati Inactive"}
                </span>
                {kantaka_shani && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    Kantaka Shani (4th)
                  </span>
                )}
                {ashtama_shani && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                    Ashtama Shani (8th)
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                {sade_sati.description}
              </p>
            </div>
          </div>
        </div>

        {/* Highlights bullets */}
        {summary_highlights.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {summary_highlights.map((hl, i) => (
              <span
                key={i}
                className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-surface/70 border border-surface-border text-slate-300 flex items-center gap-1.5"
              >
                <Sparkles className="w-3 h-3 text-gold-400" />
                {hl}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* TRANSIT PLANETARY TABLE */}
      <div className="p-5 overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-surface-border text-slate-400 uppercase text-[10px]">
              <th className="pb-2.5">Graha</th>
              <th className="pb-2.5">Transiting Sign</th>
              <th className="pb-2.5">Degree</th>
              <th className="pb-2.5">From Lagna</th>
              <th className="pb-2.5">From Moon</th>
              <th className="pb-2.5">Motion</th>
              <th className="pb-2.5">Classical Gochar Indication</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/40 text-slate-200">
            {transits.map((t) => (
              <tr key={t.planet_id} className="hover:bg-surface-card/50 transition-colors">
                <td className="py-2.5 font-bold font-serif text-white">{t.planet_id}</td>
                <td className="py-2.5 text-sky-300 font-semibold">{t.transit_sign_name}</td>
                <td className="py-2.5 text-slate-300">{t.transit_degree}°</td>
                <td className="py-2.5">House {t.house_from_lagna}</td>
                <td className="py-2.5 font-semibold text-gold-300">House {t.house_from_moon}</td>
                <td className="py-2.5">
                  {t.is_retrograde ? (
                    <span className="text-amber-400 flex items-center gap-1 text-[11px]">
                      <RotateCw className="w-3 h-3 animate-spin-slow" />
                      Retro
                    </span>
                  ) : (
                    <span className="text-emerald-400 text-[11px]">Direct</span>
                  )}
                </td>
                <td className="py-2.5 text-[11px] text-slate-400 max-w-xs truncate">
                  {t.classical_effect}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
