"use client";

import React from "react";

interface DiagramProps {
  type: string;
}

export function ArchitecturalDiagram({ type }: DiagramProps) {
  return (
    <div className="w-full my-8 overflow-x-auto">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .excalidraw-font {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
      `}</style>

      {type.includes("selected-backend") || type.includes("Selected Backend") ? (
        <BackendRoutingDiagram />
      ) : type.includes("WH_KEYBOARD_LL") ? (
        <WindowsExecutionDiagram />
      ) : type.includes("Quartz CGEventTap") ? (
        <MacExecutionDiagram />
      ) : type.includes("evdev /dev/input/") ? (
        <LinuxExecutionDiagram />
      ) : type.includes("Clone Repo & Git LFS") ? (
        <LocalSetupDiagram />
      ) : type.includes("Check dictionary") || type.includes("DictionaryOverrideDiagram") ? (
        <DictionaryOverrideDiagram />
      ) : type.includes("sounddevice") || type.includes("sequenceDiagram") ? (
        <AudioPipelineDiagram />
      ) : type.includes("evdev") || type.includes("ModelLoader") ? (
        <ThreadingModelDiagram />
      ) : (
        <SystemOverviewDiagram />
      )}
    </div>
  );
}

// Helper Arrow Definition
const SVGDefs = () => (
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#a1a1aa" />
    </marker>
  </defs>
);

// ──────────────────────────────────────────────────────────────────────
// 1. SYSTEM OVERVIEW DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function SystemOverviewDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 520" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* 1. PyQt6 UI Layer */}
        <rect x="260" y="30" width="280" height="70" rx="6" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="400" y="62" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">1. PyQt6 UI Layer</text>
        <text x="400" y="80" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">Tray Icon / Floating Recording Pill / Dashboards</text>

        {/* Connection UI -> Controller */}
        <path d="M 400 100 L 400 150" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text x="412" y="130" fill="#71717a" className="excalidraw-font text-[11px]">Signals / Events</text>

        {/* 2. App Controller & State Mixins */}
        <rect x="260" y="160" width="280" height="70" rx="6" fill="#a1a1aa" fillOpacity="0.03" stroke="#a1a1aa" strokeWidth="2" />
        <text x="400" y="192" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">2. Controller &amp; State Mixins</text>
        <text x="400" y="210" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">RecordingState, Hotkeys, and Thread Pipelines</text>

        {/* Connections Controller -> Subsystems */}
        <path d="M 330 230 Q 240 250 190 280" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text x="210" y="255" fill="#71717a" className="excalidraw-font text-[10px]" textAnchor="middle">OS Binding</text>

        <path d="M 470 230 Q 560 250 610 280" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text x="590" y="255" fill="#71717a" className="excalidraw-font text-[10px]" textAnchor="middle">Audio Ingest</text>

        {/* 3A. Platform Abstraction Layer */}
        <rect x="50" y="290" width="280" height="90" rx="6" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="190" y="322" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">3A. Platform Abstraction Layer</text>
        <text x="190" y="342" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">plat/ OS Hook Bindings</text>
        <text x="190" y="362" textAnchor="middle" fill="#3b82f6" className="excalidraw-font text-[10px]">Windows / macOS / Linux</text>

        {/* 3B. Audio & ASR Engine */}
        <rect x="470" y="290" width="280" height="90" rx="6" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="610" y="322" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">3B. Audio &amp; ASR Engine</text>
        <text x="610" y="342" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">audio/ Sounddevice Recorder</text>
        <text x="610" y="362" textAnchor="middle" fill="#10b981" className="excalidraw-font text-[10px]">Silero VAD / Local &amp; Cloud Whisper</text>

        {/* Connections Subsystems -> Infrastructure */}
        <path d="M 190 380 L 190 410" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <path d="M 610 380 L 610 410" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* 4A. Security & DB Storage */}
        <rect x="50" y="420" width="280" height="60" rx="6" fill="#f59e0b" fillOpacity="0.04" stroke="#f59e0b" strokeWidth="2" />
        <text x="190" y="455" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">SQLite Storage &amp; DPAPI Keyrings</text>

        {/* 4B. LLM & OS Injector */}
        <rect x="470" y="420" width="280" height="60" rx="6" fill="#ef4444" fillOpacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="610" y="455" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">LLM Post-Processing &amp; Injection</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 2. AUDIO PIPELINE SEQUENCE DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function AudioPipelineDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 170" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* 1. Mic Ingest */}
        <rect x="15" y="40" width="120" height="90" rx="6" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="75" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">1. Mic Ingest</text>
        <text x="75" y="95" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">16kHz Mono</text>
        <text x="75" y="110" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Float32 PCM</text>

        <path d="M 135 85 L 165 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* 2. VAD Filter */}
        <rect x="175" y="40" width="120" height="90" rx="6" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">2. VAD Slicing</text>
        <text x="235" y="95" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Silero ONNX</text>
        <text x="235" y="110" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">300ms Padding</text>

        <path d="M 295 85 L 325 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* 3. ASR Transcription */}
        <rect x="335" y="40" width="130" height="90" rx="6" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="400" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">3. Whisper ASR</text>
        <text x="400" y="95" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Groq / Gemini /</text>
        <text x="400" y="110" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Local CTranslate2</text>

        <path d="M 465 85 L 495 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* 4. LLM Clean */}
        <rect x="505" y="40" width="120" height="90" rx="6" fill="#f59e0b" fillOpacity="0.04" stroke="#f59e0b" strokeWidth="2" />
        <text x="565" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">4. LLM Clean</text>
        <text x="565" y="95" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Grammar &amp; Tone</text>
        <text x="565" y="110" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Context Prompts</text>

        <path d="M 625 85 L 655 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* 5. OS Injection */}
        <rect x="665" y="40" width="120" height="90" rx="6" fill="#ef4444" fillOpacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="725" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">5. Injection</text>
        <text x="725" y="95" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Virtual Keyboard</text>
        <text x="725" y="110" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Clipboard Paste</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 3. THREADING MODEL DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function ThreadingModelDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 300" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* Thread Box 1: Main Thread */}
        <rect x="20" y="10" width="320" height="280" rx="8" fill="none" stroke="#71717a" strokeWidth="1.5" strokeDasharray="4,4" />
        <text x="40" y="35" fill="#a1a1aa" className="excalidraw-font text-xs uppercase tracking-wider font-semibold">1. Main GUI Thread (PyQt6 Event Loop)</text>

        <rect x="40" y="60" width="280" height="50" rx="4" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="1.5" />
        <text x="180" y="90" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Window Dashboard &amp; System Tray</text>

        <rect x="40" y="130" width="280" height="50" rx="4" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="1.5" />
        <text x="180" y="160" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Floating Recording Pill Overlay</text>

        <rect x="40" y="200" width="280" height="50" rx="4" fill="#a1a1aa" fillOpacity="0.03" stroke="#a1a1aa" strokeWidth="1.5" />
        <text x="180" y="230" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">App State Mixins (Coordinator)</text>

        {/* Thread Box 2: Background Threads */}
        <rect x="460" y="10" width="320" height="280" rx="8" fill="none" stroke="#71717a" strokeWidth="1.5" strokeDasharray="4,4" />
        <text x="480" y="35" fill="#a1a1aa" className="excalidraw-font text-xs uppercase tracking-wider font-semibold">2. Background Threads &amp; Daemons</text>

        <rect x="480" y="60" width="280" height="50" rx="4" fill="#ef4444" fillOpacity="0.04" stroke="#ef4444" strokeWidth="1.5" />
        <text x="620" y="90" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Global Hotkey Listener (Daemon)</text>

        <rect x="480" y="130" width="280" height="50" rx="4" fill="#f59e0b" fillOpacity="0.04" stroke="#f59e0b" strokeWidth="1.5" />
        <text x="620" y="160" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Model Loader QThread</text>

        <rect x="480" y="200" width="280" height="50" rx="4" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="1.5" />
        <text x="620" y="230" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">ASR &amp; LLM Pipeline Worker</text>

        {/* Signals Connecting Thread Bounds */}
        <path d="M 480 85 Q 390 95 320 140" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text x="390" y="105" fill="#71717a" className="excalidraw-font text-[9px]" textAnchor="middle">Hotkey click callback</text>

        <path d="M 480 155 Q 400 155 320 155" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text x="400" y="145" fill="#71717a" className="excalidraw-font text-[9px]" textAnchor="middle">Ready signal</text>

        <path d="M 480 225 Q 390 215 320 170" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text x="400" y="200" fill="#71717a" className="excalidraw-font text-[9px]" textAnchor="middle">Payload returned</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 4. TRANSCRIPTION BACKEND ROUTING DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function BackendRoutingDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 200" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* Invisible text paths for arrow text alignment */}
        <path id="groq-text-path" d="M 280 88 L 410 38" fill="none" />
        <path id="gemini-text-path" d="M 280 88 L 410 88" fill="none" />
        <path id="local-text-path" d="M 280 92 L 410 142" fill="none" />

        {/* Core App */}
        <rect x="30" y="65" width="120" height="70" rx="5" fill="#a1a1aa" fillOpacity="0.04" stroke="#a1a1aa" strokeWidth="2" />
        <text x="90" y="100" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="90" y="115" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Captures Audio</text>

        {/* Arrow to Router */}
        <path d="M 150 100 L 200 100" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Router Box */}
        <polygon points="240,55 280,100 240,145 200,100" fill="#f59e0b" fillOpacity="0.04" stroke="#f59e0b" strokeWidth="2" />
        <text x="240" y="104" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-[10px] font-semibold">Config</text>

        {/* Split Routes with aligned arrows and text paths */}
        {/* Top: Groq */}
        <path d="M 280 100 L 410 50" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text className="excalidraw-font text-[9px]" fill="#71717a">
          <textPath href="#groq-text-path" startOffset="50%" textAnchor="middle">
            Groq Key
          </textPath>
        </text>

        {/* Mid: Gemini */}
        <path d="M 280 100 L 410 100" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text className="excalidraw-font text-[9px]" fill="#71717a">
          <textPath href="#gemini-text-path" startOffset="50%" textAnchor="middle">
            Gemini Key
          </textPath>
        </text>

        {/* Bottom: Local Client */}
        <path d="M 280 100 L 410 150" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />
        <text className="excalidraw-font text-[9px]" fill="#71717a">
          <textPath href="#local-text-path" startOffset="50%" textAnchor="middle">
            Local Client
          </textPath>
        </text>

        {/* Backends */}
        <rect x="420" y="20" width="150" height="50" rx="4" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="1.5" />
        <text x="495" y="48" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs">Groq Whisper API</text>

        <rect x="420" y="75" width="150" height="50" rx="4" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="1.5" />
        <text x="495" y="103" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs">Gemini Studio API</text>

        <rect x="420" y="130" width="150" height="50" rx="4" fill="#ef4444" fillOpacity="0.04" stroke="#ef4444" strokeWidth="1.5" />
        <text x="495" y="158" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs">Ollama (Local Port)</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 5. WINDOWS EXECUTION DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function WindowsExecutionDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 180" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* User Hotkey */}
        <rect x="20" y="45" width="100" height="80" rx="5" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="70" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Hotkey F9</text>
        <text x="70" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(Global Keypress)</text>

        <path d="M 120 85 L 160 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Keyboard Hook */}
        <rect x="170" y="45" width="130" height="80" rx="5" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">SetWindowsHookEx</text>
        <text x="235" y="92" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">pynput daemon</text>
        <text x="235" y="107" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">WH_KEYBOARD_LL</text>

        <path d="M 300 85 L 340 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Main Application */}
        <rect x="350" y="45" width="110" height="80" rx="5" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="405" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="405" y="98" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Processes WAV</text>

        <path d="M 460 85 L 500 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* OS Injection */}
        <rect x="510" y="45" width="80" height="80" rx="5" fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="550" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">SendInput</text>
        <text x="550" y="92" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Win32 paste</text>
        <text x="550" y="107" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">events</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 6. MAC EXECUTION DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function MacExecutionDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 180" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* User Hotkey */}
        <rect x="20" y="45" width="100" height="80" rx="5" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="70" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Hotkey F9</text>
        <text x="70" y="98" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(Global Keypress)</text>

        <path d="M 120 85 L 160 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Keyboard Hook */}
        <rect x="170" y="45" width="130" height="80" rx="5" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">CGEventTap</text>
        <text x="235" y="92" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Quartz daemon</text>
        <text x="235" y="107" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">CoreGraphics</text>

        <path d="M 300 85 L 340 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Main Application */}
        <rect x="350" y="45" width="110" height="80" rx="5" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="405" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="405" y="98" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Processes WAV</text>

        <path d="M 460 85 L 500 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* OS Injection */}
        <rect x="510" y="45" width="80" height="80" rx="5" fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="550" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">AXUIElement</text>
        <text x="550" y="92" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Accessibility</text>
        <text x="550" y="107" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">API Injection</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 7. LINUX EXECUTION DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function LinuxExecutionDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 180" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* User Hotkey */}
        <rect x="20" y="45" width="100" height="80" rx="5" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="70" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Hotkey F9</text>
        <text x="70" y="98" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(Global Keypress)</text>

        <path d="M 120 85 L 160 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Keyboard Hook */}
        <rect x="170" y="45" width="130" height="80" rx="5" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">evdev / dev/input</text>
        <text x="235" y="92" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Input group daemon</text>
        <text x="235" y="107" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(X11: pynput)</text>

        <path d="M 300 85 L 340 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Main Application */}
        <rect x="350" y="45" width="110" height="80" rx="5" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="405" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="405" y="98" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Processes WAV</text>

        <path d="M 460 85 L 500 85" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* OS Injection */}
        <rect x="510" y="45" width="80" height="80" rx="5" fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="550" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">wtype / xdotool</text>
        <text x="550" y="92" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Wayland type tool</text>
        <text x="550" y="107" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">or X11 events</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 8. LOCAL SETUP FLOW CHART
// ──────────────────────────────────────────────────────────────────────
function LocalSetupDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 130" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* Step 1: Git Clone */}
        <rect x="15" y="30" width="120" height="70" rx="5" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="75" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">1. Git Clone</text>
        <text x="75" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Setup Git LFS</text>

        <path d="M 135 65 L 165 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 2: C-Libraries */}
        <rect x="175" y="30" width="120" height="70" rx="5" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="235" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">2. C-Libraries</text>
        <text x="235" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">PortAudio headers</text>

        <path d="M 295 65 L 325 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 3: Venv */}
        <rect x="335" y="30" width="120" height="70" rx="5" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="395" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">3. Create Venv</text>
        <text x="395" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Python 3.12+</text>

        <path d="M 455 65 L 485 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 4: pip install */}
        <rect x="495" y="30" width="130" height="70" rx="5" fill="#f59e0b" fillOpacity="0.04" stroke="#f59e0b" strokeWidth="2" />
        <text x="560" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">4. Install Packages</text>
        <text x="560" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">pip requirements</text>

        <path d="M 625 65 L 655 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 5: Start App */}
        <rect x="665" y="30" width="120" height="70" rx="5" fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="725" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">5. Run Application</text>
        <text x="725" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">python app/main.py</text>
      </svg>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────
// 9. DICTIONARY OVERRIDE FLOW DIAGRAM
// ──────────────────────────────────────────────────────────────────────
function DictionaryOverrideDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 130" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* Step 1: Input */}
        <rect x="15" y="30" width="120" height="70" rx="5" fill="#3b82f6" fillOpacity="0.04" stroke="#3b82f6" strokeWidth="2" />
        <text x="75" y="65" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">1. Input Audio</text>
        <text x="75" y="83" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">F9 click dictation</text>

        <path d="M 135 65 L 165 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 2: Terms Lookup */}
        <rect x="175" y="30" width="120" height="70" rx="5" fill="#10b981" fillOpacity="0.04" stroke="#10b981" strokeWidth="2" />
        <text x="235" y="65" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">2. Terms Lookup</text>
        <text x="235" y="83" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Reads custom list</text>

        <path d="M 295 65 L 325 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 3: Whisper ASR Prompt */}
        <rect x="335" y="30" width="120" height="70" rx="5" fill="#e4f222" fillOpacity="0.04" stroke="#e4f222" strokeWidth="2" />
        <text x="395" y="65" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">3. Whisper ASR</text>
        <text x="395" y="83" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Prompt parameter</text>

        <path d="M 455 65 L 485 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 4: String Replacer */}
        <rect x="495" y="30" width="130" height="70" rx="5" fill="#f59e0b" fillOpacity="0.04" stroke="#f59e0b" strokeWidth="2" />
        <text x="560" y="65" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">4. String Override</text>
        <text x="560" y="83" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Hard substitution pass</text>

        <path d="M 625 65 L 655 65" stroke="#a1a1aa" strokeWidth="1.5" markerEnd="url(#arrow)" />

        {/* Step 5: Clean Output */}
        <rect x="665" y="30" width="120" height="70" rx="5" fill="#ef4444" fill-opacity="0.04" stroke="#ef4444" strokeWidth="2" />
        <text x="725" y="65" text-anchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">5. Inject Output</text>
        <text x="725" y="83" text-anchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Correct casings typed</text>
      </svg>
    </div>
  );
}
