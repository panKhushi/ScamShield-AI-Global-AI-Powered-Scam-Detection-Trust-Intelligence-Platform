"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";

export default function DebugPage() {
    const [session, setSession] = useState<any>(null);
    const [error, setError] = useState<string>("");
    const supabase = createClient();

    useEffect(() => {
        supabase.auth.getSession().then(({ data, error }) => {
            if (error) setError(error.message);
            setSession(data.session);
        });
    }, []);

    return (
        <main className="min-h-screen px-4 py-10">
            <div className="mx-auto max-w-3xl">
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#8B95AB]">Developer tools</p>
            <h1 className="font-display mb-6 mt-2 text-3xl font-bold text-white">Session information</h1>

            {error && <p className="mb-4 rounded-xl border border-[#F87171]/20 bg-[#F87171]/10 px-3 py-2 text-[#FCA5A5]">Error: {error}</p>}

            {!session && !error && <div className="surface p-6 text-[#9CA9C0]">No active session. You are not logged in.</div>}

            {session && (
                <div className="space-y-4">
                    <div className="surface p-5">
                        <p className="text-xs uppercase tracking-[0.15em] text-[#8B95AB]">Logged in as</p>
                        <p className="mt-2 text-[#E8ECF1]">{session.user.email}</p>
                    </div>

                    <div className="surface p-5">
                        <p className="mb-2 text-xs uppercase tracking-[0.15em] text-[#8B95AB]">Access token</p>
                        <textarea
                            readOnly
                            value={session.access_token}
                            className="field h-32 w-full resize-none p-3 text-xs font-mono"
                            onClick={(e) => (e.target as HTMLTextAreaElement).select()}
                        />
                    </div>
                </div>
            )}
            </div>
        </main>
    );
}