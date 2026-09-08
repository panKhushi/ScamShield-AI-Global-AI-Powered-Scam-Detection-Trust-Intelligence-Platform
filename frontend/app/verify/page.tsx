"use client";

import { useState } from "react";

type ScoreFactor = {
    name: string;
    weight: number;
    status: "good" | "warning" | "bad";
    detail: string;
};

type VerifyResponse = {
    input_value: string;
    trust_score: number;
    verdict: "safe" | "suspicious" | "dangerous";
    factors: ScoreFactor[];
    recommendations: string[];
};

type VerifyMode = "company" | "recruiter";

export default function VerifyPage() {
    const [mode, setMode] = useState<VerifyMode>("company");
    const [companyName, setCompanyName] = useState("");
    const [website, setWebsite] = useState("");
    const [recruiterEmail, setRecruiterEmail] = useState("");
    const [claimedCompany, setClaimedCompany] = useState("");
    const [result, setResult] = useState<VerifyResponse | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleVerify() {
        setLoading(true);
        setResult(null);
        try {
            const endpoint = mode === "company" ? "/api/verify-company" : "/api/verify-recruiter";
            const body =
                mode === "company"
                    ? { company_name: companyName, website }
                    : { recruiter_email: recruiterEmail, claimed_company: claimedCompany };

            const res = await fetch(`http://localhost:8000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data: VerifyResponse = await res.json();
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
                            Verification
                        </span>
                        <h1 className="font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
                            Confirm who you&apos;re really dealing with.
                        </h1>
                        <p className="mt-3 max-w-2xl text-sm text-[#8B95AB] sm:text-base">
                            Check whether a claimed company or recruiter is legitimate before you share anything.
                        </p>
                    </div>

                    <div className="reveal-up reveal-delay-2 mx-auto mb-6 max-w-md rounded-2xl border border-white/10 bg-[#0B1324]/80 p-2 shadow-inner shadow-black/20">
                        <div className="flex gap-2">
                            {(["company", "recruiter"] as VerifyMode[]).map((m) => (
                                <button
                                    key={m}
                                    onClick={() => {
                                        setMode(m);
                                        setResult(null);
                                    }}
                                    className={`flex-1 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${mode === m
                                            ? "bg-gradient-to-r from-[#22D3B8] to-[#34D399] text-[#06131A] shadow-lg shadow-[#22D3B8]/30"
                                            : "bg-transparent text-[#8B95AB] hover:bg-white/5 hover:text-white"
                                        }`}
                                >
                                    {m === "company" ? "Company" : "Recruiter"}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="reveal-up reveal-delay-3 mx-auto flex w-full max-w-md flex-col gap-3">
                        {mode === "company" ? (
                            <>
                                <input
                                    value={companyName}
                                    onChange={(e) => setCompanyName(e.target.value)}
                                    placeholder="Company name (e.g. Google)"
                                    className="rounded-2xl border border-white/10 bg-[#0F1C2F] px-4 py-3.5 text-sm text-white placeholder:text-[#7E8BA4] outline-none transition focus:border-[#22D3B8]/60 focus:bg-[#122238]"
                                />
                                <input
                                    value={website}
                                    onChange={(e) => setWebsite(e.target.value)}
                                    placeholder="Claimed website (e.g. google.com)"
                                    className="rounded-2xl border border-white/10 bg-[#0F1C2F] px-4 py-3.5 text-sm text-white placeholder:text-[#7E8BA4] outline-none transition focus:border-[#22D3B8]/60 focus:bg-[#122238]"
                                />
                            </>
                        ) : (
                            <>
                                <input
                                    value={recruiterEmail}
                                    onChange={(e) => setRecruiterEmail(e.target.value)}
                                    placeholder="Recruiter's email address"
                                    className="rounded-2xl border border-white/10 bg-[#0F1C2F] px-4 py-3.5 text-sm text-white placeholder:text-[#7E8BA4] outline-none transition focus:border-[#22D3B8]/60 focus:bg-[#122238]"
                                />
                                <input
                                    value={claimedCompany}
                                    onChange={(e) => setClaimedCompany(e.target.value)}
                                    placeholder="Company they claim to represent"
                                    className="rounded-2xl border border-white/10 bg-[#0F1C2F] px-4 py-3.5 text-sm text-white placeholder:text-[#7E8BA4] outline-none transition focus:border-[#22D3B8]/60 focus:bg-[#122238]"
                                />
                            </>
                        )}

                        <button
                            onClick={handleVerify}
                            disabled={loading}
                            className="scan-button rounded-2xl bg-gradient-to-r from-[#22D3B8] to-[#1DB7A7] px-6 py-3.5 text-sm font-bold text-[#07131C] shadow-lg shadow-[#22D3B8]/20 transition hover:scale-[1.03] hover:shadow-[#22D3B8]/35 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {loading ? "Verifying..." : "Verify"}
                        </button>
                    </div>
                </section>

                {result && (
                    <section className="reveal-up interactive-panel mx-auto mt-8 w-full max-w-md rounded-[28px] border border-white/10 bg-[#0D1728]/90 p-5 shadow-[0_20px_60px_rgba(2,6,23,0.7)] backdrop-blur-xl sm:p-6">
                        <div className="mb-6 flex items-start justify-between gap-4">
                            <div className="min-w-0">
                                <p className="mb-2 text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">Checked</p>
                                <span className="block max-w-[280px] truncate font-mono text-sm text-[#DCEAFB]">{result.input_value}</span>
                            </div>

                            <span className={`rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] ${result.verdict === "safe"
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
                                <div key={f.name} className="rounded-2xl border border-white/8 bg-[#0F1C2F]/80 p-3.5">
                                    <div className="flex items-center justify-between gap-3">
                                        <div className="min-w-0">
                                            <p className="text-sm font-semibold text-white">{f.name}</p>
                                            <p className="mt-1 text-xs leading-5 text-[#8B95AB]">{f.detail}</p>
                                        </div>
                                        <span
                                            className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] ${f.status === "good"
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
                    </section>
                )}
            </div>
        </main>
    );
}