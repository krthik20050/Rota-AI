import Link from "next/link";

export const metadata = {
  title: "Support:Rota AI",
  description: "Getting started, system requirements, FAQ, and support for Rota AI.",
};

const FAQ = [
  { q: "Is this really free?", a: "Yes. MIT licensed open source. Groq and Gemini both have free tiers. Ollama is completely free. No pro plan, no premium tier, no credit card needed." },
  { q: "How does the download work?", a: "Windows: run the installer. Mac: unzip RotaAI-macOS.zip, Control-click RotaAI.app, choose Open, and grant permissions on first launch. Linux: download the AppImage, mark it executable (chmod +x RotaAI.AppImage), and run it." },
  { q: "Can I use it without internet?", a: "Yes. Install Ollama, download a Whisper model (small is 480MB), and Rota works 100% offline. No API keys, no accounts, no internet." },
  { q: "What about Mac or Linux?", a: "Windows, macOS, and Linux builds are published from GitHub releases. The macOS build is currently unsigned, so first launch uses the standard Control-click Open workaround until Developer ID notarization is available." },
  { q: "System requirements?", a: "Windows 10/11, macOS 13+, or Linux (Ubuntu 20.04+, Fedora 36+, Arch). 4GB RAM minimum, 8GB recommended. For local GPU: NVIDIA GPU with 4GB+ VRAM. CPU-only works on any modern quad core." },
  { q: "Which Whisper model should I use?", a: "Base (140MB) for speed. Small (480MB) for best balance. Large v3 turbo (1.5GB) for best accuracy if you have 4GB+ VRAM." },
  { q: "How do I get a Groq API key?", a: "Go to console.groq.com, sign up (free), and create an API key. Paste it into Rota during onboarding." },
  { q: "Can I use my own Whisper model?", a: "Yes. Rota supports loading custom model paths. Point it to your fine-tuned model in settings." },
];

export default function SupportPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", background: "rgba(9,9,11,0.92)", backdropFilter: "blur(16px)" }}>
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo.png" alt="Rota AI" className="h-8 w-auto" />
        </Link>
        <div className="flex items-center gap-6 text-xs uppercase tracking-[0.15em] text-[#71717a]">
          <Link href="/#how-it-works" className="hover:text-[#fafafa] transition-colors hidden sm:block">How it works</Link>
          <Link href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</Link>
          <Link href="/#download" className="px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 rounded-sm" style={{ background: "#e4f222", color: "#000" }}>Download</Link>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4" style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}>Support</h1>
        <p className="text-sm text-[#71717a] mb-16">Getting started, system requirements, and frequently asked questions.</p>

        {/* Getting Started */}
        <section className="mb-16">
          <h2 className="text-base font-semibold text-[#fafafa] mb-6 font-mono text-xs uppercase tracking-[0.2em]">Getting started</h2>
          <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
            <p><strong className="text-[#fafafa]">1. Download</strong>:Get the latest release from <a href="https://github.com/krthik20050/Rota-AI/releases/latest" className="text-[#e4f222] hover:underline">GitHub releases</a>.</p>
            <p><strong className="text-[#fafafa]">2. Run</strong>:Windows: run the installer. Mac: unzip, Control-click <code className="text-xs bg-[#111113] px-1.5 py-0.5 rounded-sm text-[#e4f222] font-mono">RotaAI.app</code>, choose Open. Linux: <code className="text-xs bg-[#111113] px-1.5 py-0.5 rounded-sm text-[#e4f222] font-mono">chmod +x RotaAI.AppImage && ./RotaAI.AppImage</code></p>
            <p><strong className="text-[#fafafa]">3. Onboarding</strong>:Pick your transcription backend (Groq, Gemini, or Ollama). Add your API key if using cloud.</p>
            <p><strong className="text-[#fafafa]">4. Dictate</strong>:Press F9 in any app. Speak. Release F9. Your text appears.</p>
          </div>
        </section>

        {/* System Requirements */}
        <section className="mb-16">
          <h2 className="text-base font-semibold text-[#fafafa] mb-6 font-mono text-xs uppercase tracking-[0.2em]">System requirements</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { label: "OS", value: "Windows 10/11, macOS 13+, or Linux (Ubuntu 20.04+, Fedora 36+, Arch)" },
              { label: "RAM", value: "4 GB minimum, 8 GB recommended" },
              { label: "GPU", value: "Optional. NVIDIA with 4GB+ VRAM for local transcription" },
              { label: "Disk", value: "~600 MB for dependencies + model size (140MB–3.1GB)" },
              { label: "Microphone", value: "Any built-in or external mic" },
            ].map((item) => (
              <div key={item.label} className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                <div className="text-xs uppercase tracking-[0.15em] text-[#71717a] font-mono mb-1">{item.label}</div>
                <div className="text-sm text-[#fafafa]">{item.value}</div>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-16">
          <h2 className="text-base font-semibold text-[#fafafa] mb-6 font-mono text-xs uppercase tracking-[0.2em]">Frequently asked questions</h2>
          <div className="space-y-0">
            {FAQ.map((item, i) => (
              <details key={i} className="group border-b border-white/[.06]">
                <summary className="py-4 text-sm font-medium text-[#fafafa] cursor-pointer list-none flex items-center justify-between gap-4 hover:text-[#e4f222] transition-colors">
                  {item.q}
                  <svg className="w-4 h-4 shrink-0 text-[#71717a] transition-transform group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
                </summary>
                <p className="pb-4 text-sm text-[#a1a1aa] leading-relaxed">{item.a}</p>
              </details>
            ))}
          </div>
        </section>

        {/* Contact */}
        <section>
          <h2 className="text-base font-semibold text-[#fafafa] mb-6 font-mono text-xs uppercase tracking-[0.2em]">Still need help?</h2>
          <p className="text-sm text-[#a1a1aa] leading-relaxed mb-4">
            Open an issue on <a href="https://github.com/krthik20050/Rota-AI/issues" className="text-[#e4f222] hover:underline">GitHub</a>. I read every issue and try to respond quickly.
          </p>
        </section>
      </div>

      <footer className="py-8 px-6 sm:px-10" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-5 h-5 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}><svg className="w-2.5 h-2.5 text-black" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/></svg></div>
            <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa]">Rota AI</span>
          </div>
          <p className="text-xs uppercase tracking-widest text-[#71717a]">© 2026 Rota AI · MIT License</p>
        </div>
      </footer>
    </div>
  );
}
