import Link from "next/link";
import { Mail, MessageSquare } from "lucide-react";

export const metadata = {
  title: "Contact - Rota AI",
  description: "Get in touch with the Rota AI team. Open a GitHub issue, send an email, or join the discussion.",
};

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
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
        <Link
          href="/"
          className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors"
        >
          ← Home
        </Link>
      </nav>

      <div className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4"
          style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}
        >
          Contact
        </h1>
        <p className="text-sm text-[#71717a] mb-12 leading-relaxed">
          Questions, bug reports, feature requests, or just want to say hi. Here is how to reach us.
        </p>

        <div className="space-y-6">
          <a
            href="https://github.com/krthik20050/Rota-AI/issues" target="_blank" rel="noopener noreferrer"
            className="group flex items-start gap-5 p-5 rounded-sm transition-all hover:bg-[#0d0d10]"
            style={{ border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div
              className="w-12 h-12 flex items-center justify-center shrink-0 rounded-sm"
              style={{ background: "rgba(228,242,34,0.06)", border: "1px solid rgba(228,242,34,0.1)" }}
            >
              <svg viewBox="0 0 24 24" className="w-5 h-5 text-[#e4f222] fill-current"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-[#fafafa] mb-1 group-hover:text-[#e4f222] transition-colors">
                GitHub Issues
              </h3>
              <p className="text-xs text-[#71717a] leading-relaxed">
                Report bugs, request features, or ask technical questions. All issues are read and responded to.
              </p>
            </div>
          </a>

          <a
            href="https://github.com/krthik20050/Rota-AI/discussions" target="_blank" rel="noopener noreferrer"
            className="group flex items-start gap-5 p-5 rounded-sm transition-all hover:bg-[#0d0d10]"
            style={{ border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div
              className="w-12 h-12 flex items-center justify-center shrink-0 rounded-sm"
              style={{ background: "rgba(228,242,34,0.06)", border: "1px solid rgba(228,242,34,0.1)" }}
            >
              <MessageSquare className="w-5 h-5 text-[#e4f222]" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-[#fafafa] mb-1 group-hover:text-[#e4f222] transition-colors">
                GitHub Discussions
              </h3>
              <p className="text-xs text-[#71717a] leading-relaxed">
                Join the community conversation, share tips, and help other users.
              </p>
            </div>
          </a>

          <a
            href="mailto:tl24btcs@gmail.com"
            className="group flex items-start gap-5 p-5 rounded-sm transition-all hover:bg-[#0d0d10]"
            style={{ border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <div
              className="w-12 h-12 flex items-center justify-center shrink-0 rounded-sm"
              style={{ background: "rgba(228,242,34,0.06)", border: "1px solid rgba(228,242,34,0.1)" }}
            >
              <Mail className="w-5 h-5 text-[#e4f222]" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-[#fafafa] mb-1 group-hover:text-[#e4f222] transition-colors">
                Email
              </h3>
              <p className="text-xs text-[#71717a] leading-relaxed">
                <span className="text-[#e4f222]">tl24btcs@gmail.com</span> — For direct inquiries,
                privacy concerns, or legal requests.
              </p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
