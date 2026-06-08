"use client";

import { useEffect, useRef, useState } from "react";
import type { TocItem } from "@/lib/blog";

interface TocSidebarProps {
  items: TocItem[];
}

export function TocSidebar({ items }: TocSidebarProps) {
  const [activeId, setActiveId] = useState<string>("");
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    if (items.length === 0) return;

    // Observe all heading elements on the page
    const headings = items
      .map((item) => document.getElementById(item.id))
      .filter(Boolean) as HTMLElement[];

    if (headings.length === 0) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        // Find the first heading that's currently visible
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          setActiveId(visible[0].target.id);
        }
      },
      {
        rootMargin: "-80px 0px -70% 0px",
        threshold: 0,
      }
    );

    headings.forEach((h) => observerRef.current?.observe(h));

    return () => {
      observerRef.current?.disconnect();
    };
  }, [items]);

  if (items.length === 0) return null;

  return (
    <nav aria-label="Table of contents" className="space-y-1">
      <h4 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] mb-4 font-mono">
        On this page
      </h4>
      {items.map((item) => (
        <a
          key={item.id}
          href={`#${item.id}`}
          className={`block text-[12px] leading-relaxed transition-all duration-200 py-1 ${
            item.level === 3 ? "pl-4" : ""
          } ${
            activeId === item.id
              ? "text-[#e4f222] font-medium"
              : "text-[#71717a] hover:text-[#a1a1aa]"
          }`}
          onClick={(e) => {
            e.preventDefault();
            const el = document.getElementById(item.id);
            if (el) {
              el.scrollIntoView({ behavior: "smooth", block: "start" });
              // Update active immediately for responsive feel
              setActiveId(item.id);
            }
          }}
        >
          {item.text}
        </a>
      ))}
    </nav>
  );
}

/** Mobile collapsible TOC - shown below the title on small screens */
export function TocMobile({ items }: TocSidebarProps) {
  const [open, setOpen] = useState(false);

  if (items.length === 0) return null;

  return (
    <div className="lg:hidden mb-10">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full px-4 py-3 text-xs uppercase tracking-wider transition-all rounded-sm"
        style={{
          background: open ? "rgba(228,242,34,0.04)" : "rgba(255,255,255,0.02)",
          border: "1px solid rgba(255,255,255,0.06)",
          color: "#a1a1aa",
        }}
      >
        <svg
          className={`w-3 h-3 transition-transform duration-200 ${open ? "rotate-90" : ""}`}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span>On this page</span>
        <span className="ml-auto text-[10px] text-[#50545a] font-mono">
          {items.length} {items.length === 1 ? "section" : "sections"}
        </span>
      </button>
      {open && (
        <div
          className="mt-1 p-3 rounded-sm"
          style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)" }}
        >
          {items.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`block text-xs py-1.5 transition-colors hover:text-[#e4f222] ${
                item.level === 3 ? "pl-4" : ""
              }`}
              style={{ color: "#71717a" }}
              onClick={(e) => {
                e.preventDefault();
                setOpen(false);
                const el = document.getElementById(item.id);
                if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            >
              {item.text}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
