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
      ) : type.includes("ASR Prompt") || type.includes("Hard Replacer") ? (
        <DictionaryPipelineDiagram />
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
