import { Metadata } from "next";
import Link from "next/link";
import {
  CheckCircle2, XCircle, Minus,
  Download, ExternalLink, Star,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Rota AI vs SuperWhisper: The Honest Comparison (2026)",
  description:
    "Detailed, unbiased comparison between Rota AI (free, open source) and SuperWhisper ($8.49/month). Compare features, privacy, accuracy, and platform support.",
  alternates: {
    canonical: "https://rota.software/vs/superwhisper",
  },
  openGraph: {
    title: "Rota AI vs SuperWhisper: The Honest Comparison (2026)",
    description:
      "Free vs $8.49/month. Open source vs proprietary. See how Rota AI stacks up against SuperWhisper in features, privacy, and accuracy.",
    type: "website",
    images: [
      {
        url: "/api/og?title=Rota AI vs SuperWhisper&description=The honest 2026 comparison",
        width: 1200,
        height: 630,
        alt: "Rota AI vs SuperWhisper comparison",
      },
    ],
  },
};

const COMPARISON_ROWS = [
  {
    feature: "Price",
    rota: "Free",
    rotaBold: true,
    super: "$8.49/month or $72/year",
    winner: "rota",
  },
  {
    feature: "Open source",
    rota: "Yes, MIT license",
    rotaBold: true,
    super: "No",
    winner: "rota",
  },
  {
    feature: "Offline mode",
    rota: "Yes (via Ollama)",
    rotaBold: true,
    super: "Yes",
    winner: "tie",
  },
  {
    feature: "AI cleanup",
    rota: "Yes, context-aware",
    rotaBold: true,
    super: "Yes, multiple modes",
    winner: "tie",
  },
  {
    feature: "Context detection",
    rota: "Reads active window title & process",
    rotaBold: true,
    super: "Reads screen content",
    winner: "super",
  },
  {
    feature: "Telemetry",
    rota: "None (zero telemetry)",
    rotaBold: true,
    super: "Not fully disclosed",
    winner: "rota",
  },
  {
    feature: "Account required",
    rota: "No",
    rotaBold: true,
    super: "Yes",
    winner: "rota",
  },
  {
    feature: "API key encryption",
    rota: "OS keychain (DPAPI/macOS Keychain)",
    rotaBold: true,
    super: "Not disclosed",
    winner: "rota",
  },
  {
    feature: "Platform support",
    rota: "Windows, Mac, Linux",
    rotaBold: true,
    super: "Mac, Windows + iOS app",
    winner: "super",
  },
  {
    feature: "Voice commands",
    rota: "Yes (scratch that, translate, formal)",
    rotaBold: true,
    super: "Yes, extensive command set",
    winner: "tie",
  },
  {
    feature: "File transcription",
    rota: "Not yet",
    rotaBold: false,
    super: "Audio + video files",
    winner: "super",
  },
  {
    feature: "Cross-device sync",
    rota: "Not yet",
    rotaBold: false,
    super: "Yes (cloud)",
    winner: "super",
  },
  {
    feature: "Custom vocabulary",
    rota: "Personal dictionary",
    rotaBold: true,
    super: "Custom vocabulary",
    winner: "tie",
  },
  {
    feature: "macOS first-run",
    rota: "Unsigned (Ctrl+click to open)",
    rotaBold: false,
    super: "Signed, App Store available",
    winner: "super",
  },
  {
    feature: "iOS companion app",
    rota: "No",
    rotaBold: false,
    super: "Yes (iOS dictation)",
    winner: "super",
  },
];

const ROTA_PRO = [
  "100% free, no subscription",
  "Open source (MIT) fork and modify freely",
  "Zero telemetry your data stays private",
  "Supports Windows, Mac, AND Linux",
  "Custom personal dictionary for technical terms",
  "No account or signup needed",
  "API keys encrypted via OS keychain",
];

const ROTA_CON = [
  "No cross-device sync yet",
  "No file transcription yet",
  "No iOS companion app",
  "macOS build is unsigned requires Ctrl+click on first launch",
  "Smaller community than established tools",
];

const SUPER_PRO = [
  "Screen-reading context detection (reads full screen content)",
  "iOS companion app for mobile dictation",
  "Seamless installation signed builds + App Store",
  "File transcription (audio + video)",
  "Cross-device cloud sync",
  "Multiple AI cleanup modes to choose from",
  "More extensive voice command set",
];

const SUPER_CON = [
  "$8.49/month subscription ($72/year)",
  "Closed source no way to audit or customize",
  "Requires account for sync features",
  "No Linux desktop support",
  "Cloud sync means data passes through their servers",
  "Telemetry and data collection not fully transparent",
];

export default function VsSuperWhisperPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* BreadcrumbList JSON-LD Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
              { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://rota.software/" },
              { "@type": "ListItem", "position": 2, "name": "Comparisons", "item": "https://rota.software/blog" },
              { "@type": "ListItem", "position": 3, "name": "Rota AI vs SuperWhisper", "item": "https://rota.software/vs/superwhisper" }
            ]
          }),
        }}
      />
      {/* Product JSON-LD Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Product",
            "@id": "https://rota.software/#product",
            "name": "Rota AI",
            "description": "Free, open source voice dictation for Windows, Mac & Linux. AI-powered cleanup, offline mode, no subscriptions.",
            "url": "https://rota.software/vs/superwhisper",
            "brand": { "@type": "Brand", "name": "Rota AI" },
            "offers": {
              "@type": "Offer",
              "price": "0",
              "priceCurrency": "USD",
              "priceValidUntil": "2027-12-31",
              "availability": "https://schema.org/InStock"
            }
          }),
        }}
      />
      {/* Nav */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14"
        style={{
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(9,9,11,0.92)",
          backdropFilter: "blur(16px)",
        }}
      >
        <Link href="/" className="flex items-center">
          <img src="/logo.svg" alt="Rota AI" className="h-8 w-auto" />
        </Link>
        <div className="flex items-center gap-6 text-xs uppercase tracking-[0.15em] text-[#71717a]">
          <Link href="/" className="hover:text-[#fafafa] transition-colors">Home</Link>
          <Link href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</Link>
          <Link href="/#download" className="hover:text-[#fafafa] transition-colors">Download</Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-[#50545a] mb-8">
          <Link href="/" className="hover:text-[#fafafa] transition-colors">Home</Link>
          <span aria-hidden="true">/</span>
          <span className="text-[#71717a]">Rota AI vs SuperWhisper</span>
        </div>

        {/* Hero */}
        <div className="mb-16">
          <p className="text-[11px] uppercase tracking-[0.2em] text-[#e4f222] font-mono mb-4">Comparison</p>
          <h1
            className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-6"
            style={{ fontSize: "clamp(32px, 5vw, 56px)", color: "#fafafa" }}
          >
            Rota AI vs SuperWhisper
          </h1>
          <p className="text-sm text-[#a1a1aa] max-w-2xl leading-relaxed mb-8">
            Rota AI and SuperWhisper are both desktop voice dictation tools that use AI to clean up
            your speech into polished text. Both support offline mode, but they differ in price,
            platform support, privacy, and ecosystem breadth.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/#download"
              className="inline-flex items-center gap-2 px-6 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90"
              style={{ background: "#e4f222", color: "#000", borderRadius: 2 }}
            >
              <Download className="w-3.5 h-3.5" />
              Download Rota AI
            </Link>
            <a
              href="https://superwhisper.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 text-xs font-semibold uppercase tracking-[0.15em] border transition-all hover:border-white/15"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "#71717a", borderRadius: 2 }}
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Visit SuperWhisper
            </a>
          </div>
        </div>

        {/* At a Glance */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-16">
          <div
            className="p-6 rounded-sm"
            style={{ background: "rgba(228,242,34,0.04)", border: "1px solid rgba(228,242,34,0.15)" }}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}>
                <img src="/logo.svg" alt="Rota AI" className="w-4 h-4" style={{ filter: "brightness(0)" }} />
              </div>
              <span className="text-sm font-semibold text-[#fafafa]">Rota AI</span>
            </div>
            <div className="text-lg font-semibold text-[#e4f222] mb-1">Free</div>
            <div className="text-[11px] text-[#71717a] leading-relaxed">
              Open source · No account · MIT license · Windows, Mac, Linux
            </div>
          </div>
          <div
            className="p-6 rounded-sm"
            style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm font-semibold text-[#fafafa]">SuperWhisper</span>
            </div>
            <div className="text-lg font-semibold text-[#fafafa] mb-1">$8.49/month</div>
            <div className="text-[11px] text-[#71717a] leading-relaxed">
              Closed source · Cloud account · Mac, Windows, iOS
            </div>
          </div>
        </div>

        {/* Feature Comparison Table */}
        <div className="mb-16">
          <h2 className="text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono mb-6">
            Feature comparison
          </h2>
          <div className="overflow-x-auto -mx-6 sm:mx-0 px-6 sm:px-0">
            <table className="w-full text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-white/[.06]">
                  <th className="text-left py-3 sm:py-4 pr-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">
                    Feature
                  </th>
                  <th className="text-center py-3 sm:py-4 px-3 text-[10px] uppercase tracking-[0.2em] text-[#e4f222] font-mono">
                    Rota AI
                  </th>
                  <th className="text-center py-3 sm:py-4 pl-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">
                    SuperWhisper
                  </th>
                </tr>
              </thead>
              <tbody>
                {COMPARISON_ROWS.map((row, i) => (
                  <tr
                    key={i}
                    className="border-b border-white/[.03] transition-colors hover:bg-white/[.015]"
                  >
                    <td className="py-3 sm:py-4 pr-4 text-[12px] text-[#a1a1aa]">
                      <div className="flex items-center gap-2">
                        {row.feature}
                        {row.winner === "rota" && (
                          <Star className="w-3 h-3 text-[#e4f222] fill-[#e4f222]" />
                        )}
                      </div>
                    </td>
                    <td
                      className={`py-3 sm:py-4 px-3 text-center text-[12px] ${
                        row.rotaBold
                          ? "text-[#e4f222] font-semibold"
                          : "text-[#71717a]"
                      }`}
                    >
                      <div className="flex items-center justify-center gap-1.5">
                        {row.winner === "rota" && (
                          <CheckCircle2 className="w-3 h-3 text-[#e4f222]" />
                        )}
                        {row.winner === "super" && (
                          <Minus className="w-3 h-3 text-[#50545a]" />
                        )}
                        {row.rota}
                      </div>
                    </td>
                    <td className="py-3 sm:py-4 pl-4 text-center text-[12px] text-[#50545a]">
                      <div className="flex items-center justify-center gap-1.5">
                        {row.winner === "super" && (
                          <CheckCircle2 className="w-3 h-3 text-[#a1a1aa]" />
                        )}
                        {row.super}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pros & Cons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 mb-16">
          {/* Rota pros */}
          <div>
            <h3 className="text-xs uppercase tracking-[0.2em] text-[#e4f222] font-mono mb-4">
              Rota AI advantages
            </h3>
            <ul className="space-y-2.5">
              {ROTA_PRO.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-xs text-[#a1a1aa] leading-relaxed">
                  <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 text-[#e4f222] shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          {/* SuperWhisper pros */}
          <div>
            <h3 className="text-xs uppercase tracking-[0.2em] text-[#a1a1aa] font-mono mb-4">
              SuperWhisper advantages
            </h3>
            <ul className="space-y-2.5">
              {SUPER_PRO.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-xs text-[#a1a1aa] leading-relaxed">
                  <span className="w-3.5 h-3.5 mt-0.5 flex items-center justify-center shrink-0">
                    <Star className="w-3 h-3 text-[#a1a1aa]" />
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Rota cons (honest) */}
        <div
          className="p-6 rounded-sm mb-16"
          style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <h3 className="text-xs uppercase tracking-[0.2em] text-[#71717a] font-mono mb-4">
            Rota AI limitations (being worked on)
          </h3>
          <ul className="space-y-2.5">
            {ROTA_CON.map((item, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs text-[#71717a] leading-relaxed">
                <Minus className="w-3.5 h-3.5 mt-0.5 text-[#50545a] shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* SuperWhisper cons */}
        <div
          className="p-6 rounded-sm mb-16"
          style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          <h3 className="text-xs uppercase tracking-[0.2em] text-[#71717a] font-mono mb-4">
            SuperWhisper limitations
          </h3>
          <ul className="space-y-2.5">
            {SUPER_CON.map((item, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs text-[#71717a] leading-relaxed">
                <XCircle className="w-3.5 h-3.5 mt-0.5 text-[#50545a] shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Verdict */}
        <div
          className="p-8 rounded-sm mb-16"
          style={{
            background: "rgba(228,242,34,0.04)",
            border: "1px solid rgba(228,242,34,0.15)",
          }}
        >
          <h2 className="text-sm font-semibold text-[#fafafa] uppercase tracking-wider mb-3">
            The verdict
          </h2>
          <p className="text-sm text-[#a1a1aa] leading-relaxed mb-4">
            <strong className="text-[#fafafa]">If you want a free, private, open-source tool that works on Linux</strong> —
            Rota AI is the clear winner. It covers the core voice dictation use case with zero cost,
            zero telemetry, and zero account friction.
          </p>
          <p className="text-sm text-[#a1a1aa] leading-relaxed mb-4">
            <strong className="text-[#fafafa]">If you need the full ecosystem</strong> — SuperWhisper offers screen-reading
            context detection, an iOS app, file transcription, and cross-device sync. The $8.49/month
            is cheaper than Wispr Flow but still a recurring cost.
          </p>
          <p className="text-sm text-[#a1a1aa] leading-relaxed">
            <strong className="text-[#fafafa]">Our take:</strong> For desktop-only dictation, Rota AI matches SuperWhisper
            on accuracy and offline capabilities for free. SuperWhisper wins on ecosystem breadth
            (iOS, file transcription, screen reading). If you don&apos;t need those extras, Rota AI is
            the smarter choice.
          </p>
        </div>

        {/* CTA */}
        <div className="text-center">
          <h2 className="text-lg font-semibold text-[#fafafa] mb-3 uppercase tracking-wider">
            Try Rota AI free
          </h2>
          <p className="text-sm text-[#71717a] mb-6 max-w-sm mx-auto">
            No account. No credit card. Just download and start dictating.
          </p>
          <Link
            href="/#download"
            className="inline-flex items-center gap-2.5 px-8 py-4 text-sm font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
            style={{
              background: "#e4f222",
              color: "#000",
              borderRadius: 2,
              boxShadow: "0 4px 24px rgba(228,242,34,0.25)",
            }}
          >
            <Download className="w-4 h-4" />
            Download Rota AI
          </Link>
        </div>

        {/* Related reading */}
        <div className="mt-20 pt-12" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <h3 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono mb-6">
            Related comparisons
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Link
              href="/vs/wispr-flow"
              className="group p-4 rounded-sm transition-colors hover:bg-white/[.02]"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div className="text-xs text-[#a1a1aa] group-hover:text-[#e4f222] transition-colors">
                Rota AI vs Wispr Flow <span aria-hidden="true">&rarr;</span>
              </div>
              <div className="text-[10px] text-[#50545a] mt-1">Feature comparison and pricing breakdown</div>
            </Link>
            <Link
              href="/blog/rota-ai-vs-superwhisper-which-one-should-you-actually-use"
              className="group p-4 rounded-sm transition-colors hover:bg-white/[.02]"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div className="text-xs text-[#a1a1aa] group-hover:text-[#e4f222] transition-colors">
                Full blog comparison <span aria-hidden="true">&rarr;</span>
              </div>
              <div className="text-[10px] text-[#50545a] mt-1">In-depth blog post on the comparison</div>
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-12 px-6 sm:px-10" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-5 h-5 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}>
              <svg className="w-2.5 h-2.5 text-black" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              </svg>
            </div>
            <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa]">Rota AI</span>
          </div>
          <p className="text-[10px] uppercase tracking-widest text-[#71717a]">
            &copy; 2026 Rota AI &middot; MIT License
          </p>
        </div>
      </footer>
    </div>
  );
}
