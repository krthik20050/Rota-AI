"use client";

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";

const WORDS = [
  "Hello",
  "Bonjour",
  "Ciao",
  "Olà",
  "やあ",
  "Hallå",
  "Guten Tag",
  "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਜੀ",
];

// How far the curved bottom edge bows downward (px)
const CURVE = 200;
// Total height of the SVG cap below the white panel (must be > CURVE)
const CAP_H = 260;

export function WordsPreloader({ onComplete }: { onComplete: () => void }) {
  const [show, setShow]   = useState(true);
  const [index, setIndex] = useState(0);
  const [dims, setDims]   = useState({ w: 0, h: 0 });

  // Capture viewport once (client-only)
  useEffect(() => {
    setDims({ w: window.innerWidth, h: window.innerHeight });
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  // Word cycling: first word 1 000 ms, rest 200 ms each
  useEffect(() => {
    if (index === WORDS.length - 1) {
      const t = setTimeout(() => setShow(false), 1200);
      return () => clearTimeout(t);
    }
    const t = setTimeout(
      () => setIndex((i) => i + 1),
      index === 0 ? 1000 : 200
    );
    return () => clearTimeout(t);
  }, [index]);

  // Notify parent after exit animation finishes (delay 0.15 + duration 1.0 + buffer)
  useEffect(() => {
    if (!show) {
      const t = setTimeout(onComplete, 1400);
      return () => clearTimeout(t);
    }
  }, [show, onComplete]);

  const { w, h } = dims;

  // Curved SVG cap placed directly below the white panel.
  // Corners at y=0 (sides), center bows DOWN to y=CURVE.
  // As the whole overlay translates up by -(h + CAP_H), this curve
  // sweeps through the viewport → genuine curved-wipe exit.
  const capPath =
    w > 0
      ? `M0,0 Q${w / 2},${CURVE} ${w},0 L${w},${CAP_H} L0,${CAP_H} Z`
      : "";

  return (
    <AnimatePresence mode="wait">
      {show && (
        <motion.div
          key="preloader"
          exit={{
            // Translate UP by exactly (viewport height + cap height) so every
            // pixel — including the deepest part of the curve — leaves the screen.
            y: -(h + CAP_H),
            transition: { duration: 1.0, ease: [0.76, 0, 0.24, 1], delay: 0.15 },
          }}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            // Column layout: white panel on top, SVG cap directly below
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* ── White panel — 100 vh ── */}
          <div
            style={{
              height: "100vh",
              background: "#ffffff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <motion.p
              key={index}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.215, 0.61, 0.355, 1] } }}
              exit={{ opacity: 0, y: -16, transition: { duration: 0.25 } }}
              style={{
                margin: 0,
                // Match reference: very large display text
                fontSize: "clamp(4rem, 11vw, 10rem)",
                fontWeight: 700,
                letterSpacing: "-0.04em",
                color: "#0e0e12",
                whiteSpace: "nowrap",
                fontFamily: "var(--font-geist, system-ui, sans-serif)",
              }}
            >
              {WORDS[index]}
            </motion.p>
          </div>

          {/* ── SVG curved cap — the "rounded bottom" of the overlay ── */}
          {/* Rigid shape; no morphing. The curve naturally sweeps through  */}
          {/* the viewport as the parent translates upward.                 */}
          {w > 0 && (
            <svg
              width={w}
              height={CAP_H}
              style={{ display: "block", flexShrink: 0 }}
            >
              <path d={capPath} fill="#ffffff" />
            </svg>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
