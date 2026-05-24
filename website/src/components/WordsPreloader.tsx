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

const EXPO_OUT: [number, number, number, number] = [0.16, 1, 0.3, 1];
const WORD_IN:  [number, number, number, number] = [0.215, 0.61, 0.355, 1];
const WORD_OUT: [number, number, number, number] = [0.4, 0, 1, 1];

export function WordsPreloader({ onComplete }: { onComplete: () => void }) {
  const [show, setShow]   = useState(true);
  const [index, setIndex] = useState(0);
  const [h, setH]         = useState(0);

  useEffect(() => {
    setH(window.innerHeight);
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, []);

  // First word: 900ms · middle words: 300ms · last word: 1000ms then exit
  useEffect(() => {
    if (index === WORDS.length - 1) {
      const t = setTimeout(() => setShow(false), 1000);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setIndex((i) => i + 1), index === 0 ? 600 : 120);
    return () => clearTimeout(t);
  }, [index]);

  useEffect(() => {
    if (!show) {
      const t = setTimeout(onComplete, 1300);
      return () => clearTimeout(t);
    }
  }, [show, onComplete]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          key="preloader"
          exit={{
            y: -h,
            transition: { duration: 0.9, ease: EXPO_OUT, delay: 0.05 },
          }}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            willChange: "transform",
          }}
        >
          <AnimatePresence mode="wait">
            <motion.p
              key={index}
              initial={{ opacity: 0, y: 16 }}
              animate={{
                opacity: 1,
                y: 0,
                transition: { duration: 0.35, ease: WORD_IN },
              }}
              exit={{
                opacity: 0,
                y: -12,
                transition: { duration: 0.2, ease: WORD_OUT },
              }}
              style={{
                margin: 0,
                fontSize: "clamp(1.1rem, 2.5vw, 2rem)",
                fontWeight: 700,
                letterSpacing: "-0.02em",
                color: "#0e0e12",
                whiteSpace: "nowrap",
                fontFamily: "var(--font-cormorant, Georgia, serif)",
                willChange: "transform, opacity",
                userSelect: "none",
              }}
            >
              {WORDS[index]}
            </motion.p>
          </AnimatePresence>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
