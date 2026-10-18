"use client";

import React, { useState } from "react";
import { BirthProfile, ChartCalculationResult, ChartRecord } from "@/types/astrology";
import { Sparkles, User, MapPin, Calendar, Clock, Globe, Shield, AlertTriangle, CheckCircle2, ChevronRight } from "lucide-react";

interface BirthProfileFormProps {
  onChartCalculated: (profile: BirthProfile, chart: ChartRecord) => void;
  apiBaseUrl?: string;
}

const COMMON_TIMEZONES = [
  "Asia/Kolkata",
  "America/New_York",
  "America/Los_Angeles",
  "America/Chicago",
  "Europe/London",
  "Europe/Paris",
  "Asia/Dubai",
  "Asia/Tokyo",
  "Asia/Singapore",
  "Australia/Sydney",
  "UTC",
];

const GOLDEN_SAMPLES = [
  {
    label: "Golden Reference 1980 (New Delhi)",
    name: "Golden Native (New Delhi 1980)",
    birth_date: "1980-01-01",
    birth_time: "12:00:00",
    timezone: "Asia/Kolkata",
    birthplace: "New Delhi, India",
    latitude: 28.6139,
    longitude: 77.2090,
    confidence: "exact" as const,
  },
  {
    label: "London Midnight 1988",
    name: "London Native (1988)",
    birth_date: "1988-12-05",
    birth_time: "00:01:00",
    timezone: "Europe/London",
    birthplace: "London, UK",
    latitude: 51.5074,
    longitude: -0.1278,
    confidence: "exact" as const,
  },
  {
    label: "New York Dawn 1995",
    name: "New York Native (1995)",
    birth_date: "1995-07-20",
    birth_time: "06:15:00",
    timezone: "America/New_York",
    birthplace: "New York, USA",
    latitude: 40.7128,
    longitude: -74.0060,
    confidence: "exact" as const,
  },
];

import { API_BASE_URL } from "@/lib/api";

export function BirthProfileForm({
  onChartCalculated,
  apiBaseUrl = API_BASE_URL,
}: BirthProfileFormProps) {
  // Auth Identity simulation for testing BOLA/IDOR
  const [authRole, setAuthRole] = useState<"user-a" | "user-b" | "anonymous">("user-a");

  // Form Fields
  const [name, setName] = useState("Arjun Sharma");
  const [birthDate, setBirthDate] = useState("1980-01-01");
  const [birthTime, setBirthTime] = useState("12:00:00");
  const [isUnknownTime, setIsUnknownTime] = useState(false);
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [birthplace, setBirthplace] = useState("New Delhi, India");
  const [latitude, setLatitude] = useState(28.6139);
  const [longitude, setLongitude] = useState(77.2090);
  const [confidence, setConfidence] = useState<"exact" | "approximate" | "rectified" | "unknown">("exact");

  // Ayanamsa & Node Options
  const [ayanamsa, setAyanamsa] = useState("lahiri");
  const [nodeMode, setNodeMode] = useState("mean");

  // UI States
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const getHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (authRole !== "anonymous") {
      headers["Authorization"] = `Bearer test-token-${authRole}`;
    }
    return headers;
  };

  const handleApplySample = (sample: typeof GOLDEN_SAMPLES[0]) => {
    setName(sample.name);
    setBirthDate(sample.birth_date);
    setBirthTime(sample.birth_time);
    setIsUnknownTime(false);
    setTimezone(sample.timezone);
    setBirthplace(sample.birthplace);
    setLatitude(sample.latitude);
    setLongitude(sample.longitude);
    setConfidence(sample.confidence);
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      // 1. Create Birth Profile
      const profilePayload = {
        name,
        birth_date: birthDate,
        birth_time: isUnknownTime ? null : birthTime,
        timezone,
        birthplace,
        latitude: Number(latitude),
        longitude: Number(longitude),
        birth_time_confidence: isUnknownTime ? "unknown" : confidence,
      };

      const profileRes = await fetch(`${apiBaseUrl}/api/v1/birth-profiles`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(profilePayload),
      });

      if (!profileRes.ok) {
        const errorData = await profileRes.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Failed to create profile (${profileRes.status} ${profileRes.statusText})`
        );
      }

      const createdProfile: BirthProfile = await profileRes.json();

      // 2. Calculate Chart
      const chartPayload = {
        ayanamsa,
        node_mode: nodeMode,
        calculation_type: "D1",
      };

      const chartRes = await fetch(`${apiBaseUrl}/api/v1/birth-profiles/${createdProfile.id}/charts`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(chartPayload),
      });

      if (!chartRes.ok) {
        const errorData = await chartRes.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Failed to calculate chart (${chartRes.status} ${chartRes.statusText})`
        );
      }

      const createdChart: ChartRecord = await chartRes.json();

      setSuccessMsg(
        `Calculated successfully! Ascendant: ${createdChart.calculation_result.ascendant_sign_name || "Surya Lagna"}`
      );
      onChartCalculated(createdProfile, createdChart);
    } catch (err: any) {
      setErrorMsg(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-6">
      {/* Auth Persona Switcher for BOLA/IDOR Live Verification */}
      <div className="p-3.5 rounded-xl bg-surface-card border border-surface-border flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-mono text-slate-300">
            Auth Persona (IDOR Test Simulation):
          </span>
        </div>
        <div className="inline-flex rounded-lg bg-surface p-1 border border-surface-border text-xs font-mono">
          <button
            type="button"
            onClick={() => setAuthRole("user-a")}
            className={`px-3 py-1 rounded-md transition-all ${
              authRole === "user-a"
                ? "bg-emerald-600 text-white font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            User A (Owner)
          </button>
          <button
            type="button"
            onClick={() => setAuthRole("user-b")}
            className={`px-3 py-1 rounded-md transition-all ${
              authRole === "user-b"
                ? "bg-amber-600 text-white font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            User B (Attacker)
          </button>
          <button
            type="button"
            onClick={() => setAuthRole("anonymous")}
            className={`px-3 py-1 rounded-md transition-all ${
              authRole === "anonymous"
                ? "bg-rose-700 text-white font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Anonymous (401)
          </button>
        </div>
      </div>

      {/* Quick Fill Golden Samples */}
      <div className="space-y-2">
        <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-gold-400" />
          Quick Load Ephemeris Golden Benchmark Profiles:
        </span>
        <div className="flex flex-wrap gap-2">
          {GOLDEN_SAMPLES.map((sample) => (
            <button
              key={sample.label}
              type="button"
              onClick={() => handleApplySample(sample)}
              className="px-3 py-1.5 rounded-lg bg-surface-card hover:bg-surface-border/60 border border-surface-border text-xs text-slate-300 transition-colors"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">
            Subject Full Name
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-surface-card border border-surface-border rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-sans"
              placeholder="e.g. Arjuna Sharma"
            />
          </div>
        </div>

        {/* Date and Time */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Birth Date (YYYY-MM-DD)
            </label>
            <div className="relative">
              <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="date"
                required
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                className="w-full bg-surface-card border border-surface-border rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-mono"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-medium text-slate-300">
                Birth Time (HH:MM:SS)
              </label>
              <label className="text-[11px] text-slate-400 flex items-center gap-1 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isUnknownTime}
                  onChange={(e) => setIsUnknownTime(e.target.checked)}
                  className="rounded bg-surface border-surface-border text-gold-500 focus:ring-0"
                />
                Unknown Time
              </label>
            </div>
            <div className="relative">
              <Clock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                disabled={isUnknownTime}
                value={isUnknownTime ? "12:00:00 (Surya Lagna fallback)" : birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                className="w-full bg-surface-card border border-surface-border rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-mono disabled:opacity-50"
                placeholder="12:00:00"
              />
            </div>
          </div>
        </div>

        {/* Timezone and Place */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              IANA Timezone
            </label>
            <div className="relative">
              <Globe className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full bg-surface-card border border-surface-border rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-mono"
              >
                {COMMON_TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Birthplace Location
            </label>
            <div className="relative">
              <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                required
                value={birthplace}
                onChange={(e) => setBirthplace(e.target.value)}
                className="w-full bg-surface-card border border-surface-border rounded-xl pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-sans"
                placeholder="City, Country"
              />
            </div>
          </div>
        </div>

        {/* Coordinates */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Latitude (-90 to +90)
            </label>
            <input
              type="number"
              step="0.0001"
              required
              value={latitude}
              onChange={(e) => setLatitude(parseFloat(e.target.value))}
              className="w-full bg-surface-card border border-surface-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Longitude (-180 to +180)
            </label>
            <input
              type="number"
              step="0.0001"
              required
              value={longitude}
              onChange={(e) => setLongitude(parseFloat(e.target.value))}
              className="w-full bg-surface-card border border-surface-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Time Confidence
            </label>
            <select
              value={confidence}
              onChange={(e) => setConfidence(e.target.value as any)}
              className="w-full bg-surface-card border border-surface-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-sans capitalize"
            >
              <option value="exact">Exact (Recorded)</option>
              <option value="approximate">Approximate</option>
              <option value="rectified">Rectified</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
        </div>

        {/* Calculation Parameters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-surface-border/50">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Ayanamsa Standard
            </label>
            <select
              value={ayanamsa}
              onChange={(e) => setAyanamsa(e.target.value)}
              className="w-full bg-surface-card border border-surface-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-sans"
            >
              <option value="lahiri">Lahiri / Chitrapaksha (Standard)</option>
              <option value="raman">B.V. Raman</option>
              <option value="krishnamurti">KP (Krishnamurti)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Lunar Node Convention
            </label>
            <select
              value={nodeMode}
              onChange={(e) => setNodeMode(e.target.value)}
              className="w-full bg-surface-card border border-surface-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-gold-500 font-sans"
            >
              <option value="mean">Mean Node (Classical)</option>
              <option value="true">True Node</option>
            </select>
          </div>
        </div>

        {/* Feedback Alerts */}
        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-500/50 text-rose-200 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/50 text-emerald-200 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-gold-500 to-gold-primary hover:from-gold-400 hover:to-gold-500 text-slate-950 font-bold text-sm tracking-wide transition-all shadow-lg shadow-gold-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <span>Computing Ephemeris & Whole-Sign Bhavas...</span>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Calculate Natal Chart & Dashas
              <ChevronRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
