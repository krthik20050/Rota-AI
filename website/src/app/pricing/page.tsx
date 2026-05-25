import Link from "next/link";
import { CheckCircle2 } from "lucide-react";

export const metadata = {
  title: "Pricing - Rota AI",
  description: "Rota AI is free and open source. No subscriptions, no account, no cloud lock.",
};

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
      <Nav />

      <div className="max-w-4xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4"
          style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}
        >
          Pricing
        </h1>
        <p className="text-lg text-[#a1a1aa] mb-16 max-w-xl">
          Free and open source. No subscriptions. No account needed.
        </p>

        <div className="max-w-md">
          <div
            className="p-8 rounded-sm"
            style={{
              background: "#111113",
              border: "1px solid rgba(228,242,34,0.15)",
            }}
          >
            <div className="flex items-baseline gap-2 mb-6">
              <span
                className="font-display uppercase tracking-[0.02em]"
                style={{ fontSize: "clamp(48px, 6vw, 64px)", color: "#e4f222" }}
              >
                $0
              </span>
              <span className="text-sm text-[#71717a]">/ forever</span>
            </div>

            <p className="text-sm text-[#a1a1aa] mb-6">
              Everything. No premium tier. No feature lock. No credit card.
            </p>

            <ul className="space-y-3 mb-8">
              {[
                "AI text cleanup and formatting",
                "Context-aware tone detection",
                "Voice snippets",
                "Personal dictionary",
                "100% offline with Ollama",
                "Encrypted API key storage",
                "Zero telemetry",
                "MIT license. Fork it, modify it.",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-[#fafafa]">
                  <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "#e4f222" }} />
                  {item}
                </li>
              ))}
            </ul>

            <Link
              href="/#download"
              className="group flex items-center justify-center gap-2 w-full px-6 py-3 text-sm font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
              style={{
                background: "#e4f222",
                color: "#000",
                borderRadius: 2,
                boxShadow: "0 4px 20px rgba(228,242,34,0.2)",
              }}
            >
              Download for your OS
              <svg className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            </Link>
          </div>

          <p className="text-xs text-[#71717a] mt-4 text-center">
            Groq / Gemini API keys are free. Ollama is free. Everything is free.
          </p>
        </div>
      </div>

      <Footer />
    </div>
  );
}

function Nav() {
  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14"
      style={{
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(9,9,11,0.92)",
        backdropFilter: "blur(16px)",
      }}
    >
      <Link href="/" className="flex items-center">
        <img src="/logo.png" alt="Rota AI" className="h-8 w-auto" />
      </Link>
      <div className="flex items-center gap-6 text-xs uppercase tracking-[0.15em] text-[#71717a]">
        <Link href="/#how-it-works" className="hover:text-[#fafafa] transition-colors hidden sm:block">How it works</Link>
        <Link href="/#features" className="hover:text-[#fafafa] transition-colors hidden sm:block">Features</Link>
        <Link href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</Link>
        <Link href="/#download" className="px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 rounded-sm" style={{ background: "#e4f222", color: "#000" }}>Download</Link>
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="py-8 px-6 sm:px-10" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-5 h-5 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}>
            <svg className="w-2.5 h-2.5 text-black" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/></svg>
          </div>
          <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa]">Rota AI</span>
        </div>
        <p className="text-xs uppercase tracking-widest text-[#71717a]">© 2026 Rota AI · MIT License</p>
      </div>
    </footer>
  );
}
