"use client";

import { useEffect, useMemo, useState } from "react";
import { BriefcaseBusiness, ChevronDown, Globe2, Mail, MessageSquareText, Search, ShieldAlert, ShieldCheck, ShieldQuestion, Sparkles } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { createClient } from "@/lib/supabase";
import { PageTransition, revealGroup, revealItem } from "../components/Motion";

type Factor = { name: string; status: string; detail: string };
type HistoryItem = { id: number; input_value: string; input_type: string; domain: string; trust_score: number; verdict: string; factors: Factor[]; created_at: string };
type FilterType = "all" | "url" | "job" | "email" | "sms";
type RiskFilter = "all" | "safe" | "suspicious" | "dangerous";

const typeLabels: Record<string, string> = { url: "URL", job: "Job", email: "Email", sms: "SMS" };
const typeIcons = { url: Globe2, job: BriefcaseBusiness, email: Mail, sms: MessageSquareText };

function getScoreTone(score: number) {
    if (score >= 70) return "text-[#67E8C5]";
    if (score >= 40) return "text-[#FCD34D]";
    return "text-[#FCA5A5]";
}

function getVerdictIcon(verdict: string) {
    if (verdict === "safe") return ShieldCheck;
    if (verdict === "dangerous") return ShieldAlert;
    return ShieldQuestion;
}

function EmptyHistory() {
    return (
        <div className="surface flex flex-col items-center px-6 py-14 text-center">
            <div className="relative mb-6 flex h-24 w-24 items-center justify-center rounded-[28px] border border-[#22D3B8]/20 bg-[#22D3B8]/10">
                <svg aria-hidden="true" className="h-14 w-14 text-[#67E8C5]" viewBox="0 0 64 64" fill="none">
                    <path d="M14 18h36v30H14z" stroke="currentColor" strokeWidth="2.5" />
                    <path d="M20 26h24M20 33h17M20 40h10" stroke="currentColor" strokeLinecap="round" strokeWidth="2.5" />
                    <path d="m44 12 2.5 5L52 19l-5.5 2-2.5 5-2-5-5-2 5-2z" fill="currentColor" />
                </svg>
            </div>
            <h2 className="font-display text-xl font-bold text-white">Your scan story starts here</h2>
            <p className="mt-2 max-w-sm text-sm leading-6 text-[#9CA9C0]">Analyze a website, job offer, email, or SMS to see trust scores and evidence appear in this dashboard.</p>
        </div>
    );
}

export default function History() {
    const [items, setItems] = useState<HistoryItem[]>([]);
    const [query, setQuery] = useState("");
    const [typeFilter, setTypeFilter] = useState<FilterType>("all");
    const [riskFilter, setRiskFilter] = useState<RiskFilter>("all");
    const [expandedId, setExpandedId] = useState<number | null>(null);

    useEffect(() => {
        const supabase = createClient();
        supabase.auth.getSession().then(({ data }) => {
            const headers: HeadersInit = { "Content-Type": "application/json" };
            const token = data.session?.access_token;
            if (token) headers.Authorization = `Bearer ${token}`;
            fetch("http://localhost:8000/api/history?limit=100", { headers })
                .then((res) => res.json())
                .then((data) => setItems(Array.isArray(data) ? data : []))
                .catch(() => setItems([]));
        });
    }, []);

    const filteredItems = useMemo(() => {
        const normalizedQuery = query.trim().toLowerCase();
        return items.filter((item) => {
            const matchesType = typeFilter === "all" || item.input_type === typeFilter;
            const matchesRisk = riskFilter === "all" || item.verdict === riskFilter;
            const value = `${item.input_value} ${item.domain} ${item.input_type}`.toLowerCase();
            return matchesType && matchesRisk && (!normalizedQuery || value.includes(normalizedQuery));
        });
    }, [items, query, riskFilter, typeFilter]);

    const stats = useMemo(() => {
        const weekStart = Date.now() - 7 * 24 * 60 * 60 * 1000;
        return {
            scams: items.filter((item) => item.verdict === "dangerous").length,
            average: items.length ? Math.round(items.reduce((total, item) => total + item.trust_score, 0) / items.length) : 0,
            thisWeek: items.filter((item) => new Date(item.created_at).getTime() >= weekStart).length,
        };
    }, [items]);

    const trend = items.slice(0, 10).reverse();
    const maxTrendScore = Math.max(...trend.map((item) => item.trust_score), 100);

    return (
        <PageTransition>
        <main className="min-h-screen px-4 pb-16 pt-8 sm:pt-10">
            <div className="mx-auto max-w-6xl">
                <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                    <div><p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]">Signal center</p><h1 className="font-display mt-2 text-3xl font-bold text-white sm:text-4xl">Scan history</h1><p className="mt-2 max-w-xl text-sm leading-6 text-[#9CA9C0]">A clear view of what you checked, what looked risky, and how your trust signals are trending.</p></div>
                    <span className="surface-soft w-fit px-3 py-2 text-xs text-[#DCEAFB]">{items.length} total scans</span>
                </header>

                {items.length === 0 ? <EmptyHistory /> : (
                    <>
                        <motion.section variants={revealGroup} initial="hidden" animate="visible" className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                            {[["Total scans", items.length, "All checks", Sparkles], ["Scams detected", stats.scams, "Dangerous verdicts", ShieldAlert], ["Average trust", stats.average, "Across all scans", ShieldCheck], ["This week", stats.thisWeek, "Last 7 days", Globe2]].map(([label, value, detail, Icon]) => { const CardIcon = Icon as typeof Sparkles; return <div key={label as string} className="surface p-4 sm:p-5"><div className="mb-5 flex items-center justify-between"><p className="text-xs font-medium text-[#9CA9C0]">{label as string}</p><CardIcon className="h-4 w-4 text-[#67E8C5]" /></div><p className="font-display text-3xl font-bold text-white">{value as number}</p><p className="mt-1 text-xs text-[#718098]">{detail as string}</p></div>; })}
                        </motion.section>

                        <section className="surface mb-6 p-5 sm:p-6">
                            <div className="mb-5 flex items-end justify-between"><div><p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]">Recent trend</p><h2 className="mt-1 font-display text-lg font-bold text-white">Trust score over time</h2></div><span className="text-xs text-[#718098]">Last {trend.length} scans</span></div>
                            {trend.length > 0 && <div className="flex h-40 items-end gap-2 sm:gap-4">{trend.map((item) => <div key={item.id} className="group flex min-w-0 flex-1 flex-col items-center gap-2"><div className="relative flex h-32 w-full items-end"><div className="w-full rounded-t-lg bg-gradient-to-t from-[#22D3B8]/30 to-[#67E8C5] transition-all group-hover:from-[#22D3B8]/50" style={{ height: `${Math.max((item.trust_score / maxTrendScore) * 100, 8)}%` }} title={`${item.trust_score} trust`} /></div><span className="max-w-full truncate text-[10px] text-[#718098]">{typeLabels[item.input_type] ?? "Scan"}</span></div>)}</div>}
                        </section>

                        <section className="surface overflow-hidden">
                            <div className="border-b border-white/10 p-4 sm:p-5"><div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"><div className="relative flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#718098]" /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search scans..." className="field w-full py-2.5 pl-10 pr-3 text-sm placeholder:text-[#718098]" /></div><div className="grid grid-cols-2 gap-2 sm:flex"><select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value as FilterType)} className="field px-3 py-2 text-xs"><option value="all">All types</option><option value="url">URL</option><option value="job">Job</option><option value="email">Email</option><option value="sms">SMS</option></select><select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value as RiskFilter)} className="field px-3 py-2 text-xs"><option value="all">All risk</option><option value="safe">Safe</option><option value="suspicious">Suspicious</option><option value="dangerous">Dangerous</option></select></div></div><p className="mt-3 text-xs text-[#718098]">Showing {filteredItems.length} of {items.length} scans</p></div>
                            <div className="divide-y divide-white/10">
                                {filteredItems.length === 0 ? <p className="p-8 text-center text-sm text-[#9CA9C0]">No scans match these filters.</p> : <AnimatePresence initial={false} mode="popLayout">{filteredItems.map((item) => { const TypeIcon = typeIcons[item.input_type as keyof typeof typeIcons] ?? Sparkles; const VerdictIcon = getVerdictIcon(item.verdict); const expanded = expandedId === item.id; return <motion.div layout initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2 }} key={item.id}><motion.button whileTap={{ scale: 0.995 }} onClick={() => setExpandedId(expanded ? null : item.id)} className="grid w-full gap-3 px-4 py-4 text-left transition hover:bg-white/[0.03] sm:grid-cols-[minmax(0,1fr)_120px_28px] sm:items-center sm:px-5" aria-expanded={expanded}><span className="flex min-w-0 items-center gap-3"><span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#22D3B8]/10 text-[#67E8C5]"><TypeIcon className="h-4 w-4" /></span><span className="min-w-0"><span className="block truncate text-sm font-semibold text-white">{item.input_value || item.domain || "Unknown value"}</span><span className="mt-1 block text-xs text-[#718098]">{typeLabels[item.input_type] ?? "Scan"} · {new Date(item.created_at).toLocaleString()}</span></span></span><span className="flex items-center gap-2 sm:justify-end"><VerdictIcon className={`h-4 w-4 ${getScoreTone(item.trust_score)}`} /><span><span className={`block font-display text-lg font-bold ${getScoreTone(item.trust_score)}`}>{item.trust_score}</span><span className="block text-[10px] uppercase tracking-[0.15em] text-[#718098]">{item.verdict}</span></span></span><ChevronDown className={`h-4 w-4 text-[#718098] transition-transform ${expanded ? "rotate-180" : ""}`} /></motion.button>{expanded && <div className="bg-[#08111F]/60 px-4 pb-5 sm:px-5"><div className="grid gap-3 border-t border-white/10 pt-4 sm:grid-cols-2">{(item.factors || []).map((factor) => <div key={factor.name} className="surface-soft p-3"><div className="flex items-center justify-between gap-2"><span className="text-xs font-semibold text-white">{factor.name}</span><span className="text-[10px] uppercase tracking-[0.12em] text-[#8B95AB]">{factor.status}</span></div><p className="mt-1 text-xs leading-5 text-[#8B95AB]">{factor.detail}</p></div>)}</div></div>}</motion.div>; })}</AnimatePresence>}
                            </div>
                        </section>
                    </>
                )}
            </div>
        </main>
        </PageTransition>
    );
}
