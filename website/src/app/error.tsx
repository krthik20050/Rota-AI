"use client";

import Link from "next/link";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col items-center justify-center px-6 text-center">
      <div className="max-w-md">
        <div className="mb-8 flex justify-center">
          <Link href="/">
            <img src="/logo.svg" alt="Rota AI" className="h-16 w-auto" />
          </Link>
        </div>
        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4"
          style={{ fontSize: "clamp(72px, 15vw, 120px)", color: "#e4f222" }}
        >
          500
        </h1>
        <p className="text-sm text-[#a1a1aa] mb-8 leading-relaxed">
          Something went wrong on our end. Please try again or come back later.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-6 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90"
            style={{ background: "#e4f222", color: "#000", borderRadius: 2, border: "none", cursor: "pointer", font: "inherit" }}
          >
            Try again
          </button>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90"
            style={{ background: "rgba(255,255,255,0.06)", color: "#fafafa", borderRadius: 2 }}
          >
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
