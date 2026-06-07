import Link from "next/link";

export const metadata = {
  title: "Docs - Rota AI",
  description: "Rota AI documentation. Installation, quickstart, configuration, and reference.",
};

const SIDEBAR_SECTIONS = [
  {
    title: "Getting Started",
    items: [
      { label: "Installation", href: "#installation" },
      { label: "Quickstart", href: "#quickstart" },
      { label: "System requirements", href: "#requirements" },
    ],
  },
  {
    title: "Configuration",
    items: [
      { label: "Transcription backends", href: "#backends" },
      { label: "Voice snippets", href: "#snippets" },
      { label: "Personal dictionary", href: "#dictionary" },
      { label: "Settings reference", href: "#settings" },
    ],
  },
  {
    title: "Usage",
    items: [
      { label: "Basic dictation", href: "#basic-dictation" },
      { label: "Voice commands", href: "#voice-commands" },
      { label: "Context awareness", href: "#context" },
      { label: "Offline mode", href: "#offline" },
    ],
  },
  {
    title: "Platform",
    items: [
      { label: "Windows setup", href: "#windows" },
      { label: "macOS setup", href: "#macos" },
      { label: "Linux setup", href: "#linux" },
    ],
  },
  {
    title: "Reference",
    items: [
      { label: "Hotkeys", href: "#hotkeys" },
      { label: "Privacy & security", href: "#privacy" },
      { label: "FAQ", href: "#faq" },
      { label: "Troubleshooting", href: "#troubleshooting" },
    ],
  },
];

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      {/* Top nav */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14"
        style={{
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(9,9,11,0.92)",
          backdropFilter: "blur(16px)",
        }}
      >
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo.svg" alt="Rota AI" className="h-7 w-auto" />
          <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa] hidden sm:block">Docs</span>
        </Link>
        <div className="flex items-center gap-6 text-xs uppercase tracking-[0.15em] text-[#71717a]">
          <Link href="/" className="hover:text-[#fafafa] transition-colors">Home</Link>
          <Link href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</Link>
          <a href="/#download" className="px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 rounded-sm"
            style={{ background: "#e4f222", color: "#000" }}>Download</a>
        </div>
      </nav>

      <div className="flex pt-14">
        {/* Sidebar */}
        <aside className="w-56 lg:w-64 shrink-0 hidden md:block fixed left-0 top-14 bottom-0 overflow-y-auto px-4 py-8"
          style={{ borderRight: "1px solid rgba(255,255,255,0.06)" }}>
          <nav className="space-y-8">
            {SIDEBAR_SECTIONS.map((section) => (
              <div key={section.title}>
                <h3 className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#50545a] mb-3 px-2">
                  {section.title}
                </h3>
                <ul className="space-y-0.5">
                  {section.items.map((item) => (
                    <li key={item.label}>
                      <a
                        href={item.href}
                        className="block px-2 py-1.5 text-xs text-[#71717a] hover:text-[#fafafa] hover:bg-white/[.03] rounded-sm transition-colors"
                      >
                        {item.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </aside>

        {/* Mobile sidebar toggle */}
        <div className="md:hidden fixed top-14 left-0 right-0 z-40 px-4 py-3"
          style={{ background: "rgba(9,9,11,0.95)", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
          <details className="group">
            <summary className="text-xs uppercase tracking-[0.15em] text-[#71717a] cursor-pointer list-none flex items-center justify-between">
              <span>Jump to section</span>
              <svg className="w-3.5 h-3.5 transition-transform group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
            </summary>
            <div className="mt-3 space-y-3 pb-2">
              {SIDEBAR_SECTIONS.map((section) => (
                <div key={section.title}>
                  <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#50545a] mb-1.5">{section.title}</h4>
                  <div className="space-y-1">
                    {section.items.map((item) => (
                      <a key={item.label} href={item.href}
                        className="block text-xs text-[#71717a] hover:text-[#fafafa] py-1 transition-colors">
                        {item.label}
                      </a>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </details>
        </div>

        {/* Main content */}
        <main className="flex-1 md:ml-56 lg:ml-64 px-6 sm:px-10 pt-8 md:pt-8 pb-20 max-w-4xl">
          <div className="md:pt-8 md:mt-6">
            <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-6"
              style={{ fontSize: "clamp(32px, 5vw, 52px)", color: "#fafafa" }}>
              Documentation
            </h1>

            {/* ────────────── Getting Started ────────────── */}
            <section id="installation" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Installation</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Download the latest release for your operating system from the website or GitHub releases. No account or credit card required.</p>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-2">Windows</p>
                  <p className="text-xs">Download RotaAI-Setup.exe and run it. Follow the installer prompts.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-2">macOS</p>
                  <p className="text-xs">Download RotaAI-macOS.zip. Unzip it. Control-click RotaAI.app, choose Open, then grant permissions.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-2">Linux</p>
                  <p className="text-xs">Download the AppImage. Make it executable: <code className="text-[#e4f222]">chmod +x RotaAI.AppImage</code>. Run it.</p>
                </div>
              </div>
            </section>

            <section id="quickstart" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Quickstart</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <ol className="space-y-3 list-decimal pl-5">
                  <li><strong className="text-[#fafafa]">Download and install</strong> Rota AI for your platform.</li>
                  <li><strong className="text-[#fafafa]">Choose a backend</strong> during onboarding: Groq (free API key), Gemini (free API key), or Ollama (fully local).</li>
                  <li><strong className="text-[#fafafa]">Press F9</strong> in any text field to start recording. A floating pill appears.</li>
                  <li><strong className="text-[#fafafa]">Speak naturally</strong> at a normal pace. Rota transcribes in real time.</li>
                  <li><strong className="text-[#fafafa]">Release F9</strong> to stop recording. Your cleaned text appears where your cursor is.</li>
                </ol>
              </div>
            </section>

            <section id="requirements" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">System Requirements</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                {[
                  { label: "OS", value: "Windows 10/11, macOS 13+, or Linux (Ubuntu 20.04+, Fedora 36+, Arch)" },
                  { label: "RAM", value: "4 GB minimum, 8 GB recommended" },
                  { label: "GPU", value: "Optional. NVIDIA with 4GB+ VRAM for local transcription" },
                  { label: "Disk", value: "~600 MB for dependencies plus model size (140MB to 3.1GB)" },
                  { label: "Microphone", value: "Any built-in or external microphone" },
                ].map((item) => (
                  <div key={item.label} className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                    <div className="text-xs uppercase tracking-[0.15em] text-[#71717a] font-mono mb-1">{item.label}</div>
                    <div className="text-sm text-[#fafafa]">{item.value}</div>
                  </div>
                ))}
              </div>
            </section>

            {/* ────────────── Configuration ────────────── */}
            <section id="backends" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Transcription Backends</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI supports three transcription backends. You can switch between them anytime from Settings.</p>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">Groq (Cloud, Free Tier)</p>
                  <p className="text-xs">Fastest option. Powered by Groq LPU hardware. Sign up at console.groq.com for a free API key. Whisper Large v3 transcription with sub-second latency.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">Gemini (Cloud, Free Tier)</p>
                  <p className="text-xs">Google transcription API. Free tier includes enough credits for daily use. Get an API key from Google AI Studio.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">Ollama (Local, Fully Offline)</p>
                  <p className="text-xs">Install Ollama, download a Whisper model (small is 480MB), and Rota works 100% offline. No API keys, no accounts, no internet required.</p>
                </div>
              </div>
            </section>

            <section id="snippets" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Voice Snippets</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Voice snippets let you insert frequently used text with a spoken shortcut. Instead of typing a full sentence, say a short trigger word and Rota expands it. For example, set "sig" to expand to your full email signature.</p>
                <p>Manage your snippets from Settings {'>'} Snippets. You can add, edit, or delete snippets at any time. Snippets are stored locally and synced across sessions.</p>
              </div>
            </section>

            <section id="dictionary" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Personal Dictionary</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>The personal dictionary learns your vocabulary over time. Technical terms, project names, acronyms, and unusual words are remembered so Rota transcribes them correctly every time.</p>
                <p>If Rota consistently misrecognizes a word, add it to your dictionary by saying the word and correcting the spelling. The dictionary is stored locally and persists across updates.</p>
              </div>
            </section>

            <section id="settings" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Settings Reference</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-white/[.06]">
                        <th className="text-left py-2.5 pr-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">Setting</th>
                        <th className="text-left py-2.5 pl-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { setting: "Backend", desc: "Choose Groq, Gemini, or Ollama for transcription" },
                        { setting: "Model size", desc: "Base (fast), Small (balanced), Large (accurate)" },
                        { setting: "Hotkey", desc: "Customize the recording key (default: F9)" },
                        { setting: "Microphone", desc: "Select which microphone to use" },
                        { setting: "Language", desc: "Transcription language (auto-detect or manual)" },
                        { setting: "History retention", desc: "How long to keep session history (default: 2 days)" },
                        { setting: "AI cleanup", desc: "Enable or disable the AI cleanup pass" },
                        { setting: "Offline mode", desc: "Force local-only operation with Ollama" },
                      ].map((row) => (
                        <tr key={row.setting} className="border-b border-white/[.03]">
                          <td className="py-2.5 pr-4 text-[#fafafa] font-mono">{row.setting}</td>
                          <td className="py-2.5 pl-4 text-[#71717a]">{row.desc}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            {/* ────────────── Usage ────────────── */}
            <section id="basic-dictation" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Basic Dictation</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Basic dictation is the core feature of Rota AI. Press and hold the hotkey (default F9), speak what you want to type, then release. The transcribed and cleaned text is injected directly into the application you are using.</p>
                <p>Tips for best accuracy:</p>
                <ul className="space-y-1.5 pl-5 list-disc">
                  <li>Speak at a natural pace. Do not slow down deliberately.</li>
                  <li>Position your microphone 6 to 12 inches from your mouth.</li>
                  <li>Minimize background noise for clearer recordings.</li>
                  <li>Use a consistent volume. Avoid whispering or shouting.</li>
                  <li>Pause briefly between sentences for cleaner segmentation.</li>
                </ul>
              </div>
            </section>

            <section id="voice-commands" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Voice Commands</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI understands voice commands that let you edit text by speaking. These work during or immediately after dictation.</p>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-white/[.06]">
                        <th className="text-left py-2.5 pr-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">Command</th>
                        <th className="text-left py-2.5 pl-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { cmd: "Scratch that", action: "Removes the last transcribed sentence" },
                        { cmd: "Make it more formal", action: "Rewrites the last sentence in formal tone" },
                        { cmd: "Make it casual", action: "Rewrites in casual tone" },
                        { cmd: "Change deadline to Friday", action: "Edits text in-place based on context" },
                        { cmd: "Translate to Spanish", action: "Converts the last sentence to Spanish" },
                        { cmd: "New line", action: "Inserts a line break" },
                        { cmd: "New paragraph", action: "Starts a new paragraph" },
                      ].map((row) => (
                        <tr key={row.cmd} className="border-b border-white/[.03]">
                          <td className="py-2.5 pr-4 text-[#e4f222] font-mono">{row.cmd}</td>
                          <td className="py-2.5 pl-4 text-[#71717a]">{row.action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            <section id="context" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Context Awareness</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota detects which application is in focus and adapts the transcription output accordingly. No configuration required.</p>
                <ul className="space-y-2 pl-5 list-disc">
                  <li><strong className="text-[#fafafa]">Email (Outlook, Gmail):</strong> Formal tone, proper salutations and closings.</li>
                  <li><strong className="text-[#fafafa]">Chat (Slack, Discord, Telegram):</strong> Casual tone, shorter sentences.</li>
                  <li><strong className="text-[#fafafa]">Code (VS Code, Cursor, JetBrains):</strong> Preserves camelCase, snake_case, code syntax, and technical vocabulary.</li>
                  <li><strong className="text-[#fafafa]">Documents (Word, Notion, Google Docs):</strong> Neutral tone with proper punctuation and formatting.</li>
                </ul>
              </div>
            </section>

            <section id="offline" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Offline Mode</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI can run entirely offline using Ollama as the transcription backend. No internet connection, no API keys, and no data leaving your machine.</p>
                <ol className="space-y-2 pl-5 list-decimal">
                  <li>Install <a href="https://ollama.com" target="_blank" rel="noopener noreferrer" className="text-[#e4f222] hover:underline">Ollama</a> on your machine.</li>
                  <li>Download a Whisper model: <code className="text-[#e4f222] text-xs">ollama pull whisper-small</code> (480MB) or <code className="text-[#e4f222] text-xs">ollama pull whisper-large</code> (3.1GB).</li>
                  <li>In Rota AI Settings, change the backend to Ollama.</li>
                  <li>That is it. Rota now works completely offline.</li>
                </ol>
                <p>Offline transcription is slightly slower than cloud backends but provides complete privacy. Your voice data never leaves your computer.</p>
              </div>
            </section>

            {/* ────────────── Platform ────────────── */}
            <section id="windows" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Windows Setup</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI runs on Windows 10 and Windows 11. The installer handles all dependencies automatically.</p>
                <ul className="space-y-2 pl-5 list-disc">
                  <li>Download the .exe installer from the website.</li>
                  <li>Run the installer. No administrator privileges required.</li>
                  <li>Rota starts automatically after installation and lives in the system tray.</li>
                  <li>On first launch, Windows may ask for microphone permission. Grant it.</li>
                </ul>
              </div>
            </section>

            <section id="macos" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">macOS Setup</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI supports macOS 13+. The current build is not notarized, so first launch requires a one-time permission step.</p>
                <ul className="space-y-2 pl-5 list-disc">
                  <li>Download RotaAI-macOS.zip and unzip it.</li>
                  <li>Control-click RotaAI.app and choose Open from the context menu.</li>
                  <li>Click Open in the dialog. This is only needed on first launch.</li>
                  <li>Grant Accessibility and Microphone permissions when prompted.</li>
                </ul>
              </div>
            </section>

            <section id="linux" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Linux Setup</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI supports Ubuntu 20.04+, Fedora 36+, and Arch Linux via AppImage.</p>
                <ul className="space-y-2 pl-5 list-disc">
                  <li>Download the .AppImage file from the website.</li>
                  <li>Make it executable: <code className="text-[#e4f222] text-xs">chmod +x RotaAI.AppImage</code>.</li>
                  <li>Run it: <code className="text-[#e4f222] text-xs">./RotaAI.AppImage</code>.</li>
                  <li>For system-wide access, move it to <code className="text-[#e4f222] text-xs">~/.local/bin/</code> or <code className="text-[#e4f222] text-xs">/usr/local/bin/</code>.</li>
                </ul>
              </div>
            </section>

            {/* ────────────── Reference ────────────── */}
            <section id="hotkeys" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Hotkeys</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-white/[.06]">
                      <th className="text-left py-2.5 pr-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">Key</th>
                      <th className="text-left py-2.5 pl-4 text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { key: "F9", action: "Start / stop recording" },
                      { key: "F9 (tap)", action: "Quick record for short input" },
                      { key: "F9 (hold)", action: "Record continuously, stop on release" },
                      { key: "Esc", action: "Cancel current recording" },
                    ].map((row) => (
                      <tr key={row.key} className="border-b border-white/[.03]">
                        <td className="py-2.5 pr-4 text-[#e4f222] font-mono">{row.key}</td>
                        <td className="py-2.5 pl-4 text-[#71717a]">{row.action}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-xs text-[#71717a] mt-3">All hotkeys are customizable in Settings.</p>
            </section>

            <section id="privacy" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Privacy & Security</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <p>Rota AI is built with privacy as a core principle.</p>
                <ul className="space-y-2 pl-5 list-disc">
                  <li><strong className="text-[#fafafa]">Zero telemetry.</strong> The desktop app contains no analytics, no error reporting, no phone-home functionality.</li>
                  <li><strong className="text-[#fafafa]">Encrypted API keys.</strong> Keys are stored using DPAPI on Windows and Keychain on macOS. Encrypted at rest.</li>
                  <li><strong className="text-[#fafafa]">Local storage.</strong> Session history, snippets, and dictionary are stored in a local SQLite database you control.</li>
                  <li><strong className="text-[#fafafa]">You choose the processor.</strong> Voice data goes only to the transcription service you select. Switch to Ollama for fully offline operation.</li>
                  <li><strong className="text-[#fafafa]">Open source.</strong> Every line of code is on GitHub under the MIT license. Anyone can audit it.</li>
                </ul>
                <p>See the <Link href="/privacy" className="text-[#e4f222] hover:underline">Privacy Policy</Link> for complete details.</p>
              </div>
            </section>

            <section id="troubleshooting" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Troubleshooting</h2>
              <div className="space-y-4 text-sm text-[#a1a1aa] leading-relaxed">
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">Nothing happens when I press F9</p>
                  <p className="text-xs">Check that the microphone is connected and not muted. Verify that Rota is running in the system tray. Try restarting the app.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">Transcription is slow or inaccurate</p>
                  <p className="text-xs">Switch to a different backend in Settings. Groq offers the lowest latency. For offline use, try the Small model instead of Large.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">API key not working</p>
                  <p className="text-xs">Double-check the key in Settings. For Groq, ensure you copied the full key from console.groq.com. For Gemini, verify the key is active in Google AI Studio.</p>
                </div>
                <div className="p-4 rounded-sm" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <p className="text-[#fafafa] text-xs font-mono mb-1">Text not appearing in the target app</p>
                  <p className="text-xs">Make sure the target app has focus and the cursor is in a text field. Some applications (like password fields or terminals) may not accept text injection.</p>
                </div>
                <p className="mt-4">Still having issues? <a href="https://github.com/krthik20050/Rota-AI/issues" target="_blank" rel="noopener noreferrer" className="text-[#e4f222] hover:underline">Open a GitHub issue</a> with details about your problem.</p>
              </div>
            </section>

            <section id="faq" className="mb-16 scroll-mt-24">
              <h2 className="text-base font-semibold text-[#fafafa] mb-4 font-mono text-xs uppercase tracking-[0.2em]">Frequently Asked Questions</h2>
              <div className="space-y-0 text-sm text-[#a1a1aa] leading-relaxed">
                {[
                  { q: "Is Rota AI really free forever?", a: "Yes. MIT licensed. No pro plan, no premium tier, no credit card." },
                  { q: "Do I need an account?", a: "No. Rota AI works without any account. Cloud backends need their own free API keys." },
                  { q: "Can I use Rota AI on multiple computers?", a: "Yes. Download and install on each machine. Settings are per-machine by design." },
                  { q: "Does Rota AI work in games?", a: "It can, depending on the game. Fullscreen games may block the overlay. Windowed or borderless mode works best." },
                ].map((item, i) => (
                  <details key={i} className="group border-b border-white/[.06]">
                    <summary className="py-3.5 text-sm font-medium text-[#fafafa] cursor-pointer list-none flex items-center justify-between gap-4 hover:text-[#e4f222] transition-colors">
                      {item.q}
                      <svg className="w-3.5 h-3.5 shrink-0 text-[#71717a] transition-transform group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
                    </summary>
                    <p className="pb-3.5 text-sm text-[#a1a1aa] leading-relaxed">{item.a}</p>
                  </details>
                ))}
              </div>
            </section>
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="py-8 px-6 sm:px-10 md:ml-56 lg:ml-64" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-4 h-4 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}>
              <svg className="w-2 h-2 text-black" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/></svg>
            </div>
            <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa]">Rota AI</span>
          </div>
          <div className="flex flex-wrap justify-center gap-4 text-[10px] uppercase tracking-[0.2em] font-bold text-zinc-600">
            <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
            <Link href="/terms" className="hover:text-white transition-colors">Terms</Link>
            <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
            <a href="https://github.com/krthik20050/Rota-AI" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">GitHub</a>
          </div>
          <p className="text-[10px] uppercase tracking-widest text-[#71717a]">&copy; 2026 Rota AI &middot; MIT License</p>
        </div>
      </footer>
    </div>
  );
}
