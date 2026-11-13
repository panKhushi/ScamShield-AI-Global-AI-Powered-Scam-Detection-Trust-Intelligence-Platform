"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";

export default function AdminLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    const { error: signInError } = await createClient().auth.signInWithPassword({ email, password });

    if (signInError) {
      setError(signInError.message);
      setLoading(false);
      return;
    }

    router.replace("/admin");
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-12">
      <div className="ambient-glow absolute left-1/2 top-1/2 -z-10 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#22D3B8]/10 blur-3xl" />
      <div className="surface w-full max-w-md p-6 sm:p-8">
        <div className="mb-6 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-[#22D3B8]/30 bg-[#22D3B8]/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.2em] text-[#8FFAE0]">
            Administrator access
          </span>
          <h1 className="mt-4 font-display text-3xl font-bold text-white">Admin sign in</h1>
          <p className="mt-2 text-sm leading-6 text-[#8B95AB]">Sign in with your approved administrator account.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p role="alert" className="rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

          <div>
            <label htmlFor="admin-email" className="mb-2 block text-xs font-medium uppercase tracking-[0.15em] text-[#8B95AB]">Admin email</label>
            <input id="admin-email" type="email" placeholder="admin@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required className="field w-full px-4 py-3 text-sm placeholder:text-[#7E8BA4]" />
          </div>

          <div>
            <label htmlFor="admin-password" className="mb-2 block text-xs font-medium uppercase tracking-[0.15em] text-[#8B95AB]">Password</label>
            <input id="admin-password" type="password" placeholder="Your password" value={password} onChange={(event) => setPassword(event.target.value)} required className="field w-full px-4 py-3 text-sm placeholder:text-[#7E8BA4]" />
          </div>

          <button type="submit" disabled={loading} className="w-full rounded-[16px] bg-[#D9FFF5] px-4 py-3 text-sm font-bold text-[#06201B] shadow-lg shadow-[#22D3B8]/20 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60">
            {loading ? "Signing in..." : "Sign in to admin portal"}
          </button>
        </form>

        <a href="/login" className="mt-6 block text-center text-sm font-semibold text-[#8FFAE0] transition hover:text-[#B8FFF1]">
          Back to regular sign in
        </a>
      </div>
    </main>
  );
}
