export const metadata = {
  title: "Privacy - Rota AI",
  description: "Rota AI does not collect, store, or transmit any personal data. Your voice stays on your machine.",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", background: "rgba(9,9,11,0.92)", backdropFilter: "blur(16px)" }}>
        <a href="/" className="flex items-center">
          <img src="/logo.png" alt="Rota AI" className="h-8 w-auto" />
        </a>
        <a href="/" className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors">← Home</a>
      </nav>

      <div className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4" style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}>Privacy</h1>
        <p className="text-sm text-[#71717a] mb-12">Last updated: May 23, 2026</p>

        <div className="space-y-8 text-sm text-[#a1a1aa] leading-relaxed">
          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">No data collection</h2>
            <p>Rota AI does not collect, store, or transmit any personal data. Your voice recordings, transcriptions, and API keys stay on your local machine. Always.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">No telemetry</h2>
            <p>There is no analytics, no error reporting, no usage tracking, no phone-home of any kind. I do not know how many people use Rota AI. I do not know what features they use. I do not want to know.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">No account</h2>
            <p>Rota AI does not require an account, an email, or any personal information. Download it, run it, done.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">API keys</h2>
            <p>If you choose to use cloud transcription (Groq or Gemini), your API key is stored locally using Windows DPAPI encryption. It is never transmitted to any server except the API provider you explicitly configured.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">Offline mode</h2>
            <p>When using Ollama for local transcription, your audio never leaves your machine. Not for transcription, not for cleanup, not for anything.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">Open source</h2>
            <p>Rota AI is MIT licensed. You can read every line of code and verify exactly what it does. The source is at <a href="https://github.com/krthik20050/Rota-AI" className="text-[#e4f222] hover:underline">github.com/krthik20050/Rota-AI</a>.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">Contact</h2>
            <p>Questions about privacy? Open an issue on GitHub.</p>
          </section>
        </div>
      </div>
    </div>
  );
}
