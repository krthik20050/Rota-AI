"use client";

import * as React from "react";
import Link from "next/link";
import { WordsPreloader } from "./WordsPreloader";
import { motion, useInView, useScroll, useMotionValueEvent } from "framer-motion";
import {
  Mic, Zap, Send, Sparkles, Globe, Command, MessageSquare,
  Code2, FileText, Download,
  ChevronDown, ExternalLink, GitBranch, X, Monitor, Terminal,
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

          {/* Windows */}
          <a
            href="/api/download?platform=windows"
            download="RotaAI-Setup.exe"
            className="group flex items-center gap-4 w-full px-5 py-4 mb-3 rounded-sm transition-all hover:opacity-90"
            style={{ background: "#e4f222" }}
          >
            <div className="w-10 h-10 flex items-center justify-center rounded-sm bg-black/10">
              <Monitor size={20} className="text-black" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-semibold text-black tracking-tight">Download for Windows</div>
              <div className="text-[11px] text-black/60 mt-0.5">Installer (.exe) · Windows 10/11</div>
            </div>
            <Download size={16} className="text-black/40 group-hover:translate-y-0.5 transition-transform" />
          </a>

          {/* macOS */}
          <a
            href="/api/download?platform=macos"
            download="RotaAI-macOS.zip"
            className="group flex items-center gap-4 w-full px-5 py-4 mb-3 rounded-sm border transition-all hover:border-white/20"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
          >
            <div className="w-10 h-10 flex items-center justify-center rounded-sm bg-white/[.03]">
              <Apple size={20} className="text-[#e4f222]" />
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-semibold text-white tracking-tight">Download for Mac</div>
              <div className="text-[11px] text-zinc-500 mt-0.5">App zip · macOS 13+ · first-open permission step</div>
            </div>
            <Download size={16} className="text-zinc-600 group-hover:translate-y-0.5 transition-transform" />
          </a>

          {/* Linux */}
          <a
            href="/api/download?platform=linux"
            download="RotaAI.AppImage"
            className="group flex items-center gap-4 w-full px-5 py-4 mb-4 rounded-sm border transition-all hover:border-white/20"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.08)" }}
          >
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
            <a href="https://github.com/krthik20050/Rota-AI" target="_blank" rel="noopener noreferrer" className="hover:text-zinc-400 transition-colors flex items-center gap-1">
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
    desc: "A floating recording pill appears. Start speaking. No setup, no switching apps.",
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
    desc: "Release F9. Polished text appears where your cursor is. Gmail, Slack, VS Code, anywhere.",
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
    desc: "Gmail, Slack, Discord, VS Code, Notion. Any text field, any app.",
    large: false,
  },
  {
    icon: MessageSquare,
    title: "Voice commands",
    desc: '"Scratch that", "Change X to Y". Voice-native editing.',
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

const APPS_DATA = [
  { name: "Gmail",   domain: "gmail.com",               url: "https://gmail.com" },
  { name: "Slack",   domain: "slack.com",               url: "https://slack.com" },
  { name: "VS Code", domain: "code.visualstudio.com",   url: "https://code.visualstudio.com" },
  { name: "Notion",  domain: "notion.so",               url: "https://notion.so" },
  { name: "Discord", domain: "discord.com",             url: "https://discord.com" },
  { name: "Obsidian",domain: "obsidian.md",             url: "https://obsidian.md" },
  { name: "Chrome",  domain: "google.com",              url: "https://www.google.com/chrome" },
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
    a: "Click Download and pick your platform. Windows: run the installer. Mac: unzip RotaAI-macOS.zip, Control-click RotaAI.app, choose Open, and grant permissions on first launch. Linux: run the AppImage directly (chmod +x RotaAI.AppImage && ./RotaAI.AppImage).",
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

/* ─── Share Button ──────────────────────────────────────────────────────────── */

const SHARE_URL = "https://rotaai.app";
const SHARE_TEXT = "I've been using Rota AI — free, open source voice dictation that actually works. No subscription, no account. Try it:";

function ShareButton() {
  const [open, setOpen] = React.useState(false);
  const [copied, setCopied] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  const copyLink = () => {
    navigator.clipboard.writeText(SHARE_URL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = () => {
    if (typeof navigator !== "undefined" && navigator.share) {
      navigator.share({ title: "Rota AI", text: SHARE_TEXT, url: SHARE_URL }).catch(() => {});
    } else {
      setOpen((v) => !v);
    }
  };

  const platforms = [
    {
      label: "X / Twitter",
      icon: <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>,
      href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(SHARE_TEXT)}&url=${encodeURIComponent(SHARE_URL)}`,
    },
    {
      label: "LinkedIn",
      icon: <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>,
      href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(SHARE_URL)}`,
    },
    {
      label: "Reddit",
      icon: <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>,
      href: `https://www.reddit.com/submit?url=${encodeURIComponent(SHARE_URL)}&title=${encodeURIComponent("Rota AI: free open source voice dictation for Windows, Mac and Linux")}`,
    },
    {
      label: "WhatsApp",
      icon: <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>,
      href: `https://wa.me/?text=${encodeURIComponent(SHARE_TEXT + " " + SHARE_URL)}`,
    },
    {
      label: "Instagram (copy link)",
      icon: <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>,
      href: null,
    },
  ];

  return (
    <div ref={ref} className="relative inline-block mt-8">
      <button
        onClick={handleShare}
        className="flex items-center gap-2.5 px-5 py-2.5 text-xs font-semibold uppercase tracking-[0.15em] text-[#fafafa] rounded-sm transition-all hover:bg-white/10"
        style={{ border: "1px solid rgba(255,255,255,0.12)" }}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
          <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13"/>
        </svg>
        Share Rota AI
        <ChevronDown className={`w-3 h-3 transition-transform duration-150 ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div
          className="absolute left-0 bottom-full mb-2 w-56 rounded-sm overflow-hidden z-50"
          style={{ background: "#111113", border: "1px solid rgba(255,255,255,0.10)", boxShadow: "0 16px 40px rgba(0,0,0,0.8)" }}
        >
          {platforms.map((p) =>
            p.href ? (
              <a
                key={p.label}
                href={p.href}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-3 px-4 py-3 text-xs text-[#a1a1aa] hover:text-white hover:bg-white/[.06] transition-colors"
                onClick={() => setOpen(false)}
              >
                {p.icon}
                {p.label}
              </a>
            ) : (
              <button
                key={p.label}
                onClick={() => { copyLink(); setOpen(false); }}
                className="w-full flex items-center gap-3 px-4 py-3 text-xs text-[#a1a1aa] hover:text-white hover:bg-white/[.06] transition-colors"
                style={{ background: "none", border: "none", cursor: "pointer", font: "inherit" }}
              >
                {p.icon}
                {copied ? "Link copied!" : p.label}
              </button>
            )
          )}
          <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
            <button
              onClick={() => { copyLink(); setOpen(false); }}
              className="w-full flex items-center gap-3 px-4 py-3 text-xs text-[#a1a1aa] hover:text-white hover:bg-white/[.06] transition-colors"
              style={{ background: "none", border: "none", cursor: "pointer", font: "inherit" }}
            >
              <ExternalLink className="w-4 h-4" />
              {copied ? "Copied!" : "Copy link"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Nav ───────────────────────────────────────────────────────────────────── */

function Nav({ onDownloadClick }: { onDownloadClick: () => void }) {
  const [scrolled, setScrolled] = React.useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setScrolled(latest > 40);
  });

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
        <img src="/logo.png" alt="Rota AI" className="h-11 sm:h-14 w-auto" />
      </Link>

      <div className="hidden sm:flex items-center gap-8 text-xs tracking-[0.18em] uppercase text-[#71717a]">
        <a href="#how-it-works" className="hover:text-[#fafafa] transition-colors">How it works</a>
        <a href="#features" className="hover:text-[#fafafa] transition-colors">Features</a>
        <a href="#comparison" className="hover:text-[#fafafa] transition-colors">Compare</a>
        <Link href="/blog" className="hover:text-[#fafafa] transition-colors">Blog</Link>
        <button onClick={onDownloadClick} className="hover:text-[#fafafa] transition-colors" style={{ background: "none", border: "none", cursor: "pointer", font: "inherit", color: "inherit" }}>Download</button>
      </div>

      <button
        onClick={onDownloadClick}
        style={{ background: "#e4f222", color: "#000", borderRadius: 2, border: "none", cursor: "pointer" }}
        className="flex items-center gap-2 px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 active:scale-95"
      >
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

  return (
    <>
      {!preloaderDone && (
        <WordsPreloader onComplete={() => setPreloaderDone(true)} />
      )}
      <DownloadModal open={downloadModalOpen} onClose={() => setDownloadModalOpen(false)} />
    <div className="min-h-screen bg-[#09090b]">
      <Nav onDownloadClick={() => setDownloadModalOpen(true)} />

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
          Now available: Windows, Mac &amp; Linux
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.08 }}
          className="relative z-10 font-display uppercase leading-[0.92] tracking-[0.02em] px-4"
          style={{ fontSize: "clamp(40px, 7vw, 96px)", color: "#fafafa" }}
        >
          Type at the
          <br />
          <span style={{ color: "#e4f222" }}>speed of light.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative z-10 mt-7 max-w-md text-sm leading-relaxed text-[#a1a1aa]"
        >
          Voice dictation that actually works. AI-cleaned, context-aware text
          injected directly into any app with a single keypress.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="relative z-10 mt-10 flex flex-col sm:flex-row items-center gap-3"
        >
          <button
            onClick={() => setDownloadModalOpen(true)}
            className="group flex items-center gap-2.5 px-7 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
            style={{
              background: "#e4f222",
              color: "#000",
              borderRadius: 2,
              boxShadow: "0 4px 20px rgba(228,242,34,0.2)",
              border: "none",
              cursor: "pointer",
              font: "inherit",
            }}
          >
            Download
            <Download className="w-3.5 h-3.5 group-hover:translate-y-0.5 transition-transform" />
          </button>
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
              style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}
            >
              Three steps.
              <br />
              <span style={{ color: "#e4f222" }}>Zero friction.</span>
            </h2>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/[.04]">
            {HOW_STEPS.map((step, i) => (
              <FadeIn key={i} delay={0.1 * i}>
                <div className="p-8 bg-[#09090b] relative overflow-hidden">
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
                    className="w-12 h-12 flex items-center justify-center mb-6"
                    style={{
                      background: "rgba(228,242,34,0.06)",
                      borderRadius: 2,
                      border: "1px solid rgba(228,242,34,0.1)",
                    }}
                  >
                    <step.icon className="w-5 h-5 text-[#e4f222]" />
                  </div>
                  <h3 className="text-sm font-semibold text-white mb-2 uppercase tracking-wider">{step.title}</h3>
                  <p className="text-sm leading-relaxed text-[#71717a]">{step.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
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
              style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}
            >
              Everything you need.
              <br />
              <span style={{ color: "#e4f222" }}>Nothing you do not.</span>
            </h2>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-white/[.04]">
            {FEATURES.map((feat, i) => (
              <FadeIn key={i} delay={0.05 * i} className="h-full">
                <div className={`p-8 bg-[#09090b] h-full ${feat.large ? "md:col-span-2 lg:col-span-1" : ""}`}>
                  <div
                    className="w-10 h-10 flex items-center justify-center mb-5"
                    style={{ background: "rgba(228,242,34,0.06)", borderRadius: 2 }}
                  >
                    <feat.icon className="w-4 h-4 text-[#e4f222]" />
                  </div>
                  <h3 className="text-sm font-semibold text-white mb-2 uppercase tracking-wider">{feat.title}</h3>
                  <p className="text-sm leading-relaxed text-[#71717a]">{feat.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── Works everywhere ── */}
      <section
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-6xl mx-auto">
          <FadeIn>
            <SectionLabel n="03" title="Works everywhere" />
          </FadeIn>
          <FadeIn className="mb-14">
            <h2
              className="font-display uppercase leading-[0.92] tracking-[0.02em]"
              style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}
            >
              Any app.
              <br />
              <span style={{ color: "#e4f222" }}>Any text field.</span>
            </h2>
          </FadeIn>
          <FadeIn>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 mb-4">
              {APPS_DATA.map((app) => (
                <a
                  key={app.name}
                  href={app.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex flex-col items-center gap-3 p-6 border border-white/[.06] rounded-sm transition-all hover:border-white/20 hover:bg-white/[.02]"
                >
                  <img
                    src={`https://www.google.com/s2/favicons?domain=${app.domain}&sz=64`}
                    alt={app.name}
                    className="w-10 h-10 rounded-sm"
                  />
                  <span className="text-xs uppercase tracking-[0.15em] text-[#71717a] group-hover:text-[#a1a1aa] transition-colors">
                    {app.name}
                  </span>
                </a>
              ))}
            </div>
            {/* Rota AI — center, bottom */}
            <div className="flex justify-center mt-6">
              <div
                className="flex items-center gap-3 px-8 py-4 rounded-sm"
                style={{
                  border: "1px solid rgba(228,242,34,0.25)",
                  background: "rgba(228,242,34,0.04)",
                }}
              >
                <div className="w-9 h-9 bg-[#e4f222] flex items-center justify-center rounded-sm">
                  <Mic size={18} className="text-black" />
                </div>
                <span className="text-sm font-semibold tracking-[0.15em] uppercase text-[#fafafa]">Rota AI</span>
                <span className="text-xs text-[#71717a] tracking-wider">injects here</span>
              </div>
            </div>
            <p className="text-center text-[11px] text-[#50545a] mt-4 uppercase tracking-[0.2em]">
              + Cursor, Figma, Telegram, and every other text field
            </p>
          </FadeIn>
        </div>
      </section>

      {/* ── Comparison ── */}
      <section
        id="comparison"
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-4xl mx-auto">
          <FadeIn>
            <SectionLabel n="04" title="Comparison" />
          </FadeIn>
          <FadeIn className="mb-14">
            <h2
              className="font-display uppercase leading-[0.92] tracking-[0.02em]"
              style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}
            >
              Why Rota AI?
            </h2>
          </FadeIn>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/[.06]">
                  <th className="text-left py-4 pr-6 text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono">Feature</th>
                  <th className="text-center py-4 px-4 text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono">Wispr Flow</th>
                  <th className="text-center py-4 px-4 text-xs uppercase tracking-[0.2em] text-[#50545a] font-mono">SuperWhisper</th>
                  <th className="text-center py-4 pl-4 text-xs uppercase tracking-[0.2em] text-[#e4f222] font-mono">Rota AI</th>
                </tr>
              </thead>
              <tbody>
                {COMPARE_ROWS.map((row, i) => (
                  <tr key={i} className="border-b border-white/[.03]">
                    <td className="py-4 pr-6 text-[#a1a1aa]">{row.feature}</td>
                    <td className="py-4 px-4 text-center text-[#50545a]">{row.wispr}</td>
                    <td className="py-4 px-4 text-center text-[#50545a]">{row.superwhisper}</td>
                    <td className={`py-4 pl-4 text-center ${row.rotaBold ? "text-[#e4f222] font-semibold" : "text-[#a1a1aa]"}`}>{row.rota}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section
        className="py-28 px-6 sm:px-10"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="max-w-2xl mx-auto">
          <FadeIn>
            <SectionLabel n="05" title="FAQ" />
          </FadeIn>
          <div className="space-y-px bg-white/[.04]">
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
              style={{ fontSize: "clamp(36px, 5.5vw, 72px)", color: "#fafafa" }}
            >
              Download &amp;
              <br />
              <span style={{ color: "#e4f222" }}>start speaking.</span>
            </h2>
          </FadeIn>
          <FadeIn delay={0.1}>
            <p className="text-sm mb-10 max-w-md text-[#a1a1aa]">
              Windows, Mac &amp; Linux · Free &amp; open source · No account needed
            </p>
            <button
              onClick={() => setDownloadModalOpen(true)}
              className="group inline-flex items-center gap-3 px-8 py-4 text-sm font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 active:scale-[0.98]"
              style={{
                background: "#e4f222",
                color: "#000",
                borderRadius: 2,
                boxShadow: "0 4px 24px rgba(228,242,34,0.25)",
                border: "none",
                cursor: "pointer",
                font: "inherit",
              }}
            >
              <Download className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
              Download Rota AI
            </button>

            {/* Share */}
            <ShareButton />
          </FadeIn>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-12">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-[#e4f222] flex items-center justify-center rounded-sm">
               <Mic className="text-black" size={16} />
            </div>
            <span className="text-sm font-bold text-white tracking-widest uppercase">ROTA AI</span>
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
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-5 text-left"
        style={{ background: "none", border: "none", cursor: "pointer", font: "inherit" }}
      >
        <span className="text-sm text-white pr-4">{question}</span>
        <ChevronDown
          className="w-4 h-4 text-[#50545a] shrink-0 transition-transform duration-200"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
        />
      </button>
      {open && (
        <div className="px-6 pb-5">
          <p className="text-sm leading-relaxed text-[#71717a]">{answer}</p>
        </div>
      )}
    </div>
  );
}
