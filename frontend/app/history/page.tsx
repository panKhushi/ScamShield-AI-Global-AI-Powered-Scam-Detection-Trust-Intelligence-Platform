"use client";
import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";

type HistoryItem = {
    id: number;
    input_value: string;
    input_type: string;
    domain: string;
    trust_score: number;
    verdict: string;
    created_at: string;
};

const typeLabels: Record<string, string> = {
    url: "URL Scan",
    job: "Job Scan",
    email: "Email Scan",
};

export default function History() {
    const [items, setItems] = useState<HistoryItem[]>([]);

    useEffect(() => {
        const supabase = createClient();

        supabase.auth.getSession().then(({ data }) => {
            const headers: HeadersInit = { "Content-Type": "application/json" };
            const token = data.session?.access_token;
            if (token) {
                headers.Authorization = `Bearer ${token}`;
            }

            fetch("http://localhost:8000/api/history", { headers })
                .then((res) => res.json())
                .then((data) => setItems(Array.isArray(data) ? data : []))
                .catch(() => setItems([]));
        });
    }, []);

    return (
        <main className="min-h-screen px-4 pb-16 pt-10">
            <div className="mx-auto max-w-4xl">
                <div className="mb-8 flex items-center justify-between gap-3">
                    <div>
                        <p className="text-[10px] uppercase tracking-[0.2em] text-[#8B95AB]">Overview</p>
                        <h1 className="font-display text-3xl font-bold text-white">Scan History</h1>
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-[#DCEAFB]">
                        {items.length} records
                    </span>
                </div>

                {items.length === 0 ? (
                    <div className="rounded-[28px] border border-white/10 bg-[#0D1728]/90 p-8 text-center text-[#8B95AB] shadow-[0_20px_60px_rgba(2,6,23,0.7)]">
                        No scan history yet.
                    </div>
                ) : (
                    <div className="space-y-3">
                        {items.map((item) => {
                            const typeLabel = typeLabels[item.input_type] ?? item.input_type ?? "Scan";
                            const displayValue = item.input_value || item.domain || "Unknown value";

                            return (
                                <div key={item.id} className="rounded-[24px] border border-white/10 bg-[#0D1728]/90 p-4 shadow-[0_18px_50px_rgba(2,6,23,0.55)] sm:p-5">
                                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                        <div className="min-w-0">
                                            <div className="mb-2 flex flex-wrap items-center gap-2">
                                                <span className="rounded-full border border-[#22D3B8]/30 bg-[#22D3B8]/10 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#8FFAE0]">
                                                    {typeLabel}
                                                </span>
                                                {item.domain && item.domain !== "N/A" && (
                                                    <span className="text-xs text-[#8B95AB]">{item.domain}</span>
                                                )}
                                            </div>
                                            <p className="break-all text-sm font-medium text-[#E8ECF1]">{displayValue}</p>
                                            <p className="mt-2 text-xs text-[#8B95AB]">{new Date(item.created_at).toLocaleString()}</p>
                                        </div>

                                        <div className="text-left sm:text-right">
                                            <p className="font-display text-2xl font-bold text-white">{item.trust_score}</p>
                                            <p className="text-[10px] uppercase tracking-[0.18em] text-[#8B95AB]">{item.verdict}</p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </main>
    );
}