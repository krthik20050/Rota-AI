"use client";

import * as React from "react";
import Link from "next/link";
import { WordsPreloader } from "./WordsPreloader";
import { motion, useInView, useScroll, useMotionValueEvent, AnimatePresence } from "framer-motion";
import {
  Mic, Zap, Send, Sparkles, Globe, Command, MessageSquare,
  Code2, FileText, Download,
  ChevronDown, GitBranch, X, Monitor, Terminal,
  Apple,
} from "lucide-react";

/* ─── Download Modal ───────────────────────────────────────────────────────── */

function DownloadModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="relative z-10 w-full max-w-md border border-white/[.08] rounded-sm"
        style={{ background: "#0c0c10", boxShadow: "0 32px 80px rgba(0,0,0,0.8)" }}
      >
        <button onClick={onClose} className="absolute top-4 right-4 text-zinc-600 hover:text-white transition-colors">
          <X size={18} />
        </button>
        <div className="p-8">
          <h3 className="text-lg font-semibold text-white mb-1 tracking-tight">Download Rota AI</h3>
          <p className="text-xs text-zinc-500 mb-6">Free &amp; open source. No account needed.</p>
          <a href="/api/download?platform=windows" download="RotaAI-Setup.exe"
            className="group flex items-center gap-4 w-full px-5 py-4 mb-3 rounded-sm transition-all hover:opacity-90"
            style={{ background: "#e4f222" }}>
            <div className="w-10 h-10 flex items-center justify-center rounded-sm bg-black/10">
              <Monitor size={20} className="text-black" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-semibold text-black tracking-tight">Download for Windows</div>
              <div className="text-[11px] text-black/60 mt-0.5">Installer (.exe) · Windows 10/11</div>
            </div>
            <Download size={16} className="text-black/40 group-hover:translate-y-0.5 transition-transform" />
          </a>
          <a href="/api/download?platform=macos" download="RotaAI-macOS.zip"
            className="group flex items-center gap-4 w-full px-5 py-4 mb-3 rounded-sm border transition-all hover:border-white/20"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
            <div className="w-10 h-10 flex items-center justify-center rounded-sm bg-white/[.03]">
              <Apple size={20} className="text-[#e4f222]" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-semibold text-white tracking-tight">Download for Mac</div>
              <div className="text-[11px] text-zinc-500 mt-0.5">App zip · macOS 13+ · first-open permission step</div>
            </div>
            <Download size={16} className="text-zinc-600 group-hover:translate-y-0.5 transition-transform" />
          </a>
          <a href="/api/download?platform=linux" download="RotaAI.AppImage"
            className="group flex items-center gap-4 w-full px-5 py-4 mb-4 rounded-sm border transition-all hover:border-white/20"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}>
            <div className="w-10 h-10 flex items-center justify-center rounded-sm bg-white/[.03]">
              <Terminal size={20} className="text-[#e4f222]" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-semibold text-white tracking-tight">Download for Linux</div>
              <div className="text-[11px] text-zinc-500 mt-0.5">AppImage · Ubuntu, Fedora, Arch</div>
            </div>
            <Download size={16} className="text-zinc-600 group-hover:translate-y-0.5 transition-transform" />
          </a>
          <div className="mb-6 rounded-sm border border-[#e4f222]/15 bg-[#e4f222]/[0.03] p-3 text-[11px] leading-relaxed text-zinc-500">
            Mac note: this student build is not Apple Developer ID notarized yet. On first launch,
            Control-click RotaAI.app, choose Open, then grant Accessibility and Microphone permissions.
          </div>
          <div className="flex items-center gap-3 text-[11px] text-zinc-600">
            <a href="https://github.com/krthik20050/Rota-AI" target="_blank" rel="noopener noreferrer"
              className="hover:text-zinc-400 transition-colors flex items-center gap-1">
              <GitBranch size={12} /> View on GitHub
            </a>
            <span className="text-zinc-800">·</span>
            <span>MIT License</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

/* ─── Waveform (animated) ──────────────────────────────────────────────────── */

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

const BASE_WAVE = genWave(140);

function AnimatedWaveform() {
  const [bars, setBars] = React.useState<number[]>(BASE_WAVE);
  const tRef = React.useRef(0);

  React.useEffect(() => {
    const id = setInterval(() => {
      tRef.current += 0.04;
      const t = tRef.current;
      setBars(BASE_WAVE.map((base, i) => {
        const w1 = Math.sin(t + i * 0.14) * 9;
        const w2 = Math.sin(t * 1.8 + i * 0.07) * 5;
        return Math.max(3, Math.min(50, base + w1 + w2));
      }));
    }, 55);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="w-full flex items-end justify-between px-2" style={{ height: 64 }}>
      {bars.map((h, i) => (
        <div
          key={i}
          style={{
            width: 2,
            height: h,
            borderRadius: "1px 1px 0 0",
            flexShrink: 0,
            background: `rgba(228,242,34,${0.06 + (h / 50) * 0.38})`,
            boxShadow: h > 22 ? `0 0 ${Math.round(h / 3.5)}px rgba(228,242,34,0.18)` : "none",
            transition: "height 0.055s ease-out",
          }}
        />
      ))}
    </div>
  );
}

/* ─── Hover Recording Pill (hero) ──────────────────────────────────────────── */

function HoverRecordingPill() {
  const [active, setActive] = React.useState(false);
  const [bars, setBars] = React.useState<number[]>(Array(24).fill(4));
  const iRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  const activate = React.useCallback(() => {
    iRef.current = setInterval(() => {
      setBars(Array(24).fill(0).map(() => Math.round(4 + Math.random() * 52)));
    }, 80);
    setActive(true);
  }, []);

  const deactivate = React.useCallback(() => {
    if (iRef.current) clearInterval(iRef.current);
    setBars(Array(24).fill(4));
    setActive(false);
  }, []);

  React.useEffect(() => () => { if (iRef.current) clearInterval(iRef.current); }, []);

  return (
    <div
      onMouseEnter={activate}
      onMouseLeave={deactivate}
      className="flex items-center gap-4 px-6 py-4 select-none cursor-default transition-all duration-300"
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
      <div className="flex items-center justify-center w-9 h-9 shrink-0 transition-colors duration-300"
        style={{ background: active ? "rgba(228,242,34,0.1)" : "rgba(255,255,255,0.03)", borderRadius: 2 }}>
        <Mic className="w-4 h-4 transition-colors duration-300" style={{ color: active ? "#e4f222" : "#50545a" }} />
      </div>
      <div className="flex items-center gap-[3px] flex-1 h-14">
        {bars.map((h, i) => (
          <div key={i} style={{
            width: 3, height: h, borderRadius: 1, flexShrink: 0,
            background: active ? "#e4f222" : "#262830",
            transition: active ? "height 0.08s ease-out" : "height 0.4s ease-out, background 0.3s",
          }} />
        ))}
      </div>
      <div className="shrink-0 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full transition-colors duration-300" style={{
          background: active ? "#e4f222" : "#262830",
          boxShadow: active ? "0 0 6px #e4f222" : "none",
          animation: active ? "dot-pulse 1.2s ease-in-out infinite" : "none",
        }} />
        <span className="text-xs uppercase tracking-widest transition-colors duration-300"
          style={{ color: active ? "#e4f222" : "#50545a" }}>
          {active ? "rec" : "F9"}
        </span>
      </div>
    </div>
  );
}

/* ─── F9 Key Illustration (hover-only, no auto-play) ──────────────────────── */

function F9KeyIllustration() {
  const [hoveredKey, setHoveredKey] = React.useState<string | null>(null);
  const keys = ["F7", "F8", "F9", "F10", "F11"];

  return (
    <div className="flex flex-col items-center gap-6 py-10">
      <div className="relative">
        <div className="flex gap-2">
          {keys.map((k) => {
            const hov = hoveredKey === k;
            return (
              <motion.div
                key={k}
                animate={{ scale: hov ? 1.22 : 0.9 }}
                transition={{ duration: 0.14, type: "spring", stiffness: 420, damping: 22 }}
                onMouseEnter={() => setHoveredKey(k)}
                onMouseLeave={() => setHoveredKey(null)}
                className="w-12 h-10 flex items-center justify-center text-xs font-mono rounded-sm select-none cursor-default"
                style={{
                  background: hov ? "rgba(228,242,34,0.22)" : "rgba(255,255,255,0.04)",
                  border: `1px solid ${hov ? "rgba(228,242,34,0.7)" : "rgba(255,255,255,0.07)"}`,
                  color: hov ? "#e4f222" : "#3a3a3a",
                  transition: "background 0.08s, border-color 0.08s, color 0.08s",
                }}
              >
                {k}
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Fixed-height slot — no layout shift, shows for any hovered key */}
      <div style={{ height: 36, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <AnimatePresence>
          {hoveredKey && (
            <motion.div
              initial={{ opacity: 0, y: -3, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -2, scale: 0.98 }}
              transition={{ duration: 0.08 }}
              className="flex items-center gap-2 px-3 py-1.5 rounded-sm text-xs"
              style={{
                background: "rgba(228,242,34,0.06)",
                border: "1px solid rgba(228,242,34,0.22)",
                color: "#e4f222",
                whiteSpace: "nowrap",
              }}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#e4f222] animate-pulse" />
              {hoveredKey === "F9" ? "Recording pill appears" : `${hoveredKey} key active`}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <p className="text-[10px] text-[#2a2a2a] uppercase tracking-[0.22em] font-mono">
        Hover any key to interact
      </p>
    </div>
  );
}

/* ─── Text Injection Mock (3 simultaneous windows, no loop) ────────────────── */

function AppWindowTyping({ label, domain, text, delay }: {
  label: string; domain: string; text: string; delay: number;
}) {
  const [displayed, setDisplayed] = React.useState("");
  const [done, setDone] = React.useState(false);

  React.useEffect(() => {
    const startTimer = setTimeout(() => {
      let i = 0;
      const id = setInterval(() => {
        i++;
        setDisplayed(text.slice(0, i));
        if (i >= text.length) { clearInterval(id); setDone(true); }
      }, 36);
      return () => clearInterval(id);
    }, delay);
    return () => clearTimeout(startTimer);
  }, [text, delay]);

  return (
    <div className="rounded-sm overflow-hidden" style={{
      background: "rgba(255,255,255,0.025)",
      border: "1px solid rgba(255,255,255,0.08)",
    }}>
      <div className="flex items-center gap-2 px-3 py-2" style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <img src={`https://www.google.com/s2/favicons?domain=${domain}&sz=32`} className="w-3.5 h-3.5" alt={label} />
        <span className="text-[10px] text-[#50545a] uppercase tracking-widest">{label}</span>
      </div>
      <div className="p-3 min-h-[2.75rem]">
        <span className="text-xs text-[#a1a1aa] leading-relaxed">{displayed}</span>
        {!done && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 0.65 }}
            className="inline-block w-0.5 h-3.5 bg-[#e4f222] ml-0.5 align-middle"
          />
        )}
      </div>
    </div>
  );
}

function TextInjectionMock() {
  const apps = [
    { label: "Gmail",  domain: "gmail.com",                text: "I wanted to follow up regarding the project deadline. Would extending it by one week be feasible?", delay: 0 },
    { label: "Slack",  domain: "slack.com",                text: "Hey team! Quick update on the deadline, can we push it by a week? Lmk!", delay: 900 },
    { label: "VS Code",domain: "code.visualstudio.com",   text: "// TODO: Follow up on deadline, request 1-week extension", delay: 1900 },
  ];
  return (
    <div className="w-full max-w-sm space-y-2.5">
      {apps.map((a) => <AppWindowTyping key={a.label} {...a} />)}
    </div>
  );
}

/* ─── Flowchart Demo (Works Everywhere) ────────────────────────────────────── */

function FlowchartDemo() {
  const [activeApp, setActiveApp] = React.useState<number | null>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const inView = useInView(containerRef, { once: true, margin: "-80px" });

  const apps = [
    {
      label: "Gmail", domain: "gmail.com", tone: "// formal",
      short: "Professional, clear, no fillers.",
      text: 'To: Team\nSubject: Deadline Update\n\nI wanted to follow up regarding the project deadline. Would extending it by one week be feasible?',
    },
    {
      label: "Slack", domain: "slack.com", tone: "// casual",
      short: "Friendly, direct, emoji-ready.",
      text: "Hey team! Quick update on the deadline — can we push it by a week? Lmk what works!",
    },
    {
      label: "Discord", domain: "discord.com", tone: "// conversational",
      short: "Chill, informal, relatable.",
      text: "yo update on deadline — thinking ~1 week push, thoughts? lol",
    },
    {
      label: "VS Code", domain: "code.visualstudio.com", tone: "// technical",
      short: "Concise, code-friendly.",
      text: "// TODO: follow_up(deadline)\n// action: request_extension(days=7)\n// status: pending_review",
    },
    {
      label: "Notion", domain: "notion.so", tone: "// structured",
      short: "Formatted, action-oriented.",
      text: "**Action Item**\nFollow up: project deadline\nProposal: +1 week extension\nStatus: [ ] Awaiting approval",
    },
  ];

  const rawVoice = `"uh so I wanted to follow up about the deadline and um maybe we can push it by like a week"`;
  // Bezier curve targets for 5 cards in grid-cols-5
  const curveTargets = [50, 150, 250, 350, 450];

  return (
    <div ref={containerRef} className="max-w-3xl mx-auto">
      {/* Voice input node */}
      <div className="flex justify-center">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
          className="inline-flex flex-col items-start gap-2 px-5 py-4 rounded-sm max-w-sm w-full font-mono"
          style={{ background: "rgba(228,242,34,0.04)", border: "1px solid rgba(228,242,34,0.18)" }}
        >
          <div className="flex items-center gap-2">
            <Mic className="w-3.5 h-3.5 text-[#e4f222]" />
            <span className="text-[10px] uppercase tracking-widest text-[#e4f222]">voice_input</span>
            <span className="ml-auto text-[10px] text-[#2e2e2e]">raw</span>
          </div>
          <p className="text-xs text-[#71717a] italic leading-relaxed">{rawVoice}</p>
        </motion.div>
      </div>

      {/* Vertical line down to Rota node */}
      <div className="flex justify-center">
        <motion.div
          initial={{ scaleY: 0, opacity: 0 }}
          animate={inView ? { scaleY: 1, opacity: 1 } : {}}
          transition={{ duration: 0.35, delay: 0.28, ease: "easeOut" }}
          style={{ width: 1, height: 36, background: "linear-gradient(rgba(228,242,34,0.55) 0%, rgba(228,242,34,0.25) 100%)", transformOrigin: "top" }}
        />
      </div>

      {/* Rota AI processing node */}
      <div className="flex justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.88 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.3, delay: 0.45 }}
          className="flex items-center justify-center px-6 py-3 rounded-sm"
          style={{ background: "rgba(9,9,11,1)", border: "1px solid rgba(228,242,34,0.28)", boxShadow: "0 0 28px rgba(228,242,34,0.1)" }}
        >
          <img src="/logo.svg" className="h-9 w-auto" alt="Rota AI" />
        </motion.div>
      </div>

      {/* Curved SVG branching lines */}
      <div className="relative" style={{ height: 72 }}>
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 500 72" preserveAspectRatio="none">
          <defs>
            <marker id="arrowhead" markerWidth="5" markerHeight="4" refX="4" refY="2" orient="auto">
              <polygon points="0 0, 5 2, 0 4" fill="rgba(228,242,34,0.4)" />
            </marker>
          </defs>
          {curveTargets.map((x, i) => (
            <motion.path
              key={i}
              d={`M 250 0 C 250 36 ${x} 36 ${x} 72`}
              stroke="rgba(228,242,34,0.22)"
              strokeWidth="1"
              fill="none"
              markerEnd="url(#arrowhead)"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={inView ? { pathLength: 1, opacity: 1 } : {}}
              transition={{ duration: 0.55, delay: 0.6 + i * 0.07, ease: "easeOut" }}
            />
          ))}
        </svg>
      </div>

      {/* App output cards — hover to expand */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        {apps.map((app, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 12 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.3, delay: 0.65 + i * 0.05 }}
            onMouseEnter={() => setActiveApp(i)}
            onMouseLeave={() => setActiveApp(null)}
            className="p-3 rounded-sm cursor-default transition-all duration-200 group overflow-hidden"
            style={{
              background: activeApp === i ? "rgba(228,242,34,0.06)" : "rgba(255,255,255,0.025)",
              border: `1px solid ${activeApp === i ? "rgba(228,242,34,0.32)" : "rgba(255,255,255,0.07)"}`,
              boxShadow: activeApp === i ? "0 0 16px rgba(228,242,34,0.08)" : "none",
              height: 170,
            }}
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <img src={`https://www.google.com/s2/favicons?domain=${app.domain}&sz=32`} className="w-4 h-4" alt={app.label} />
              <span className="text-[10px] text-[#71717a] font-semibold">{app.label}</span>
            </div>
            <div className="text-[8px] font-mono mb-2 text-[#9da833]">{app.tone}</div>
            <AnimatePresence mode="wait">
              {activeApp === i ? (
                <motion.pre
                  key="expanded"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="text-[10px] text-[#a1a1aa] leading-relaxed font-mono whitespace-pre-wrap break-words"
                >
                  {app.text}
                </motion.pre>
              ) : (
                <motion.p
                  key="short"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="text-[10px] text-[#3a3a3a] leading-relaxed line-clamp-2"
                >
                  {app.short}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      <p className="mt-3 text-center text-[9px] text-[#2a2a2a] uppercase tracking-widest font-mono">
        hover any app to see output
      </p>
    </div>
  );
}

/* ─── Fade In ──────────────────────────────────────────────────────────────── */

function FadeIn({
  children,
  delay = 0,
  className = "",
  y = 20,
  x = 0,
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
  y?: number;
  x?: number;
}) {
  const ref = React.useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y, x }}
      animate={inView ? { opacity: 1, y: 0, x: 0 } : {}}
      transition={{ duration: 0.55, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      {children}
    </motion.div>
  );
}

/* ─── Section Label ─────────────────────────────────────────────────────────── */

function SectionLabel({ n, title }: { n: string; title: string }) {
  return (
    <div className="flex items-center gap-4 mb-14">
      <span className="text-xs tracking-[0.25em] uppercase text-[#e4f222] font-mono">§{n}</span>
      <div className="flex-1 h-px bg-white/[.06]" />
      <span className="text-xs tracking-[0.25em] uppercase text-[#50545a] font-mono">{title}</span>
    </div>
  );
}

/* ─── Data ──────────────────────────────────────────────────────────────────── */

const HOW_STEPS = [
  {
    num: "01",
    icon: Command,
    title: "Press F9",
    desc: "A floating recording pill appears anywhere on screen. No setup, no switching apps. Just press and speak.",
  },
  {
    num: "02",
    icon: Mic,
    title: "Speak naturally",
    desc: "Say exactly what you want to type. Rota transcribes in real time and understands which app you are in, adapting tone automatically.",
  },
  {
    num: "03",
    icon: Send,
    title: "Text injected",
    desc: "Release F9. Polished, context-aware text appears exactly where your cursor is. Gmail, Slack, VS Code, Notion, anywhere.",
  },
];

const FEATURES = [
  {
    icon: Sparkles,
    title: "AI-powered cleanup",
    desc: "Rota automatically detects what app you are in and removes all filler words, fixes your punctuation, and matches your writing style: formal in Gmail, casual in Slack, technical in VS Code.",
    badge: "Smart",
  },
  {
    icon: Zap,
    title: "Sub-second latency",
    desc: "Powered by Groq Whisper with smart caching. Text appears in under a second, faster than you can reach for the keyboard.",
    badge: null,
  },
  {
    icon: Globe,
    title: "Works everywhere",
    desc: "Gmail, Slack, Discord, VS Code, Notion, Figma, Linear, Chrome, any browser tab, any native app. If it has a text field, Rota works.",
    badge: null,
  },
  {
    icon: MessageSquare,
    title: "Voice commands",
    desc: 'Edit by speaking: "Scratch that" removes the last sentence. "Make it more formal" shifts the tone. "Change deadline to Friday" edits in-place. "Translate to Spanish" converts on the fly.',
    badge: "Hands-free",
  },
  {
    icon: FileText,
    title: "Context-aware tone",
    desc: "Rota reads which app is in focus before transcribing. Email becomes professional. Slack messages get casual. Code comments stay concise. Zero configuration.",
    badge: null,
  },
  {
    icon: Code2,
    title: "Personal dictionary",
    desc: "Learns your vocabulary, project names, and technical terms over time. Say 'Kubernetes' and it won't come out as 'Cube net ease'.",
    badge: null,
  },
];

// Ordered by global daily active users — most used apps first, center of row 1 gets most attention
const APPS_DATA: { name: string; domain: string; invert?: boolean }[] = [
  // Row 1 — Billions / hundreds of millions of users
  { name: "YouTube",           domain: "youtube.com" },
  { name: "WhatsApp",          domain: "whatsapp.com" },
  { name: "Facebook",          domain: "facebook.com" },
  { name: "Instagram",         domain: "instagram.com" },
  { name: "TikTok",            domain: "tiktok.com" },
  { name: "Gmail",             domain: "gmail.com" },
  { name: "Telegram",          domain: "telegram.org" },
  { name: "Snapchat",          domain: "snapchat.com" },
  { name: "X / Twitter",       domain: "twitter.com" },
  { name: "Spotify",           domain: "spotify.com" },
  { name: "Netflix",           domain: "netflix.com" },
  { name: "LinkedIn",          domain: "linkedin.com" },
  { name: "Reddit",            domain: "reddit.com" },
  { name: "Amazon",            domain: "amazon.com" },
  { name: "Outlook",           domain: "outlook.com" },
  { name: "Zoom",              domain: "zoom.us" },
  // Row 2 — Major productivity & work tools
  { name: "Slack",             domain: "slack.com" },
  { name: "Discord",           domain: "discord.com" },
  { name: "Microsoft Teams",   domain: "teams.microsoft.com" },
  { name: "Google Docs",       domain: "docs.google.com" },
  { name: "ChatGPT",           domain: "chat.openai.com" },
  { name: "Perplexity",        domain: "perplexity.ai" },
  { name: "Claude",            domain: "claude.ai" },
  { name: "Gemini",            domain: "gemini.google.com" },
  { name: "Copilot",           domain: "copilot.microsoft.com" },
  { name: "Windsurf",          domain: "windsurf.com" },
  { name: "Replit",            domain: "replit.com" },
  { name: "Arc Browser",       domain: "arc.net" },
  { name: "Raycast",           domain: "raycast.com" },
  { name: "VS Code",           domain: "code.visualstudio.com" },
  { name: "Notion",            domain: "notion.so" },
  { name: "Figma",             domain: "figma.com" },
  { name: "GitHub",            domain: "github.com" },
  { name: "Canva",             domain: "canva.com" },
  { name: "Dropbox",           domain: "dropbox.com" },
  { name: "OneDrive",          domain: "onedrive.live.com" },
  { name: "Threads",           domain: "threads.net" },
  // Row 3 — Professional & developer tools
  { name: "Cursor",            domain: "cursor.com" },
  { name: "Jira",              domain: "atlassian.com" },
  { name: "Trello",            domain: "trello.com" },
  { name: "Asana",             domain: "asana.com" },
  { name: "Monday.com",        domain: "monday.com" },
  { name: "Linear",            domain: "linear.app" },
  { name: "Airtable",          domain: "airtable.com" },
  { name: "Miro",              domain: "miro.com" },
  { name: "ClickUp",           domain: "clickup.com" },
  { name: "HubSpot",           domain: "hubspot.com" },
  { name: "Salesforce",        domain: "salesforce.com" },
  { name: "Intercom",          domain: "intercom.com" },
  { name: "Zendesk",           domain: "zendesk.com" },
  { name: "Loom",              domain: "loom.com" },
  { name: "Grammarly",         domain: "grammarly.com" },
  { name: "Confluence",        domain: "confluence.atlassian.com" },
  // Row 4 — Niche but popular
  { name: "Obsidian",          domain: "obsidian.md" },
  { name: "Warp",              domain: "warp.dev" },
  { name: "Webflow",           domain: "webflow.com" },
  { name: "Shopify",           domain: "shopify.com" },
  { name: "Stripe",            domain: "stripe.com" },
  { name: "Substack",          domain: "substack.com" },
  { name: "Medium",            domain: "medium.com" },
  { name: "Todoist",           domain: "todoist.com" },
  { name: "Coda",              domain: "coda.io" },
  { name: "Proton Mail",       domain: "proton.me" },
  { name: "Calendly",          domain: "calendly.com" },
  { name: "Typeform",          domain: "typeform.com" },
  { name: "Basecamp",          domain: "basecamp.com" },
  { name: "Superhuman",        domain: "superhuman.com" },
  { name: "Vercel",            domain: "vercel.com" },
  { name: "Supabase",          domain: "supabase.com" },
  { name: "Craft",             domain: "craft.do" },
  { name: "Feedly",            domain: "feedly.com" },
  { name: "Bear",              domain: "bear.app" },
  { name: "Instapaper",        domain: "instapaper.com" },
  { name: "Skype",             domain: "skype.com" },
  { name: "Pinterest",         domain: "pinterest.com" },
  { name: "Stack Overflow",    domain: "stackoverflow.com" },
  { name: "Quora",             domain: "quora.com" },
  { name: "Hey",               domain: "hey.com" },
  { name: "Fastmail",          domain: "fastmail.com" },
  { name: "Pitch",             domain: "pitch.com" },
  { name: "Nuclino",           domain: "nuclino.com" },
  // Row 5 — More tools
  { name: "Google Meet",       domain: "meet.google.com" },
  { name: "Google Drive",      domain: "drive.google.com" },
  { name: "Google Calendar",   domain: "calendar.google.com" },
  { name: "Signal",            domain: "signal.org" },
  { name: "Twitch",            domain: "twitch.tv" },
  { name: "Framer",            domain: "framer.com", invert: true },
  { name: "Penpot",            domain: "penpot.app" },
  { name: "GitLab",            domain: "gitlab.com" },
  { name: "Postman",           domain: "postman.com" },
  { name: "Docker",            domain: "docker.com" },
  { name: "Bluesky",           domain: "bsky.app" },
  { name: "Zed",               domain: "zed.dev", invert: true },
  { name: "JetBrains",         domain: "jetbrains.com" },
  { name: "1Password",         domain: "1password.com" },
  { name: "Bitwarden",         domain: "bitwarden.com" },
  { name: "Logseq",            domain: "logseq.com" },
  { name: "Readwise",          domain: "readwise.io" },
  { name: "Day One",           domain: "dayoneapp.com" },
  { name: "Anytype",           domain: "anytype.io" },
  { name: "Whimsical",         domain: "whimsical.com" },
  { name: "Excalidraw",        domain: "excalidraw.com" },
  { name: "Amplitude",         domain: "amplitude.com" },
  { name: "Mixpanel",          domain: "mixpanel.com" },
  { name: "Beehiiv",           domain: "beehiiv.com" },
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
  { feature: "Mac / Linux / iOS", wispr: "All", superwhisper: "Mac, Win, iOS", rota: "Win, Mac, Linux", rotaBold: true },
];

const FAQ_ITEMS = [
  {
    q: "Is this really free?",
    a: "Yes. MIT licensed open source. Groq and Gemini both have free tiers that are enough for daily use. Ollama is completely free with no limits. There is no pro plan, no premium tier, no credit card needed.",
  },
  {
    q: "How does the download work?",
    a: "Click Download and pick your platform. Windows: run the installer. Mac: unzip RotaAI-macOS.zip, Control-click RotaAI.app, choose Open, and grant permissions on first launch. Linux: run the AppImage directly.",
  },
  {
    q: "Can I use it without internet?",
    a: "Yes. Install Ollama, download a Whisper model (small is 480MB), and Rota works 100% offline. No API keys, no accounts, no internet. Your voice data never leaves your machine.",
  },
  {
    q: "What about Mac or Linux?",
    a: "Windows, macOS, and Linux builds are published from GitHub releases. macOS currently uses an unsigned student-friendly build, so the first launch requires the standard Control-click Open workaround until we have Apple Developer ID notarization.",
  },
  {
    q: "What are the system requirements?",
    a: "Windows 10/11, macOS 13+, or Linux (Ubuntu 20.04+, Fedora 36+, Arch). 4GB RAM minimum, 8GB recommended. For local GPU transcription: NVIDIA GPU with 4GB+ VRAM. CPU-only works on any modern quad-core.",
  },
];

/* ─── Share Row ─────────────────────────────────────────────────────────────── */

const SHARE_URL = "https://rotaai.app";
const TWEET_TEXT = "Found a free open-source alternative to Wispr Flow. @RotaAI speaks into any app (Gmail, Slack, VS Code) and AI cleans it up perfectly. No subscription. No account. Just your voice. Crazy that this is free:";

const SHARE_PLATFORMS = [
  {
    name: "Twitter",
    href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(TWEET_TEXT)}&url=${encodeURIComponent(SHARE_URL)}`,
    color: "#e2e8f0",
    hoverBg: "rgba(255,255,255,0.14)",
    borderHover: "rgba(255,255,255,0.3)",
    icon: <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>,
  },
  {
    name: "WhatsApp",
    href: `https://wa.me/?text=${encodeURIComponent("Found a free open-source alternative to Wispr Flow. Rota AI speaks into any app and AI cleans it up. No subscription needed. " + SHARE_URL)}`,
    color: "#25D366",
    hoverBg: "rgba(37,211,102,0.15)",
    borderHover: "rgba(37,211,102,0.45)",
    icon: <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" /></svg>,
  },
  {
    name: "LinkedIn",
    href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(SHARE_URL)}`,
    color: "#0A66C2",
    hoverBg: "rgba(10,102,194,0.15)",
    borderHover: "rgba(10,102,194,0.5)",
    icon: <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>,
  },
  {
    name: "Instagram",
    href: "https://www.instagram.com/create/story",
    color: "#E1306C",
    hoverBg: "rgba(225,48,108,0.15)",
    borderHover: "rgba(225,48,108,0.45)",
    icon: <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" /></svg>,
  },
];

function ShareButton({ platform }: { platform: typeof SHARE_PLATFORMS[number] }) {
  const [hov, setHov] = React.useState(false);
  return (
    <a
      href={platform.href}
      target="_blank"
      rel="noreferrer"
      title={`Share on ${platform.name}`}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      className="flex flex-col items-center gap-2.5"
      style={{ transform: hov ? "scale(1.1)" : "scale(1)", transition: "transform 0.18s ease" }}
    >
      <div
        className="flex items-center justify-center w-16 h-16 rounded-2xl"
        style={{
          background: hov ? platform.hoverBg : "rgba(255,255,255,0.05)",
          border: `1px solid ${hov ? platform.borderHover : "rgba(255,255,255,0.09)"}`,
          color: hov ? platform.color : "#71717a",
          boxShadow: hov ? `0 0 22px ${platform.hoverBg}` : "none",
          transition: "background 0.18s, border-color 0.18s, color 0.18s, box-shadow 0.18s",
        }}
      >
        {platform.icon}
      </div>
      <span className="text-[10px] uppercase tracking-widest font-mono"
        style={{ color: hov ? platform.color : "#3a3a3a", transition: "color 0.18s" }}>
        {platform.name}
      </span>
    </a>
  );
}

function ShareRow() {
  return (
    <div className="flex items-end justify-center gap-6 flex-wrap">
      {SHARE_PLATFORMS.map((p) => <ShareButton key={p.name} platform={p} />)}
    </div>
  );
}

/* ─── App Icon (floating, custom tooltip) ──────────────────────────────────── */

function AppIcon({ app, floatName, dur, del }: {
  app: { name: string; domain: string; invert?: boolean };
  floatName: string; dur: number; del: number;
}) {
  const [hov, setHov] = React.useState(false);
  return (
    <div
      className="relative flex items-center justify-center w-12 h-12 rounded-xl cursor-default"
      style={{
        animation: `${floatName} ${dur}s ease-in-out ${del}s infinite`,
        border: `1px solid ${hov ? "rgba(228,242,34,0.25)" : "transparent"}`,
        background: hov ? "rgba(228,242,34,0.05)" : undefined,
        transform: hov ? "scale(1.28)" : undefined,
        animationPlayState: hov ? "paused" : "running",
        transition: "transform 0.15s, border-color 0.15s, background 0.15s",
      }}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
    >
      <img
        src={`https://www.google.com/s2/favicons?domain=${app.domain}&sz=64`}
        alt={app.name}
        className="w-7 h-7"
        style={{ imageRendering: "auto", filter: app.invert ? "brightness(0) invert(1) opacity(0.75)" : undefined }}
      />
      <AnimatePresence>
        {hov && (
          <motion.div
            initial={{ opacity: 0, y: 4, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.08 }}
            className="absolute bottom-full left-1/2 mb-2 px-2 py-1 text-[10px] font-mono whitespace-nowrap rounded-sm pointer-events-none z-50"
            style={{
              transform: "translateX(-50%)",
              background: "rgba(9,9,11,0.97)",
              border: "1px solid rgba(228,242,34,0.4)",
              color: "#e4f222",
              letterSpacing: "0.08em",
            }}
          >
            {app.name}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ─── Circular App Grid ─────────────────────────────────────────────────────── */

function CircularAppGrid() {
  const [hoveredApp, setHoveredApp] = React.useState<string | null>(null);

  // Split apps across 3 rings: outer 32, middle 26, inner = rest
  const outerApps = APPS_DATA.slice(0, 32);
  const midApps   = APPS_DATA.slice(32, 58);
  const innerApps = APPS_DATA.slice(58);

  const rings = [
    { radiusPct: 44, apps: outerApps, size: 34, img: 20 },
    { radiusPct: 30, apps: midApps,   size: 30, img: 18 },
    { radiusPct: 17, apps: innerApps, size: 26, img: 16 },
  ];

  // Circle border diameters as % of container
  const borders = [
    { d: 100, offset: 0 },
    { d: 62,  offset: 19 },
    { d: 36,  offset: 32 },
  ];

  return (
    <div className="flex flex-col items-center gap-6">
      <div
        className="relative mx-auto select-none"
        style={{ width: "min(580px, 90vw)", height: "min(580px, 90vw)" }}
      >
        {/* Ring borders */}
        {borders.map((b, i) => (
          <div
            key={i}
            className="absolute rounded-full pointer-events-none"
            style={{
              width: `${b.d}%`, height: `${b.d}%`,
              top: `${b.offset}%`, left: `${b.offset}%`,
              border: `1px solid rgba(228,242,34,${0.14 - i * 0.04})`,
            }}
          />
        ))}

        {/* Center: Rota logo */}
        <div
          className="absolute"
          style={{ top: "50%", left: "50%", transform: "translate(-50%, -50%)" }}
        >
          <img src="/logo.svg" alt="Rota AI" style={{ height: 34, width: "auto", opacity: 0.85 }} />
        </div>

        {/* App icons on rings */}
        {rings.flatMap(({ radiusPct, apps, size, img }, ri) =>
          apps.map((app, i) => {
            const angle = (i / apps.length) * 2 * Math.PI - Math.PI / 2;
            const leftPct = +(50 + radiusPct * Math.cos(angle)).toFixed(4);
            const topPct  = +(50 + radiusPct * Math.sin(angle)).toFixed(4);
            const isHov   = hoveredApp === app.name;

            return (
              <div
                key={`${ri}-${app.name}`}
                className="absolute"
                style={{
                  left: `${leftPct}%`,
                  top:  `${topPct}%`,
                  transform: "translate(-50%, -50%)",
                  zIndex: isHov ? 20 : 1,
                }}
                onMouseEnter={() => setHoveredApp(app.name)}
                onMouseLeave={() => setHoveredApp(null)}
              >
                <div
                  className="flex items-center justify-center rounded-full cursor-default"
                  style={{
                    width: size, height: size,
                    background: isHov ? "rgba(228,242,34,0.12)" : "rgba(255,255,255,0.04)",
                    border: `1px solid ${isHov ? "rgba(228,242,34,0.4)" : "rgba(255,255,255,0.07)"}`,
                    transform: isHov ? "scale(1.4)" : "scale(1)",
                    transition: "all 0.1s ease",
                  }}
                >
                  <img
                    src={`https://www.google.com/s2/favicons?domain=${app.domain}&sz=32`}
                    alt={app.name}
                    style={{ width: img, height: img }}
                  />
                </div>
                <AnimatePresence>
                  {isHov && (
                    <motion.div
                      initial={{ opacity: 0, y: 4, scale: 0.9 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ duration: 0.08 }}
                      className="absolute left-1/2 bottom-full mb-2 px-2 py-1 text-[10px] font-mono whitespace-nowrap rounded-sm pointer-events-none"
                      style={{
                        transform: "translateX(-50%)",
                        background: "rgba(9,9,11,0.97)",
                        border: "1px solid rgba(228,242,34,0.4)",
                        color: "#e4f222",
                        letterSpacing: "0.08em",
                      }}
                    >
                      {app.name}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })
        )}
      </div>
      <p className="text-[11px] text-[#2a2a2a] uppercase tracking-[0.2em] font-mono">
        + any app with a text field
      </p>
    </div>
  );
}

/* ─── Nav ───────────────────────────────────────────────────────────────────── */

function Nav({ onDownloadClick }: { onDownloadClick: () => void }) {
  const [scrolled, setScrolled] = React.useState(false);
  const { scrollY } = useScroll();
  useMotionValueEvent(scrollY, "change", (latest) => setScrolled(latest > 40));

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-18 transition-colors duration-200"
      style={{
        borderBottom: `1px solid ${scrolled ? "rgba(255,255,255,0.06)" : "transparent"}`,
        background: scrolled ? "rgba(9,9,11,0.92)" : "transparent",
        backdropFilter: scrolled ? "blur(16px)" : "none",
      }}
    >
      <Link href="/" className="flex items-center">
        <img src="/logo.svg" alt="Rota AI" className="h-14 sm:h-16 w-auto" />
      </Link>
      <div className="hidden sm:flex items-center gap-8 text-xs tracking-[0.18em] uppercase text-[#71717a]">
        <a href="#features" className="hover:text-[#fafafa] transition-colors">Features</a>
        <a href="#comparison" className="hover:text-[#fafafa] transition-colors">Compare</a>
        <Link href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</Link>
        <button onClick={onDownloadClick} className="hover:text-[#fafafa] transition-colors"
          style={{ background: "none", border: "none", cursor: "pointer", font: "inherit", color: "inherit" }}>
          Download
        </button>
      </div>
      <button onClick={onDownloadClick}
        style={{ background: "#e4f222", color: "#000", borderRadius: 2, border: "none", cursor: "pointer" }}
        className="flex items-center gap-2 px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 active:scale-95">
        <Download className="w-3 h-3" />
        Download
      </button>
    </nav>
  );
}

/* ─── LandingPage ───────────────────────────────────────────────────────────── */

export function LandingPage() {
  const [preloaderDone, setPreloaderDone] = React.useState(false);
  const [downloadModalOpen, setDownloadModalOpen] = React.useState(false);
  const [hoveredStep, setHoveredStep] = React.useState<number | null>(null);

  return (
    <>
      {!preloaderDone && <WordsPreloader onComplete={() => setPreloaderDone(true)} />}
      <DownloadModal open={downloadModalOpen} onClose={() => setDownloadModalOpen(false)} />
      <div className="min-h-screen bg-[#09090b]">
        <Nav onDownloadClick={() => setDownloadModalOpen(true)} />

        {/* ── Hero ── */}
        <section className="relative flex flex-col items-center justify-center text-center overflow-hidden"
          style={{ paddingTop: 112, paddingBottom: 0, minHeight: "92vh" }}>
          <div className="absolute inset-0 pointer-events-none" style={{
            backgroundImage: "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.035) 3px,rgba(0,0,0,0.035) 4px)",
            zIndex: 1,
          }} />
          <div className="absolute top-0 left-1/2 -translate-x-1/2 pointer-events-none" style={{
            width: 900, height: 600,
            background: "radial-gradient(ellipse at center top, rgba(228,242,34,0.045) 0%, transparent 60%)",
            zIndex: 0,
          }} />

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
            className="relative z-10 inline-flex items-center gap-2 px-4 py-1.5 mb-8 border text-xs tracking-[0.2em] uppercase"
            style={{ borderColor: "rgba(228,242,34,0.18)", background: "rgba(228,242,34,0.04)", color: "#e4f222", borderRadius: 2 }}>
            <span className="w-1.5 h-1.5 rounded-full bg-[#e4f222] animate-pulse" />
            Now available: Windows, Mac &amp; Linux
          </motion.div>

          <motion.h1 initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.08 }}
            className="relative z-10 font-display uppercase leading-[0.92] tracking-[0.02em] px-4"
            style={{ fontSize: "clamp(40px, 7vw, 96px)", color: "#fafafa" }}>
            Type at the
            <br />
            <span style={{ color: "#e4f222" }}>speed of light.</span>
          </motion.h1>

          <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="relative z-10 mt-7 max-w-md text-sm leading-relaxed text-[#a1a1aa]">
            Voice dictation that actually works. AI-cleaned, context-aware text
            injected directly into any app with a single keypress.
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="relative z-10 mt-10 flex flex-col sm:flex-row items-center gap-3">
            <button onClick={() => setDownloadModalOpen(true)}
              className="group flex items-center gap-2.5 px-7 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
              style={{ background: "#e4f222", color: "#000", borderRadius: 2, boxShadow: "0 4px 20px rgba(228,242,34,0.2)", border: "none", cursor: "pointer", font: "inherit" }}>
              Download
              <Download className="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform" />
            </button>
            <a href="#how-it-works"
              className="flex items-center gap-2 px-6 py-3 text-xs uppercase tracking-[0.15em] border transition-all hover:border-white/15"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "#71717a", borderRadius: 2 }}>
              See how it works
            </a>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 24, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="relative z-10 mt-14 flex flex-col items-center gap-3">
            <p className="text-xs uppercase tracking-[0.25em] text-[#71717a]">Hover to demo</p>
            <HoverRecordingPill />
          </motion.div>

          {/* Animated waveform */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.7 }}
            className="relative z-10 w-full mt-14">
            <AnimatedWaveform />
          </motion.div>
        </section>

        {/* ── How it works ── */}
        <section id="how-it-works" className="py-20 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-6xl mx-auto">
            <FadeIn><SectionLabel n="01" title="How it works" /></FadeIn>
            <FadeIn className="mb-16" x={-20}>
              <h2 className="font-display uppercase leading-[0.92] tracking-[0.02em]"
                style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}>
                Three steps.
                <br />
                <span style={{ color: "#e4f222" }}>Zero friction.</span>
              </h2>
            </FadeIn>

            <div className="space-y-px" style={{ background: "rgba(255,255,255,0.04)" }}>
              {HOW_STEPS.map((step, i) => {
                const isEven = i % 2 === 0;
                const IllustrationSlot =
                  i === 0 ? F9KeyIllustration
                  : i === 1 ? () => <div className="flex items-center justify-center py-8"><HoverRecordingPill /></div>
                  : TextInjectionMock;

                return (
                  <FadeIn key={i} delay={0.1 * i}>
                    <div
                      className="grid grid-cols-1 lg:grid-cols-2 bg-[#09090b]"
                      onMouseEnter={() => setHoveredStep(i)}
                      onMouseLeave={() => setHoveredStep(null)}
                    >
                      {/* Text panel */}
                      <div className={`p-10 lg:p-12 flex flex-col justify-center relative overflow-hidden ${isEven ? "lg:order-1" : "lg:order-2"}`}>
                        <div
                          className="absolute top-6 right-6 font-display uppercase leading-none select-none pointer-events-none transition-all duration-500"
                          style={{
                            fontSize: 96,
                            color: "#e4f222",
                            opacity: hoveredStep === i ? 0.9 : 0.06,
                            letterSpacing: "0.02em",
                          }}
                        >
                          {step.num}
                        </div>
                        <div className="w-12 h-12 flex items-center justify-center mb-6 transition-all duration-300"
                          style={{
                            background: hoveredStep === i ? "rgba(228,242,34,0.12)" : "rgba(228,242,34,0.06)",
                            borderRadius: 2,
                            border: `1px solid ${hoveredStep === i ? "rgba(228,242,34,0.32)" : "rgba(228,242,34,0.1)"}`,
                          }}>
                          <step.icon className="w-5 h-5" style={{ color: hoveredStep === i ? "#e4f222" : "#9da833" }} />
                        </div>
                        <h3 className="text-base font-semibold text-white mb-3 uppercase tracking-wider">{step.title}</h3>
                        <p className="text-sm leading-relaxed text-[#71717a] max-w-xs">{step.desc}</p>
                      </div>

                      {/* Illustration panel */}
                      <div
                        className={`p-10 lg:p-12 flex items-center justify-center ${isEven ? "lg:order-2 border-t lg:border-t-0 lg:border-l" : "lg:order-1 border-t lg:border-t-0 lg:border-r"}`}
                        style={{ borderColor: "rgba(255,255,255,0.04)", minHeight: 220 }}>
                        <IllustrationSlot />
                      </div>
                    </div>
                  </FadeIn>
                );
              })}
            </div>
          </div>
        </section>

        {/* ── Features ── */}
        <section id="features" className="py-20 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-6xl mx-auto">
            <FadeIn><SectionLabel n="02" title="Features" /></FadeIn>
            <FadeIn className="mb-16" x={-20}>
              <h2 className="font-display uppercase leading-[0.92] tracking-[0.02em]"
                style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}>
                Built for how
                <br />
                <span style={{ color: "#e4f222" }}>you actually think.</span>
              </h2>
            </FadeIn>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px" style={{ background: "rgba(255,255,255,0.04)" }}>
              {FEATURES.map((feat, i) => (
                <FadeIn key={i} delay={0.05 * i} y={16} className="h-full">
                  <div className="group p-8 bg-[#09090b] h-full relative overflow-hidden transition-all duration-300 hover:bg-[#0d0d10]">
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                      style={{ background: "radial-gradient(circle at 50% 0%, rgba(228,242,34,0.04) 0%, transparent 60%)" }} />
                    <div className="w-10 h-10 flex items-center justify-center mb-5 transition-all duration-300"
                      style={{
                        background: "rgba(228,242,34,0.06)", borderRadius: 2, border: "1px solid rgba(228,242,34,0.1)",
                      }}>
                      <feat.icon className="w-4 h-4 text-[#e4f222] transition-all duration-300 group-hover:scale-110" />
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-sm font-semibold text-white uppercase tracking-wider">{feat.title}</h3>
                      {feat.badge && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded-sm font-mono uppercase tracking-wider"
                          style={{ background: "rgba(228,242,34,0.07)", color: "#e4f222", border: "1px solid rgba(228,242,34,0.15)" }}>
                          {feat.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-sm leading-relaxed text-[#71717a]">{feat.desc}</p>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── Works everywhere ── */}
        <section id="apps" className="pt-14 pb-12 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-6xl mx-auto">
            <FadeIn><SectionLabel n="03" title="Works everywhere" /></FadeIn>

            {/* Big logo as section hero */}
            <FadeIn className="flex justify-center mb-4">
              <img src="/logo.svg" alt="Rota AI" className="h-28 sm:h-40 w-auto" />
            </FadeIn>
            <FadeIn className="mb-16">
              <p className="text-center text-sm text-[#71717a] max-w-lg mx-auto leading-relaxed">
                One voice. Every surface. Rota detects which app you are typing in and adapts
                the tone, punctuation, and vocabulary to match. Automatically.
              </p>
            </FadeIn>

            {/* Flowchart demo */}
            <FadeIn delay={0.1} className="mb-20">
              <FlowchartDemo />
            </FadeIn>

            {/* Floating icon grid — icons only, no names */}
            <FadeIn delay={0.15}>
              <p className="text-[10px] uppercase tracking-[0.25em] text-[#50545a] font-mono mb-8">
                Compatible with 90+ apps
              </p>
              <style>{`
                @keyframes float-a { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }
                @keyframes float-b { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
                @keyframes float-c { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-9px)} }
                @keyframes float-d { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
              `}</style>
              <div className="flex flex-wrap gap-3">
                {APPS_DATA.slice(0, 95).map((app, i) => {
                  const floatNames = ["float-a", "float-b", "float-c", "float-d"];
                  const floatName = floatNames[i % 4];
                  const dur = 2.4 + (i % 5) * 0.45;
                  const del = (i * 0.12) % 2;
                  return (
                    <AppIcon key={app.name} app={app} floatName={floatName} dur={dur} del={del} />
                  );
                })}
              </div>
              <p className="text-[11px] text-[#2a2a2a] mt-8 uppercase tracking-[0.2em]">+ any app with a text field</p>
            </FadeIn>
          </div>
        </section>

        {/* ── Comparison ── */}
        <section id="comparison" className="py-20 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-4xl mx-auto">
            <FadeIn><SectionLabel n="04" title="Comparison" /></FadeIn>
            <FadeIn className="mb-14 text-center">
              <h2 className="font-display uppercase leading-[0.92] tracking-[0.02em]"
                style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}>
                Why Rota AI?
              </h2>
            </FadeIn>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[.06]">
                    <th className="text-left py-4 pr-6 text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono">Feature</th>
                    <th className="text-center py-4 px-4 text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono">Wispr Flow</th>
                    <th className="text-center py-4 px-4 text-xs uppercase tracking-[0.2em] text-[#e4f222] font-mono">Rota AI</th>
                    <th className="text-center py-4 pl-4 text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono">SuperWhisper</th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARE_ROWS.map((row, i) => (
                    <motion.tr
                      key={i}
                      className="border-b border-white/[.03]"
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.35, delay: i * 0.04 }}
                    >
                      <td className="py-4 pr-6 text-[#a1a1aa]">{row.feature}</td>
                      <td className="py-4 px-4 text-center text-[#50545a]">{row.wispr}</td>
                      <td className={`py-4 px-4 text-center ${row.rotaBold ? "text-[#e4f222] font-semibold" : "text-[#a1a1aa]"}`}>{row.rota}</td>
                      <td className="py-4 pl-4 text-center text-[#50545a]">{row.superwhisper}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* ── FAQ ── */}
        <section className="py-20 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-2xl mx-auto">
            <FadeIn><SectionLabel n="05" title="FAQ" /></FadeIn>
            <div className="space-y-px bg-white/[.04]">
              {FAQ_ITEMS.map((item, i) => (
                <FadeIn key={i} delay={0.06 * i}>
                  <FAQItem question={item.q} answer={item.a} />
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── Download ── */}
        <section id="download" className="py-20 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-2xl mx-auto text-center">
            <FadeIn><SectionLabel n="06" title="Download" /></FadeIn>
            <FadeIn className="mb-10">
              <h2 className="font-display uppercase leading-[0.92] tracking-[0.02em]"
                style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}>
                Download &amp;
                <br />
                <span style={{ color: "#e4f222" }}>start speaking.</span>
              </h2>
            </FadeIn>
            <FadeIn delay={0.1}>
              <p className="text-sm mb-10 text-[#a1a1aa]">
                Windows, Mac &amp; Linux · Free &amp; open source · No account needed
              </p>
              <button onClick={() => setDownloadModalOpen(true)}
                className="group inline-flex items-center gap-3 px-8 py-4 text-sm font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
                style={{ background: "#e4f222", color: "#000", borderRadius: 2, boxShadow: "0 4px 24px rgba(228,242,34,0.25)", border: "none", cursor: "pointer", font: "inherit" }}>
                <Download className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
                Download Rota AI
              </button>
            </FadeIn>
          </div>
        </section>

        {/* ── Share ── */}
        <section id="share" className="py-20 px-6 sm:px-10"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="max-w-2xl mx-auto text-center">
            <FadeIn><SectionLabel n="07" title="Share" /></FadeIn>
            <FadeIn className="mb-10">
              <h2 className="font-display uppercase leading-[0.92] tracking-[0.02em]"
                style={{ fontSize: "clamp(28px, 4vw, 52px)", color: "#fafafa" }}>
                Share with your
                <br />
                <span style={{ color: "#e4f222" }}>friends &amp; family.</span>
              </h2>
            </FadeIn>
            <FadeIn delay={0.1}>
              <p className="text-sm text-[#71717a] mb-12">
                Love Rota AI? Help spread the word.
              </p>
              <ShareRow />
            </FadeIn>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-20 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-12">
            <div className="flex items-center">
              <img src="/logo.svg" alt="Rota AI" className="h-16 sm:h-20 w-auto" />
            </div>
            <div className="flex gap-12 text-[10px] uppercase tracking-[0.2em] font-bold text-zinc-600">
              <a href="https://github.com/krthik20050/Rota-AI" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">Github</a>
              <a href="#" className="hover:text-white transition-colors">Documentation</a>
              <a href="#" className="hover:text-white transition-colors">Security</a>
            </div>
            <div className="text-[10px] uppercase tracking-[0.2em] font-bold text-zinc-700">
              © 2026 ROTA_STUDIO_LABS
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
    <div className="bg-[#09090b]">
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-5 text-left"
        style={{ background: "none", border: "none", cursor: "pointer", font: "inherit" }}>
        <span className="text-sm text-white pr-4">{question}</span>
        <ChevronDown className="w-4 h-4 text-[#50545a] shrink-0 transition-transform duration-200"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-5">
              <p className="text-sm leading-relaxed text-[#71717a]">{answer}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
