"use client";

import * as React from "react";
import { WordsPreloader } from "./WordsPreloader";
import { motion, useInView, useScroll, useMotionValueEvent } from "framer-motion";
import {
  Mic, Zap, Send, Sparkles, Globe, Command, MessageSquare,
  Code2, FileText, CheckCircle2, ArrowRight, Download,
  ChevronDown, ExternalLink, GitBranch,
} from "lucide-react";

/* ─── Waveform ─────────────────────────────────────────────────────────────── */

function genWave(n: number, seed = 17): number[] {
  const out: number[] = [];
  let v = seed >>> 0;
  for (let i = 0; i < n; i++) {
    v = (v * 1664525 + 1013904223) >>> 0;
    const r = v / 0xffffffff;
    const env = Math.sin((i / n) * Math.PI);
    out.push(Math.round(3 + r * 38 * 0.6 + env * 38 * 0.4));
  }
  return out;
}

const WAVE = genWave(140);

/* ─── Recording Pill Demo ──────────────────────────────────────────────────── */

function RecordingPillDemo() {
  const [active, setActive] = React.useState(false);
  const [bars, setBars] = React.useState<number[]>(Array(24).fill(4));
  const iRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  React.useEffect(() => {
    const cycle = setInterval(() => {
      setActive((prev) => {
        if (!prev) {
          iRef.current = setInterval(() => {
            setBars(Array(24).fill(0).map(() => Math.round(4 + Math.random() * 52)));
          }, 80);
          return true;
        }
        if (iRef.current) clearInterval(iRef.current);
        setBars(Array(24).fill(4));
        return false;
      });
    }, 4000);
    return () => {
      clearInterval(cycle);
      if (iRef.current) clearInterval(iRef.current);
    };
  }, []);

  const toggle = () => {
    if (active) {
      if (iRef.current) clearInterval(iRef.current);
      setBars(Array(24).fill(4));
      setActive(false);
    } else {
      iRef.current = setInterval(() => {
        setBars(Array(24).fill(0).map(() => Math.round(4 + Math.random() * 52)));
      }, 80);
      setActive(true);
    }
  };

  return (
    <div
      onClick={toggle}
      className="flex items-center gap-4 px-6 py-4 select-none cursor-pointer transition-all duration-300"
      style={{
        background: "rgba(12,12,14,0.9)",
        backdropFilter: "blur(12px)",
        border: `1px solid ${active ? "rgba(228,242,34,0.3)" : "rgba(255,255,255,0.06)"}`,
        borderRadius: 2,
        boxShadow: active
          ? "0 0 28px rgba(228,242,34,0.08), 0 8px 32px rgba(0,0,0,0.8)"
          : "0 8px 32px rgba(0,0,0,0.7)",
        width: "min(420px, 90vw)",
      }}
    >
      <div
        className="flex items-center justify-center w-9 h-9 shrink-0 transition-colors duration-300"
        style={{
          background: active ? "rgba(228,242,34,0.1)" : "rgba(255,255,255,0.03)",
          borderRadius: 2,
        }}
      >
        <Mic
          className="w-4 h-4 transition-colors duration-300"
          style={{ color: active ? "#e4f222" : "#50545a" }}
        />
      </div>

      <div className="flex items-center gap-[3px] flex-1 h-14">
        {bars.map((h, i) => (
          <div
            key={i}
            style={{
              width: 3,
              height: h,
              borderRadius: 1,
              flexShrink: 0,
              background: active ? "#e4f222" : "#262830",
              transition: active ? "height 0.08s ease-out" : "height 0.4s ease-out, background 0.3s",
            }}
          />
        ))}
      </div>

      <div className="shrink-0 flex items-center gap-2">
        <div
          className="w-2 h-2 rounded-full transition-colors duration-300"
          style={{
            background: active ? "#e4f222" : "#262830",
            boxShadow: active ? "0 0 6px #e4f222" : "none",
            animation: active ? "dot-pulse 1.2s ease-in-out infinite" : "none",
          }}
        />
        <span
          className="text-xs uppercase tracking-widest transition-colors duration-300"
          style={{ color: active ? "#e4f222" : "#50545a" }}
        >
          {active ? "rec" : "F9"}
        </span>
      </div>
      <style>{`@keyframes dot-pulse{0%,100%{opacity:1}50%{opacity:.35}}`}</style>
    </div>
  );
}

/* ─── Fade In ──────────────────────────────────────────────────────────────── */

function FadeIn({
  children,
  delay = 0,
  className = "",
  y = 20,
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
  y?: number;
}) {
  const ref = React.useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      {children}
    </motion.div>
  );
}

/* ─── Section Label ─────────────────────────────────────────────────────────── */

function SectionLabel({ n, title }: { n: string; title: string }) {
  return (
    <div className="flex items-center gap-4 mb-14">
      <span className="text-xs tracking-[0.25em] uppercase text-[#e4f222] font-mono">
        §{n}
      </span>
      <div className="flex-1 h-px bg-white/[.06]" />
      <span className="text-xs tracking-[0.25em] uppercase text-[#50545a] font-mono">
        {title}
      </span>
    </div>
  );
}

/* ─── Data ──────────────────────────────────────────────────────────────────── */

const HOW_STEPS = [
  {
    num: "01",
    icon: Command,
    title: "Press F9",
    desc: "A floating recording pill appears. Start speaking — no setup, no switching apps.",
  },
  {
    num: "02",
    icon: Mic,
    title: "Speak naturally",
    desc: "Say exactly what you want to type. Rota listens, transcribes, and cleans in real time.",
  },
  {
    num: "03",
    icon: Send,
    title: "Text injected",
    desc: "Release F9. Polished text appears where your cursor is — Gmail, Slack, VS Code, anywhere.",
  },
];

const FEATURES = [
  {
    icon: Sparkles,
    title: "AI-powered cleanup",
    desc: "Context-aware AI removes fillers, fixes punctuation, and matches your writing style for each app.",
    large: true,
  },
  {
    icon: Zap,
    title: "Sub-second latency",
    desc: "Groq Whisper + smart caching. Text appears in under a second.",
    large: false,
  },
  {
    icon: Globe,
    title: "Works everywhere",
    desc: "Gmail, Slack, Discord, VS Code, Notion — any text field, any app.",
    large: false,
  },
  {
    icon: MessageSquare,
    title: "Voice commands",
    desc: '"Scratch that", "Change X to Y" — voice-native editing.',
    large: false,
  },
  {
    icon: FileText,
    title: "Context-aware tone",
    desc: "Knows if you're in email, chat, or code. Adapts automatically.",
    large: false,
  },
  {
    icon: Code2,
    title: "Personal dictionary",
    desc: "Learns your vocabulary and technical terms over time.",
    large: false,
  },
];

const APPS = [
  "Gmail", "Slack", "VS Code", "Notion", "Discord",
  "Obsidian", "Chrome", "Cursor", "Telegram", "Figma",
];

const WITHOUT = [
  "Typing slowly, interrupting your flow",
  "Copy/paste between dictation tools",
  "Raw transcripts full of fillers",
  "Wrong tone for the app you're in",
  "Losing your train of thought",
];

const WITH = [
  "Speak at 150+ words per minute",
  "Text appears right where you type",
  "AI-polished prose, every time",
  "Context-aware tone per app",
  "Stay in flow, speak your thoughts",
];

const COMPARE_ROWS = [
  { feature: "Price", wispr: "$15/mo", superwhisper: "$8.49/mo", rota: "Free", rotaBold: true },
  { feature: "Open source", wispr: "No", superwhisper: "No", rota: "Yes, MIT", rotaBold: true },
  { feature: "Offline mode", wispr: "No", superwhisper: "Yes", rota: "Yes", rotaBold: true },
  { feature: "Account required", wispr: "Yes", superwhisper: "Yes", rota: "No", rotaBold: true },
  { feature: "AI cleanup", wispr: "Yes", superwhisper: "Yes, multiple modes", rota: "Yes", rotaBold: true },
  { feature: "Context awareness", wispr: "Yes", superwhisper: "Reads screen", rota: "Detects app", rotaBold: true },
  { feature: "Encrypted key storage", wispr: "Not disclosed", superwhisper: "Not disclosed", rota: "OS keychain", rotaBold: true },
  { feature: "Telemetry", wispr: "Cloud based", superwhisper: "Not fully disclosed", rota: "None", rotaBold: true },
  { feature: "File transcription", wispr: "No", superwhisper: "Audio + video", rota: "Not yet", rotaBold: false },
  { feature: "Cross-device sync", wispr: "Yes", superwhisper: "Yes", rota: "Not yet", rotaBold: false },
  { feature: "Mac / Linux / iOS", wispr: "All", superwhisper: "Mac, Win, iOS", rota: "Windows & Linux", rotaBold: true },
];

const FAQ_ITEMS = [
  {
    q: "Is this really free?",
    a: "Yes. MIT licensed open source. Groq and Gemini both have free tiers that are enough for daily use. Ollama is completely free with no limits. There is no pro plan, no premium tier, no credit card needed.",
  },
  {
    q: "How does the download work?",
    a: "On Windows: download the installer and run it. On Linux: download the AppImage, mark it executable (chmod +x RotaAI.AppImage), and run it directly — no install needed. First launch walks you through picking your transcription backend.",
  },
  {
    q: "Can I use it without internet?",
    a: "Yes. Install Ollama, download a Whisper model (small is 480MB), and Rota works 100% offline. No API keys, no accounts, no internet. Your voice data never leaves your machine.",
  },
  {
    q: "What about Mac or Linux?",
    a: "Linux is now supported — download the AppImage and run it directly, no install needed. macOS is still on the roadmap.",
  },
  {
    q: "What are the system requirements?",
    a: "Windows 10/11 or Linux (Ubuntu 20.04+, Fedora 36+, Arch). 4GB RAM minimum, 8GB recommended. For local GPU transcription: NVIDIA GPU with 4GB+ VRAM. CPU-only works on any modern quad core.",
  },
];

/* ─── Nav ───────────────────────────────────────────────────────────────────── */

function Nav() {
  const [scrolled, setScrolled] = React.useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setScrolled(latest > 40);
  });

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14 transition-colors duration-200"
      style={{
        borderBottom: `1px solid ${scrolled ? "rgba(255,255,255,0.06)" : "transparent"}`,
        background: scrolled ? "rgba(9,9,11,0.92)" : "transparent",
        backdropFilter: scrolled ? "blur(16px)" : "none",
      }}
    >
      <a href="/" className="flex items-center gap-2.5">
        <div
          className="w-6 h-6 flex items-center justify-center"
          style={{ background: "#e4f222", borderRadius: 2 }}
        >
          <Mic className="w-3 h-3 text-black" />
        </div>
        <span className="text-sm font-semibold tracking-[0.12em] uppercase text-[#fafafa]">
          Rota AI
        </span>
      </a>

      <div className="hidden sm:flex items-center gap-8 text-xs tracking-[0.18em] uppercase text-[#71717a]">
        <a href="#how-it-works" className="hover:text-[#fafafa] transition-colors">How it works</a>
        <a href="#features" className="hover:text-[#fafafa] transition-colors">Features</a>
        <a href="#comparison" className="hover:text-[#fafafa] transition-colors">Compare</a>
        <a href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</a>
        <a href="#download" className="hover:text-[#fafafa] transition-colors">Download</a>
      </div>

      <a
        href="https://github.com/krthik20050/Rota-AI"
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 active:scale-95"
        style={{ background: "#e4f222", color: "#000", borderRadius: 2 }}
      >
        <Download className="w-3 h-3" />
        Download
      </a>
    </nav>
  );
}

/* ─── LandingPage ───────────────────────────────────────────────────────────── */

export function LandingPage() {
  const [preloaderDone, setPreloaderDone] = React.useState(false);

  return (
    <>
      {!preloaderDone && (
        <WordsPreloader onComplete={() => setPreloaderDone(true)} />
      )}
    <div className="min-h-screen bg-[#09090b]">
      <Nav />

      {/* ── Hero ── */}
      <section
        className="relative flex flex-col items-center justify-center text-center overflow-hidden"
        style={{ paddingTop: 112, paddingBottom: 0, minHeight: "92vh" }}
      >
        {/* Scanline overlay */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage:
              "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.035) 3px,rgba(0,0,0,0.035) 4px)",
            zIndex: 1,
          }}
        />
        {/* Radial glow */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 pointer-events-none"
          style={{
            width: 900,
            height: 600,
            background:
              "radial-gradient(ellipse at center top, rgba(228,242,34,0.045) 0%, transparent 60%)",
            zIndex: 0,
          }}
        />

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="relative z-10 inline-flex items-center gap-2 px-4 py-1.5 mb-8 border text-xs tracking-[0.2em] uppercase"
          style={{
            borderColor: "rgba(228,242,34,0.18)",
            background: "rgba(228,242,34,0.04)",
            color: "#e4f222",
            borderRadius: 2,
          }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#e4f222] animate-pulse" />
          Now available — Windows &amp; Linux
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.08 }}
          className="relative z-10 font-display uppercase leading-[0.92] tracking-[0.02em] px-4"
          style={{ fontSize: "clamp(68px, 12.5vw, 176px)", color: "#fafafa" }}
        >
          Type at the
          <br />
          <span style={{ color: "#e4f222" }}>speed of speech.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative z-10 mt-7 max-w-md text-sm leading-relaxed text-[#a1a1aa]"
        >
          Voice dictation that actually works. AI-cleaned, context-aware text
          injected directly into any app — with a single keypress.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="relative z-10 mt-10 flex flex-col sm:flex-row items-center gap-3"
        >
          <a
            href="/api/download?platform=windows"
            className="group flex items-center gap-2.5 px-7 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
            style={{
              background: "#e4f222",
              color: "#000",
              borderRadius: 2,
              boxShadow: "0 4px 20px rgba(228,242,34,0.2)",
            }}
          >
            Download for Windows
            <Download className="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform" />
          </a>
          <a
            href="/api/download?platform=linux"
            className="group flex items-center gap-2.5 px-7 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
            style={{
              background: "transparent",
              color: "#e4f222",
              borderRadius: 2,
              border: "1px solid rgba(228,242,34,0.3)",
            }}
          >
            Download for Linux
            <Download className="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform" />
          </a>
          <a
            href="#how-it-works"
            className="flex items-center gap-2 px-6 py-3 text-xs uppercase tracking-[0.15em] border transition-all hover:border-white/15"
            style={{ borderColor: "rgba(255,255,255,0.08)", color: "#71717a", borderRadius: 2 }}
          >
            See how it works
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.45 }}
          className="relative z-10 mt-14 flex flex-col items-center gap-3"
        >
          <p className="text-xs uppercase tracking-[0.25em] text-[#71717a]">Click to demo</p>
          <RecordingPillDemo />
        </motion.div>

        {/* Full-width waveform */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.7 }}
          className="relative z-10 w-full mt-14 flex items-end justify-between px-2"
          style={{ height: 64 }}
        >
          {WAVE.map((h, i) => (
            <div
              key={i}
              style={{
                width: 2,
                height: h,
                borderRadius: "1px 1px 0 0",
                flexShrink: 0,
                background: `rgba(228,242,34,${0.05 + (h / 41) * 0.18})`,
              }}
            />
          ))}
        </motion.div>
      </section>

      {/* ── How it works ── */}
      <section
        id="how-it-works"
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <SectionLabel n="01" title="How it works" />
          </FadeIn>
          <FadeIn className="mb-14">
            <h2
              className="font-display uppercase leading-[0.92] tracking-[0.02em]"
              style={{ fontSize: "clamp(52px, 7.5vw, 112px)", color: "#fafafa" }}
            >
              Three steps.
              <br />
              <span style={{ color: "#e4f222" }}>Zero friction.</span>
            </h2>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/[.04]">
            {HOW_STEPS.map((step, i) => (
              <FadeIn key={step.num} delay={i * 0.1}>
                <div className="relative p-8 h-full bg-[#09090b]">
                  <div
                    className="absolute top-6 right-6 font-display uppercase leading-none select-none"
                    style={{
                      fontSize: 96,
                      color: "#e4f222",
                      opacity: 0.055,
                      letterSpacing: "0.02em",
                    }}
                  >
                    {step.num}
                  </div>
                  <div
                    className="inline-flex items-center justify-center w-10 h-10 mb-6"
                    style={{ background: "rgba(228,242,34,0.06)", borderRadius: 2 }}
                  >
                    <step.icon className="w-5 h-5" style={{ color: "#e4f222" }} />
                  </div>
                  <h3 className="text-base font-semibold mb-3 text-[#fafafa]">{step.title}</h3>
                  <p className="text-sm leading-relaxed text-[#a1a1aa]">{step.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── Compatible apps ── */}
      <section
        className="py-14 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <p className="text-xs uppercase tracking-[0.22em] mb-5 text-[#71717a] font-mono">
              Works natively in every app you already use
            </p>
            <div className="flex flex-wrap items-center gap-2">
              {APPS.map((app) => (
                <div
                  key={app}
                  className="px-4 py-2 text-xs uppercase tracking-widest border border-white/[.06] bg-[#111113] text-[#a1a1aa] rounded-sm"
                >
                  {app}
                </div>
              ))}
              <div
                className="px-4 py-2 text-xs uppercase tracking-widest border rounded-sm"
                style={{
                  borderColor: "rgba(228,242,34,0.18)",
                  background: "rgba(228,242,34,0.04)",
                  color: "#e4f222",
                }}
              >
                + any text field
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Features ── */}
      <section
        id="features"
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <SectionLabel n="02" title="Features" />
          </FadeIn>
          <FadeIn className="mb-14">
            <h2
              className="font-display uppercase leading-[0.92] tracking-[0.02em]"
              style={{ fontSize: "clamp(52px, 7.5vw, 112px)", color: "#fafafa" }}
            >
              Built for how you
              <br />
              <span style={{ color: "#e4f222" }}>actually think.</span>
            </h2>
          </FadeIn>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-white/[.04]">
            {FEATURES.map((feat, i) => (
              <FadeIn
                key={feat.title}
                delay={i * 0.06}
                className={feat.large ? "sm:col-span-2 lg:col-span-2" : ""}
              >
                <div className="p-7 h-full bg-[#09090b]">
                  <div
                    className="inline-flex items-center justify-center w-10 h-10 mb-5"
                    style={{ background: "rgba(228,242,34,0.05)", borderRadius: 2 }}
                  >
                    <feat.icon className="w-5 h-5" style={{ color: "#e4f222" }} />
                  </div>
                  <h3 className="text-base font-semibold mb-2.5 text-[#fafafa]">{feat.title}</h3>
                  <p className="text-sm leading-relaxed text-[#a1a1aa]">{feat.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── Comparison ── */}
      <section
        id="comparison"
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <SectionLabel n="03" title="The difference" />
          </FadeIn>
          <FadeIn>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/[.04]">
              <div className="p-10 bg-[#09090b]">
                <p className="text-xs uppercase tracking-[0.22em] mb-8 text-[#71717a] font-mono">
                  Without Rota AI
                </p>
                <ul className="space-y-5">
                  {WITHOUT.map((item) => (
                    <li
                      key={item}
                      className="flex items-start gap-4 text-sm text-[#71717a]"
                    >
                      <span className="mt-0.5 shrink-0 text-[#3a3a40]">—</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-10 bg-[#111113]">
                <p className="text-xs uppercase tracking-[0.22em] mb-8 text-[#e4f222] font-mono">
                  With Rota AI
                </p>
                <ul className="space-y-5">
                  {WITH.map((item) => (
                    <li
                      key={item}
                      className="flex items-start gap-4 text-sm text-[#fafafa]"
                    >
                      <CheckCircle2
                        className="w-4 h-4 mt-0.5 shrink-0"
                        style={{ color: "#e4f222" }}
                      />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Comparison Table ── */}
      <section
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <SectionLabel n="04" title="Compare" />
          </FadeIn>
          <FadeIn>
            <p className="text-sm text-[#a1a1aa] max-w-lg mb-10">
              Honest comparison. I would rather tell you the truth than make claims I cannot back up.
            </p>
          </FadeIn>
          <FadeIn delay={0.1}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse" style={{ minWidth: 640 }}>
                <thead>
                  <tr>
                    <th className="text-left py-3 px-5 text-xs uppercase tracking-[0.15em] text-[#71717a] font-mono font-normal border-b border-white/[.06]" />
                    <th className="text-left py-3 px-5 text-xs uppercase tracking-[0.15em] text-[#71717a] font-mono font-normal border-b border-white/[.06]">
                      Wispr Flow
                    </th>
                    <th className="text-left py-3 px-5 text-xs uppercase tracking-[0.15em] text-[#71717a] font-mono font-normal border-b border-white/[.06]">
                      SuperWhisper
                    </th>
                    <th
                      className="text-left py-3 px-5 text-xs uppercase tracking-[0.15em] font-mono font-normal border-b"
                      style={{ color: "#e4f222", borderColor: "rgba(228,242,34,0.15)" }}
                    >
                      Rota AI
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARE_ROWS.map((row, i) => (
                    <tr
                      key={row.feature}
                      className="transition-colors hover:bg-white/[.015]"
                    >
                      <td className="py-3.5 px-5 text-[#a1a1aa] border-b border-white/[.04] font-mono text-xs">
                        {row.feature}
                      </td>
                      <td className="py-3.5 px-5 text-[#a1a1aa] border-b border-white/[.04]">
                        {row.wispr}
                      </td>
                      <td className="py-3.5 px-5 text-[#a1a1aa] border-b border-white/[.04]">
                        {row.superwhisper}
                      </td>
                      <td
                        className="py-3.5 px-5 border-b"
                        style={{
                          color: row.rotaBold ? "#fafafa" : "#a1a1aa",
                          fontWeight: row.rotaBold ? 500 : 400,
                          background: "rgba(228,242,34,0.02)",
                          borderColor: "rgba(255,255,255,0.04)",
                        }}
                      >
                        {row.rota}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div
              className="mt-8 p-6 rounded-sm"
              style={{
                background: "#111113",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              <p className="text-sm text-[#a1a1aa] leading-relaxed">
                <strong className="text-[#fafafa] font-medium">The honest version:</strong>{" "}
                Wispr Flow is a polished product with cross-device sync, mobile apps, and Mac support.
                It has a full team and funding. SuperWhisper has more AI modes and file transcription.
                Rota is free, open source, and private. It is one developer working on it in free time.
                I am closing the gaps.
              </p>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-3xl mx-auto">
          <FadeIn>
            <SectionLabel n="05" title="Questions" />
          </FadeIn>
          <div className="mt-8">
            {FAQ_ITEMS.map((item, i) => (
              <FAQItem key={i} question={item.q} answer={item.a} />
            ))}
          </div>
        </div>
      </section>

      {/* ── Download ── */}
      <section
        id="download"
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <SectionLabel n="06" title="Download" />
          </FadeIn>
          <FadeIn className="mb-12">
            <h2
              className="font-display uppercase leading-[0.92] tracking-[0.02em]"
              style={{ fontSize: "clamp(52px, 7.5vw, 112px)", color: "#fafafa" }}
            >
              Download &amp;
              <br />
              <span style={{ color: "#e4f222" }}>start speaking.</span>
            </h2>
          </FadeIn>
          <FadeIn delay={0.1}>
            <p className="text-sm mb-10 max-w-md text-[#a1a1aa]">
              Windows &amp; Linux · Free &amp; open source · No account needed
            </p>
            <div className="flex flex-col sm:flex-row items-start gap-4">
              <a
                href="/api/download?platform=windows"
                className="group inline-flex items-center gap-3 px-8 py-4 text-sm font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
                style={{
                  background: "#e4f222",
                  color: "#000",
                  borderRadius: 2,
                  boxShadow: "0 4px 24px rgba(228,242,34,0.25)",
                }}
              >
                <Download className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
                Download for Windows
              </a>
              <a
                href="/api/download?platform=linux"
                className="group inline-flex items-center gap-3 px-8 py-4 text-sm font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
                style={{
                  background: "transparent",
                  color: "#e4f222",
                  borderRadius: 2,
                  border: "1px solid rgba(228,242,34,0.3)",
                  boxShadow: "0 4px 24px rgba(228,242,34,0.08)",
                }}
              >
                <Download className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
                Download for Linux
              </a>
              <a
                href="https://github.com/krthik20050/Rota-AI"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-4 text-xs uppercase tracking-[0.15em] border transition-all hover:border-white/15"
                style={{
                  borderColor: "rgba(255,255,255,0.08)",
                  color: "#71717a",
                  borderRadius: 2,
                }}
              >
                View on GitHub <ArrowRight className="w-3 h-3" />
              </a>
            </div>
            <div
              className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-px bg-white/[.04]"
              style={{ maxWidth: 640 }}
            >
              {[
                { step: "1", label: "Download & run", desc: "Windows: run the installer. Linux: download the AppImage, chmod +x, and run." },
                { step: "2", label: "Add your API key", desc: "Enter your Groq or Gemini key when prompted. Or use Ollama for fully local." },
                { step: "3", label: "Press F9 to speak", desc: "That is it. Dictate into any app, anywhere." },
              ].map(({ step, label, desc }) => (
                <div key={step} className="p-6 bg-[#09090b]">
                  <div className="text-xs uppercase tracking-widest mb-2 text-[#e4f222] font-mono">
                    Step {step}
                  </div>
                  <div className="text-sm font-semibold mb-1 text-[#fafafa]">{label}</div>
                  <div className="text-xs text-[#a1a1aa]">{desc}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer
        className="py-8 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div
              className="w-5 h-5 flex items-center justify-center"
              style={{ background: "#e4f222", borderRadius: 2 }}
            >
              <Mic className="w-2.5 h-2.5 text-black" />
            </div>
            <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa]">
              Rota AI
            </span>
          </div>
          <p className="text-xs uppercase tracking-widest text-[#71717a]">
            © 2026 Rota AI · MIT License
          </p>
          <div className="flex items-center gap-6 text-xs uppercase tracking-widest text-[#71717a]">
            <a
              href="https://github.com/krthik20050/Rota-AI"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#a1a1aa] transition-colors flex items-center gap-1"
            >
              GitHub <ExternalLink className="w-2.5 h-2.5" />
            </a>
            <a href="#how-it-works" className="hover:text-[#a1a1aa] transition-colors">
              How it works
            </a>
            <a href="/blog" className="hover:text-[#a1a1aa] transition-colors">
              Blog
            </a>
            <a href="#download" className="hover:text-[#a1a1aa] transition-colors">
              Download
            </a>
          </div>
        </div>
      </footer>
    </div>
    </>
  );
}

/* ─── FAQ Item ─────────────────────────────────────────────────────────────── */

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div className="border-b border-white/[.06]">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between py-5 text-left group"
      >
        <span className="text-sm font-medium text-[#fafafa] pr-4">{question}</span>
        <ChevronDown
          className="w-4 h-4 shrink-0 text-[#71717a] transition-transform duration-200"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
        />
      </button>
      <motion.div
        initial={false}
        animate={{ height: open ? "auto" : 0, opacity: open ? 1 : 0 }}
        transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="overflow-hidden"
      >
        <p className="pb-5 text-sm text-[#a1a1aa] leading-relaxed max-w-xl">{answer}</p>
      </motion.div>
    </div>
  );
}
