import React from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getDocContent } from "@/lib/docs";
import { DocsSidebar, DocsMobileMenu } from "@/components/DocsNavigation";
import { ArchitecturalDiagram } from "@/components/ArchitecturalDiagrams";

export const metadata = {
  title: "Docs - Rota AI",
  description: "Rota AI documentation. Installation, quickstart, configuration, and reference.",
};

const SIDEBAR_SECTIONS = [
  {
    title: "Getting Started",
    items: [
      { label: "Installation", href: "#installation", slug: "installation" },
      { label: "Quickstart", href: "#quickstart", slug: "quickstart" },
      { label: "System requirements", href: "#requirements", slug: "requirements" },
    ],
  },
  {
    title: "Configuration",
    items: [
      { label: "Transcription backends", href: "#backends", slug: "backends" },
      { label: "Voice snippets", href: "#snippets", slug: "snippets" },
      { label: "Personal dictionary", href: "#dictionary", slug: "dictionary" },
      { label: "Settings reference", href: "#settings", slug: "settings" },
    ],
  },
  {
    title: "Usage",
    items: [
      { label: "Basic dictation", href: "#basic-dictation", slug: "basic-dictation" },
      { label: "Voice commands", href: "#voice-commands", slug: "voice-commands" },
      { label: "Context awareness", href: "#context", slug: "context" },
      { label: "Offline mode", href: "#offline", slug: "offline" },
    ],
  },
  {
    title: "Platform",
    items: [
      { label: "Windows setup", href: "#windows", slug: "windows" },
      { label: "macOS setup", href: "#macos", slug: "macos" },
      { label: "Linux setup", href: "#linux", slug: "linux" },
    ],
  },
  {
    title: "Architecture",
    items: [
      { label: "System overview", href: "#system-overview", slug: "system-overview" },
      { label: "Audio pipeline", href: "#audio-pipeline", slug: "audio-pipeline" },
      { label: "Threading model", href: "#threading-model", slug: "threading-model" },
      { label: "Platform abstraction", href: "#platform-abstraction", slug: "platform-abstraction" },
      { label: "Security & storage", href: "#security-storage", slug: "security-storage" },
    ],
  },
  {
    title: "Development",
    items: [
      { label: "Getting the code", href: "#getting-code", slug: "getting-code" },
      { label: "Local setup", href: "#local-setup", slug: "local-setup" },
      { label: "Building releases", href: "#building-releases", slug: "building-releases" },
      { label: "Contributing", href: "#contributing", slug: "contributing" },
    ],
  },
  {
    title: "Reference",
    items: [
      { label: "Hotkeys", href: "#hotkeys", slug: "hotkeys" },
      { label: "Privacy & security", href: "#privacy", slug: "privacy" },
      { label: "FAQ", href: "#faq", slug: "faq" },
      { label: "Troubleshooting", href: "#troubleshooting", slug: "troubleshooting" },
    ],
  },
];

const proseClasses =
  "prose prose-invert max-w-none " +
  "prose-headings:text-[#fafafa] prose-headings:font-semibold prose-headings:scroll-mt-24 " +
  "prose-h3:text-[19px] prose-h3:mt-8 prose-h3:mb-4 prose-h3:leading-snug " +
  "prose-h4:text-[15px] prose-h4:mt-6 prose-h4:mb-3 prose-h4:leading-snug " +
  "prose-p:text-[#d4d4d8] prose-p:leading-[1.75] prose-p:mb-5 prose-p:text-[15px] " +
  "prose-strong:text-[#fafafa] prose-strong:font-semibold " +
  "prose-em:text-[#d4d4d8] prose-em:not-italic prose-em:font-semibold " +
  "prose-a:text-[#e5c118] prose-a:font-normal prose-a:underline hover:prose-a:underline " +
  "prose-code:text-[#e5c118] prose-code:font-normal prose-code:bg-zinc-900/80 prose-code:border prose-code:border-white/[0.04] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-sm prose-code:text-[13px] prose-code:font-mono prose-code:before:content-none prose-code:after:content-none " +
  "prose-pre:bg-[#111113] prose-pre:border prose-pre:border-white/[.06] prose-pre:rounded-sm prose-pre:p-4 " +
  "prose-pre:overflow-x-auto " +
  "prose-blockquote:border-l-[#e4f222]/40 prose-blockquote:text-[#a1a1aa] prose-blockquote:pl-5 prose-blockquote:italic " +
  "prose-li:text-[#d4d4d8] prose-li:mb-2 prose-li:text-[14.5px] prose-li:leading-[1.7] " +
  "prose-ul:my-6 prose-ol:my-6 " +
  "prose-hr:border-white/[.06] prose-hr:my-10 " +
  "prose-img:rounded-sm prose-img:my-8 " +
  "prose-table:text-[13px] prose-table:my-8 w-full " +
  "prose-th:text-[#fafafa] prose-th:font-medium prose-th:py-2.5 prose-th:px-4 prose-th:border-b prose-th:border-white/[.08] prose-th:text-left " +
  "prose-td:text-[#d4d4d8] prose-td:py-2.5 prose-td:px-4 prose-td:border-b prose-td:border-white/[.04]";

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
          <Link href="/#download" className="px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 rounded-sm"
            style={{ background: "#e4f222", color: "#000" }}>Download</Link>
        </div>
      </nav>

      <div className="flex pt-14">
        {/* Sidebar */}
        <aside className="w-56 lg:w-64 shrink-0 hidden md:block fixed left-0 top-14 bottom-0 overflow-y-auto px-4 py-8"
          style={{ borderRight: "1px solid rgba(255,255,255,0.06)" }}>
          <DocsSidebar sections={SIDEBAR_SECTIONS} />
        </aside>

        {/* Mobile sidebar toggle */}
        <div className="md:hidden fixed top-14 left-0 right-0 z-40 px-4 py-3"
          style={{ background: "rgba(9,9,11,0.95)", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
          <DocsMobileMenu sections={SIDEBAR_SECTIONS} />
        </div>

        {/* Main content */}
        <main className="flex-1 md:ml-56 lg:ml-64 px-6 sm:px-10 pt-8 md:pt-8 pb-20 max-w-4xl">
          <div className="md:pt-8 md:mt-6">
            <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-12"
              style={{ fontSize: "clamp(32px, 5vw, 52px)", color: "#fafafa" }}>
              Documentation
            </h1>

            {SIDEBAR_SECTIONS.map((section) => (
              <div key={section.title} className="mb-20">
                <h2 className="text-[10px] uppercase tracking-[0.25em] font-bold text-zinc-400 font-mono border-b border-white/[.06] pb-3 mb-12">
                  {section.title}
                </h2>

                <div className="space-y-16">
                  {section.items.map((item) => {
                    const doc = getDocContent(item.slug);
                    if (!doc.content) return null;
                    return (
                      <section
                        key={item.slug}
                        id={item.href.replace("#", "")}
                        className="scroll-mt-24 border-b border-white/[.02] pb-16 last:border-0 last:pb-0"
                      >
                        <h3 className="text-xl font-semibold text-[#fafafa] mb-6 font-mono text-xs uppercase tracking-[0.2em]">
                          {doc.title || item.label}
                        </h3>
                        <div className={proseClasses}>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              pre({ children, ...props }) {
                                const childrenArray = React.Children.toArray(children);
                                const mermaidChild = childrenArray.find(
                                  (child) =>
                                    React.isValidElement(child) &&
                                    (child.props as any).className?.includes("language-mermaid")
                                ) as React.ReactElement<{ className?: string; children?: React.ReactNode }> | undefined;

                                if (mermaidChild) {
                                  return <ArchitecturalDiagram type={String(mermaidChild.props.children || "")} />;
                                }
                                return <pre {...props}>{children}</pre>;
                              },
                              code({ className, children, ...props }) {
                                return (
                                  <code className={className} {...props}>
                                    {children}
                                  </code>
                                );
                              }
                            }}
                          >
                            {doc.content}
                          </ReactMarkdown>
                        </div>
                      </section>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* FAQPage JSON-LD Schema */}
            <script
              type="application/ld+json"
              dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                  "@context": "https://schema.org",
                  "@type": "FAQPage",
                  "mainEntity": [
                    {
                      "@type": "Question",
                      "name": "Is Rota AI really free forever?",
                      "acceptedAnswer": { "@type": "Answer", "text": "Yes. MIT licensed. No pro plan, no premium tier, no credit card." }
                    },
                    {
                      "@type": "Question",
                      "name": "Do I need an account?",
                      "acceptedAnswer": { "@type": "Answer", "text": "No. Rota AI works without any account. Cloud backends need their own free API keys." }
                    },
                    {
                      "@type": "Question",
                      "name": "Can I use Rota AI on multiple computers?",
                      "acceptedAnswer": { "@type": "Answer", "text": "Yes. Download and install on each machine. Settings are per-machine by design." }
                    },
                    {
                      "@type": "Question",
                      "name": "Does Rota AI work in games?",
                      "acceptedAnswer": { "@type": "Answer", "text": "It can, depending on the game. Fullscreen games may block the overlay. Windowed or borderless mode works best." }
                    }
                  ]
                }),
              }}
            />
            {/* BreadcrumbList JSON-LD Schema */}
            <script
              type="application/ld+json"
              dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                  "@context": "https://schema.org",
                  "@type": "BreadcrumbList",
                  "itemListElement": [
                    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://rota.software/" },
                    { "@type": "ListItem", "position": 2, "name": "Docs", "item": "https://rota.software/docs" }
                  ]
                }),
              }}
            />
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
