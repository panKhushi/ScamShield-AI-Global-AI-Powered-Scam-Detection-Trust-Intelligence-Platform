"use client";

import { useEffect, useState } from "react";

type Report = {
    id: number;
    category: string;
    description: string;
    created_at: string;
    evidence_url?: string;
};

export default function CommunityReports({
    targetValue,
}: {
    targetValue: string;
}) {
    const [reports, setReports] = useState<Report[]>([]);

    useEffect(() => {
        fetch(
            `/backend/api/reports/${encodeURIComponent(targetValue)}`
        )
            .then(async (res) => {
                const data: unknown = await res.json();

                if (!res.ok || !Array.isArray(data)) {
                    console.error("Failed to load community reports", res.status, data);
                    setReports([]);
                    return;
                }

                setReports(data as Report[]);
            })
            .catch((error) => {
                console.error("Failed to load community reports", error);
                setReports([]);
            });
    }, [targetValue]);

    if (reports.length === 0) return null;

    return (
        <div className="mt-4">
            <p className="text-sm font-medium text-[#E8ECF1] mb-2">
                Community Reports ({reports.length})
            </p>

            <div className="space-y-2">
                {reports.map((r) => (
                    <div key={r.id} className="rounded-[16px] border border-[#F87171]/20 bg-[#F87171]/10 p-3 text-sm">
                        <p className="font-medium text-[#EF4444] capitalize">
                            {r.category.replace("_", " ")}
                        </p>

                        <p className="text-[#C4CCDA]">
                            {r.description}
                        </p>

                        {r.evidence_url && (
                            <img
                                src={r.evidence_url}
                                alt="Evidence"
                                className="mt-2 rounded-lg max-h-40 border border-[#232E45]"
                            />
                        )}

                        <p className="text-xs text-[#8B95AB] mt-1 font-mono">
                            {new Date(r.created_at).toLocaleDateString()}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}