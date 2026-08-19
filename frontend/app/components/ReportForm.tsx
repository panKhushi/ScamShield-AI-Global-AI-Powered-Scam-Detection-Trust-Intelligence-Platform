"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase";
import { uploadEvidenceImage } from "@/lib/cloudinary";

type Props = {
    targetValue: string;
    targetType: string;
    onSuccess: () => void;
};

const categories = [
    { value: "payment_scam", label: "Asked for upfront payment" },
    { value: "phishing", label: "Phishing / credential theft" },
    { value: "fake_job", label: "Fake job offer" },
    { value: "counterfeit", label: "Counterfeit product / seller" },
    { value: "other", label: "Other" },
];

export default function ReportForm({ targetValue, targetType, onSuccess }: Props) {
    const [category, setCategory] = useState("payment_scam");
    const [description, setDescription] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [uploadingImage, setUploadingImage] = useState(false);
    const [error, setError] = useState("");
    const supabase = createClient();

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSubmitting(true);
        setError("");

        const { data: sessionData } = await supabase.auth.getSession();
        const token = sessionData.session?.access_token;

        if (!token) {
            setError("You must be logged in to submit a report.");
            setSubmitting(false);
            return;
        }

        let evidenceUrl: string | null = null;
        if (file) {
            setUploadingImage(true);
            evidenceUrl = await uploadEvidenceImage(file);
            setUploadingImage(false);
            if (!evidenceUrl) {
                setError("Image upload failed, but you can still submit without it.");
            }
        }

        try {
            const res = await fetch("http://localhost:8000/api/report", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    target_value: targetValue,
                    target_type: targetType,
                    category,
                    description,
                    evidence_url: evidenceUrl,
                }),
            });

            if (!res.ok) throw new Error("Failed to submit report");

            onSuccess();
        } catch (err) {
            setError("Something went wrong submitting your report.");
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} className="mt-3 space-y-3 bg-[#0B1120] border border-[#232E45] p-4 rounded-lg">
            {error && <p className="text-[#EF4444] text-sm">{error}</p>}

            <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-[#131B2E] border border-[#232E45] text-[#E8ECF1] rounded-lg px-3 py-2 text-sm"
            >
                {categories.map((c) => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                ))}
            </select>

            <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what happened..."
                rows={3}
                required
                className="w-full bg-[#131B2E] border border-[#232E45] text-[#E8ECF1] placeholder-[#8B95AB] rounded-lg px-3 py-2 text-sm resize-none"
            />

            <div>
                <label className="text-sm text-[#8B95AB] block mb-1">
                    Evidence screenshot (optional)
                </label>
                <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="text-sm text-[#8B95AB]"
                />
            </div>

            <button
                type="submit"
                disabled={submitting || uploadingImage}
                className="bg-[#EF4444] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#DC2626] disabled:opacity-50 transition-colors"
            >
                {uploadingImage ? "Uploading image..." : submitting ? "Submitting..." : "Submit Report"}
            </button>
        </form>
    )
}