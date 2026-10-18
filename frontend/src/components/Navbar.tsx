"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, Compass } from "lucide-react";
import { getApiUrl } from "@/lib/api";

export function Navbar() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    fetch(getApiUrl("/health/live"))
      .then((res) => {
        if (res.ok) setBackendStatus("online");
        else setBackendStatus("offline");
      })
      .catch(() => setBackendStatus("offline"));
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full glass-panel border-b border-surface-border/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-500/20 via-cosmic-primary/30 to-surface-card flex items-center justify-center border border-gold-500/30">
            <Compass className="w-6 h-6 text-gold-400 animate-pulse" />
          </div>
          <div>
            <span className="font-serif text-xl font-bold tracking-wider text-white">
              ASTRO<span className="text-gold-400">MIND</span>
            </span>
            <span className="ml-1 text-[10px] uppercase tracking-widest px-1.5 py-0.5 rounded bg-cosmic-dark/50 text-cosmic-light border border-cosmic-primary/30">
              AI Core
            </span>
          </div>
        </a>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
          <a href="/chart" className="text-gold-400 font-semibold hover:text-gold-300 transition-colors">
            Kundli Portal
          </a>
          <a href="/#features" className="hover:text-gold-400 transition-colors">
            Deterministic Engine
          </a>
          <a href="/#architecture" className="hover:text-gold-400 transition-colors">
            Architecture
          </a>
          <a href="/#disclaimer" className="hover:text-gold-400 transition-colors">
            Ethics & Scope
          </a>
        </nav>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-surface-card border border-surface-border text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "online"
                  ? "bg-emerald-400 shadow-[0_0_8px_#34d399]"
                  : backendStatus === "checking"
                  ? "bg-amber-400 animate-ping"
                  : "bg-rose-500"
              }`}
            />
            <span className="text-slate-300 capitalize text-[11px] font-mono">
              API: {backendStatus}
            </span>
          </div>

          <a
            href="/chart"
            className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-gold-600 to-gold-primary hover:from-gold-500 hover:to-gold-600 text-slate-950 font-semibold text-xs tracking-wide transition-all shadow-lg shadow-gold-500/10"
          >
            <Sparkles className="w-4 h-4" />
            Launch Portal
          </a>
        </div>
      </div>
    </header>
  );
}
