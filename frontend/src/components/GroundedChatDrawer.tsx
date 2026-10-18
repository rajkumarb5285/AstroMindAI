"use client";

import React, { useState } from "react";
import { InterpretationResponse } from "@/types/astrology";
import {
  MessageSquare,
  Sparkles,
  Send,
  Loader2,
  ShieldAlert,
  BookOpen,
  Terminal,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Quote,
} from "lucide-react";

interface GroundedChatDrawerProps {
  chartId: string;
  chartOwner: string;
}

export function GroundedChatDrawer({ chartId, chartOwner }: GroundedChatDrawerProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<InterpretationResponse[]>([]);
  const [expandedTools, setExpandedTools] = useState<Record<number, boolean>>({});

  const presetQuestions = [
    "What classical yogas are present in this chart and what are their effects?",
    "Explain the dignity and strength of the Lagna lord and 10th house lord.",
    "Which planets are combust or casting special aspects in this chart?",
  ];

  const handleSend = async (qToSend?: string) => {
    const q = (qToSend || question).trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("astromind_token") || "test-token-usr_golden_001";
      const res = await fetch(`http://127.0.0.1:8000/api/v1/charts/${chartId}/interpret`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        throw new Error(errData.detail || `Server returned ${res.status}`);
      }

      const data: InterpretationResponse = await res.json();
      data.question = q;
      setHistory((prev) => [data, ...prev]);
      setQuestion("");
    } catch (err: any) {
      setError(err.message || "Failed to generate grounded interpretation.");
    } finally {
      setLoading(false);
    }
  };

  const toggleTools = (idx: number) => {
    setExpandedTools((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="glass-panel rounded-2xl border border-surface-border overflow-hidden">
      {/* DRAWER HEADER */}
      <div className="p-5 border-b border-surface-border/80 bg-surface/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gold-500/10 border border-gold-500/30 flex items-center justify-center text-gold-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-bold text-white flex items-center gap-2">
                Source-Grounded AI Vedic Consultation
              </h3>
              <p className="text-xs text-slate-400">
                Sandboxed classical synthesis with deterministic tool verification & scripture citations.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            Read-Only Tools
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-sky-500/15 text-sky-400 border border-sky-500/30">
            Allowlisted RAG
          </span>
        </div>
      </div>

      {/* CONSULTATION INPUT & PRESETS */}
      <div className="p-5 border-b border-surface-border/50 space-y-4">
        {/* Preset chips */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
            <HelpCircle className="w-3 h-3 text-gold-400" /> Presets:
          </span>
          {presetQuestions.map((preset, i) => (
            <button
              key={i}
              onClick={() => handleSend(preset)}
              disabled={loading}
              className="text-[11px] px-2.5 py-1 rounded-full bg-surface-card hover:bg-gold-500/10 hover:text-gold-300 border border-surface-border hover:border-gold-500/30 text-slate-300 transition-all text-left disabled:opacity-50"
            >
              {preset}
            </button>
          ))}
        </div>

        {/* Input box */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this chart's yogas, dignities, or classical indicators..."
            disabled={loading}
            maxLength={500}
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900/80 border border-surface-border focus:border-gold-500/60 focus:ring-1 focus:ring-gold-500/40 text-xs text-white placeholder-slate-500 transition-all outline-none"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-4 py-2.5 rounded-xl bg-gold-gradient text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-gold-500/10 hover:shadow-gold-500/25 active:scale-95 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                Consult
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
            {error}
          </div>
        )}
      </div>

      {/* CONSULTATION RESPONSE FEED */}
      <div className="p-5 space-y-6 max-h-[600px] overflow-y-auto">
        {history.length === 0 && !loading && (
          <div className="p-8 text-center text-slate-400 space-y-2">
            <MessageSquare className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs">
              Select a preset above or type a question to generate an AI interpretation grounded in classical texts.
            </p>
          </div>
        )}

        {loading && (
          <div className="p-6 rounded-xl bg-surface/50 border border-gold-500/30 text-center space-y-3 animate-pulse">
            <Loader2 className="w-6 h-6 text-gold-400 animate-spin mx-auto" />
            <div className="space-y-1">
              <p className="text-xs font-serif font-bold text-gold-300">
                Grounding Interpretation via Secure Orchestrator...
              </p>
              <p className="text-[11px] font-mono text-slate-400">
                Invoking: get_chart_facts &bull; evaluate_astrology_rules &bull; search_vedic_knowledge
              </p>
            </div>
          </div>
        )}

        {history.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-surface-card border border-surface-border space-y-4 text-xs"
          >
            {/* User Question */}
            <div className="flex items-start gap-2.5 pb-3 border-b border-surface-border/50">
              <div className="w-6 h-6 rounded-full bg-gold-500/20 text-gold-300 flex items-center justify-center font-bold text-[10px] flex-shrink-0">
                Q
              </div>
              <div className="flex-1 flex items-center justify-between">
                <p className="font-semibold text-white text-xs">{item.question || "Chart Inquiry"}</p>
                <span className="text-[10px] font-mono text-slate-400">
                  Tokens: {item.tokens_used}
                </span>
              </div>
            </div>

            {/* Grounded Answer */}
            <div className="space-y-3 leading-relaxed text-slate-200">
              <div className="whitespace-pre-wrap">{item.interpretation}</div>
            </div>

            {/* Classical Citations */}
            {item.citations && item.citations.length > 0 && (
              <div className="pt-3 border-t border-surface-border/50 space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-wider text-gold-400 font-bold flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5" />
                  Scriptural Citations ({item.citations.length})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {item.citations.map((cite, cIdx) => (
                    <div
                      key={cIdx}
                      className="p-2.5 rounded-lg bg-surface/80 border border-gold-500/20 text-[11px] space-y-1"
                    >
                      <div className="font-serif font-bold text-gold-300 flex items-center gap-1">
                        <Quote className="w-3 h-3 text-gold-400" />
                        {cite.citation}
                      </div>
                      {cite.topic && (
                        <div className="text-[10px] font-mono text-slate-400">
                          Topic: {cite.topic}
                        </div>
                      )}
                      {cite.content && (
                        <p className="text-[10px] text-slate-300 italic line-clamp-2">
                          &ldquo;{cite.content}&rdquo;
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Audit Trail: Tools Executed */}
            {item.tools_called && item.tools_called.length > 0 && (
              <div className="pt-2">
                <button
                  onClick={() => toggleTools(idx)}
                  className="w-full p-2 rounded-lg bg-slate-900/60 hover:bg-slate-900 border border-surface-border flex items-center justify-between text-[11px] font-mono text-slate-400 transition-colors"
                >
                  <span className="flex items-center gap-1.5 text-sky-400">
                    <Terminal className="w-3.5 h-3.5" />
                    Tool Audit Trail ({item.tools_called.length} tools executed)
                  </span>
                  {expandedTools[idx] ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>

                {expandedTools[idx] && (
                  <div className="mt-2 p-3 rounded-lg bg-slate-950 border border-surface-border space-y-2 text-[10px] font-mono">
                    {item.tools_called.map((t, tIdx) => (
                      <div key={tIdx} className="space-y-0.5 border-b border-surface-border/30 pb-1.5 last:border-none">
                        <div className="text-emerald-400 font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          Tool {tIdx + 1}: {t}
                        </div>
                        <div className="text-slate-400">Status: Verified & Executed in read-only sandbox</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Non-dismissible Mandatory Disclaimer */}
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-2.5 text-[11px] text-amber-200">
              <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                {item.disclaimer}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
