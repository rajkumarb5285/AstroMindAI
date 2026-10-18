import React from "react";
import { Shield, Lock, AlertTriangle, BookOpen } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full bg-surface border-t border-surface-border/50 py-12 px-4 sm:px-6 lg:px-8 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Ethical & Legal Disclaimer Banner required by product specification */}
        <div id="disclaimer" className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200/90 text-xs leading-relaxed flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-amber-300 mb-1">
              Important Ethical & Non-Predictive Disclaimer
            </p>
            <p>
              Vedic Astrology (Jyotish) is a traditional interpretive symbolic practice, not an empirical scientifically validated method for predicting future events. AstroMind AI does not make guaranteed claims, predictions of absolute certainty, or replace licensed medical, mental health, legal, investment, or financial advice. All interpretations are source-grounded reflective insights.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pt-4">
          <div className="space-y-3">
            <h4 className="font-serif text-white font-semibold tracking-wider text-base">
              AstroMind AI
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Deterministic Vedic astrology calculation engine paired with source-grounded AI intelligence. Built with defense-in-depth and mathematical rigor.
            </p>
          </div>

          <div>
            <h5 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">
              Calculation Standards
            </h5>
            <ul className="space-y-2 text-xs">
              <li>Sidereal Zodiac Coordinate System</li>
              <li>Lahiri / Chitrapaksha Ayanamsa</li>
              <li>Whole-Sign Houses (Bhavas)</li>
              <li>Mean & True Lunar Nodes (Rahu/Ketu)</li>
              <li>365.25-Day Vimshottari Dasha Standard</li>
            </ul>
          </div>

          <div>
            <h5 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">
              Security Architecture
            </h5>
            <ul className="space-y-2 text-xs">
              <li className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                Row-Level Security (RLS)
              </li>
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-emerald-400" />
                Zero Secrets in LLM Prompts
              </li>
              <li className="flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
                Curated Allowlisted RAG Sources
              </li>
              <li>Strict Object-Level Authorization</li>
            </ul>
          </div>

          <div>
            <h5 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">
              Data Privacy
            </h5>
            <p className="text-xs text-slate-400 leading-relaxed mb-2">
              Birth details, charts, and private readings are strictly segregated per tenant. User conversations are never embedded into public knowledge indexes.
            </p>
            <p className="text-[11px] text-slate-500">
              © {new Date().getFullYear()} AstroMind AI. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
