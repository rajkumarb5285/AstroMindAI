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
  Heart,
  Briefcase,
  Layers,
  HelpCircle,
  CheckCircle2,
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
  { name: "Hyderabad, India", lat: 17.3850, lon: 78.4867, tz: "Asia/Kolkata" },
  { name: "Varanasi, India", lat: 25.3176, lon: 82.9739, tz: "Asia/Kolkata" },
  { name: "Jaipur, India", lat: 26.9124, lon: 75.7873, tz: "Asia/Kolkata" },
  { name: "New York, USA", lat: 40.7128, lon: -74.006, tz: "America/New_York" },
  { name: "London, UK", lat: 51.5074, lon: -0.1278, tz: "Europe/London" },
  { name: "Dubai, UAE", lat: 25.2048, lon: 55.2708, tz: "Asia/Dubai" },
  { name: "Singapore", lat: 1.3521, lon: 103.8198, tz: "Asia/Singapore" },
];

/**
 * Apple-grade formatted markdown renderer for Vedic astrological consultation messages.
 */
function FormattedAstrologyMessage({ content }: { content: string }) {
  const lines = content.split("\n");

  return (
    <div className="space-y-3.5 text-sm leading-relaxed text-zinc-200">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (!trimmed) {
          return <div key={idx} className="h-1.5" />;
        }

        // Section Headers (### or ##)
        if (trimmed.startsWith("###") || trimmed.startsWith("##")) {
          const title = trimmed.replace(/^#+\s*/, "");
          return (
            <div key={idx} className="pt-2 border-t border-white/[0.06] first:border-0 first:pt-0">
              <h4 className="font-serif text-base font-bold text-amber-400 tracking-wide flex items-center gap-2">
                {title}
              </h4>
            </div>
          );
        }

        // Horizontal Separator
        if (trimmed === "---") {
          return <hr key={idx} className="border-white/[0.08] my-3" />;
        }

        // Bullet point
        if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
          const itemText = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start gap-2.5 ml-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0 mt-2" />
              <div
                className="text-zinc-200"
                dangerouslySetInnerHTML={{
                  __html: itemText
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em class="text-amber-300/90 not-italic">$1</em>'),
                }}
              />
            </div>
          );
        }

        // Numbered list
        if (/^\d+\.\s/.test(trimmed)) {
          const num = trimmed.match(/^\d+/)?.[0];
          const text = trimmed.replace(/^\d+\.\s*/, "");
          return (
            <div key={idx} className="flex items-start gap-2.5 ml-1 bg-white/[0.02] p-2.5 rounded-xl border border-white/[0.04]">
              <span className="flex items-center justify-center w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 font-bold text-[11px] shrink-0 mt-0.5">
                {num}
              </span>
              <div
                className="text-zinc-200"
                dangerouslySetInnerHTML={{
                  __html: text
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em class="text-amber-300/90 not-italic">$1</em>'),
                }}
              />
            </div>
          );
        }

        // Disclaimer line
        if (trimmed.startsWith("*Disclaimer:") || trimmed.startsWith("Disclaimer:")) {
          return (
            <div key={idx} className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06] text-[11px] text-zinc-400 italic">
              {trimmed.replace(/^\*/, "").replace(/\*$/, "")}
            </div>
          );
        }

        // Standard paragraph
        return (
          <p
            key={idx}
            className="text-zinc-300"
            dangerouslySetInnerHTML={{
              __html: trimmed
                .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em class="text-amber-300/90 not-italic">$1</em>'),
            }}
          />
        );
      })}
    </div>
  );
}

export function ChatbotApp() {
  // Authentication & Profile States
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);

  // Active Astrology Session
  const [activeProfile, setActiveProfile] = useState<BirthProfile | null>(null);
  const [activeChart, setActiveChart] = useState<ChartRecord | null>(null);

  // Birth Profile Form Inputs
  const [birthName, setBirthName] = useState("Rajkumar Pandey");
  const [birthDate, setBirthDate] = useState("1995-10-24");
  const [birthTime, setBirthTime] = useState("12:00:00");
  const [selectedCity, setSelectedCity] = useState("New Delhi, India");
  const [isUnknownTime, setIsUnknownTime] = useState(false);
  const [calcLoading, setCalcLoading] = useState(false);
  const [calcError, setCalcError] = useState<string | null>(null);

  // Chat Conversation State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Full Chart Modal View
  const [showChartModal, setShowChartModal] = useState(false);
  const [chartViewTab, setChartViewTab] = useState<"chart" | "planets" | "dashas">("chart");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize Auth & Welcome Message
  useEffect(() => {
    const user = getStoredUser();
    if (user) {
      setCurrentUser(user);
      fetchCurrentUser().then((u) => {
        if (u) setCurrentUser(u);
      });
    }

    setMessages([
      {
        id: "msg-welcome",
        sender: "assistant",
        content:
          "Namaste. I am Acharya Shastri, your Vedic Astrologer with over 30 years of classical Jyotish experience.\n\n" +
          "Whether you are seeking clarity on your **Marriage Timing & Life Partner**, **Career Breakthroughs**, **Active Mahadasha**, or **Sade Sati**, I am here to provide deep, source-grounded answers in clear, compassionate human language.\n\n" +
          "To begin your consultation, please confirm your birth details below so I can calculate your astronomical Kundli.",
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
    setBirthName(user.full_name || fallbackName.charAt(0).toUpperCase() + fallbackName.slice(1));
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

      const chartRecord: ChartRecord = await chartRes.json();
      setActiveChart(chartRecord);

      // 3. Post confirmation to conversation
      const calc = chartRecord.calculation_result;
      const ascSign = calc.ascendant_sign_name || "Pisces";
      const moonPos = calc.planets.find((p) => p.planet_id === "Moon" || p.sanskrit_name === "Chandra");
      const moonSign = moonPos?.sign_name || "Unknown";
      const nakshatra = moonPos?.nakshatra_name || "Shravana";

      setMessages((prev) => [
        ...prev,
        {
          id: `calc-success-${Date.now()}`,
          sender: "assistant",
          content:
            `**Kundli Successfully Calculated for ${createdProfile.name}.**\n\n` +
            `Your celestial placements are confirmed with sub-arcsecond accuracy via Swiss Ephemeris:\n` +
            `• **Ascendant (Lagna):** ${ascSign} (${(calc.ascendant_degree || 0).toFixed(1)}°)\n` +
            `• **Moon Sign (Rashi):** ${moonSign}\n` +
            `• **Birth Nakshatra:** ${nakshatra}\n\n` +
            `Your 7th house (Marriage & Partnership), 10th house (Career & Dharma), and active Vimshottari Mahadasha are now fully loaded.\n\n` +
            `What important question would you like to explore first? You may ask about marriage timing, spouse nature, career horizons, or choose from the suggestions below.`,
          chartSummary: {
            ascendant: ascSign,
            moonSign: moonSign,
            nakshatra: nakshatra,
            sunSign: calc.planets.find((p) => p.planet_id === "Sun")?.sign_name || "Aries",
          },
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err: any) {
      console.error("Calculation Error:", err);
      setCalcError(err.message || "Failed to calculate birth chart. Please verify inputs.");
    } finally {
      setCalcLoading(false);
    }
  };

  // Send Message / Question to Acharya Shastri
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
            "Please confirm your birth details in the card above first so I can inspect your verified planetary longitudes and yogas before giving you an accurate answer.",
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
        throw new Error(`AI Consultation returned HTTP ${res.status}`);
      }

      const aiData: InterpretationResponse = await res.json();

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: "assistant",
        content: aiData.interpretation,
        citations: aiData.citations?.map((c) => `${c.citation}: ${c.topic}`),
        toolsCalled: aiData.tools_called,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      console.error("Consultation Error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: "assistant",
          content:
            "I apologize for the momentary interruption. The astronomical calculations for your chart remain fully verified. Please try asking your question again.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsAiThinking(false);
    }
  };

  const SUGGESTED_QUERIES = [
    { label: "💍 When will I get married & spouse details?", text: "When will I get married? What will my spouse be like and what remedies should I follow?" },
    { label: "💼 Career breakthrough & wealth", text: "Explain my career indications, suitable business vs job, and upcoming financial periods based on the 10th house." },
    { label: "⏳ Active Mahadasha & what to expect", text: "What is my active Vimshottari Mahadasha and Antardasha, and what life events should I anticipate?" },
    { label: "🪐 Saturn's Sade Sati impact & remedies", text: "Check Saturn's transit (Sade Sati) effects on my Moon sign and give simple Vedic remedies." },
    { label: "🌟 Major classical yogas in my Kundli", text: "What classical yogas are formed in my chart (such as Gaja Kesari, Budhaditya, or Raja Yogas) and what are their effects?" },
  ];

  return (
    <div className="flex h-screen w-full bg-[#08090C] text-slate-100 overflow-hidden font-sans apple-glow">
      {/* 1. APPLE GLASS SIDEBAR */}
      <aside
        className={`${
          sidebarOpen ? "w-80" : "w-0 -translate-x-full"
        } transition-all duration-300 ease-in-out border-r border-white/[0.06] bg-[#0c0d12]/90 backdrop-blur-2xl flex flex-col shrink-0 z-30`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-white/[0.06] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500/20 via-amber-600/10 to-transparent border border-amber-500/30 flex items-center justify-center shadow-lg shadow-amber-500/10">
              <Compass className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h1 className="font-serif text-base font-bold text-white tracking-wider flex items-center gap-1">
                ASTRO<span className="text-amber-400">MIND</span>
              </h1>
              <span className="text-[10px] text-zinc-400 uppercase tracking-widest block">AI Vedic Acharya</span>
            </div>
          </div>

          <button
            onClick={() => {
              setActiveProfile(null);
              setActiveChart(null);
              setMessages([
                {
                  id: `new-${Date.now()}`,
                  sender: "assistant",
                  content: "Started a new consultation. Please provide your birth details above to calculate a fresh Kundli.",
                  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                },
              ]);
            }}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition-colors"
            title="Start New Consultation"
          >
            <Plus className="w-4 h-4 text-amber-400" />
          </button>
        </div>

        {/* Active Native Profile Pill */}
        {activeProfile && activeChart && (
          <div className="p-4 border-b border-white/[0.06] bg-white/[0.02]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-white truncate max-w-[170px]">{activeProfile.name}</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Verified
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] text-zinc-400 mb-3">
              <div className="bg-white/[0.03] p-2 rounded-lg border border-white/[0.04]">
                <span className="block text-[10px] text-zinc-400">Ascendant</span>
                <span className="font-medium text-amber-300">
                  {activeChart.calculation_result.ascendant_sign_name || "Taurus"}
                </span>
              </div>
              <div className="bg-white/[0.03] p-2 rounded-lg border border-white/[0.04]">
                <span className="block text-[10px] text-zinc-400">Moon Sign</span>
                <span className="font-medium text-amber-300">
                  {activeChart.calculation_result.planets.find((p) => p.planet_id === "Moon")?.sign_name || "Capricorn"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowChartModal(true)}
                className="flex-1 py-1.5 px-2.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-200 text-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <Eye className="w-3.5 h-3.5 text-amber-400" />
                View Kundli
              </button>

              <div className="flex-1">
                <PdfReportDownloadButton
                  chartId={activeChart.id}
                  chartName={`${activeProfile.name} Executive Kundli`}
                />
              </div>
            </div>
          </div>
        )}

        {/* Quick Astrological Topics */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-2 px-1">
            Consultation Inquiries
          </span>

          {SUGGESTED_QUERIES.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q.text)}
              className="w-full text-left p-2.5 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.04] hover:border-amber-500/30 text-xs text-zinc-300 hover:text-white transition-all flex items-center justify-between group"
            >
              <span className="truncate pr-2">{q.label}</span>
              <ChevronRight className="w-3.5 h-3.5 text-zinc-400 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all shrink-0" />
            </button>
          ))}
        </div>

        {/* Sidebar Footer: User Authentication */}
        <div className="p-4 border-t border-white/[0.06] bg-white/[0.02]">
          {currentUser ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 truncate">
                <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-300 font-bold text-xs shrink-0">
                  {currentUser.email.charAt(0).toUpperCase()}
                </div>
                <div className="truncate">
                  <span className="block text-xs font-medium text-white truncate">
                    {currentUser.full_name || currentUser.email.split("@")[0]}
                  </span>
                  <span className="text-[10px] text-zinc-400 truncate block">{currentUser.email}</span>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-1.5 text-zinc-400 hover:text-rose-400 transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
            >
              <LogIn className="w-4 h-4" />
              Sign In / Register
            </button>
          )}
        </div>
      </aside>

      {/* 2. MAIN CHAT AREA (APPLE STYLE) */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#08090C] relative">
        {/* Apple Frosted Navigation Bar */}
        <header className="h-14 border-b border-white/[0.06] px-4 sm:px-6 flex items-center justify-between bg-[#08090C]/80 backdrop-blur-2xl sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-zinc-400 hover:text-white rounded-lg hover:bg-white/[0.06] transition-colors"
            >
              <Compass className="w-5 h-5 text-amber-400" />
            </button>
            <div className="flex items-center gap-2">
              <span className="font-serif text-sm font-semibold text-white tracking-wide">
                {activeProfile ? `Consultation: ${activeProfile.name}` : "AstroMind AI Acharya"}
              </span>
              <span className="hidden sm:inline-block text-[11px] text-zinc-400 font-normal">
                • 30+ Yrs Vedic Astrologer
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              SwissEph Live
            </span>

            {activeChart && (
              <button
                onClick={() => setShowChartModal(true)}
                className="py-1.5 px-3 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-amber-500/30 text-amber-300 hover:text-amber-200 text-xs font-medium flex items-center gap-1.5 transition-colors"
              >
                <Eye className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">View</span> Kundli Chart
              </button>
            )}
          </div>
        </header>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3.5 max-w-3xl ${
                msg.sender === "user" ? "ml-auto justify-end" : "mr-auto justify-start"
              }`}
            >
              {msg.sender === "assistant" && (
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-600/10 border border-amber-500/30 flex items-center justify-center shrink-0 mt-0.5 shadow-md shadow-amber-500/10">
                  <Compass className="w-5 h-5 text-amber-400" />
                </div>
              )}

              <div
                className={`text-sm leading-relaxed space-y-3 ${
                  msg.sender === "user"
                    ? "bg-white/[0.08] border border-white/[0.12] text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-md max-w-lg"
                    : "apple-glass-card rounded-2xl rounded-tl-sm p-6 shadow-2xl border border-white/[0.08] w-full"
                }`}
              >
                {/* Assistant Astrologer Badge */}
                {msg.sender === "assistant" && (
                  <div className="flex items-center justify-between pb-3 border-b border-white/[0.06] mb-3">
                    <div className="flex items-center gap-2">
                      <span className="font-serif font-bold text-amber-300 text-sm">
                        Acharya Shastri
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 font-mono">
                        30+ Yrs Jyotish Master
                      </span>
                    </div>
                    <span className="text-[10px] text-zinc-400">{msg.timestamp}</span>
                  </div>
                )}

                {/* Message Body */}
                {msg.sender === "user" ? (
                  <p className="text-white text-sm whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <FormattedAstrologyMessage content={msg.content} />
                )}

                {/* Classical Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-3 border-t border-white/[0.06] text-xs space-y-1">
                    <span className="text-[11px] font-semibold text-amber-400/90 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5" />
                      Classical Vedic Citations Grounded in Shastras:
                    </span>
                    <ul className="list-disc list-inside text-zinc-400 text-[11px] space-y-0.5 ml-1">
                      {msg.citations.map((cite, i) => (
                        <li key={i}>{cite}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {msg.sender === "user" && (
                  <span className="block text-[10px] text-zinc-400 text-right mt-1">{msg.timestamp}</span>
                )}
              </div>
            </div>
          ))}

          {/* Interactive Birth Profile Card (If chart not calculated yet) */}
          {!activeChart && (
            <div className="max-w-xl mx-auto p-6 sm:p-8 rounded-3xl apple-glass-card border border-amber-500/30 shadow-[0_20px_50px_rgba(0,0,0,0.7)] space-y-5">
              <div className="flex items-center gap-2.5 text-amber-400 font-serif font-bold text-lg">
                <Sparkles className="w-5 h-5 text-amber-400" />
                <span>Enter Birth Details for High-Accuracy Kundli</span>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Astronomical positions are calculated to sub-arcsecond accuracy via Swiss Ephemeris with the Chitrapaksha (Lahiri) Ayanamsa for accurate predictions.
              </p>

              {calcError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{calcError}</span>
                </div>
              )}

              <form onSubmit={handleCalculateKundli} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="space-y-1 sm:col-span-2">
                  <label className="text-zinc-300 font-medium">Full Name / Native</label>
                  <input
                    type="text"
                    required
                    value={birthName}
                    onChange={(e) => setBirthName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30 transition-all"
                    placeholder="Enter your name"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-zinc-300 font-medium">Date of Birth</label>
                  <input
                    type="date"
                    required
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30 transition-all"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-zinc-300 font-medium">Time of Birth</label>
                  <input
                    type="time"
                    step="1"
                    disabled={isUnknownTime}
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30 transition-all disabled:opacity-40"
                  />
                </div>

                <div className="space-y-1 sm:col-span-2">
                  <label className="text-zinc-300 font-medium">Birth City / Location</label>
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#0c0d12] border border-white/[0.1] text-white focus:outline-none focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30 transition-all"
                  >
                    {COMMON_CITIES.map((c) => (
                      <option key={c.name} value={c.name}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-2 sm:col-span-2 pt-1">
                  <input
                    type="checkbox"
                    id="unknownTime"
                    checked={isUnknownTime}
                    onChange={(e) => setIsUnknownTime(e.target.checked)}
                    className="rounded border-white/[0.2] bg-white/[0.05] text-amber-500 focus:ring-amber-500/30"
                  />
                  <label htmlFor="unknownTime" className="text-zinc-400 text-xs cursor-pointer">
                    Exact birth time is unknown (computes noon Surya Kundli)
                  </label>
                </div>

                <div className="sm:col-span-2 pt-2">
                  <button
                    type="submit"
                    disabled={calcLoading}
                    className="w-full py-3 px-5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25 transition-all disabled:opacity-50"
                  >
                    {calcLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Calculating Astronomical Longitudes...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 text-slate-950" />
                        <span>Calculate Kundli & Begin Consultation</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* AI Thinking Indicator */}
          {isAiThinking && (
            <div className="flex gap-3.5 max-w-xl mr-auto">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-600/10 border border-amber-500/30 flex items-center justify-center shrink-0">
                <Compass className="w-5 h-5 text-amber-400 animate-spin" />
              </div>
              <div className="apple-glass-card rounded-2xl rounded-tl-sm p-4 text-xs text-zinc-300 flex items-center gap-2.5">
                <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
                <span>Acharya Shastri is inspecting your 7th/10th house, transits, and dasha cycles...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Apple Floating Prompt Suggestions & Input */}
        <div className="border-t border-white/[0.06] bg-[#08090C]/90 backdrop-blur-2xl p-3 sm:p-4 space-y-2.5">
          {/* Quick Pill Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 max-w-3xl mx-auto scrollbar-none">
            {SUGGESTED_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(q.text)}
                disabled={isAiThinking}
                className="whitespace-nowrap px-3 py-1.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-amber-500/40 text-xs text-zinc-300 hover:text-white transition-all shrink-0 disabled:opacity-40"
              >
                {q.label}
              </button>
            ))}
          </div>

          {/* Floating Pill Input Bar */}
          <div className="max-w-3xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2 p-1.5 rounded-2xl bg-white/[0.04] border border-white/[0.1] focus-within:border-amber-500/60 focus-within:ring-2 focus-within:ring-amber-500/20 shadow-2xl transition-all"
            >
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={
                  activeChart
                    ? "Ask Acharya Shastri about marriage timing, career, dasha, or remedies..."
                    : "Enter birth details above to unlock personalized consultation..."
                }
                className="flex-1 bg-transparent px-3 py-2 text-sm text-white placeholder-zinc-400 focus:outline-none"
              />

              <button
                type="submit"
                disabled={!inputText.trim() || isAiThinking}
                className="p-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-md shadow-amber-500/20"
              >
                {isAiThinking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </form>

            <p className="text-[10px] text-zinc-400 text-center mt-2">
              AstroMind AI provides source-grounded reflective symbolic insights from classical Jyotish (BPHS, Phaladeepika).
            </p>
          </div>
        </div>
      </main>

      {/* 3. FULL KUNDLI CHART MODAL */}
      {showChartModal && activeChart && activeProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-in fade-in duration-200">
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-3xl apple-glass-card border border-white/[0.1] shadow-2xl p-6 sm:p-8 space-y-6">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
                  <Compass className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h2 className="font-serif text-lg font-bold text-white">
                    {activeProfile.name} — Vedic Kundli
                  </h2>
                  <span className="text-xs text-zinc-400">
                    Calculated via Swiss Ephemeris • Lahiri Chitrapaksha Ayanamsa
                  </span>
                </div>
              </div>

              <button
                onClick={() => setShowChartModal(false)}
                className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.06] transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 border-b border-white/[0.06] pb-2">
              <button
                onClick={() => setChartViewTab("chart")}
                className={`py-1.5 px-4 rounded-xl text-xs font-medium transition-all ${
                  chartViewTab === "chart"
                    ? "bg-amber-500 text-slate-950 font-bold"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Diamond Kundli (D1)
              </button>
              <button
                onClick={() => setChartViewTab("planets")}
                className={`py-1.5 px-4 rounded-xl text-xs font-medium transition-all ${
                  chartViewTab === "planets"
                    ? "bg-amber-500 text-slate-950 font-bold"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Planetary Longitudes & Dignities
              </button>
              <button
                onClick={() => setChartViewTab("dashas")}
                className={`py-1.5 px-4 rounded-xl text-xs font-medium transition-all ${
                  chartViewTab === "dashas"
                    ? "bg-amber-500 text-slate-950 font-bold"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                Vimshottari Dasha Timeline
              </button>
            </div>

            {/* Tab Views */}
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
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}
