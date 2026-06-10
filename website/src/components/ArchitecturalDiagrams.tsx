"use client";

import React, { useState, useEffect, useRef } from "react";

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
      ) : type.includes("ASR Prompt") || type.includes("Hard Replacer") ? (
        <DictionaryPipelineDiagram />
      ) : type.includes("Check dictionary") || type.includes("DictionaryOverrideDiagram") ? (
        <DictionaryOverrideDiagram />
      ) : type.includes("sounddevice") || type.includes("sequenceDiagram") ? (
        <AudioPipelineDiagram />
      ) : type.includes("evdev") || type.includes("ModelLoader") ? (
        <ThreadingModelDiagram />
      ) : type.includes("Full Application Lifecycle") || type.includes("Instance Mutex") ? (
        <FullApplicationLifecycleDiagram />
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
// DETAILED WOBBLY (EXCALIDRAW) PRIMITIVES (DETERMINISTIC TO PREVENT JITTER)
// ──────────────────────────────────────────────────────────────────────

function getDeterministicSketchyPath(x1: number, y1: number, x2: number, y2: number, seedOffset = 0): string {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const distance = Math.sqrt(dx * dx + dy * dy);
  if (distance === 0) return "";

  // Deterministic seed based on coordinates
  const seedBase = Math.abs(x1 * 31 + y1 * 73 + x2 * 107 + y2 * 139 + seedOffset);

  // Number of segments depends on line length
  const segments = Math.max(2, Math.floor(distance / 25));

  // Helper for deterministic random numbers in range [-0.5, 0.5]
  const getRandomValue = (index: number) => {
    const s = seedBase + index * 97;
    const val = Math.sin(s) * 10000;
    return (val - Math.floor(val)) - 0.5;
  };

  let path = `M ${x1.toFixed(1)} ${y1.toFixed(1)}`;

  // Direction vectors
  const perpX = -dy / distance;
  const perpY = dx / distance;

  for (let i = 1; i < segments; i++) {
    const t = i / segments;
    const px = x1 + dx * t;
    const py = y1 + dy * t;

    // Max noise amplitude scales with length, up to 1.8 pixels
    const maxNoise = Math.min(1.8, distance * 0.05);
    const noise = getRandomValue(i) * maxNoise;

    const nx = px + perpX * noise;
    const ny = py + perpY * noise;

    path += ` L ${nx.toFixed(1)} ${ny.toFixed(1)}`;
  }

  // Add a slight overshoot at the end
  const overshootAmount = 1.5;
  const endNoiseX = getRandomValue(segments) * overshootAmount;
  const endNoiseY = getRandomValue(segments + 1) * overshootAmount;

  path += ` L ${(x2 + endNoiseX).toFixed(1)} ${(y2 + endNoiseY).toFixed(1)}`;

  return path;
}

function getDeterministicSketchyCurvePath(x1: number, y1: number, qx: number, qy: number, x2: number, y2: number, seedOffset = 0): string {
  const points: { x: number; y: number }[] = [];
  const segments = 10;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const x = (1 - t) * (1 - t) * x1 + 2 * (1 - t) * t * qx + t * t * x2;
    const y = (1 - t) * (1 - t) * y1 + 2 * (1 - t) * t * qy + t * t * y2;
    points.push({ x, y });
  }

  const seedBase = Math.abs(x1 * 31 + y1 * 73 + x2 * 107 + y2 * 139 + seedOffset);
  const getRandomValue = (index: number) => {
    const s = seedBase + index * 97;
    const val = Math.sin(s) * 10000;
    return (val - Math.floor(val)) - 0.5;
  };

  let path = `M ${x1.toFixed(1)} ${y1.toFixed(1)}`;
  for (let i = 1; i <= segments; i++) {
    const p = points[i];
    const dx = p.x - points[i - 1].x;
    const dy = p.y - points[i - 1].y;
    const len = Math.sqrt(dx * dx + dy * dy);
    const perpX = len > 0 ? -dy / len : 0;
    const perpY = len > 0 ? dx / len : 0;

    const noise = getRandomValue(i) * 1.5;
    const nx = p.x + perpX * noise;
    const ny = p.y + perpY * noise;

    path += ` L ${nx.toFixed(1)} ${ny.toFixed(1)}`;
  }
  return path;
}

interface SketchyLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  stroke?: string;
  strokeWidth?: number;
  markerEnd?: string;
  className?: string;
  strokeDasharray?: string;
}

export function SketchyLine({
  x1,
  y1,
  x2,
  y2,
  stroke = "#a1a1aa",
  strokeWidth = 1.5,
  markerEnd,
  className,
  strokeDasharray,
  ...props
}: SketchyLineProps) {
  const path1 = getDeterministicSketchyPath(x1, y1, x2, y2, 0);
  const path2 = getDeterministicSketchyPath(x1, y1, x2, y2, 500);

  return (
    <g className={className}>
      {markerEnd && (
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="none" fill="none" markerEnd={markerEnd} />
      )}
      <path d={path1} stroke={stroke} strokeWidth={strokeWidth} fill="none" strokeDasharray={strokeDasharray} {...props} />
      <path d={path2} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} strokeDasharray={strokeDasharray} {...props} />
    </g>
  );
}

interface SketchyCurveProps {
  x1: number;
  y1: number;
  qx: number;
  qy: number;
  x2: number;
  y2: number;
  stroke?: string;
  strokeWidth?: number;
  markerEnd?: string;
  className?: string;
  strokeDasharray?: string;
}

export function SketchyCurve({
  x1,
  y1,
  qx,
  qy,
  x2,
  y2,
  stroke = "#a1a1aa",
  strokeWidth = 1.5,
  markerEnd,
  className,
  strokeDasharray,
  ...props
}: SketchyCurveProps) {
  const path1 = getDeterministicSketchyCurvePath(x1, y1, qx, qy, x2, y2, 0);
  const path2 = getDeterministicSketchyCurvePath(x1, y1, qx, qy, x2, y2, 500);

  return (
    <g className={className}>
      {markerEnd && (
        <path d={`M ${x1} ${y1} Q ${qx} ${qy} ${x2} ${y2}`} stroke="none" fill="none" markerEnd={markerEnd} />
      )}
      <path d={path1} stroke={stroke} strokeWidth={strokeWidth} fill="none" strokeDasharray={strokeDasharray} {...props} />
      <path d={path2} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} strokeDasharray={strokeDasharray} {...props} />
    </g>
  );
}

interface SketchyRectProps {
  x: number;
  y: number;
  width: number;
  height: number;
  stroke?: string;
  fill?: string;
  fillOpacity?: number;
  strokeWidth?: number;
  className?: string;
}

export function SketchyRect({
  x,
  y,
  width,
  height,
  stroke = "#a1a1aa",
  fill,
  fillOpacity = 0.04,
  strokeWidth = 1.5,
  className,
  ...props
}: SketchyRectProps) {
  const xLeft = x;
  const xRight = x + width;
  const yTop = y;
  const yBottom = y + height;

  const top1 = getDeterministicSketchyPath(xLeft, yTop, xRight, yTop, 10);
  const top2 = getDeterministicSketchyPath(xLeft, yTop, xRight, yTop, 20);

  const right1 = getDeterministicSketchyPath(xRight, yTop, xRight, yBottom, 30);
  const right2 = getDeterministicSketchyPath(xRight, yTop, xRight, yBottom, 40);

  const bottom1 = getDeterministicSketchyPath(xRight, yBottom, xLeft, yBottom, 50);
  const bottom2 = getDeterministicSketchyPath(xRight, yBottom, xLeft, yBottom, 60);

  const left1 = getDeterministicSketchyPath(xLeft, yBottom, xLeft, yTop, 70);
  const left2 = getDeterministicSketchyPath(xLeft, yBottom, xLeft, yTop, 80);

  return (
    <g className={className}>
      {fill && (
        <rect x={x} y={y} width={width} height={height} fill={fill} fillOpacity={fillOpacity} stroke="none" />
      )}
      <path d={top1} stroke={stroke} strokeWidth={strokeWidth} fill="none" />
      <path d={top2} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} />

      <path d={right1} stroke={stroke} strokeWidth={strokeWidth} fill="none" />
      <path d={right2} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} />

      <path d={bottom1} stroke={stroke} strokeWidth={strokeWidth} fill="none" />
      <path d={bottom2} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} />

      <path d={left1} stroke={stroke} strokeWidth={strokeWidth} fill="none" />
      <path d={left2} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} />
    </g>
  );
}

interface SketchyPolygonProps {
  points: { x: number; y: number }[];
  stroke?: string;
  fill?: string;
  fillOpacity?: number;
  strokeWidth?: number;
  className?: string;
}

export function SketchyPolygon({
  points,
  stroke = "#a1a1aa",
  fill,
  fillOpacity = 0.04,
  strokeWidth = 1.5,
  className,
  ...props
}: SketchyPolygonProps) {
  if (!points || points.length < 2) return null;

  const lines: string[][] = [];
  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];

    lines.push([
      getDeterministicSketchyPath(p1.x, p1.y, p2.x, p2.y, i * 100 + 1),
      getDeterministicSketchyPath(p1.x, p1.y, p2.x, p2.y, i * 100 + 50)
    ]);
  }

  const pointsStr = points.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <g className={className}>
      {fill && (
        <polygon points={pointsStr} fill={fill} fillOpacity={fillOpacity} stroke="none" />
      )}
      {lines.map((line, idx) => (
        <React.Fragment key={idx}>
          <path d={line[0]} stroke={stroke} strokeWidth={strokeWidth} fill="none" />
          <path d={line[1]} stroke={stroke} strokeWidth={strokeWidth * 0.75} fill="none" opacity={0.5} />
        </React.Fragment>
      ))}
    </g>
  );
}

// ──────────────────────────────────────────────────────────────────────
// DIAGRAM COMPONENTS
// ──────────────────────────────────────────────────────────────────────

function SystemOverviewDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 520" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={260} y={30} width={280} height={70} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x={400} y={62} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">1. PyQt6 UI Layer</text>
        <text x={400} y={80} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">Tray Icon / Floating Recording Pill / Dashboards</text>
        <SketchyLine x1={400} y1={100} x2={400} y2={150} markerEnd="url(#arrow)" />
        <text x={412} y={130} fill="#71717a" className="excalidraw-font text-[11px]">Signals / Events</text>
        <SketchyRect x={260} y={160} width={280} height={70} stroke="#a1a1aa" fill="#a1a1aa" fillOpacity={0.03} />
        <text x={400} y={192} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">2. Controller &amp; State Mixins</text>
        <text x={400} y={210} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">RecordingState, Hotkeys, and Thread Pipelines</text>

        <SketchyCurve x1={330} y1={230} qx={240} qy={250} x2={190} y2={280} markerEnd="url(#arrow)" />
        <text x={210} y={255} fill="#71717a" className="excalidraw-font text-[10px]" textAnchor="middle">OS Binding</text>

        <SketchyCurve x1={470} y1={230} qx={560} qy={250} x2={610} y2={280} markerEnd="url(#arrow)" />
        <text x={590} y={255} fill="#71717a" className="excalidraw-font text-[10px]" textAnchor="middle">Audio Ingest</text>

        <SketchyRect x={50} y={290} width={280} height={90} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x={190} y={322} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">3A. Platform Abstraction Layer</text>
        <text x={190} y={342} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">plat/ OS Hook Bindings</text>
        <text x={190} y={362} textAnchor="middle" fill="#3b82f6" className="excalidraw-font text-[10px]">Windows / macOS / Linux</text>

        <SketchyRect x={470} y={290} width={280} height={90} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x={610} y={322} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-base font-semibold">3B. Audio &amp; ASR Engine</text>
        <text x={610} y={342} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[10px]">audio/ Sounddevice Recorder</text>
        <text x={610} y={362} textAnchor="middle" fill="#10b981" className="excalidraw-font text-[10px]">Silero VAD / Local &amp; Cloud Whisper</text>

        <SketchyLine x1={190} y1={380} x2={190} y2={410} markerEnd="url(#arrow)" />
        <SketchyLine x1={610} y1={380} x2={610} y2={410} markerEnd="url(#arrow)" />

        <SketchyRect x={50} y={420} width={280} height={60} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x={190} y={455} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">SQLite Storage &amp; DPAPI Keyrings</text>

        <SketchyRect x={470} y={420} width={280} height={60} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x={610} y={455} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">LLM Post-Processing &amp; Injection</text>
      </svg>
    </div>
  );
}

function AudioPipelineDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 170" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={15} y={40} width={120} height={90} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x={75} y={75} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">1. Mic Ingest</text>
        <text x={75} y={95} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">16kHz Mono</text>
        <text x={75} y={110} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Float32 PCM</text>
        <SketchyLine x1={135} y1={85} x2={165} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={175} y={40} width={120} height={90} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x={235} y={75} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">2. VAD Slicing</text>
        <text x={235} y={95} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Silero ONNX</text>
        <text x={235} y={110} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">300ms Padding</text>
        <SketchyLine x1={295} y1={85} x2={325} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={335} y={40} width={130} height={90} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x={400} y={75} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">3. Whisper ASR</text>
        <text x={400} y={95} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Groq / Gemini /</text>
        <text x={400} y={110} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Local CTranslate2</text>
        <SketchyLine x1={465} y1={85} x2={495} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={505} y={40} width={120} height={90} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x={565} y={75} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">4. LLM Clean</text>
        <text x={565} y={95} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Grammar &amp; Tone</text>
        <text x={565} y={110} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Context Prompts</text>
        <SketchyLine x1={625} y1={85} x2={655} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={665} y={40} width={120} height={90} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x={725} y={75} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-sm font-semibold">5. Injection</text>
        <text x={725} y={95} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Virtual Keyboard</text>
        <text x={725} y={110} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Clipboard Paste</text>
      </svg>
    </div>
  );
}

function ThreadingModelDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 300" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        {/* Dashed outer boundary */}
        <path d="M 20 10 L 340 10 L 340 290 L 20 290 Z" stroke="#71717a" strokeWidth={1.5} strokeDasharray="4,4" />
        <text x="40" y="35" fill="#a1a1aa" className="excalidraw-font text-xs uppercase tracking-wider font-semibold">1. Main GUI Thread (PyQt6 Event Loop)</text>

        <SketchyRect x={40} y={60} width={280} height={50} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x="180" y="90" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Window Dashboard &amp; System Tray</text>

        <SketchyRect x={40} y={130} width={280} height={50} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x="180" y="160" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Floating Recording Pill Overlay</text>

        <SketchyRect x={40} y={200} width={280} height={50} stroke="#a1a1aa" fill="#a1a1aa" fillOpacity={0.03} />
        <text x="180" y="230" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">App State Mixins (Coordinator)</text>

        {/* Dashed outer boundary 2 */}
        <path d="M 460 10 L 780 10 L 780 290 L 460 290 Z" stroke="#71717a" strokeWidth={1.5} strokeDasharray="4,4" />
        <text x="480" y="35" fill="#a1a1aa" className="excalidraw-font text-xs uppercase tracking-wider font-semibold">2. Background Threads &amp; Daemons</text>

        <SketchyRect x={480} y={60} width={280} height={50} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x="620" y="90" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Global Hotkey Listener (Daemon)</text>

        <SketchyRect x={480} y={130} width={280} height={50} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x="620" y="160" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Model Loader QThread</text>

        <SketchyRect x={480} y={200} width={280} height={50} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x="620" y="230" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">ASR &amp; LLM Pipeline Worker</text>

        <SketchyLine x1={480} y1={85} x2={320} y2={140} markerEnd="url(#arrow)" />
        <text x="400" y="105" fill="#71717a" className="excalidraw-font text-[9px]" textAnchor="middle">Hotkey click callback</text>

        <SketchyLine x1={480} y1={155} x2={320} y2={155} markerEnd="url(#arrow)" />
        <text x="400" y="145" fill="#71717a" className="excalidraw-font text-[9px]" textAnchor="middle">Ready signal</text>

        <SketchyLine x1={480} y1={225} x2={320} y2={170} markerEnd="url(#arrow)" />
        <text x="400" y="200" fill="#71717a" className="excalidraw-font text-[9px]" textAnchor="middle">Payload returned</text>
      </svg>
    </div>
  );
}

function BackendRoutingDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 200" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={30} y={65} width={120} height={70} stroke="#a1a1aa" fill="#a1a1aa" fillOpacity={0.04} />
        <text x="90" y="100" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="90" y="115" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Captures Audio</text>

        <SketchyLine x1={150} y1={100} x2={200} y2={100} markerEnd="url(#arrow)" />

        <SketchyPolygon points={[{ x: 240, y: 55 }, { x: 280, y: 100 }, { x: 240, y: 145 }, { x: 200, y: 100 }]} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x="240" y="104" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-[10px] font-semibold">Config</text>

        {/* Dynamic Arrows */}
        <SketchyLine x1={280} y1={100} x2={410} y2={50} markerEnd="url(#arrow)" />
        <text x={345} y={65} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Groq Key</text>

        <SketchyLine x1={280} y1={100} x2={410} y2={100} markerEnd="url(#arrow)" />
        <text x={345} y={92} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Gemini Key</text>

        <SketchyLine x1={280} y1={100} x2={410} y2={150} markerEnd="url(#arrow)" />
        <text x={345} y={135} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Local Client</text>

        {/* Targets */}
        <SketchyRect x={420} y={20} width={150} height={50} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x="495" y="48" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs">Groq Whisper API</text>

        <SketchyRect x={420} y={75} width={150} height={50} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x="495" y="103" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs">Gemini Studio API</text>

        <SketchyRect x={420} y={130} width={150} height={50} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x="495" y="158" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs">Ollama (Local Port)</text>
      </svg>
    </div>
  );
}

function WindowsExecutionDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 180" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={20} y={45} width={100} height={80} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x="70" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Hotkey F9</text>
        <text x="70" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(Global Keypress)</text>

        <SketchyLine x1={120} y1={85} x2={160} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={170} y={45} width={130} height={80} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">SetWindowsHookEx</text>
        <text x="235" y="92" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">pynput daemon</text>
        <text x="235" y="107" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">WH_KEYBOARD_LL</text>

        <SketchyLine x1={300} y1={85} x2={340} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={350} y={45} width={110} height={80} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x="405" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="405" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Processes WAV</text>

        <SketchyLine x1={460} y1={85} x2={500} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={510} y={45} width={80} height={80} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x="550" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">SendInput</text>
        <text x="550" y="92" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Win32 paste events</text>
      </svg>
    </div>
  );
}

function MacExecutionDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 180" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={20} y={45} width={100} height={80} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x="70" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Hotkey F9</text>
        <text x="70" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(Global Keypress)</text>

        <SketchyLine x1={120} y1={85} x2={160} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={170} y={45} width={130} height={80} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">CGEventTap</text>
        <text x="235" y="92" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Quartz daemon</text>
        <text x="235" y="107" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">CoreGraphics</text>

        <SketchyLine x1={300} y1={85} x2={340} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={350} y={45} width={110} height={80} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x="405" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="405" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Processes WAV</text>

        <SketchyLine x1={460} y1={85} x2={500} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={510} y={45} width={80} height={80} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x="550" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">AXUIElement</text>
        <text x="550" y="92" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Accessibility API</text>
      </svg>
    </div>
  );
}

function LinuxExecutionDiagram() {
  return (
    <div className="min-w-[600px] mx-auto">
      <svg viewBox="0 0 600 180" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={20} y={45} width={100} height={80} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x="70" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Hotkey F9</text>
        <text x="70" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(Global Keypress)</text>

        <SketchyLine x1={120} y1={85} x2={160} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={170} y={45} width={130} height={80} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x="235" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">evdev / dev/input</text>
        <text x="235" y="92" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Input group daemon</text>
        <text x="235" y="107" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">(X11: pynput)</text>

        <SketchyLine x1={300} y1={85} x2={340} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={350} y={45} width={110} height={80} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x="405" y="80" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Rota AI App</text>
        <text x="405" y="98" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Processes WAV</text>

        <SketchyLine x1={460} y1={85} x2={500} y2={85} markerEnd="url(#arrow)" />

        <SketchyRect x={510} y={45} width={80} height={80} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x="550" y="75" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">wtype / xdotool</text>
        <text x="550" y="92" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Wayland / X11 injection</text>
      </svg>
    </div>
  );
}

function LocalSetupDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 130" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        <SketchyRect x={15} y={30} width={120} height={70} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x="75" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">1. Git Clone</text>
        <text x="75" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Setup Git LFS</text>

        <SketchyLine x1={135} y1={65} x2={165} y2={65} markerEnd="url(#arrow)" />

        <SketchyRect x={175} y={30} width={120} height={70} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x="235" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">2. C-Libraries</text>
        <text x="235" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">PortAudio headers</text>

        <SketchyLine x1={295} y1={65} x2={325} y2={65} markerEnd="url(#arrow)" />

        <SketchyRect x={335} y={30} width={120} height={70} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x="395" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">3. Create Venv</text>
        <text x="395" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Python 3.12+</text>

        <SketchyLine x1={455} y1={65} x2={485} y2={65} markerEnd="url(#arrow)" />

        <SketchyRect x={495} y={30} width={130} height={70} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x="560" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">4. Install Packages</text>
        <text x="560" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">pip requirements</text>

        <SketchyLine x1={625} y1={65} x2={655} y2={65} markerEnd="url(#arrow)" />

        <SketchyRect x={665} y={30} width={120} height={70} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x="725" y="65" textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">5. Run Application</text>
        <text x="725" y="83" textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">python app/main.py</text>
      </svg>
    </div>
  );
}

function DictionaryPipelineDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 130" className="w-full h-auto select-none" fill="none">
        <SVGDefs />
        {/* Step 1: Input */}
        <SketchyRect x={15} y={30} width={130} height={70} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x={80} y={65} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">1. Input Audio</text>
        <text x={80} y={83} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">F9 click dictation</text>

        <SketchyLine x1={145} y1={65} x2={175} y2={65} markerEnd="url(#arrow)" />

        {/* Step 2: ASR Prompt */}
        <SketchyRect x={175} y={30} width={130} height={70} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x={240} y={65} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">2. ASR Prompt</text>
        <text x={240} y={83} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Whisper prompt hint</text>

        <SketchyLine x1={305} y1={65} x2={335} y2={65} markerEnd="url(#arrow)" />

        {/* Step 3: LLM Context */}
        <SketchyRect x={335} y={30} width={130} height={70} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x={400} y={65} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">3. LLM Context</text>
        <text x={400} y={83} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Grammar &amp; Vocabulary</text>

        <SketchyLine x1={465} y1={65} x2={495} y2={65} markerEnd="url(#arrow)" />

        {/* Step 4: Hard Replacer */}
        <SketchyRect x={495} y={30} width={130} height={70} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x={560} y={65} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">4. Hard Replacer</text>
        <text x={560} y={83} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Regex substitutions</text>

        <SketchyLine x1={625} y1={65} x2={655} y2={65} markerEnd="url(#arrow)" />

        {/* Step 5: Clean Output */}
        <SketchyRect x={655} y={30} width={130} height={70} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x={720} y={65} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">5. Inject Output</text>
        <text x={720} y={83} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Correct text typed</text>
      </svg>
    </div>
  );
}

function DictionaryOverrideDiagram() {
  return (
    <div className="min-w-[760px] mx-auto">
      <svg viewBox="0 0 800 390" className="w-full h-auto select-none" fill="none">
        <SVGDefs />

        {/* --- ROW 1: USER & CONFIGURATION --- */}
        {/* PyQt6 Settings UI */}
        <SketchyRect x={50} y={30} width={180} height={65} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x={140} y={58} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">PyQt6 Settings UI</text>
        <text x={140} y={76} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Add / Remove Terms Manually</text>

        {/* Audio Input Trigger */}
        <SketchyRect x={310} y={30} width={180} height={65} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x={400} y={58} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">1. Mic Audio Input</text>
        <text x={400} y={76} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">F9 Global Hotkey Pressed</text>

        {/* --- ROW 2: CONTROLLER & STORAGE --- */}
        {/* personal_dictionary.json */}
        <SketchyRect x={50} y={150} width={180} height={75} stroke="#10b981" fill="#10b981" fillOpacity={0.04} />
        <text x={140} y={178} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">personal_dictionary.json</text>
        <text x={140} y={196} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Persistent JSON Storage</text>
        <text x={140} y={210} textAnchor="middle" fill="#10b981" className="excalidraw-font text-[9px] font-mono">%APPDATA% / RotaAI</text>

        {/* Whisper ASR Engine */}
        <SketchyRect x={310} y={150} width={180} height={75} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x={400} y={178} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">2. ASR Transcriber</text>
        <text x={400} y={196} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Groq / Gemini / Local Whisper</text>
        <text x={400} y={210} textAnchor="middle" fill="#e4f222" className="excalidraw-font text-[9px]">(Injected via prompt param)</text>

        {/* --- ROW 3: POST-PROCESSING & LLM CASCADE --- */}
        {/* Auto-Learning Engine */}
        <SketchyRect x={50} y={280} width={180} height={85} stroke="#ef4444" fill="#ef4444" fillOpacity={0.04} />
        <text x={140} y={308} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">Auto-Learning Engine</text>
        <text x={140} y={326} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Extracts Proper Nouns/Acronyms</text>
        <text x={140} y={342} textAnchor="middle" fill="#ef4444" className="excalidraw-font text-[9px] font-mono">learn_from_text()</text>

        {/* LLM Post-Processing Cascade */}
        <SketchyRect x={310} y={280} width={180} height={85} stroke="#e4f222" fill="#e4f222" fillOpacity={0.04} />
        <text x={400} y={308} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">3. LLM Cascade Pass</text>
        <text x={400} y={326} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Dynamic system prompt instruction</text>
        <text x={400} y={342} textAnchor="middle" fill="#e4f222" className="excalidraw-font text-[9px]">## PERSONAL VOCABULARY</text>

        {/* --- ROW 4: NORMALIZATION & INJECTION --- */}
        {/* Local Normalizer (Regex Replacer) */}
        <SketchyRect x={560} y={150} width={190} height={75} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.04} />
        <text x={655} y={180} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">4. Regex Normalizer</text>
        <text x={655} y={198} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Hard substitution string match</text>
        <text x={655} y={212} textAnchor="middle" fill="#f59e0b" className="excalidraw-font text-[9px]">Final fallback alignment</text>

        {/* Active Application Window */}
        <SketchyRect x={560} y={280} width={190} height={85} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.04} />
        <text x={655} y={315} textAnchor="middle" fill="#fafafa" className="excalidraw-font text-xs font-semibold">5. Active Window Target</text>
        <text x={655} y={333} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Injects finalized cleaned text</text>

        {/* --- PATHS & DIRECTIONS --- */}
        {/* UI -> Storage */}
        <SketchyLine x1={140} y1={95} x2={140} y2={150} markerEnd="url(#arrow)" />

        {/* Storage -> ASR Prompt */}
        <SketchyLine x1={230} y1={187} x2={310} y2={187} markerEnd="url(#arrow)" />
        <text x={270} y={180} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">ASR Hint</text>

        {/* Storage -> LLM System Prompt */}
        <SketchyLine x1={140} y1={225} x2={140} y2={280} markerEnd="url(#arrow)" />
        <text x={140} y={252} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Context terms</text>

        {/* Audio Input -> ASR */}
        <SketchyLine x1={400} y1={95} x2={400} y2={150} markerEnd="url(#arrow)" />

        {/* ASR -> LLM Cascade */}
        <SketchyLine x1={400} y1={225} x2={400} y2={280} markerEnd="url(#arrow)" />
        <text x={400} y={252} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Raw transcript</text>

        {/* LLM Cascade -> Regex Normalizer */}
        <SketchyCurve x1={490} y1={322} qx={530} qy={322} x2={550} y2={225} markerEnd="url(#arrow)" />
        <text x={540} y={280} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Clean text</text>

        {/* Regex Normalizer -> Active Window */}
        <SketchyLine x1={655} y1={225} x2={655} y2={280} markerEnd="url(#arrow)" />
        <text x={655} y={252} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Pasted/Typed</text>

        {/* Active Window -> Auto-Learning Engine */}
        <SketchyLine x1={560} y1={322} x2={230} y2={322} strokeDasharray="3,3" markerEnd="url(#arrow)" />
        <text x={395} y={315} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Polished output fed to learn_from_text()</text>

        {/* Auto-Learning Engine -> Storage */}
        <SketchyLine x1={90} y1={280} x2={90} y2={225} strokeDasharray="3,3" markerEnd="url(#arrow)" />
        <text x={70} y={252} textAnchor="middle" fill="#71717a" className="excalidraw-font text-[9px]">Update JSON</text>
      </svg>
    </div>
  );
}

interface StepDetail {
  title: string;
  badge: string;
  badgeColor: string;
  file: string;
  classMethod: string;
  input: string;
  output: string;
  logs: string[];
}

const STEPS: StepDetail[] = [
  {
    title: "System Idle & Listener Active",
    badge: "Ready",
    badgeColor: "text-zinc-400 bg-zinc-900/80 border border-zinc-800",
    file: "desktop/app/rota_app.py",
    classMethod: "RotaApp.run()",
    input: "None - Waiting for hotkey",
    output: "PyQt6 event loop active",
    logs: [
      "[INFO] Initializing RotaApp (desktop/app/rota_app.py)",
      "[INFO] Loading single-instance guard (desktop/app/instance_guard.py)",
      "[INFO] SQLite database connection established: data/rota.db",
      "[INFO] System Tray UI initialized successfully",
      "[INFO] Global Hotkey Listener registered. Press [F9] to dictate."
    ]
  },
  {
    title: "Global Hotkey Event Captured",
    badge: "Hotkey Pressed",
    badgeColor: "text-blue-400 bg-blue-950/40 border border-blue-900",
    file: "desktop/audio/hotkey.py",
    classMethod: "HotkeyHandler._on_press()",
    input: "Global Keypress [F9] (Hold State)",
    output: "Qt Signal: toggle_recording(start=True)",
    logs: [
      "[INFO] pynput hook intercepted VK_F9 key-down",
      "[INFO] RecordingStateMixin: State changed to RECORDING",
      "[INFO] Floating Overlay Pill animated to active recording state",
      "[INFO] Muting background system audio channels (if enabled)"
    ]
  },
  {
    title: "Real-time Audio Ingestion",
    badge: "Recording",
    badgeColor: "text-cyan-400 bg-cyan-950/40 border border-cyan-900",
    file: "desktop/audio/recorder.py",
    classMethod: "AudioRecorder.start_stream()",
    input: "Analog Microphone Input",
    output: "NumPy Array (Float32, 16kHz, Mono)",
    logs: [
      "[INFO] sounddevice InputStream opened successfully",
      "[INFO] Capturing audio frames at 16,000 samples per second",
      "[INFO] PCM buffer streaming started (Float32 format)",
      "[INFO] Average signal amplitude: -28dB"
    ]
  },
  {
    title: "Speech Verification (VAD Filter)",
    badge: "Processing VAD",
    badgeColor: "text-teal-400 bg-teal-950/40 border border-teal-900",
    file: "desktop/audio/vad.py",
    classMethod: "VADFilter.is_speech()",
    input: "Audio Stream Chunk (512 samples)",
    output: "Speech Probability [0.0 - 1.0]",
    logs: [
      "[INFO] Silero VAD running local ONNX model inference",
      "[INFO] Chunk speech probability: 0.963 -> buffering chunk",
      "[INFO] Active speech section detected, prepending 300ms window",
      "[INFO] Writing speech frames to memory WAV buffer"
    ]
  },
  {
    title: "ASR Speech-to-Text Transcription",
    badge: "Transcribing",
    badgeColor: "text-yellow-400 bg-yellow-950/40 border border-yellow-900",
    file: "desktop/ai/ai_processor.py",
    classMethod: "AIProcessor.transcribe_audio()",
    input: "Memory WAV Buffer (16-bit PCM)",
    output: "Raw text: \"rota ai is awsom\"",
    logs: [
      "[INFO] User released F9 hotkey -> Recording session stopped",
      "[INFO] WAV buffer compiled (Size: 112 KB, duration: 3.5s)",
      "[INFO] Dispatching audio to API backend (Groq Whisper-large-v3)",
      "[INFO] API transcription completed in 210ms",
      "[INFO] Raw transcript text: \"rota ai is awsom\""
    ]
  },
  {
    title: "LLM Contextual Post-Processing",
    badge: "Cleaning Text",
    badgeColor: "text-yellow-400 bg-yellow-950/40 border border-yellow-900",
    file: "desktop/ai/auto_improvement.py",
    classMethod: "AutoImprovement.apply_cascade()",
    input: "\"rota ai is awsom\" + App: \"VS Code\"",
    output: "\"Rota AI is awesome.\"",
    logs: [
      "[INFO] Detecting active window: \"Visual Studio Code - main.py\"",
      "[INFO] Loading terminology context from personal_dictionary.json",
      "[INFO] Prompting Gemini Flash with contextual terminology",
      "[INFO] LLM cascade output: \"Rota AI is awesome.\"",
      "[INFO] Running local regex replacements (Snippets overrides)"
    ]
  },
  {
    title: "Virtual Text Injection into Active App",
    badge: "Injecting",
    badgeColor: "text-red-400 bg-red-950/40 border border-red-900",
    file: "desktop/injection/injector.py",
    classMethod: "TextInjector.inject_text()",
    input: "Clean text: \"Rota AI is awesome.\"",
    output: "OS Input Event: Virtual Keypresses",
    logs: [
      "[INFO] Bringing target window to focus",
      "[INFO] Injecting text: \"Rota AI is awesome.\"",
      "[INFO] Method: Win32 SendInput keyboard sequence",
      "[INFO] Target field text length updated (+19 characters)",
      "[INFO] Play success feedback tone (if enabled)"
    ]
  },
  {
    title: "Auto-Learning & Dictionary Logging",
    badge: "Updating DB",
    badgeColor: "text-orange-400 bg-orange-950/40 border border-orange-900",
    file: "desktop/ai/personal_dictionary.py",
    classMethod: "PersonalDictionary.learn_from_text()",
    input: "Polished transcript history log",
    output: "Database insert & JSON write",
    logs: [
      "[INFO] SQLite: Saved transcription log row (ID: 1042)",
      "[INFO] Extraction: parsing terminology in background thread",
      "[INFO] Extracted term \"Rota AI\" -> added to dictionary JSON",
      "[INFO] Vocabulary feedback loop updated for next transcription prompt"
    ]
  }
];

const CODE_SNIPPETS: { [key: number]: { file: string; code: string } } = {
  0: {
    file: "desktop/app/rota_app.py",
    code: `class RotaApp(QApplication):
    def run(self):
        # Initialize thread lifecycle mixins
        self.init_instance_guard()
        self.init_database()
        self.init_tray_ui()

        # Start global hotkey listener
        self.start_hotkey_listener()

        # Start PyQt6 event loop
        sys.exit(self.exec())`
  },
  1: {
    file: "desktop/audio/hotkey.py",
    code: `class HotkeyHandler(threading.Thread):
    def _on_press(self, key):
        if key == Key.f9 and not self.is_held:
            self.is_held = True
            # Dispatch signal to main thread
            self.signals.toggle_recording.emit(True)
            self.logger.info("F9 hold event registered")`
  },
  2: {
    file: "desktop/audio/recorder.py",
    code: `class AudioRecorder:
    def start_stream(self):
        self.buffer = []
        self.stream = sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype='float32',
            callback=self._audio_callback
        )
        self.stream.start()`
  },
  3: {
    file: "desktop/audio/vad.py",
    code: `class VADFilter:
    def __init__(self):
        # Load local Silero VAD model via ONNX
        self.model = ort.InferenceSession("silero_vad.onnx")

    def is_speech(self, audio_chunk):
        # Run ONNX inference on Float32 PCM chunk
        prob = self.model.run(None, {"input": audio_chunk})[0]
        return prob > 0.5`
  },
  4: {
    file: "desktop/ai/ai_processor.py",
    code: `class AIProcessor:
    def transcribe_audio(self, wav_bytes):
        # Choose active backend
        backend = self.config.get("backend")
        if backend == "groq":
            return self.groq_client.audio.transcriptions.create(
                file=("dictation.wav", wav_bytes),
                model="whisper-large-v3"
            ).text`
  },
  5: {
    file: "desktop/ai/auto_improvement.py",
    code: `class AutoImprovement:
    def apply_cascade(self, raw_text, app_context):
        # Combine transcription with active window info
        system_prompt = self.prompts.get_context_prompt(app_context)

        # Get correction from Gemini/Ollama
        corrected = self.llm.generate(
            prompt=raw_text,
            system=system_prompt
        )
        return self.snippets.replace(corrected)`
  },
  6: {
    file: "desktop/injection/injector.py",
    code: `class TextInjector:
    def inject_text(self, text):
        # Use Win32 SendInput for low-level injection
        inputs = []
        for char in text:
            inputs.append(self._create_keyboard_input(char, down=True))
            inputs.append(self._create_keyboard_input(char, down=False))

        win32api.SendInput(len(inputs), inputs)`
  },
  7: {
    file: "desktop/ai/personal_dictionary.py",
    code: `class PersonalDictionary:
    def learn_from_text(self, text):
        # Extract potential terminology/acronyms
        new_terms = self.extractor.find_proper_nouns(text)

        for term in new_terms:
            self.dictionary.add_entry(term)

        # Write to JSON file and SQLite logs
        self.save_to_json()`
  }
};

function FullApplicationLifecycleDiagram() {
  const [activeStep, setActiveStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Auto-play interval
  useEffect(() => {
    let timer: NodeJS.Timeout;
    let progressTimer: NodeJS.Timeout;

    if (isPlaying) {
      timer = setInterval(() => {
        setActiveStep((prev) => (prev + 1) % STEPS.length);
        setProgress(0);
      }, 4000);

      progressTimer = setInterval(() => {
        setProgress((prev) => Math.min(prev + 2.5, 100));
      }, 100);
    }

    return () => {
      clearInterval(timer);
      clearInterval(progressTimer);
    };
  }, [isPlaying]);

  // Scroll terminal logs on step change
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [activeStep]);

  const handleNext = () => {
    setActiveStep((prev) => (prev + 1) % STEPS.length);
    setProgress(0);
  };

  const handlePrev = () => {
    setActiveStep((prev) => (prev - 1 + STEPS.length) % STEPS.length);
    setProgress(0);
  };

  const handleReset = () => {
    setActiveStep(0);
    setProgress(0);
    setIsPlaying(false);
  };

  const handleStepClick = (index: number) => {
    setActiveStep(index);
    setProgress(0);
  };

  const getAccumulatedLogs = () => {
    let accumulated: string[] = [];
    for (let i = 0; i <= activeStep; i++) {
      accumulated = [...accumulated, ...STEPS[i].logs];
    }
    return accumulated;
  };

  // Subsystem active checks
  const isSub1Active = activeStep === 1 || activeStep === 6;
  const isSub2Active = activeStep === 2 || activeStep === 3;
  const isSub3Active = activeStep === 4 || activeStep === 5;
  const isSub4Active = activeStep === 7;

  // Arrow transition triggers
  const line1Active = activeStep === 1;
  const line2Active = activeStep === 3;
  const line3Active = activeStep === 5;
  const line4Active = activeStep === 6;
  const line5Active = activeStep === 7;

  return (
    <div className="flex flex-col gap-6 w-full max-w-[950px] mx-auto text-zinc-100 font-sans p-6 rounded-lg bg-zinc-950 border border-white/[0.06] shadow-xl">
      <style>{`
        @keyframes sketchyDash {
          to {
            stroke-dashoffset: -20;
          }
        }
        .animate-dash {
          stroke-dasharray: 6, 4;
          animation: sketchyDash 0.8s linear infinite;
        }
        .terminal-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .terminal-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .terminal-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.08);
          border-radius: 4px;
        }
      `}</style>

      {/* --- SVG INTERACTIVE DIAGRAM PANEL --- */}
      <div className="w-full relative bg-zinc-900/20 border border-white/[0.02] rounded-md p-2 overflow-x-auto">
        <svg viewBox="0 0 900 530" className="w-full h-auto select-none min-w-[840px]" fill="none">
          <SVGDefs />

          {/* --- SUBSYSTEM 1: FRONTEND & OS INTERFACE --- */}
          <SketchyRect
            x={50}
            y={40}
            width={340}
            height={190}
            stroke={isSub1Active ? "#3b82f6" : "#27272a"}
            fill={isSub1Active ? "#3b82f6" : "#27272a"}
            fillOpacity={isSub1Active ? 0.08 : 0.02}
            strokeWidth={isSub1Active ? 2.5 : 1.25}
          />
          <text x={70} y={75} fill={isSub1Active ? "#3b82f6" : "#a1a1aa"} className="excalidraw-font text-sm font-semibold transition-colors duration-300">1. Frontend &amp; OS Interface</text>
          <text x={75} y={110} fill={activeStep === 1 || activeStep === 6 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• PyQt6 System Tray &amp; Recording Pill Overlay</text>
          <text x={75} y={135} fill={activeStep === 1 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Global Hotkey Daemon (SetWindowsHookEx)</text>
          <text x={75} y={165} fill={activeStep === 5 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Active Window Tracker (Context awareness)</text>
          <text x={75} y={190} fill={activeStep === 6 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• OS Virtual Text Injector (SendInput API)</text>

          {/* --- SUBSYSTEM 2: AUDIO INGEST PIPELINE --- */}
          <SketchyRect
            x={510}
            y={40}
            width={340}
            height={190}
            stroke={isSub2Active ? "#06b6d4" : "#27272a"}
            fill={isSub2Active ? "#06b6d4" : "#27272a"}
            fillOpacity={isSub2Active ? 0.08 : 0.02}
            strokeWidth={isSub2Active ? 2.5 : 1.25}
          />
          <text x={530} y={75} fill={isSub2Active ? "#06b6d4" : "#a1a1aa"} className="excalidraw-font text-sm font-semibold transition-colors duration-300">2. Audio Ingest Pipeline</text>
          <text x={535} y={110} fill={activeStep === 2 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• sounddevice Recorder (16kHz Mono PCM)</text>
          <text x={535} y={135} fill={activeStep === 3 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Silero VAD ONNX Filter (Speech probability)</text>
          <text x={535} y={165} fill={isSub2Active ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Temporary WAV Buffer Session Management</text>
          <text x={535} y={190} fill={activeStep === 2 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Sound Level &amp; Signal Energy Estimator</text>

          {/* --- SUBSYSTEM 3: ASR & LLM ENGINES --- */}
          <SketchyRect
            x={510}
            y={300}
            width={340}
            height={190}
            stroke={isSub3Active ? "#e4f222" : "#27272a"}
            fill={isSub3Active ? "#e4f222" : "#27272a"}
            fillOpacity={isSub3Active ? 0.08 : 0.02}
            strokeWidth={isSub3Active ? 2.5 : 1.25}
          />
          <text x={530} y={335} fill={isSub3Active ? "#e4f222" : "#a1a1aa"} className="excalidraw-font text-sm font-semibold transition-colors duration-300">3. ASR &amp; LLM Engines</text>
          <text x={535} y={370} fill={activeStep === 4 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Whisper ASR (Groq, Gemini, or CTranslate2 Local)</text>
          <text x={535} y={395} fill={activeStep === 5 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• LLM Post-Processor (Grammar &amp; Tone formatting)</text>
          <text x={535} y={420} fill={activeStep === 5 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Contextual Prompter (Active window context pass)</text>
          <text x={535} y={445} fill={activeStep === 5 ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Local Voice Snippets &amp; Abbreviation Processor</text>

          {/* --- SUBSYSTEM 4: LOCAL STORAGE & LEARNING --- */}
          <SketchyRect
            x={50}
            y={300}
            width={340}
            height={190}
            stroke={isSub4Active ? "#f59e0b" : "#27272a"}
            fill={isSub4Active ? "#f59e0b" : "#27272a"}
            fillOpacity={isSub4Active ? 0.08 : 0.02}
            strokeWidth={isSub4Active ? 2.5 : 1.25}
          />
          <text x={70} y={335} fill={isSub4Active ? "#f59e0b" : "#a1a1aa"} className="excalidraw-font text-sm font-semibold transition-colors duration-300">4. Local Storage &amp; Learning</text>
          <text x={75} y={370} fill={isSub4Active ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• SQLite DB (Transcription history &amp; configuration)</text>
          <text x={75} y={395} fill={isSub4Active ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Personal Dictionary (Persistent custom term JSON)</text>
          <text x={75} y={420} fill={isSub4Active ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Auto-Learning Engine (learn_from_text worker)</text>
          <text x={75} y={445} fill={isSub4Active ? "#fafafa" : "#71717a"} className="excalidraw-font text-xs">• Windows DPAPI Secure API Keyrings</text>

          {/* --- CONNECTIONS & TRANSITIONS --- */}

          {/* Transition 1: Interface -> Audio Pipeline */}
          <SketchyLine
            x1={390}
            y1={135}
            x2={510}
            y2={135}
            stroke={line1Active ? "#3b82f6" : "#2d2d30"}
            strokeWidth={line1Active ? 2.5 : 1.5}
            className={line1Active ? "animate-dash" : ""}
            markerEnd="url(#arrow)"
          />
          <text x={450} y={115} textAnchor="middle" fill={line1Active ? "#3b82f6" : "#52525b"} className="excalidraw-font text-[10px] font-semibold transition-colors duration-300">F9 Held</text>
          <text x={450} y={130} textAnchor="middle" fill={line1Active ? "#fafafa" : "#3f3f46"} className="excalidraw-font text-[9px]">Start Ingest</text>

          {/* Transition 2: Audio Pipeline -> Engines */}
          <SketchyLine
            x1={680}
            y1={230}
            x2={680}
            y2={300}
            stroke={line2Active ? "#06b6d4" : "#2d2d30"}
            strokeWidth={line2Active ? 2.5 : 1.5}
            className={line2Active ? "animate-dash" : ""}
            markerEnd="url(#arrow)"
          />
          <text x={695} y={260} fill={line2Active ? "#06b6d4" : "#52525b"} className="excalidraw-font text-[10px] font-semibold transition-colors duration-300">F9 Released</text>
          <text x={695} y={275} fill={line2Active ? "#fafafa" : "#3f3f46"} className="excalidraw-font text-[9px]">Pass WAV Buffer</text>

          {/* Transition 3: Engines -> Interface */}
          <SketchyCurve
            x1={510}
            y1={320}
            qx={430}
            qy={240}
            x2={390}
            y2={200}
            stroke={line3Active ? "#e4f222" : "#2d2d30"}
            strokeWidth={line3Active ? 2.5 : 1.5}
            className={line3Active ? "animate-dash" : ""}
            markerEnd="url(#arrow)"
          />
          <text x={425} y={250} textAnchor="middle" fill={line3Active ? "#e4f222" : "#52525b"} className="excalidraw-font text-[10px] font-semibold transition-colors duration-300">Clean Text</text>
          <text x={425} y={265} textAnchor="middle" fill={line3Active ? "#fafafa" : "#3f3f46"} className="excalidraw-font text-[9px]">Virtual OS Type</text>

          {/* Transition 4: Interface -> Storage & Learning */}
          <SketchyLine
            x1={220}
            y1={230}
            x2={220}
            y2={300}
            stroke={line4Active ? "#ef4444" : "#2d2d30"}
            strokeWidth={line4Active ? 2.5 : 1.5}
            className={line4Active ? "animate-dash" : ""}
            markerEnd="url(#arrow)"
          />
          <text x={205} y={260} textAnchor="end" fill={line4Active ? "#ef4444" : "#52525b"} className="excalidraw-font text-[10px] font-semibold transition-colors duration-300">Injected Text</text>
          <text x={205} y={275} textAnchor="end" fill={line4Active ? "#fafafa" : "#3f3f46"} className="excalidraw-font text-[9px]">Log &amp; Auto-Learn</text>

          {/* Transition 5: Storage -> Engines (Dashed feedback loop) */}
          <SketchyLine
            x1={390}
            y1={395}
            x2={510}
            y2={395}
            stroke={line5Active ? "#f59e0b" : "#2d2d30"}
            strokeWidth={line5Active ? 2.5 : 1.5}
            strokeDasharray="4,4"
            className={line5Active ? "animate-dash" : ""}
            markerEnd="url(#arrow)"
          />
          <text x={450} y={375} textAnchor="middle" fill={line5Active ? "#f59e0b" : "#52525b"} className="excalidraw-font text-[10px] font-semibold transition-colors duration-300">Feedback Loop</text>
          <text x={450} y={420} textAnchor="middle" fill={line5Active ? "#fafafa" : "#3f3f46"} className="excalidraw-font text-[9px]">Vocabulary &amp; Snippets</text>
        </svg>
      </div>

      {/* --- DASHBOARD STEPS NAVIGATION BAR --- */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/[0.04] pb-4">
        {/* Playback Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrev}
            className="p-2 rounded bg-zinc-900 border border-white/[0.06] hover:bg-zinc-800 transition-colors text-zinc-400 hover:text-white"
            title="Previous step"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
            </svg>
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-semibold uppercase tracking-wider bg-[#e4f222] hover:opacity-90 text-black transition-all"
          >
            {isPlaying ? (
              <>
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
                <span>Pause</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <span>Simulate</span>
              </>
            )}
          </button>

          <button
            onClick={handleNext}
            className="p-2 rounded bg-zinc-900 border border-white/[0.06] hover:bg-zinc-800 transition-colors text-zinc-400 hover:text-white"
            title="Next step"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
            </svg>
          </button>

          <button
            onClick={handleReset}
            className="p-2 rounded bg-zinc-900 border border-white/[0.06] hover:bg-zinc-800 transition-colors text-zinc-400 hover:text-white"
            title="Reset simulation"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
            </svg>
          </button>
        </div>

        {/* Step Buttons */}
        <div className="flex items-center gap-1">
          {STEPS.map((step, idx) => (
            <button
              key={idx}
              onClick={() => handleStepClick(idx)}
              className={`w-7 h-7 rounded-full text-xs font-semibold flex items-center justify-center border transition-all duration-300 ${
                activeStep === idx
                  ? "bg-zinc-100 text-zinc-950 border-white"
                  : "bg-zinc-900 text-zinc-400 border-white/[0.04] hover:bg-zinc-800"
              }`}
            >
              {idx}
            </button>
          ))}
        </div>
      </div>

      {/* Auto-Play Progress Indicator */}
      {isPlaying && (
        <div className="w-full bg-zinc-900 h-0.5 rounded overflow-hidden -mt-4">
          <div
            className="bg-[#e4f222] h-full transition-all duration-100 ease-linear"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* --- STEP TRACE DETAILS & EMULATED CONSOLE --- */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start mt-2">
        {/* Left Side: Step info & Code tab */}
        <div className="md:col-span-7 flex flex-col gap-4">
          {/* Active step title & badge */}
          <div className="flex items-start justify-between gap-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#e4f222]">Step {activeStep}: {STEPS[activeStep].badge}</span>
              <h4 className="text-[16px] font-semibold text-white leading-tight mt-1">{STEPS[activeStep].title}</h4>
            </div>
            <span className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-widest font-mono font-bold ${STEPS[activeStep].badgeColor}`}>
              {STEPS[activeStep].badge}
            </span>
          </div>

          {/* Dynamic Mock Data Inspector */}
          <div className="bg-[#121214] border border-white/[0.03] rounded p-3">
            <div className="text-[10px] uppercase font-bold tracking-wider text-zinc-500 mb-2 font-mono">💡 In-Memory Data Pipeline</div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-[9px] font-mono text-zinc-500">INPUT DATA</div>
                <div className="text-[11px] font-mono text-zinc-300 mt-0.5 font-medium truncate" title={STEPS[activeStep].input}>
                  {STEPS[activeStep].input}
                </div>
              </div>
              <div>
                <div className="text-[9px] font-mono text-zinc-500">OUTPUT PAYLOAD</div>
                <div className="text-[11px] font-mono text-zinc-300 mt-0.5 font-medium truncate" title={STEPS[activeStep].output}>
                  {STEPS[activeStep].output}
                </div>
              </div>
            </div>
          </div>

          {/* Code Inspector Block */}
          <div className="bg-[#121214] border border-white/[0.04] rounded overflow-hidden">
            {/* Fake IDE Header Tab */}
            <div className="flex items-center justify-between bg-[#18181b] border-b border-white/[0.04] px-4 py-1.5">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-blue-500/80" />
                <span className="text-[10px] font-mono text-zinc-400 font-semibold">{CODE_SNIPPETS[activeStep].file}</span>
              </div>
              <span className="text-[9px] font-mono uppercase tracking-widest text-zinc-600 font-bold">{STEPS[activeStep].classMethod}</span>
            </div>

            {/* Snippet Output */}
            <pre className="p-4 overflow-x-auto text-[11px] font-mono text-zinc-300 leading-relaxed max-h-[170px] select-text">
              <code>{CODE_SNIPPETS[activeStep].code}</code>
            </pre>
          </div>
        </div>

        {/* Right Side: Log Console emulator */}
        <div className="md:col-span-5 flex flex-col gap-2 h-full">
          <div className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 font-mono">📋 Live Daemon Log Output</div>

          {/* Terminal Window container */}
          <div className="bg-[#09090b] border border-white/[0.08] rounded flex flex-col h-[280px]">
            {/* Header bar */}
            <div className="flex items-center justify-between border-b border-white/[0.04] px-3.5 py-2 shrink-0">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-zinc-800" />
                <span className="w-2 h-2 rounded-full bg-zinc-800" />
                <span className="w-2 h-2 rounded-full bg-zinc-800" />
              </div>
              <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest font-semibold">rota-ai-daemon.log</span>
            </div>

            {/* Log viewport */}
            <div className="flex-1 p-3.5 overflow-y-auto terminal-scrollbar space-y-2 select-text">
              {getAccumulatedLogs().map((log, idx) => {
                let colorClass = "text-zinc-400";
                if (log.includes("[INFO]")) {
                  colorClass = "text-zinc-300";
                } else if (log.includes("[WARNING]")) {
                  colorClass = "text-yellow-500 font-medium";
                }

                // Highlight variables/payloads inside logs
                const formatted = log
                  .replace(/RECORDING/g, '<span class="text-red-400 font-semibold">RECORDING</span>')
                  .replace(/"rota ai is awsom"/g, '<span class="text-emerald-400">"rota ai is awsom"</span>')
                  .replace(/"Rota AI is awesome."/g, '<span class="text-emerald-400 font-semibold">"Rota AI is awesome."</span>');

                return (
                  <div
                    key={idx}
                    className={`text-[10px] leading-relaxed font-mono ${colorClass}`}
                    dangerouslySetInnerHTML={{ __html: formatted }}
                  />
                );
              })}
              <div ref={terminalEndRef} />

              <span className="text-cyan-400 ml-1 inline-block animate-pulse font-bold text-[10px] -mt-1">▋</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
