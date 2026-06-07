import Link from "next/link";

export const metadata = {
  title: "About - Rota AI",
  description: "Learn about Rota AI, a free and open source voice dictation app for Windows, macOS and Linux.",
};

export default function AboutPage() {
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
          About Rota AI
        </h1>
        <p className="text-sm text-[#71717a] mb-12 leading-relaxed">
          Free voice dictation that works in any app. Open source, private, and built by a student
          who needed a tool that actually existed.
        </p>

        <div className="space-y-8 text-sm text-[#a1a1aa] leading-relaxed">
          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">The Story</h2>
            <p className="mb-3">
              Rota AI started the way most useful software does: as a personal need. After trying
              Wispr Flow and loving it, the 14-day free trial ended, and the $15/month subscription
              was not something a student could justify.
            </p>
            <p className="mb-3">
              So the next best option was to build it. Months of reverse engineering, reading
              research papers on Whisper and voice activity detection, and late nights debugging
              Windows text injection later, Rota AI was born.
            </p>
            <p>
              Today, Rota AI is used by developers, writers, students, and accessibility users
              around the world. It is free, open source, and always will be.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">What Makes Rota AI Different</h2>
            <ul className="space-y-3 pl-5 list-disc">
              <li><strong className="text-[#fafafa]">Privacy first:</strong> Zero telemetry. No analytics in the desktop app. Your voice data stays on your machine when using local models.</li>
              <li><strong className="text-[#fafafa]">Truly free:</strong> MIT licensed. No pro plan, no premium tier, no credit card. Bring your own API keys or go fully offline.</li>
              <li><strong className="text-[#fafafa]">Context-aware:</strong> Rota detects what app you are typing in and adapts tone, punctuation, and formatting automatically. Formal in email, casual in chat, technical in code.</li>
              <li><strong className="text-[#fafafa]">Works anywhere:</strong> Any app with a text field. Gmail, Slack, VS Code, Notion, Discord, your terminal. If you can type in it, Rota works in it.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">The Technology</h2>
            <p className="mb-3">
              Rota AI is built with Python and PySide6 on the desktop, powered by OpenAI Whisper
              for transcription (via Groq, Gemini, or local Ollama), Silero VAD for voice activity
              detection, and an LLM-based cleanup pass for natural, polished output.
            </p>
            <p className="mb-3">
              The architecture is a 7-stage pipeline running on dedicated threads (audio capture,
              voice activity detection, transcription, AI cleanup, context detection, text injection,
              and persistence), ensuring the UI never freezes during processing.
            </p>
            <p>
              API keys are encrypted at rest using platform-native encryption (DPAPI on Windows,
              Keychain on macOS). Session history is stored in a local SQLite database that you
              can clear at any time.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">Open Source</h2>
            <p className="mb-3">
              Every line of Rota AI is available on GitHub under the MIT license. You can audit the
              code, contribute improvements, fork it for your own projects, or just verify that
              it does exactly what it claims to do and nothing more.
            </p>
            <p>
              The project is built in the open. Issues, discussions, and pull requests are welcome.
              No corporate walled garden. No hidden agenda. Just a tool that should exist.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">Contact</h2>
            <p>
              Have questions, suggestions, or want to contribute? Reach out via{" "}
              <a href="https://github.com/krthik20050/Rota-AI" target="_blank" rel="noopener noreferrer" className="text-[#e4f222] hover:underline">GitHub</a>{" "}
              or email{" "}
              <a href="mailto:tl24btcs@gmail.com" className="text-[#e4f222] hover:underline">tl24btcs@gmail.com</a>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
