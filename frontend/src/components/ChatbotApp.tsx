"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Compass,
  Sparkles,
  Send,
  Loader2,
  Download,
  Calendar,
  Clock,
  MapPin,
  User,
  Shield,
  BookOpen,
  ChevronRight,
  Plus,
  RefreshCw,
  LogOut,
  LogIn,
  Eye,
  Crown,
  Flame,
  Orbit,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { getApiUrl } from "@/lib/api";
import { getStoredToken, getStoredUser, clearAuthSession, AuthUser, fetchCurrentUser } from "@/lib/auth";
import { AuthModal } from "@/components/AuthModal";
import { KundliChart } from "@/components/KundliChart";
import { PlanetaryTable } from "@/components/PlanetaryTable";
import { DashaTimeline } from "@/components/DashaTimeline";
import { PdfReportDownloadButton } from "@/components/PdfReportDownloadButton";
import { BirthProfile, ChartRecord, InterpretationResponse } from "@/types/astrology";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  content: string;
  citations?: string[];
  toolsCalled?: string[];
  chartSummary?: {
    ascendant: string;
    moonSign: string;
    nakshatra: string;
    sunSign: string;
  };
  timestamp: string;
}

const COMMON_CITIES = [
  { name: "New Delhi, India", lat: 28.6139, lon: 77.209, tz: "Asia/Kolkata" },
  { name: "Mumbai, India", lat: 19.076, lon: 72.8777, tz: "Asia/Kolkata" },
  { name: "Bangalore, India", lat: 12.9716, lon: 77.5946, tz: "Asia/Kolkata" },
  { name: "Kolkata, India", lat: 22.5726, lon: 88.3639, tz: "Asia/Kolkata" },
  { name: "Chennai, India", lat: 13.0827, lon: 80.2707, tz: "Asia/Kolkata" },
  { name: "New York, USA", lat: 40.7128, lon: -74.006, tz: "America/New_York" },
  { name: "London, UK", lat: 51.5074, lon: -0.1278, tz: "Europe/London" },
  { name: "Dubai, UAE", lat: 25.2048, lon: 55.2708, tz: "Asia/Dubai" },
  { name: "Singapore", lat: 1.3521, lon: 103.8198, tz: "Asia/Singapore" },
];

export function ChatbotApp() {
  // Authentication State
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<"login" | "signup">("login");

  // Chart & Consultation State
  const [activeProfile, setActiveProfile] = useState<BirthProfile | null>(null);
  const [activeChart, setActiveChart] = useState<ChartRecord | null>(null);
  const [chartViewTab, setChartViewTab] = useState<"chart" | "planets" | "dashas">("chart");
  const [showChartModal, setShowChartModal] = useState(false);

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Birth Profile Form inside chat
  const [birthName, setBirthName] = useState("Arjun Sharma");
  const [birthDate, setBirthDate] = useState("1980-01-01");
  const [birthTime, setBirthTime] = useState("12:00:00");
  const [isUnknownTime, setIsUnknownTime] = useState(false);
  const [selectedCity, setSelectedCity] = useState(COMMON_CITIES[0].name);
  const [calcLoading, setCalcLoading] = useState(false);
  const [calcError, setCalcError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initial load
  useEffect(() => {
    const user = getStoredUser();
    if (user) {
      setCurrentUser(user);
    }
    fetchCurrentUser().then((u) => {
      if (u) setCurrentUser(u);
    });

    // Initial greeting message
    setMessages([
      {
        id: "msg-welcome",
        sender: "assistant",
        content: `**Namaste! I am your AstroMind AI Vedic Astrologer.** 

I evaluate natal horoscopes through deterministic ephemeris calculations (Chitrapaksha / Lahiri Ayanamsa and Whole-Sign Bhavas) and source-grounded Parashari analysis.

To begin your personalized Vedic consultation, please confirm your birth details below so I can compute your authentic Natal Kundli.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAiThinking]);

  // Auth Handlers
  const handleAuthSuccess = (user: AuthUser) => {
    setCurrentUser(user);
    const fallbackName = user.email.split("@")[0];
    setBirthName(user.full_name || (fallbackName.charAt(0).toUpperCase() + fallbackName.slice(1)));
  };

  const handleLogout = () => {
    clearAuthSession();
    setCurrentUser(null);
  };

  // Calculate Chart
  const handleCalculateKundli = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setCalcLoading(true);
    setCalcError(null);

    const cityObj = COMMON_CITIES.find((c) => c.name === selectedCity) || COMMON_CITIES[0];
    const token = getStoredToken() || "test-token-usr_golden_001";

    try {
      // 1. Create Birth Profile
      const profPayload = {
        name: birthName.trim() || "Consultation Native",
        birth_date: birthDate,
        birth_time: isUnknownTime ? null : birthTime,
        timezone: cityObj.tz,
        birthplace: cityObj.name,
        latitude: cityObj.lat,
        longitude: cityObj.lon,
        birth_time_confidence: isUnknownTime ? "unknown" : "exact",
      };

      const profRes = await fetch(getApiUrl("/api/v1/birth-profiles"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(profPayload),
      });

      if (!profRes.ok) {
        const errJson = await profRes.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned HTTP ${profRes.status}`);
      }

      const createdProfile: BirthProfile = await profRes.json();
      setActiveProfile(createdProfile);

      // 2. Calculate Chart
      const chartRes = await fetch(getApiUrl(`/api/v1/birth-profiles/${createdProfile.id}/charts`), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          calculation_type: "D1",
          engine: "pyswisseph",
          ayanamsa: "lahiri",
          node_mode: "mean",
        }),
      });

      if (!chartRes.ok) {
        throw new Error(`Chart calculation error (HTTP ${chartRes.status})`);
      }

      const createdChart: ChartRecord = await chartRes.json();
      setActiveChart(createdChart);

      const calc = createdChart.calculation_result;
      const ascSign = calc.ascendant_sign_name || "Pisces";
      const moonPos = calc.planets?.find((p) => p.planet_id === "Moon");
      const sunPos = calc.planets?.find((p) => p.planet_id === "Sun");

      // Append confirmation message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: `chart-ready-${Date.now()}`,
          sender: "assistant",
          content: `✨ **Natal Kundli Successfully Calculated!**

- **Native:** ${createdProfile.name} (${createdProfile.birth_date})
- **Lagna (Ascendant):** ${ascSign} (${(calc.ascendant_longitude || 0).toFixed(2)}°)
- **Janma Rashi (Moon Sign):** ${moonPos?.sign_name || "Gemini"} in **${moonPos?.nakshatra_name || "Mrigashira"}** (Pada ${moonPos?.pada || 1})
- **Surya (Sun Sign):** ${sunPos?.sign_name || "Sagittarius"} (${sunPos?.sign_sanskrit || "Dhanu"})

You can now ask me any question regarding your career, classical yogas, dasha periods, or planetary transits.`,
          chartSummary: {
            ascendant: ascSign,
            moonSign: moonPos?.sign_name || "Gemini",
            nakshatra: moonPos?.nakshatra_name || "Mrigashira",
            sunSign: sunPos?.sign_name || "Sagittarius",
          },
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err: any) {
      setCalcError(err.message || "Failed to calculate birth chart. Please try again.");
    } finally {
      setCalcLoading(false);
    }
  };

  // Send Chat Message to Groq LLM Layer
  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || isAiThinking) return;

    if (!activeChart) {
      setMessages((prev) => [
        ...prev,
        {
          id: `user-msg-${Date.now()}`,
          sender: "user",
          content: text,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
        {
          id: `ai-ask-chart-${Date.now()}`,
          sender: "assistant",
          content:
            "Please compute your birth details above first so I can inspect your verified planetary longitudes and yogas before answering.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setInputText("");
      return;
    }

    // Add user message
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setIsAiThinking(true);

    const token = getStoredToken() || "test-token-usr_golden_001";

    try {
      const res = await fetch(getApiUrl(`/api/v1/charts/${activeChart.id}/interpret`), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: text }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `AI consultation returned HTTP ${res.status}`);
      }

      const interp: InterpretationResponse = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          sender: "assistant",
          content: interp.interpretation,
          citations: interp.citations?.map((c: any) =>
            typeof c === "string"
              ? c
              : `${c.source_work || "Classical Jyotish"}${c.chapter_verse ? ` (${c.chapter_verse})` : ""}${c.topic ? ` — ${c.topic}` : ""}`
          ),
          toolsCalled: interp.tools_called,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: "assistant",
          content: `⚠️ Consultation Error: ${err.message || "Failed to reach AI provider."}`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsAiThinking(false);
    }
  };

  const starterPrompts = [
    "What classical yogas are formed in my chart and what are their effects?",
    "Explain my career indications and strengths based on the 10th house.",
    "What is my active Vimshottari Mahadasha and what should I anticipate?",
    "Check Saturn's transit (Sade Sati) effects on my Moon sign.",
    "Which planets are combust or in debilitation in this Kundli?",
  ];

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* 1. LEFT SIDEBAR */}
      <aside
        className={`${
          sidebarOpen ? "w-80" : "w-0 -translate-x-full"
        } transition-all duration-300 ease-in-out border-r border-surface-border/50 bg-surface-card/60 backdrop-blur-xl flex flex-col shrink-0 z-30`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-surface-border/50 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-gold-500/20 via-cosmic-primary/40 to-surface-card border border-gold-500/30 flex items-center justify-center">
              <Compass className="w-5 h-5 text-gold-400" />
            </div>
            <div>
              <h1 className="font-serif text-lg font-bold text-white tracking-wider flex items-center gap-1.5">
                ASTRO<span className="text-gold-400">MIND</span>
              </h1>
              <span className="text-[10px] text-slate-400 uppercase tracking-widest">AI Vedic Astrologer</span>
            </div>
          </div>

          <button
            onClick={() => {
              setActiveProfile(null);
              setActiveChart(null);
              setMessages((prev) => [
                ...prev,
                {
                  id: `new-${Date.now()}`,
                  sender: "assistant",
                  content: "Started a new consultation. Please provide your birth details above to calculate a fresh Kundli.",
                  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                },
              ]);
            }}
            title="New Reading"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-border/60 transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Active Kundli Mini-Widget */}
        <div className="p-4 flex-1 overflow-y-auto space-y-4 text-xs">
          {activeProfile && activeChart ? (
            <div className="p-3.5 rounded-2xl glass-panel-gold border border-gold-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white text-sm">{activeProfile.name}</span>
                <span className="px-2 py-0.5 rounded-full bg-gold-500/20 text-gold-300 font-mono text-[10px]">Active</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-slate-300">
                <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Ascendant</span>
                  <span className="font-semibold text-white">
                    {activeChart.calculation_result.ascendant_sign_name || "Pisces"}
                  </span>
                </div>
                <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Moon Sign</span>
                  <span className="font-semibold text-white">
                    {activeChart.calculation_result.planets?.find((p) => p.planet_id === "Moon")?.sign_name || "Gemini"}
                  </span>
                </div>
              </div>

              <div className="flex gap-2 pt-1">
                <button
                  onClick={() => setShowChartModal(true)}
                  className="flex-1 py-1.5 px-2.5 rounded-lg bg-surface-card hover:bg-surface-border text-slate-200 font-medium text-[11px] border border-surface-border flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Eye className="w-3.5 h-3.5 text-gold-400" />
                  View Kundli
                </button>
                <div className="flex-1">
                  <PdfReportDownloadButton chartId={activeChart.id} chartName={activeProfile.name} />
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-surface-card/40 border border-surface-border/50 text-center space-y-2">
              <Sparkles className="w-6 h-6 text-gold-400 mx-auto" />
              <p className="font-medium text-slate-200">No Chart Loaded</p>
              <p className="text-[11px] text-slate-400">Fill in your birth details in the chat to compute your Kundli.</p>
            </div>
          )}

          {/* Prompt Topics */}
          <div className="space-y-1.5 pt-2">
            <span className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold px-1">
              Astrological Inquiries
            </span>
            {starterPrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(p)}
                className="w-full text-left p-2.5 rounded-xl bg-surface-card/40 hover:bg-surface-border/60 text-slate-300 hover:text-white transition-colors text-xs leading-snug line-clamp-2 border border-surface-border/30"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* User Footer */}
        <div className="p-3 border-t border-surface-border/50 bg-slate-950/80">
          {currentUser ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 overflow-hidden">
                <div className="w-8 h-8 rounded-full bg-gold-500/20 text-gold-300 border border-gold-500/40 flex items-center justify-center font-bold text-xs">
                  {currentUser.full_name?.charAt(0) || currentUser.email.charAt(0).toUpperCase()}
                </div>
                <div className="truncate">
                  <p className="text-xs font-semibold text-white truncate">{currentUser.full_name || "User"}</p>
                  <p className="text-[10px] text-slate-400 truncate">{currentUser.email}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                title="Sign Out"
                className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-surface-card transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => {
                setAuthModalMode("login");
                setAuthModalOpen(true);
              }}
              className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-gold-500 to-gold-primary text-slate-950 font-semibold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-gold-500/10 hover:opacity-95"
            >
              <LogIn className="w-3.5 h-3.5" />
              Sign In / Register
            </button>
          )}
        </div>
      </aside>

      {/* 2. MAIN CHAT AREA */}
      <main className="flex-1 flex flex-col min-w-0 bg-cosmic-dark relative">
        {/* Top Header */}
        <header className="h-14 border-b border-surface-border/50 px-4 flex items-center justify-between bg-surface-card/40 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-surface-border/50"
            >
              <Compass className="w-5 h-5 text-gold-400" />
            </button>
            <span className="font-serif text-sm font-semibold text-white">
              {activeProfile ? `Consultation: ${activeProfile.name}` : "Vedic Astrology AI Copilot"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              SwissEph Live
            </span>

            {activeChart && (
              <button
                onClick={() => setShowChartModal(true)}
                className="py-1 px-3 rounded-lg glass-panel text-gold-300 hover:text-gold-200 border border-gold-500/30 text-xs font-medium flex items-center gap-1.5 transition-colors"
              >
                <Eye className="w-3.5 h-3.5" />
                View Full Chart
              </button>
            )}
          </div>
        </header>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${
                msg.sender === "user" ? "ml-auto justify-end" : "mr-auto justify-start"
              }`}
            >
              {msg.sender === "assistant" && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-gold-500/30 to-cosmic-primary/40 border border-gold-500/40 flex items-center justify-center shrink-0 mt-1">
                  <Compass className="w-4 h-4 text-gold-300" />
                </div>
              )}

              <div
                className={`rounded-2xl p-4 text-sm leading-relaxed space-y-3 ${
                  msg.sender === "user"
                    ? "bg-gradient-to-br from-gold-500/20 to-cosmic-primary/30 border border-gold-500/40 text-white rounded-tr-none"
                    : "glass-panel border-surface-border text-slate-200 rounded-tl-none shadow-xl"
                }`}
              >
                {/* Message Body */}
                <div className="whitespace-pre-line prose prose-invert prose-sm max-w-none">
                  {msg.content}
                </div>

                {/* Classical Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2 border-t border-surface-border/40 text-xs space-y-1">
                    <span className="text-[11px] font-semibold text-gold-400 flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5" />
                      Classical Jyotish Authorities Cited:
                    </span>
                    <ul className="list-disc list-inside text-slate-400 text-[11px] space-y-0.5">
                      {msg.citations.map((cite, i) => (
                        <li key={i}>{cite}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <span className="block text-[10px] text-slate-500 text-right">{msg.timestamp}</span>
              </div>
            </div>
          ))}

          {/* Interactive Birth Profile Card (If chart not calculated yet) */}
          {!activeChart && (
            <div className="max-w-2xl mx-auto p-6 rounded-2xl glass-panel border border-gold-500/30 shadow-2xl space-y-4">
              <div className="flex items-center gap-2 text-gold-400 font-serif font-bold text-base">
                <Sparkles className="w-5 h-5 text-gold-400" />
                <span>Enter Birth Details for High-Precision Calculation</span>
              </div>
              <p className="text-xs text-slate-400">
                Planetary coordinates, whole-sign houses, and Vimshottari dashas will be calculated automatically using
                the Chitrapaksha (Lahiri) Ayanamsa.
              </p>

              {calcError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{calcError}</span>
                </div>
              )}

              <form onSubmit={handleCalculateKundli} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="space-y-1 sm:col-span-2">
                  <label className="text-slate-300 font-medium">Full Name / Native</label>
                  <input
                    type="text"
                    required
                    value={birthName}
                    onChange={(e) => setBirthName(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-surface-card border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-slate-300 font-medium">Date of Birth</label>
                  <input
                    type="date"
                    required
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-surface-card border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-slate-300 font-medium">Time of Birth</label>
                  <input
                    type="time"
                    step="1"
                    disabled={isUnknownTime}
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-surface-card border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 disabled:opacity-50"
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="text-slate-300 font-medium">Birth City / Location</label>
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="w-full p-2.5 rounded-xl bg-surface-card border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500"
                  >
                    {COMMON_CITIES.map((c) => (
                      <option key={c.name} value={c.name} className="bg-slate-900 text-white">
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="sm:col-span-2 pt-2">
                  <button
                    type="submit"
                    disabled={calcLoading}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-gold-500 via-gold-primary to-amber-500 text-slate-950 font-bold text-xs tracking-wide shadow-lg shadow-gold-500/20 hover:opacity-95 transition-all flex items-center justify-center gap-2"
                  >
                    {calcLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Computing Planetary Longitudes...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        <span>Compute Natal Kundli & Start Consultation</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* AI Thinking Animation */}
          {isAiThinking && (
            <div className="flex gap-3 items-center mr-auto text-slate-400 text-xs pl-2">
              <div className="w-7 h-7 rounded-lg bg-gold-500/20 flex items-center justify-center border border-gold-500/30">
                <Compass className="w-4 h-4 text-gold-400 animate-spin" />
              </div>
              <span className="animate-pulse">AstroMind AI is evaluating classical rules & citations...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Bar */}
        <div className="p-4 border-t border-surface-border/50 bg-slate-950/80 backdrop-blur-md">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="max-w-3xl mx-auto flex items-center gap-2"
          >
            <input
              type="text"
              placeholder={
                activeChart
                  ? "Ask AstroMind about yogas, career, finances, dasha, or transits..."
                  : "Please compute your birth details above to start consulting..."
              }
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isAiThinking}
              className="flex-1 py-3 px-4 rounded-xl bg-surface-card border border-surface-border text-white text-sm focus:outline-none focus:border-gold-500/60 placeholder:text-slate-500"
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isAiThinking}
              className="p-3 rounded-xl bg-gradient-to-r from-gold-500 to-gold-primary text-slate-950 font-bold hover:opacity-95 disabled:opacity-40 transition-all shadow-md shadow-gold-500/10"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <p className="text-center text-[10px] text-slate-500 mt-2">
            AstroMind AI provides source-grounded reflective symbolic insights from classical Jyotish. Not medical, legal, or financial advice.
          </p>
        </div>
      </main>

      {/* 3. MODAL: FULL CHART DETAILS (KUNDLI, PLANETS, DASHAS) */}
      {showChartModal && activeChart && activeProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in">
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6 rounded-2xl glass-panel border border-gold-500/40 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-surface-border pb-4">
              <div>
                <h3 className="font-serif text-xl font-bold text-white">
                  Natal Kundli & Planetary Table — {activeProfile.name}
                </h3>
                <p className="text-xs text-slate-400">
                  {activeProfile.birthplace} &bull; {activeProfile.birth_date} {activeProfile.birth_time || ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <PdfReportDownloadButton chartId={activeChart.id} chartName={activeProfile.name} />
                <button
                  onClick={() => setShowChartModal(false)}
                  className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-surface-border"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Tab Selector */}
            <div className="flex gap-2 border-b border-surface-border pb-2 text-xs font-semibold">
              <button
                onClick={() => setChartViewTab("chart")}
                className={`py-1.5 px-3 rounded-lg transition-colors ${
                  chartViewTab === "chart" ? "bg-gold-500 text-slate-950" : "text-slate-400 hover:text-white"
                }`}
              >
                North Indian Kundli
              </button>
              <button
                onClick={() => setChartViewTab("planets")}
                className={`py-1.5 px-3 rounded-lg transition-colors ${
                  chartViewTab === "planets" ? "bg-gold-500 text-slate-950" : "text-slate-400 hover:text-white"
                }`}
              >
                Planetary Dignities
              </button>
              <button
                onClick={() => setChartViewTab("dashas")}
                className={`py-1.5 px-3 rounded-lg transition-colors ${
                  chartViewTab === "dashas" ? "bg-gold-500 text-slate-950" : "text-slate-400 hover:text-white"
                }`}
              >
                Vimshottari Dasha
              </button>
            </div>

            {/* Tab Contents */}
            <div>
              {chartViewTab === "chart" && (
                <div className="flex justify-center p-4">
                  <div className="w-full max-w-md">
                    <KundliChart
                      calculation={activeChart.calculation_result}
                      title={`${activeProfile.name} — Rashi Kundli (D1)`}
                    />
                  </div>
                </div>
              )}

              {chartViewTab === "planets" && (
                <PlanetaryTable calculation={activeChart.calculation_result} />
              )}

              {chartViewTab === "dashas" && (
                <DashaTimeline dashas={activeChart.calculation_result.vimshottari_dashas} />
              )}
            </div>
          </div>
        </div>
      )}

      {/* 4. AUTH MODAL */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
        initialMode={authModalMode}
      />
    </div>
  );
}
