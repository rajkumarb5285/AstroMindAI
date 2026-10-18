"use client";

import React, { useState } from "react";
import { CompatibilityResult, KootaScore } from "@/types/astrology";
import { getApiUrl } from "@/lib/api";
import {
  Heart,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  Loader2,
  CheckCircle2,
  XCircle,
  HelpCircle,
} from "lucide-react";

interface CompatibilityModalProps {
  currentChartId?: string;
  currentProfileName?: string;
}

export function CompatibilityModal({ currentChartId, currentProfileName }: CompatibilityModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CompatibilityResult | null>(null);

  // Form inputs
  const [brideSign, setBrideSign] = useState(2); // Taurus
  const [brideNakshatra, setBrideNakshatra] = useState(4); // Rohini
  const [bridePada, setBridePada] = useState(1);

  const [groomSign, setGroomSign] = useState(6); // Virgo
  const [groomNakshatra, setGroomNakshatra] = useState(13); // Hasta
  const [groomPada, setGroomPada] = useState(2);

  const nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
  ];

  const signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
  ];

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("astromind_token") || "test-token-usr_golden_001";
      const res = await fetch(getApiUrl("/api/v1/compatibility"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          bride_moon_sign: Number(brideSign),
          bride_nakshatra: Number(brideNakshatra),
          bride_pada: Number(bridePada),
          groom_moon_sign: Number(groomSign),
          groom_nakshatra: Number(groomNakshatra),
          groom_pada: Number(groomPada),
        }),
      });

      if (!res.ok) {
        throw new Error(`Compatibility calculation returned ${res.status}`);
      }

      const json: CompatibilityResult = await res.json();
      setResult(json);
    } catch (err: any) {
      setError(err.message || "Failed to evaluate Ashta Koota compatibility.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => {
          setIsOpen(true);
          if (!result) handleCalculate();
        }}
        className="px-4 py-2 rounded-xl bg-pink-500/15 hover:bg-pink-500/25 border border-pink-500/40 text-pink-300 font-medium text-xs flex items-center gap-2 transition-all shadow-sm"
      >
        <Heart className="w-3.5 h-3.5 text-pink-400 fill-pink-400" />
        <span>Ashta Koota Compatibility (Guna Milan)</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-3xl rounded-3xl border border-surface-border overflow-hidden shadow-2xl max-h-[90vh] flex flex-col">
            {/* MODAL HEADER */}
            <div className="p-5 border-b border-surface-border bg-surface/80 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-pink-500/15 border border-pink-500/30 flex items-center justify-center text-pink-400">
                  <Heart className="w-4 h-4 fill-pink-400" />
                </div>
                <div>
                  <h3 className="font-serif text-lg font-bold text-white">
                    36-Point Ashta Koota Compatibility
                  </h3>
                  <p className="text-xs text-slate-400">
                    Deterministic Vedic Guna Milan with dosha detection and classical cancellations.
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-lg hover:bg-surface-card text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                &times;
              </button>
            </div>

            {/* MODAL BODY */}
            <div className="p-6 overflow-y-auto space-y-6">
              {/* PARAMETERS SELECTION */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 rounded-2xl bg-surface/60 border border-surface-border">
                {/* Bride Column */}
                <div className="space-y-3">
                  <h4 className="font-serif text-sm font-bold text-pink-300 flex items-center gap-1.5">
                    <span>Bride (Kanya) Parameters</span>
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <label className="text-slate-400 block mb-1">Moon Sign</label>
                      <select
                        value={brideSign}
                        onChange={(e) => setBrideSign(Number(e.target.value))}
                        className="w-full p-2 rounded-lg bg-slate-900 border border-surface-border text-white text-xs outline-none"
                      >
                        {signs.map((s, i) => (
                          <option key={i} value={i + 1}>{s}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-slate-400 block mb-1">Nakshatra</label>
                      <select
                        value={brideNakshatra}
                        onChange={(e) => setBrideNakshatra(Number(e.target.value))}
                        className="w-full p-2 rounded-lg bg-slate-900 border border-surface-border text-white text-xs outline-none"
                      >
                        {nakshatras.map((n, i) => (
                          <option key={i} value={i + 1}>{i + 1}. {n}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* Groom Column */}
                <div className="space-y-3">
                  <h4 className="font-serif text-sm font-bold text-sky-300 flex items-center gap-1.5">
                    <span>Groom (Vara) Parameters</span>
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <label className="text-slate-400 block mb-1">Moon Sign</label>
                      <select
                        value={groomSign}
                        onChange={(e) => setGroomSign(Number(e.target.value))}
                        className="w-full p-2 rounded-lg bg-slate-900 border border-surface-border text-white text-xs outline-none"
                      >
                        {signs.map((s, i) => (
                          <option key={i} value={i + 1}>{s}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-slate-400 block mb-1">Nakshatra</label>
                      <select
                        value={groomNakshatra}
                        onChange={(e) => setGroomNakshatra(Number(e.target.value))}
                        className="w-full p-2 rounded-lg bg-slate-900 border border-surface-border text-white text-xs outline-none"
                      >
                        {nakshatras.map((n, i) => (
                          <option key={i} value={i + 1}>{i + 1}. {n}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleCalculate}
                  disabled={loading}
                  className="px-5 py-2.5 rounded-xl bg-gold-gradient text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md active:scale-95 transition-all disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  Compute Compatibility
                </button>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
                  {error}
                </div>
              )}

              {/* RESULTS CARD */}
              {result && (
                <div className="space-y-6">
                  {/* SCORE HERO BANNER */}
                  <div className="p-5 rounded-2xl bg-surface-card border border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">
                        Total Compatibility Score
                      </span>
                      <div className="flex items-baseline gap-2 mt-1">
                        <span className="font-serif text-3xl font-bold text-white">
                          {result.total_points}
                        </span>
                        <span className="text-slate-400 font-mono text-sm">/ 36.0 Points</span>
                        <span className="text-xs font-mono text-gold-300">({result.percentage}%)</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div
                        className={`px-4 py-2 rounded-xl text-xs font-serif font-bold uppercase tracking-wider border ${
                          result.verdict === "Excellent" || result.verdict === "Good"
                            ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/40"
                            : "bg-amber-500/15 text-amber-300 border-amber-500/40"
                        }`}
                      >
                        {result.verdict} Alignment
                      </div>
                    </div>
                  </div>

                  {/* DOSHAS & CANCELLATIONS */}
                  {(result.doshas.length > 0 || result.cancellations.length > 0) && (
                    <div className="space-y-2">
                      {result.cancellations.map((c, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 flex items-start gap-2"
                        >
                          <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <span>{c}</span>
                        </div>
                      ))}
                      {result.doshas.map((d, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start gap-2"
                        >
                          <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                          <span>{d}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 8 KOOTAS BREAKDOWN TABLE */}
                  <div className="rounded-xl border border-surface-border overflow-hidden">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-surface/70 text-slate-400 uppercase text-[10px] border-b border-surface-border">
                        <tr>
                          <th className="p-3">Koota</th>
                          <th className="p-3">Score</th>
                          <th className="p-3">Status</th>
                          <th className="p-3">Classical Analysis</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-surface-border/50 text-slate-200">
                        {result.kootas.map((k) => (
                          <tr key={k.koota_name} className="hover:bg-surface-card/40 transition-colors">
                            <td className="p-3 font-serif font-bold text-white">{k.koota_name}</td>
                            <td className="p-3 font-semibold text-gold-300">
                              {k.points_obtained} / {k.max_points}
                            </td>
                            <td className="p-3">
                              {k.status === "auspicious" && (
                                <span className="text-emerald-400 flex items-center gap-1 text-[11px]">
                                  <CheckCircle2 className="w-3.5 h-3.5" /> Auspicious
                                </span>
                              )}
                              {k.status === "cancelled" && (
                                <span className="text-sky-300 flex items-center gap-1 text-[11px]">
                                  <ShieldCheck className="w-3.5 h-3.5 text-sky-400" /> Cancelled
                                </span>
                              )}
                              {k.status === "dosha" && (
                                <span className="text-rose-400 flex items-center gap-1 text-[11px]">
                                  <XCircle className="w-3.5 h-3.5" /> Dosha
                                </span>
                              )}
                              {k.status === "neutral" && (
                                <span className="text-slate-400 text-[11px]">Moderate</span>
                              )}
                            </td>
                            <td className="p-3 text-[11px] text-slate-300 max-w-xs leading-tight">
                              {k.description}
                              {k.cancellation_reason && (
                                <span className="block text-emerald-400 font-semibold mt-0.5">
                                  {k.cancellation_reason}
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
