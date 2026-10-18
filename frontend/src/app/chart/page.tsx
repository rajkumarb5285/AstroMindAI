"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { BirthProfileForm } from "@/components/BirthProfileForm";
import { KundliChart } from "@/components/KundliChart";
import { PlanetaryTable } from "@/components/PlanetaryTable";
import { DashaTimeline } from "@/components/DashaTimeline";
import { RulesSummaryCard } from "@/components/RulesSummaryCard";
import { GroundedChatDrawer } from "@/components/GroundedChatDrawer";
import { GocharTransitCard } from "@/components/GocharTransitCard";
import { CompatibilityModal } from "@/components/CompatibilityModal";
import { PdfReportDownloadButton } from "@/components/PdfReportDownloadButton";
import { BirthProfile, ChartRecord } from "@/types/astrology";
import {
  Compass,
  Sparkles,
  Shield,
  FileCode,
  Layers,
  ChevronDown,
  ChevronUp,
  Download,
  AlertCircle,
} from "lucide-react";

export default function ChartPortalPage() {
  const [activeProfile, setActiveProfile] = useState<BirthProfile | null>(null);
  const [activeChart, setActiveChart] = useState<ChartRecord | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);

  const handleChartCalculated = (profile: BirthProfile, chart: ChartRecord) => {
    setActiveProfile(profile);
    setActiveChart(chart);
  };

  const calculation = activeChart?.calculation_result;

  return (
    <div className="flex-1 flex flex-col cosmic-gradient min-h-screen">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* HEADER BANNER */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border/60 pb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-panel-gold text-gold-300 text-xs font-mono mb-2 border-gold-glow">
              <Sparkles className="w-3.5 h-3.5 text-gold-400" />
              <span>Phase 6 &bull; Chat, Compatibility, Transits & PDF Reports</span>
            </div>
            <h1 className="font-serif text-3xl sm:text-4xl font-bold text-white tracking-tight">
              Natal Chart & Vedic Kundli Portal
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              Compute geocentric planetary positions, Ascendant, Whole-Sign houses, and Vimshottari
              Dashas using Swiss Ephemeris. Protected by server-side owner-scoped authorization.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <CompatibilityModal
              currentChartId={activeChart?.id}
              currentProfileName={activeProfile?.name}
            />
            {activeChart && activeProfile && (
              <PdfReportDownloadButton
                chartId={activeChart.id}
                chartName={activeProfile.name}
              />
            )}
            <div className="glass-panel p-3 rounded-xl border border-surface-border text-right">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">
                Security Model
              </span>
              <span className="text-xs font-semibold text-emerald-400 flex items-center justify-end gap-1 mt-0.5">
                <Shield className="w-3.5 h-3.5" />
                Owner-Scoped API
              </span>
            </div>
          </div>
        </div>

        {/* WORKSPACE GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* LEFT COLUMN: Input Form (4 cols on lg) */}
          <div className="lg:col-span-5 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-serif text-lg font-bold text-white flex items-center gap-2">
                <Compass className="w-5 h-5 text-gold-400" />
                Birth Profile & Parameters
              </h2>
            </div>

            <BirthProfileForm onChartCalculated={handleChartCalculated} />

            {/* Ethical Scope Callout */}
            <div className="p-4 rounded-xl bg-surface/60 border border-surface-border/60 text-xs text-slate-400 space-y-1.5">
              <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                <AlertCircle className="w-3.5 h-3.5 text-gold-400" />
                <span>Ephemeris Precision Notice</span>
              </div>
              <p className="leading-relaxed text-[11px]">
                Planetary positions are calculated to sub-arcsecond astronomical accuracy via Swiss
                Ephemeris. Astrology is a traditional interpretive discipline; calculations do not
                constitute financial, legal, or medical guarantees.
              </p>
            </div>
          </div>

          {/* RIGHT COLUMN: Kundli, Table, Dashas (7 cols on lg) */}
          <div className="lg:col-span-7 space-y-6">
            {calculation && activeProfile ? (
              <>
                {/* QUICK STATS SUMMARY CARD */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="glass-panel p-3.5 rounded-xl border border-surface-border">
                    <span className="text-[10px] font-mono uppercase text-slate-400 block">
                      Lagna (Ascendant)
                    </span>
                    <span className="font-serif text-base font-bold text-sky-400 mt-0.5 block">
                      {calculation.ascendant_sign_name || "Surya Lagna"}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {calculation.ascendant_degree !== null ? `${calculation.ascendant_degree.toFixed(2)}° • Pada ${calculation.ascendant_pada}` : "Approximate"}
                    </span>
                  </div>

                  <div className="glass-panel p-3.5 rounded-xl border border-surface-border">
                    <span className="text-[10px] font-mono uppercase text-slate-400 block">
                      Moon Sign (Rashi)
                    </span>
                    <span className="font-serif text-base font-bold text-white mt-0.5 block">
                      {calculation.planets.find((p) => p.planet_id === "Moon")?.sign_name || "N/A"}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {calculation.planets.find((p) => p.planet_id === "Moon")?.nakshatra_name || ""}
                    </span>
                  </div>

                  <div className="glass-panel p-3.5 rounded-xl border border-surface-border">
                    <span className="text-[10px] font-mono uppercase text-slate-400 block">
                      Sun Sign
                    </span>
                    <span className="font-serif text-base font-bold text-gold-400 mt-0.5 block">
                      {calculation.planets.find((p) => p.planet_id === "Sun")?.sign_name || "N/A"}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      House {calculation.planets.find((p) => p.planet_id === "Sun")?.house_number || 1}
                    </span>
                  </div>

                  <div className="glass-panel p-3.5 rounded-xl border border-surface-border">
                    <span className="text-[10px] font-mono uppercase text-slate-400 block">
                      Profile Owner
                    </span>
                    <span className="font-mono text-xs font-bold text-emerald-400 mt-1 block truncate">
                      {activeProfile.owner_id}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      ID: {activeProfile.id.slice(0, 8)}...
                    </span>
                  </div>
                </div>

                {/* KUNDLI VISUALIZER */}
                <KundliChart
                  calculation={calculation}
                  title={`${activeProfile.name} — Kundli`}
                />

                {/* PLANETARY LONGITUDES TABLE */}
                <PlanetaryTable calculation={calculation} />

                {/* VIMSHOTTARI DASHA PROGRESSION */}
                <DashaTimeline dashas={calculation.vimshottari_dashas} />

                {/* PHASE 5: DETERMINISTIC CLASSICAL RULE ENGINE EVALUATION */}
                <RulesSummaryCard chartId={activeChart.id} />

                {/* PHASE 6: REAL-TIME PLANETARY GOCHAR TRANSITS & SADE SATI */}
                <GocharTransitCard chartId={activeChart.id} />

                {/* PHASE 5: SOURCE-GROUNDED AI VEDIC CONSULTATION */}
                <GroundedChatDrawer
                  chartId={activeChart.id}
                  chartOwner={activeProfile.owner_id}
                />

                {/* RAW EPHEMERIS PAYLOAD INSPECTION (Security & Verification) */}
                <div className="glass-panel rounded-2xl border border-surface-border overflow-hidden">
                  <button
                    onClick={() => setShowRawJson(!showRawJson)}
                    className="w-full p-4 flex items-center justify-between text-left text-xs font-mono text-slate-300 hover:bg-surface-card transition-colors"
                  >
                    <span className="flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-gold-400" />
                      Inspect Raw Ephemeris JSON Payload (Deterministic Proof)
                    </span>
                    {showRawJson ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </button>

                  {showRawJson && (
                    <div className="p-4 bg-slate-950/80 border-t border-surface-border overflow-x-auto max-h-96 text-[11px] font-mono text-emerald-300">
                      <pre>{JSON.stringify(activeChart, null, 2)}</pre>
                    </div>
                  )}
                </div>
              </>
            ) : (
              /* EMPTY STATE: Guidance & Teaser */
              <div className="glass-panel p-12 rounded-2xl border border-surface-border/60 text-center space-y-6">
                <div className="w-16 h-16 rounded-2xl bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-400 mx-auto">
                  <Compass className="w-8 h-8 animate-spin-slow" />
                </div>

                <div className="max-w-md mx-auto space-y-2">
                  <h3 className="font-serif text-xl font-bold text-white">
                    Chart Visualizer Ready
                  </h3>
                  <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                    Select a Golden Benchmark profile on the left or enter birth coordinates to generate
                    an astronomical Kundli diagram and Vimshottari Dasha timeline.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-lg mx-auto text-left pt-4">
                  <div className="p-3 rounded-xl bg-surface/60 border border-surface-border text-xs">
                    <span className="text-gold-400 font-bold block mb-1">D1 Rashi</span>
                    <span className="text-slate-400 text-[11px]">
                      Ascendant & 9 Grahas mapped to Whole-Sign Bhavas.
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-surface/60 border border-surface-border text-xs">
                    <span className="text-gold-400 font-bold block mb-1">D9 Navamsa</span>
                    <span className="text-slate-400 text-[11px]">
                      Verified classical divisional harmonic coordinates.
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-surface/60 border border-surface-border text-xs">
                    <span className="text-gold-400 font-bold block mb-1">120-Yr Dasha</span>
                    <span className="text-slate-400 text-[11px]">
                      Sub-period boundary calculations with active phase detection.
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
