"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { PageTransition } from "../components/Motion";

type Report = {
  id: number;
  target_value: string;
  target_type: string;
  category: string;
  description: string;
  evidence_url?: string | null;
  created_at: string;
};

export default function AdminPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadReports() {
    const { data } = await createClient().auth.getSession();
    const token = data.session?.access_token;
    if (!token) {
      setError("Administrator sign-in is required.");
      setLoading(false);
      return;
    }
    const response = await fetch("/backend/api/admin/reports?status=pending", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      setError(response.status === 403 ? "Administrator access is required. Configure your email or user ID in backend/.env." : "Could not load reports.");
      setLoading(false);
      return;
    }
    setReports(await response.json());
    setLoading(false);
  }

  async function review(id: number, reviewStatus: "approved" | "rejected") {
    const { data } = await createClient().auth.getSession();
    const token = data.session?.access_token;
    if (!token) {
      setError("Administrator sign-in is required.");
      return;
    }
    const response = await fetch(`/backend/api/admin/reports/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ review_status: reviewStatus }),
    });
    if (response.ok) setReports((current) => current.filter((report) => report.id !== id));
    else setError("Could not update this report.");
  }

  useEffect(() => {
    void Promise.resolve().then(() => loadReports());
  }, []);

  return (
    <PageTransition>
      <main className="min-h-screen px-4 pb-16 pt-8 sm:pt-10">
        <div className="mx-auto max-w-5xl">
          <header className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="eyebrow flex items-center gap-2"><span className="status-dot" /> Moderation workspace</p>
              <h1 className="font-display mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">Community reports</h1>
              <p className="mt-2 max-w-xl text-sm leading-6 text-[#9CA9C0]">Review reports before they influence public community intelligence.</p>
            </div>
            <div className="surface-soft flex items-center gap-3 px-4 py-3">
              <span className="text-2xl font-bold text-white">{reports.length}</span>
              <span className="max-w-20 text-[10px] font-semibold uppercase leading-4 tracking-[0.14em] text-[#8B95AB]">Awaiting review</span>
            </div>
          </header>
          {error && <p role="alert" className="mb-5 rounded-2xl border border-[#F87171]/20 bg-[#F87171]/10 px-4 py-3 text-sm leading-6 text-[#FCA5A5]">{error}</p>}
          {loading ? (
            <div className="space-y-3" aria-label="Loading reports">
              {[1, 2].map((item) => <div key={item} className="surface h-40 animate-pulse bg-white/[0.03]" />)}
            </div>
          ) : reports.length === 0 ? (
            <div className="surface flex flex-col items-center px-6 py-16 text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#22D3B8]/10 text-2xl text-[#22D3B8]">✓</div>
              <h2 className="font-display text-lg font-bold text-white">Queue is clear</h2>
              <p className="mt-2 max-w-sm text-sm leading-6 text-[#9CA9C0]">There are no pending community reports to review right now.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <article key={report.id} className="surface interactive-panel p-5 sm:p-6">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <p className="eyebrow">{report.target_type} · {report.category}</p>
                      <p className="mt-2 break-words font-mono text-sm text-white">{report.target_value}</p>
                      <p className="mt-3 text-sm leading-6 text-[#C4CCDA]">{report.description}</p>
                      <p className="mt-4 text-xs text-[#71809A]">{new Date(report.created_at).toLocaleString()}</p>
                      {report.evidence_url && <img src={report.evidence_url} alt="Submitted evidence" className="mt-4 max-h-48 rounded-xl border border-white/10 object-contain" />}
                    </div>
                    <div className="flex shrink-0 gap-2 sm:flex-col">
                      <button onClick={() => void review(report.id, "approved")} className="rounded-xl bg-[#D9FFF5] px-4 py-2.5 text-xs font-bold text-[#06201B] transition hover:bg-white">Approve</button>
                      <button onClick={() => void review(report.id, "rejected")} className="rounded-xl border border-[#F87171]/30 px-4 py-2.5 text-xs font-bold text-[#FCA5A5] transition hover:bg-[#F87171]/10">Reject</button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </main>
    </PageTransition>
  );
}
