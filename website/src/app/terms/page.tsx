export const metadata = {
  title: "Terms — Rota AI",
  description: "MIT License terms for Rota AI.",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#09090b]">
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)", background: "rgba(9,9,11,0.92)", backdropFilter: "blur(16px)" }}>
        <a href="/" className="flex items-center gap-2.5">
          <div className="w-6 h-6 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}><svg className="w-3 h-3 text-black" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/></svg></div>
          <span className="text-sm font-semibold tracking-[0.12em] uppercase text-[#fafafa]">Rota AI</span>
        </a>
        <a href="/" className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors">← Home</a>
      </nav>

      <div className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4" style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}>Terms</h1>
        <p className="text-sm text-[#71717a] mb-12">MIT License</p>

        <div className="space-y-6 text-sm text-[#a1a1aa] leading-relaxed">
          <p>Copyright (c) 2026 Rota AI Contributors</p>
          <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
          <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
          <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>

          <div className="pt-8" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
            <h2 className="text-base font-semibold text-[#fafafa] mb-3">Disclaimer</h2>
            <p>Rota AI is provided as-is. It is one developer working on it in free time. There are no guarantees of support, updates, or bug fixes. Use at your own risk.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
