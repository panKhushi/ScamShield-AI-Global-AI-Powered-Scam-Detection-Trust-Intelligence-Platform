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
        <main className="min-h-screen p-8 bg-slate-50">
            <h1 className="text-2xl font-bold mb-4">Debug: Session Info</h1>

            {error && <p className="text-red-600 mb-4">Error: {error}</p>}

            {!session && !error && <p>No active session — you are not logged in.</p>}

            {session && (
                <div className="space-y-4">
                    <div className="bg-white p-4 rounded-lg shadow">
                        <p className="font-medium">Logged in as:</p>
                        <p className="text-slate-600">{session.user.email}</p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow">
                        <p className="font-medium mb-2">Access Token (copy this):</p>
                        <textarea
                            readOnly
                            value={session.access_token}
                            className="w-full h-32 text-xs font-mono border border-slate-300 rounded p-2"
                            onClick={(e) => (e.target as HTMLTextAreaElement).select()}
                        />
                    </div>
                </div>
            )}
        </main>
    );
}