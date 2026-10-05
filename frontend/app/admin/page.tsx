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
  review_status: string | null;
  moderator_note?: string | null;
  created_at: string;
};

export default function AdminPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadReports() {
    setError("");
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
      setError(response.status === 403 ? "Administrator access is required." : "Could not load reports.");
      setLoading(false);
      return;
    }
    setReports(await response.json());
    setLoading(false);
  }

  async function review(id: number, reviewStatus: "approved" | "rejected") {
    const { data } = await createClient().auth.getSession();
    const token = data.session?.access_token;
    const response = await fetch(`/backend/api/admin/reports/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token ?? ""}` },
      body: JSON.stringify({ review_status: reviewStatus }),
    });
    if (response.ok) setReports((current) => current.filter((report) => report.id !== id));
    else setError("Could not update this report.");
  }

  useEffect(() => {
    void loadReports();
  }, []);

  return (
    <PageTransition>
      <main className="min-h-screen px-4 pb-16 pt-8 sm:pt-10">
        <div className="mx-auto max-w-5xl">
          <header className="mb-8">
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]">Moderation</p>
            <h1 className="font-display mt-2 text-3xl font-bold text-white">Community reports</h1>
            <p className="mt-2 text-sm text-[#9CA9C0]">Review reports before they influence public community intelligence.</p>
          </header>
          {error && <p role="alert" className="mb-4 rounded-xl border border-[#F87171]/20 bg-[#F87171]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}
          {loading ? <p className="text-sm text-[#9CA9C0]">Loading reports...</p> : reports.length === 0 ? <p className="text-sm text-[#9CA9C0]">No pending reports.</p> : (
            <div className="space-y-3">
              {reports.map((report) => (
                <article key={report.id} className="surface p-5">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <p className="text-xs uppercase tracking-[0.12em] text-[#8B95AB]">{report.target_type} · {report.category}</p>
                      <p className="mt-2 break-words font-mono text-sm text-white">{report.target_value}</p>
                      <p className="mt-3 text-sm leading-6 text-[#C4CCDA]">{report.description}</p>
                      {report.evidence_url && <img src={report.evidence_url} alt="Submitted evidence" className="mt-3 max-h-48 rounded-lg" />}
                    </div>
                    <div className="flex shrink-0 gap-2">
                      <button onClick={() => void review(report.id, "approved")} className="rounded-lg bg-[#D9FFF5] px-3 py-2 text-xs font-bold text-[#06201B]">Approve</button>
                      <button onClick={() => void review(report.id, "rejected")} className="rounded-lg border border-[#F87171]/30 px-3 py-2 text-xs font-bold text-[#FCA5A5]">Reject</button>
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
