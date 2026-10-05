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
            if (!file.type.startsWith("image/") || file.size > 5 * 1024 * 1024) {
                setError("Evidence must be an image smaller than 5 MB.");
                setSubmitting(false);
                return;
            }
            setUploadingImage(true);
            evidenceUrl = await uploadEvidenceImage(file);
            setUploadingImage(false);
            if (!evidenceUrl) {
                setError("Image upload failed, but you can still submit without it.");
            }
        }

        try {
            const res = await fetch("/backend/api/report", {
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
        <form onSubmit={handleSubmit} className="surface-soft mt-4 space-y-3 p-4">
            {error && <p className="rounded-xl border border-[#F87171]/20 bg-[#F87171]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

            <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="field w-full px-3 py-2 text-sm"
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
                className="field w-full resize-none px-3 py-2 text-sm placeholder:text-[#8B95AB]"
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
                className="rounded-xl bg-[#F87171] px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#EF4444] disabled:opacity-50"
            >
                {uploadingImage ? "Uploading image..." : submitting ? "Submitting..." : "Submit Report"}
            </button>
        </form>
    )
}