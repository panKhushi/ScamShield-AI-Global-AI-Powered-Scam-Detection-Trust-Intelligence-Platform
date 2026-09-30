"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isSignUp, setIsSignUp] = useState(false);
    const [nextPath, setNextPath] = useState("/");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();
    const supabase = createClient();

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const requestedPath = params.get("next");
        if (requestedPath?.startsWith("/")) setNextPath(requestedPath);
        if (params.get("mode") === "signup") setIsSignUp(true);
    }, []);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("");
        setLoading(true);

        const { error } = isSignUp
            ? await supabase.auth.signUp({ email, password })
            : await supabase.auth.signInWithPassword({ email, password });

        setLoading(false);

        if (error) {
            setError(error.message);
        } else {
            router.push(nextPath);
        }
    }

    return (
        <main className="flex min-h-screen items-center justify-center px-4 py-12">
            <div className="surface w-full max-w-md p-6 sm:p-8">
                <div className="mb-6 text-center">
                    <span className="inline-flex items-center gap-2 rounded-full border border-[#22D3B8]/30 bg-[#22D3B8]/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.2em] text-[#8FFAE0]">
                        Secure Access
                    </span>
                    <h1 className="mt-4 font-display text-3xl font-bold text-white">
                        {isSignUp ? "Create account" : "Welcome back"}
                    </h1>
                    <p className="mt-2 text-sm text-[#8B95AB]">
                        {isSignUp ? "Join ScamShield AI and save your scan history." : "Log in to access your saved scam checks."}
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && <p className="rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

                    <div>
                        <label className="mb-2 block text-xs font-medium uppercase tracking-[0.15em] text-[#8B95AB]">Email</label>
                        <input
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="field w-full px-4 py-3 text-sm placeholder:text-[#7E8BA4]"
                        />
                    </div>

                    <div>
                        <label className="mb-2 block text-xs font-medium uppercase tracking-[0.15em] text-[#8B95AB]">Password</label>
                        <input
                            type="password"
                            placeholder="Minimum 6 characters"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={6}
                            className="field w-full px-4 py-3 text-sm placeholder:text-[#7E8BA4]"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full rounded-[16px] bg-[#D9FFF5] px-4 py-3 text-sm font-bold text-[#06201B] shadow-lg shadow-[#22D3B8]/20 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {loading ? "Please wait..." : isSignUp ? "Create account" : "Log In"}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-[#8B95AB]">
                    {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
                    <button
                        type="button"
                        onClick={() => setIsSignUp(!isSignUp)}
                        className="font-semibold text-[#8FFAE0] transition hover:text-[#B8FFF1]"
                    >
                        {isSignUp ? "Log in" : "Sign up"}
                    </button>
                </p>
            </div>
        </main>
    );
}