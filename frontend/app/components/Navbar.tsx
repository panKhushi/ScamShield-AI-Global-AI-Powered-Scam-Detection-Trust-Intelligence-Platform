"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../providers/AuthProvider";

export default function Navbar() {
    const { user, loading, signOut } = useAuth();
    const pathname = usePathname();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const isActive = (href: string) => pathname === href;

    const navLinks = [
        { href: "/", label: "Home" },
        { href: "/verify", label: "Verify" },
        { href: "/history", label: "History" },
        { href: "/admin", label: "Admin" },
    ];

    return (
        <nav className="sticky top-0 z-20 border-b border-white/10 bg-[#07111f]/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-3 text-white transition hover:opacity-90">
                    <span className="flex h-9 w-9 items-center justify-center rounded-[14px] bg-[#D9FFF5] shadow-lg shadow-[#22D3B8]/20">
                        <span className="h-2.5 w-2.5 rounded-full bg-[#07111f]" />
                    </span>
                    <span className="font-display text-lg font-bold tracking-tight">
                        ScamShield <span className="text-[#22D3B8]">AI</span>
                    </span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden md:flex md:items-center md:gap-6">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`rounded-xl border px-3 py-2 text-sm font-medium transition ${
                                isActive(link.href)
                                    ? "border-[#22D3B8]/50 bg-[#22D3B8]/10 text-[#8FFAE0]"
                                    : "border-white/10 text-[#DCEAFB] hover:border-[#22D3B8]/50 hover:text-white"
                            }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </div>

                {/* Auth Section */}
                <div className="flex items-center gap-2 sm:gap-3">
                    {loading ? (
                        <div className="h-8 w-24 animate-pulse rounded-full bg-white/10" />
                    ) : user ? (
                        <>
                            <div className="hidden items-center gap-2 sm:flex">
                                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-[#8B95AB]">
                                    {user.email?.split("@")[0]}
                                </span>
                                <button
                                    onClick={() => signOut()}
                                    className="rounded-full border border-[#EF4444]/20 bg-[#EF4444]/10 px-4 py-2 text-sm font-medium text-[#FCA5A5] transition hover:bg-[#EF4444]/15 hover:text-white"
                                >
                                    Log out
                                </button>
                            </div>
                            {/* Mobile logout */}
                            <button
                                onClick={() => signOut()}
                                className="sm:hidden rounded-full border border-[#EF4444]/20 bg-[#EF4444]/10 px-3 py-2 text-xs font-medium text-[#FCA5A5] transition hover:bg-[#EF4444]/15"
                            >
                                Log out
                            </button>
                        </>
                    ) : (
                        <Link
                            href="/login"
                            className="rounded-xl bg-[#D9FFF5] px-4 py-2 text-sm font-bold text-[#06201B] shadow-lg shadow-[#22D3B8]/20 transition hover:bg-white"
                        >
                            Log in
                        </Link>
                    )}

                    {/* Mobile Menu Toggle */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden rounded-full border border-white/10 p-2 text-[#DCEAFB] hover:text-white"
                    >
                        {mobileMenuOpen ? (
                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        ) : (
                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>

            {/* Mobile Navigation Menu */}
            {mobileMenuOpen && (
                <div className="border-t border-white/10 bg-[#07111f]/95 md:hidden">
                    <div className="space-y-2 px-4 py-4">
                        {navLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                onClick={() => setMobileMenuOpen(false)}
                                className={`block rounded-lg px-4 py-2 text-sm font-medium transition ${
                                    isActive(link.href)
                                        ? "border border-[#22D3B8] bg-[#22D3B8]/10 text-[#22D3B8]"
                                        : "text-[#DCEAFB] hover:bg-white/5 hover:text-white"
                                }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </nav>
    );
}