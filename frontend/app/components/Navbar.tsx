"use client";

import Link from "next/link";
import { useAuth } from "../providers/AuthProvider";

export default function Navbar() {
    const { user, loading, signOut } = useAuth();

    return (
        <nav className="sticky top-0 z-20 border-b border-white/10 bg-[#07111f]/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
                <Link href="/" className="flex items-center gap-3 text-white transition hover:opacity-90">
                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#22D3B8] to-[#34D399] shadow-lg shadow-[#22D3B8]/30">
                        <span className="h-2.5 w-2.5 rounded-full bg-[#07111f]" />
                    </span>
                    <span className="font-display text-lg font-bold tracking-tight">
                        ScamShield <span className="text-[#22D3B8]">AI</span>
                    </span>
                </Link>

                <div className="flex items-center gap-3">
                    <Link href="/history" className="hidden rounded-full border border-white/10 px-3 py-2 text-sm text-[#DCEAFB] transition hover:border-[#22D3B8]/50 hover:text-white sm:inline-flex">
                        History
                    </Link>

                    {!loading && user && (
                        <>
                            <span className="hidden rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-[#8B95AB] sm:inline-block">
                                {user.email}
                            </span>
                            <button
                                onClick={signOut}
                                className="rounded-full border border-[#EF4444]/20 bg-[#EF4444]/10 px-4 py-2 text-sm font-medium text-[#FCA5A5] transition hover:bg-[#EF4444]/15"
                            >
                                Log out
                            </button>
                        </>
                    )}

                    {!loading && !user && (
                        <Link
                            href="/login"
                            className="rounded-full bg-gradient-to-r from-[#22D3B8] to-[#34D399] px-4 py-2 text-sm font-bold text-[#07131C] shadow-lg shadow-[#22D3B8]/20 transition hover:scale-[1.01]"
                        >
                            Log in
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}