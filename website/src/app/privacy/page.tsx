import Link from "next/link";

export const metadata = {
  title: "Privacy - Rota AI",
  description: "Rota AI is designed to minimize data collection. Your voice recordings stay on your machine. Learn about our privacy practices.",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", background: "rgba(9,9,11,0.92)", backdropFilter: "blur(16px)" }}>
        <Link href="/" className="flex items-center">
          <img src="/logo.svg" alt="Rota AI" className="h-8 w-auto" />
        </Link>
        <Link href="/" className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors">← Home</Link>
      </nav>

      <div className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4" style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}>Privacy Policy</h1>
        <p className="text-sm text-[#71717a] mb-4">Last updated: June 7, 2026</p>
        <p className="text-sm text-[#71717a] mb-12 leading-relaxed">
          This Privacy Policy describes how Rota AI (&quot;we&quot;, &quot;our&quot;, or &quot;the app&quot;) handles your information when you use our voice dictation software. Rota AI is built with a privacy-first architecture. This policy complies with the Digital Personal Data Protection Act, 2023 (DPDP Act) of India.
        </p>

        <div className="space-y-8 text-sm text-[#a1a1aa] leading-relaxed">

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">1. Information We Collect</h2>
            <p className="mb-3">Rota AI is designed to minimize data collection. Here is what we process:</p>
            <ul className="space-y-2 pl-5 list-disc">
              <li><strong className="text-[#fafafa]">Voice recordings:</strong> Captured momentarily when you press the hotkey. These are sent to the transcription service you choose (Groq, Gemini, or local Ollama). We do not store or transmit your voice data to any server we control.</li>
              <li><strong className="text-[#fafafa]">Transcription text:</strong> The transcribed text is stored locally on your machine for session history and analytics. You can clear this at any time.</li>
              <li><strong className="text-[#fafafa]">API keys:</strong> If you choose cloud transcription (Groq or Gemini), your API key is stored locally using DPAPI encryption on Windows or system keychain on macOS. It is never transmitted except to your chosen API provider.</li>
              <li><strong className="text-[#fafafa]">Usage analytics:</strong> The desktop app itself contains no telemetry, no analytics, and no phone-home functionality.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">2. How We Use Your Information</h2>
            <p>Your information is used only for the purpose you intend:</p>
            <ul className="space-y-2 pl-5 list-disc mt-2">
              <li>Voice recordings are transcribed into text</li>
              <li>Transcribed text is optionally cleaned by an AI model you select</li>
              <li>The resulting text is inserted into the application you are using</li>
              <li>Session history is stored locally so you can review past transcriptions</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">3. Data Storage and Retention</h2>
            <p className="mb-3">All data is stored locally on your machine:</p>
            <ul className="space-y-2 pl-5 list-disc">
              <li><strong className="text-[#fafafa]">Session history:</strong> Stored in a local SQLite database. Retained for the duration you specify in settings (default: 2 days). You can delete all history at any time from the app settings.</li>
              <li><strong className="text-[#fafafa]">Personal dictionary:</strong> Stored locally. Persists until you delete it.</li>
              <li><strong className="text-[#fafafa]">API keys:</strong> Encrypted and stored locally. You can remove them at any time.</li>
              <li><strong className="text-[#fafafa]">Configuration:</strong> Stored locally in encrypted or plain-text config files.</li>
            </ul>
            <p className="mt-3">We do not retain any of your data on any server we operate. When you use third-party APIs (Groq, Gemini), their retention policies apply to the data you send them.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">4. Third-Party Data Processors</h2>
            <p className="mb-3">If you choose cloud transcription, your voice recordings are processed by:</p>
            <ul className="space-y-2 pl-5 list-disc">
              <li><strong className="text-[#fafafa]">Groq Inc.</strong>: Whisper transcription API. Voice data sent to Groq&apos;s servers for processing. See <a href="https://groq.com/privacy" className="text-[#e4f222] hover:underline">Groq&apos;s Privacy Policy</a>.</li>
              <li><strong className="text-[#fafafa]">Google (Gemini API)</strong>: Gemini transcription and AI cleanup. Voice data sent to Google&apos;s servers. See <a href="https://policies.google.com/privacy" className="text-[#e4f222] hover:underline">Google&apos;s Privacy Policy</a>.</li>
              <li><strong className="text-[#fafafa]">Ollama (local)</strong>: When using local transcription, no data leaves your machine. No third-party processing.</li>
            </ul>
            <p className="mt-3">You choose which processor to use. You can switch at any time. You can use Rota AI entirely offline with Ollama, eliminating all third-party data processing.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">5. Consent and Withdrawal</h2>
            <p className="mb-3">Your use of Rota AI with cloud transcription constitutes consent to process your voice data through your chosen provider. You have the right to:</p>
            <ul className="space-y-2 pl-5 list-disc">
              <li><strong className="text-[#fafafa]">Withdraw consent at any time</strong> by switching to offline mode (Ollama) in settings, or by uninstalling the app.</li>
              <li><strong className="text-[#fafafa]">Delete your data</strong> by clearing session history and personal dictionary in the app settings.</li>
              <li><strong className="text-[#fafafa]">Request information</strong> about what data we process by contacting us.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">6. Your Rights Under DPDP Act (India)</h2>
            <p className="mb-3">If you are in India, the Digital Personal Data Protection Act, 2023 provides you with the following rights:</p>
            <ul className="space-y-2 pl-5 list-disc">
              <li><strong className="text-[#fafafa]">Right to access:</strong> Request a summary of your personal data processed.</li>
              <li><strong className="text-[#fafafa]">Right to correction:</strong> Have inaccurate personal data corrected.</li>
              <li><strong className="text-[#fafafa]">Right to erasure:</strong> Request deletion of your personal data.</li>
              <li><strong className="text-[#fafafa]">Right to grievance redressal:</strong> File a complaint with our Grievance Officer (see Section 9).</li>
              <li><strong className="text-[#fafafa]">Right to nominate:</strong> Nominate a person to exercise your rights in case of death or incapacity.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">7. No Telemetry</h2>
            <p>Rota AI has zero telemetry. There is no analytics, no error reporting, no usage tracking, no phone-home of any kind within the desktop application. We do not know how many people use Rota AI, what features they use, or how often they use it. This is a deliberate design choice.</p>
            <p className="mt-3">The website (rota.software) uses privacy-respecting analytics (Umami) for basic page view tracking. No personal data is collected.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">8. Open Source and Auditability</h2>
            <p>Rota AI is MIT licensed. The complete source code is available at <a href="https://github.com/krthik20050/Rota-AI" target="_blank" rel="noopener noreferrer" className="text-[#e4f222] hover:underline">github.com/krthik20050/Rota-AI</a>. Anyone can audit the code to verify exactly what it does with your data. The answer: nothing except what you explicitly configure.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">9. Grievance Officer</h2>
            <p className="mb-3">Under the Digital Personal Data Protection Act, 2023, we have appointed a Grievance Officer to address any concerns regarding your personal data:</p>
            <div className="p-4 rounded-sm mt-2" style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.06)" }}>
              <p className="text-[#fafafa]"><strong>Grievance Officer:</strong> Karthik Krishnan</p>
              <p className="text-[#fafafa]"><strong>Email:</strong> <a href="mailto:tl24btcs@gmail.com" className="text-[#e4f222] hover:underline">tl24btcs@gmail.com</a></p>
              <p className="text-[#fafafa]"><strong>Response time:</strong> We aim to respond within 48 hours</p>
            </div>
            <p className="mt-4">You may contact the Grievance Officer to:</p>
            <ul className="space-y-2 pl-5 list-disc mt-2">
              <li>File a complaint regarding processing of your personal data</li>
              <li>Request access to, correction of, or erasure of your data</li>
              <li>Withdraw consent for data processing</li>
              <li>Ask any questions about this Privacy Policy</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">10. Changes to This Policy</h2>
            <p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated &ldquo;Last updated&rdquo; date. Material changes will be notified through the app or on our website.</p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">11. Contact</h2>
            <p>Questions, concerns, or data requests? Open an issue on <a href="https://github.com/krthik20050/Rota-AI/issues" target="_blank" rel="noopener noreferrer" className="text-[#e4f222] hover:underline">GitHub</a> or email our Grievance Officer at <a href="mailto:tl24btcs@gmail.com" className="text-[#e4f222] hover:underline">tl24btcs@gmail.com</a>.</p>
          </section>

        </div>
      </div>
    </div>
  );
}
