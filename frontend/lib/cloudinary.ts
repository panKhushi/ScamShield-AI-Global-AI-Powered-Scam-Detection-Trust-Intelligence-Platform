export async function uploadEvidenceImage(file: File): Promise<string | null> {
    const cloudName = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
    const uploadPreset = process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET;

    if (!cloudName || !uploadPreset || !file.type.startsWith("image/") || file.size > 5 * 1024 * 1024) {
        return null;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("upload_preset", uploadPreset!);

    try {
        const res = await fetch(
            `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`,
            { method: "POST", body: formData }
        );
        if (!res.ok) return null;
        const data = await res.json();
        return data.secure_url || null;
    } catch (err) {
        console.error("Cloudinary upload failed:", err);
        return null;
    }
}