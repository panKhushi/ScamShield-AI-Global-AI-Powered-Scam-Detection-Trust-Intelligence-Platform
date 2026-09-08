"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase";
import { useAuth } from "./providers/AuthProvider";
import ReportForm from "./components/ReportForm";
import CommunityReports from "./components/CommunityReports";

type ScoreFactor = {
  name: string;
  weight: number;
  status: "good" | "warning" | "bad";
  detail: string;
};

type RiskBreakdown = { [component: string]: number };

type FeatureExplanation = {
  feature: string;
  contribution: number;
  direction: string;
};

type AnalyzeResponse = {
  input_value: string;
  input_type: string;
  trust_score: number;
  verdict: "safe" | "suspicious" | "dangerous";
  factors: ScoreFactor[];
  ml_scam_probability: number;
  recommendations: string[];
  risk_breakdown: RiskBreakdown;
  explanation: FeatureExplanation[];
};

type InputMode = "url" | "job" | "email";

const modeConfig = {
  url: { label: "URL / Website", placeholder: "Enter a URL, e.g. example.com", endpoint: "/api/analyze" },
  job: { label: "Job Offer", placeholder: "Paste the job offer text here...", endpoint: "/api/analyze-job" },
  email: { label: "Email", placeholder: "Paste the email content here...", endpoint: "/api/analyze-email" },
};

export default function Home() {
  const [mode, setMode] = useState<InputMode>("url");
  const [input, setInput] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);
  const { user } = useAuth();

  async function handleAnalyze() {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    setShowReportForm(false);
    try {
      const supabase = createClient();
      const { data: sessionData } = await supabase.auth.getSession();
      const token = sessionData.session?.access_token;

      const res = await fetch(`http://localhost:8000${modeConfig[mode].endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ input_type: mode, value: input }),
      });
      const data: AnalyzeResponse = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center px-4 pb-16 pt-12 text-[#E8ECF1]">
      <div className="relative w-full max-w-6xl">
        <div className="ambient-glow absolute inset-x-0 top-0 -z-10 mx-auto h-72 w-72 rounded-full bg-[#22D3B8]/20 blur-3xl" />

        <section className="reveal-up interactive-panel rounded-[32px] border border-white/10 bg-white/5 p-6 shadow-[0_25px_80px_rgba(15,23,42,0.7)] backdrop-blur-xl sm:p-8">
          <div className="reveal-up reveal-delay-1 mb-8 flex flex-col items-center text-center">
            <span className="mb-4 inline-flex items-center gap-2 rounded-full border border-[#22D3B8]/30 bg-[#22D3B8]/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-[#8FFAE0]">
              ScamShield AI
            </span>
            <h1 className="font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
              Smart protection for every suspicious click.
            </h1>
            <p className="mt-3 max-w-2xl text-sm text-[#8B95AB] sm:text-base">
              Check a website, job offer, or email with AI-powered scam detection and real-time threat scoring.
            </p>
          </div>

          <div className="reveal-up reveal-delay-2 mx-auto mb-6 max-w-xl rounded-2xl border border-white/10 bg-[#0B1324]/80 p-2 shadow-inner shadow-black/20">
            <div className="flex flex-wrap gap-2">
              {(Object.keys(modeConfig) as InputMode[]).map((m) => (
                <button
                  key={m}
                  onClick={() => {
                    setMode(m);
                    setResult(null);
                    setInput("");
                  }}
                  className={`flex-1 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${
                    mode === m
                      ? "bg-gradient-to-r from-[#22D3B8] to-[#34D399] text-[#06131A] shadow-lg shadow-[#22D3B8]/30"
                      : "bg-transparent text-[#8B95AB] hover:bg-white/5 hover:text-white"
                  }`}
                >
                  {modeConfig[m].label}
                </button>
              ))}
            </div>
          </div>

          <div className="reveal-up reveal-delay-3 mx-auto w-full max-w-2xl">
            {mode === "url" ? (
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={modeConfig[mode].placeholder}
                  className="flex-1 rounded-2xl border border-white/10 bg-[#0F1C2F] px-4 py-3.5 text-sm text-white placeholder:text-[#7E8BA4] outline-none ring-0 transition focus:border-[#22D3B8]/60 focus:bg-[#122238]"
                />
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="scan-button rounded-2xl bg-gradient-to-r from-[#22D3B8] to-[#1DB7A7] px-6 py-3.5 text-sm font-bold text-[#07131C] shadow-lg shadow-[#22D3B8]/20 transition hover:scale-[1.03] hover:shadow-[#22D3B8]/35 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "Scanning..." : "Analyze"}
                </button>
              </div>
            ) : (
              <>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={modeConfig[mode].placeholder}
                  rows={6}
                  className="w-full resize-none rounded-2xl border border-white/10 bg-[#0F1C2F] px-4 py-3.5 text-sm text-white placeholder:text-[#7E8BA4] outline-none transition focus:border-[#22D3B8]/60 focus:bg-[#122238]"
                />
                <div className="mt-3 flex justify-end">
                  <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="scan-button rounded-2xl bg-gradient-to-r from-[#22D3B8] to-[#1DB7A7] px-6 py-3 text-sm font-bold text-[#07131C] shadow-lg shadow-[#22D3B8]/20 transition hover:scale-[1.03] hover:shadow-[#22D3B8]/35 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loading ? "Scanning..." : "Analyze"}
                  </button>
                </div>
              </>
            )}
          </div>
        </section>

        {result && (
          <section className="reveal-up interactive-panel mx-auto mt-8 w-full max-w-2xl rounded-[28px] border border-white/10 bg-[#0D1728]/90 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.7)] backdrop-blur-xl sm:p-6">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="mb-2 text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">Checked input</p>
                <span className="block max-w-[420px] truncate font-mono text-sm text-[#DCEAFB]">{result.input_value}</span>
              </div>

              <span className={`rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] ${
                result.verdict === "safe"
                  ? "bg-[#0f766e]/20 text-[#8FFAE0]"
                  : result.verdict === "suspicious"
                  ? "bg-[#F59E0B]/20 text-[#FCD34D]"
                  : "bg-[#EF4444]/20 text-[#FCA5A5]"
              }`}>
                {result.verdict}
              </span>
            </div>

            <div className="mb-6 flex justify-center">
              <div className="relative h-32 w-32">
                <svg className="h-32 w-32 -rotate-90" viewBox="0 0 128 128">
                  <circle cx="64" cy="64" r="52" stroke="#1F2A3B" strokeWidth="10" fill="none" />
                  <circle
                    cx="64"
                    cy="64"
                    r="52"
                    stroke={result.trust_score >= 70 ? "#22D3B8" : result.trust_score >= 40 ? "#F5A623" : "#EF4444"}
                    strokeWidth="10"
                    fill="none"
                    strokeDasharray={`${(result.trust_score / 100) * 326.7} 326.7`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-display text-3xl font-bold text-white">{result.trust_score}</span>
                  <span className="text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">/ 100</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {result.factors.map((f) => (
                <div
                  key={f.name}
                  className="rounded-2xl border border-white/8 bg-[#0F1C2F]/80 p-3.5"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-white">{f.name}</p>
                      <p className="mt-1 text-xs leading-5 text-[#8B95AB]">{f.detail}</p>
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] ${
                        f.status === "good"
                          ? "bg-[#0f766e]/20 text-[#8FFAE0]"
                          : f.status === "warning"
                          ? "bg-[#F59E0B]/20 text-[#FCD34D]"
                          : "bg-[#EF4444]/20 text-[#FCA5A5]"
                      }`}
                    >
                      {f.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {result.risk_breakdown && Object.keys(result.risk_breakdown).length > 0 && (
              <div className="mt-6 border-t border-white/10 pt-5">
                <p className="mb-3 text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">Risk Component Breakdown</p>
                <div className="space-y-3">
                  {Object.entries(result.risk_breakdown).map(([component, score]) => (
                    <div key={component} className="flex items-center gap-3">
                      <span className="w-32 text-xs capitalize text-[#8B95AB]">{component.replace("_", " ")}</span>
                      <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/5">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${score}%`,
                            backgroundColor: score >= 70 ? "#22D3B8" : score >= 40 ? "#F5A623" : "#EF4444",
                          }}
                        />
                      </div>
                      <span className="w-10 text-right font-mono text-xs text-[#E8ECF1]">{score}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.explanation && result.explanation.length > 0 && (
              <div className="mt-6 border-t border-white/10 pt-5">
                <p className="mb-3 text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">What Influenced the ML Score</p>
                <div className="space-y-2">
                  {result.explanation.map((item) => (
                    <div key={item.feature} className="flex items-center justify-between text-sm">
                      <span className="text-[#DCEAFB]">{item.feature}</span>
                      <span className={`font-mono text-xs ${item.direction === "increases_risk" ? "text-[#FCA5A5]" : "text-[#8FFAE0]"}`}>
                        {item.contribution > 0 ? "+" : ""}{item.contribution} ({item.direction === "increases_risk" ? "↑ risk" : "↓ risk"})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.recommendations && result.recommendations.length > 0 && (
              <div className="mt-6 border-t border-white/10 pt-5">
                <p className="mb-3 text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">Recommended Actions</p>
                <ul className="space-y-2">
                  {result.recommendations.map((rec, i) => (
                    <li key={i} className="flex gap-2 text-sm text-[#DCEAFB]">
                      <span className="shrink-0 text-[#8FFAE0]">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {mode === "url" && (
              <div className="mt-6 border-t border-white/10 pt-4">
                {user ? (
                  <button
                    onClick={() => setShowReportForm(!showReportForm)}
                    className="text-sm font-semibold text-[#F87171] transition hover:text-[#FCA5A5]"
                  >
                    {showReportForm ? "Cancel" : "Report this as a scam"}
                  </button>
                ) : (
                  <p className="text-sm text-[#8B95AB]">Log in to report this domain</p>
                )}

                {showReportForm && (
                  <ReportForm
                    targetValue={result.input_value}
                    targetType="url"
                    onSuccess={() => setShowReportForm(false)}
                  />
                )}

                <div className="mt-4">
                  <CommunityReports targetValue={result.input_value} />
                </div>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}