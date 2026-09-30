"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { useAuth } from "./providers/AuthProvider";
import ReportForm from "./components/ReportForm";
import CommunityReports from "./components/CommunityReports";
import { BriefcaseBusiness, Globe2, Mail, MessageSquareText } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { AnimatedNumber, PageTransition, ScanLoader, revealGroup, revealItem } from "./components/Motion";

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

type InputMode = "url" | "job" | "email" | "sms";

const modeIcons: Record<InputMode, string> = {
  url: "M4 5h16v14H4z M8 9h8 M8 13h5",
  job: "M4 7h16v12H4z M8 7V5h8v2 M8 12h8 M8 16h5",
  email: "M4 6h16v12H4z M4 7l8 6 8-6",
  sms: "M5 5h14v10H9l-4 4z M8 9h8 M8 12h5",
};

export const scanTypeIcons = {
  url: Globe2,
  job: BriefcaseBusiness,
  email: Mail,
  sms: MessageSquareText,
};

function ModeIcon({ mode }: { mode: InputMode }) {
  return (
    <svg aria-hidden="true" className="h-4 w-4" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      {modeIcons[mode].split(" M").map((path, index) => (
        <path key={index} d={`${index > 0 ? "M" : ""}${path}`} />
      ))}
    </svg>
  );
}

function scoreTone(score: number) {
  if (score >= 70) return { text: "text-[#67E8C5]", ring: "#22D3B8", label: "Trusted" };
  if (score >= 40) return { text: "text-[#FCD34D]", ring: "#FBBF24", label: "Needs caution" };
  return { text: "text-[#FCA5A5]", ring: "#F87171", label: "High risk" };
}

const modeConfig = {
  url: { label: "Website", shortLabel: "URL", placeholder: "Enter a URL, e.g. example.com", endpoint: "/api/analyze" },
  job: { label: "Job offer", shortLabel: "Job", placeholder: "Paste the job offer text here...", endpoint: "/api/analyze-job" },
  email: { label: "Email", shortLabel: "Email", placeholder: "Paste the email content here...", endpoint: "/api/analyze-email" },
  sms: { label: "SMS", shortLabel: "SMS", placeholder: "Paste the SMS message here...", endpoint: "/api/analyze-sms" },
};

export default function Home() {
  const router = useRouter();
  const [mode, setMode] = useState<InputMode>("url");
  const [input, setInput] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);
  const { user, loading: authLoading } = useAuth();
  const tone = result ? scoreTone(result.trust_score) : null;
  const ResultIcon = scanTypeIcons[mode];

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login?next=/");
    }
  }, [authLoading, router, user]);

  if (authLoading || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center px-4 text-sm text-[#9CA9C0]">
        Checking your secure session...
      </main>
    );
  }

  async function handleAnalyze() {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    setShowReportForm(false);
    try {
      const supabase = createClient();
      const { data: sessionData } = await supabase.auth.getSession();
      const token = sessionData.session?.access_token;

      const res = await fetch(`/backend${modeConfig[mode].endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ input_type: mode, value: input }),
      });
      if (!res.ok) {
        const errorBody = await res.text();
        throw new Error(`Analysis request failed (${res.status}): ${errorBody || res.statusText}`);
      }
      const data: AnalyzeResponse = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageTransition>
    <main className="min-h-screen px-4 pb-16 pt-8 text-[#E8ECF1] sm:pt-12">
      <div className="relative mx-auto w-full max-w-6xl">
        <div className="ambient-glow absolute -top-10 left-1/2 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-[#22D3B8]/15 blur-3xl" />

        <section className="surface reveal-up p-5 sm:p-8">
          <div className="reveal-up reveal-delay-1 mb-7 max-w-3xl">
            <span className="mb-4 inline-flex items-center gap-2 rounded-full border border-[#22D3B8]/30 bg-[#22D3B8]/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-[#8FFAE0]">
              ScamShield AI
            </span>
            <h1 className="font-display max-w-2xl text-3xl font-bold leading-tight tracking-tight text-white sm:text-5xl">
              Make the next message easier to trust.
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-[#9CA9C0] sm:text-base">
              Scan a website, job offer, email, or SMS before you click, reply, or share personal details.
            </p>
          </div>

          <div className="reveal-up reveal-delay-2 segmented-control mx-auto mb-6 max-w-2xl" role="tablist" aria-label="Analysis type">
              {(Object.keys(modeConfig) as InputMode[]).map((m) => (
                <motion.button
                  key={m}
                  role="tab"
                  aria-selected={mode === m}
                  onClick={() => {
                    setMode(m);
                    setResult(null);
                    setInput("");
                  }}
                  whileHover={{ scale: 1.015 }}
                  whileTap={{ scale: 0.98 }}
                  className={`relative flex min-w-0 items-center justify-center gap-2 rounded-[14px] px-3 py-3 text-sm font-semibold transition-colors ${mode === m ? "text-[#06201B]" : "text-[#8B95AB] hover:text-white"}`}
                >
                  {mode === m && <motion.span layoutId="active-mode" className="absolute inset-0 -z-0 rounded-[14px] bg-[#D9FFF5] shadow-[0_8px_20px_rgba(34,211,184,0.18)] transition-shadow" transition={{ type: "spring", stiffness: 500, damping: 36 }} />}
                  <span className="relative z-10 flex items-center gap-2">
                  <ModeIcon mode={m} />
                  <span className="hidden sm:inline">{modeConfig[m].label}</span>
                  <span className="sm:hidden">{modeConfig[m].shortLabel}</span>
                  </span>
                </motion.button>
              ))}
          </div>

          <div className="reveal-up reveal-delay-3 mx-auto w-full max-w-2xl">
            {mode === "url" ? (
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={modeConfig[mode].placeholder}
                  className="field min-h-14 flex-1 px-4 py-3.5 text-sm placeholder:text-[#7E8BA4]"
                />
                <motion.button
                  onClick={handleAnalyze}
                  disabled={loading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="scan-button min-h-14 rounded-[16px] bg-[#D9FFF5] px-6 py-3.5 text-sm font-bold text-[#06201B] shadow-lg shadow-[#22D3B8]/20 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? <ScanLoader /> : "Analyze"}
                </motion.button>
              </div>
            ) : (
              <>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={modeConfig[mode].placeholder}
                  rows={6}
                  className="field w-full resize-none px-4 py-3.5 text-sm placeholder:text-[#7E8BA4]"
                />
                <div className="mt-3 flex justify-end">
                  <motion.button
                    onClick={handleAnalyze}
                    disabled={loading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="scan-button min-h-12 rounded-[16px] bg-[#D9FFF5] px-6 py-3 text-sm font-bold text-[#06201B] shadow-lg shadow-[#22D3B8]/20 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loading ? <ScanLoader /> : "Analyze"}
                  </motion.button>
                </div>
              </>
            )}
          </div>
        </section>

        <AnimatePresence mode="wait">
        {result && (
          <motion.section key={`${mode}-${result.input_value}`} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.28 }} className="surface mx-auto mt-6 w-full max-w-4xl p-5 sm:mt-8 sm:p-7">
            <div className="mb-6 flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <div className="mb-3 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]"><span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#22D3B8]/10 text-[#67E8C5]"><ResultIcon className="h-4 w-4" /></span>{modeConfig[mode].label}</div>
                <span className="block max-w-[560px] break-words font-mono text-sm text-[#DCEAFB]">{result.input_value}</span>
              </div>

              <span className={`w-fit rounded-full border px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.18em] ${tone?.text} ${result.verdict === "safe" ? "border-[#22D3B8]/30 bg-[#22D3B8]/10" : result.verdict === "suspicious" ? "border-[#FBBF24]/30 bg-[#FBBF24]/10" : "border-[#F87171]/30 bg-[#F87171]/10"}`}>
                {tone?.label}
              </span>
            </div>

            <div className="grid items-center gap-7 border-b border-white/10 pb-7 md:grid-cols-[220px_1fr]">
              <div className="flex flex-col items-center justify-center">
                <div className="relative h-44 w-44">
                  <svg className="h-44 w-44 -rotate-90" viewBox="0 0 128 128">
                    <circle cx="64" cy="64" r="52" stroke="#1B2A3D" strokeWidth="10" fill="none" />
                    <circle
                      cx="64"
                      cy="64"
                      r="52"
                      stroke={tone?.ring}
                      strokeWidth="10"
                      fill="none"
                      strokeDasharray={`${(result.trust_score / 100) * 326.7} 326.7`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`font-display text-5xl font-bold ${tone?.text}`}><AnimatedNumber value={result.trust_score} /></span>
                    <span className="mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]">trust / 100</span>
                  </div>
                </div>
                <p className="mt-3 text-center text-sm text-[#9CA9C0]">{result.verdict} assessment</p>
              </div>

              <div>
                <div className="mb-4 flex items-end justify-between gap-3">
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]">Risk breakdown</p>
                    <p className="mt-1 text-sm text-[#DCEAFB]">How the score was assembled</p>
                  </div>
                  <span className="font-mono text-xs text-[#8B95AB]">{result.ml_scam_probability}% ML risk</span>
                </div>
                <motion.div variants={revealGroup} initial="hidden" animate="visible" className="space-y-4">
                  {Object.entries(result.risk_breakdown).map(([component, score]) => (
                    <motion.div key={component} variants={revealItem}>
                      <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
                        <span className="capitalize text-[#9CA9C0]">{component.replace("_", " ")}</span>
                        <span className="font-mono text-[#E8ECF1]">{score}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-[#17263A]">
                        <motion.div initial={{ width: 0 }} animate={{ width: `${score}%` }} transition={{ duration: 0.35, ease: "easeOut" }} className="h-full rounded-full bg-gradient-to-r from-[#22D3B8] to-[#60A5FA]" />
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              </div>
            </div>

            {result.recommendations && result.recommendations.length > 0 && (
              <details open className="mt-6 border-b border-white/10 pb-5">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold text-white">
                  Recommended actions
                  <span className="text-xs font-normal text-[#8B95AB]">{result.recommendations.length} actions</span>
                </summary>
                <motion.ul variants={revealGroup} initial="hidden" animate="visible" className="mt-4 space-y-3">
                  {result.recommendations.map((rec, i) => (
                    <motion.li variants={revealItem} key={i} className="flex gap-3 text-sm leading-6 text-[#DCEAFB]">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-[#22D3B8]" />
                      {rec}
                    </motion.li>
                  ))}
                </motion.ul>
              </details>
            )}

            <details className="border-b border-white/10 py-5">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold text-white">
                Evidence detected
                <span className="text-xs font-normal text-[#8B95AB]">{result.factors.length} checks</span>
              </summary>
              <motion.div variants={revealGroup} initial="hidden" animate="visible" className="mt-4 grid gap-3 sm:grid-cols-2">
                {result.factors.map((f) => (
                  <motion.div variants={revealItem} key={f.name} className="surface-soft p-3.5">
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-sm font-semibold text-white">{f.name}</p>
                      <span className={`rounded-full px-2 py-1 text-[9px] font-bold uppercase tracking-[0.14em] ${f.status === "good" ? "bg-[#22D3B8]/10 text-[#8FFAE0]" : f.status === "warning" ? "bg-[#FBBF24]/10 text-[#FCD34D]" : "bg-[#F87171]/10 text-[#FCA5A5]"}`}>
                        {f.status}
                      </span>
                    </div>
                    <p className="mt-2 text-xs leading-5 text-[#8B95AB]">{f.detail}</p>
                  </motion.div>
                ))}
              </motion.div>
            </details>

            {result.explanation && result.explanation.length > 0 && (
              <details className="py-5">
                <summary className="cursor-pointer list-none text-sm font-semibold text-white">What influenced the ML score</summary>
                <div className="mt-4 space-y-2">
                  {result.explanation.map((item) => (
                    <div key={item.feature} className="flex items-center justify-between gap-4 text-sm">
                      <span className="text-[#DCEAFB]">{item.feature}</span>
                      <span className={`font-mono text-xs ${item.direction === "increases_risk" ? "text-[#FCA5A5]" : "text-[#8FFAE0]"}`}>
                        {item.contribution > 0 ? "+" : ""}{item.contribution} ({item.direction === "increases_risk" ? "up risk" : "down risk"})
                      </span>
                    </div>
                  ))}
                </div>
              </details>
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
          </motion.section>
        )}
        </AnimatePresence>
      </div>
    </main>
    </PageTransition>
  );
}