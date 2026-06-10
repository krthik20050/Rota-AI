"use client";

import { useEffect, useRef, useState } from "react";

interface SidebarItem {
  label: string;
  href: string;
  slug: string;
}

interface SidebarSection {
  title: string;
  items: SidebarItem[];
}

interface DocsNavigationProps {
  sections: SidebarSection[];
}

export function DocsSidebar({ sections }: DocsNavigationProps) {
  const [activeId, setActiveId] = useState<string>("");
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const ids = sections.flatMap((section) => section.items.map((item) => item.href.replace("#", "")));
    const elements = ids.map((id) => document.getElementById(id)).filter(Boolean) as HTMLElement[];

    if (elements.length === 0) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          const sorted = [...visible].sort((a, b) => a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top);
          setActiveId(sorted[0].target.id);
        }
      },
      {
        rootMargin: "-80px 0px -60% 0px",
        threshold: 0,
      }
    );

    elements.forEach((el) => observerRef.current?.observe(el));

    return () => {
      observerRef.current?.disconnect();
    };
  }, [sections]);

  return (
    <nav className="space-y-8">
      {sections.map((section) => (
        <div key={section.title}>
          <h3 className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#50545a] mb-3 px-2">
            {section.title}
          </h3>
          <ul className="space-y-0.5">
            {section.items.map((item) => {
              const id = item.href.replace("#", "");
              const isActive = activeId === id;
              return (
                <li key={item.label} className="relative">
                  {isActive && (
                    <div className="absolute left-0 top-2 bottom-2 w-[2px] bg-[#e4f222] rounded-full" />
                  )}
                  <a
                    href={item.href}
                    className={`block py-1.5 text-xs rounded-sm transition-all duration-200 pl-4 ${
                      isActive
                        ? "text-[#fafafa] font-semibold bg-white/[0.02]"
                        : "text-[#71717a] hover:text-[#fafafa] hover:bg-white/[.01]"
                    }`}
                    onClick={(e) => {
                      e.preventDefault();
                      const el = document.getElementById(id);
                      if (el) {
                        el.scrollIntoView({ behavior: "smooth", block: "start" });
                        setActiveId(id);
                      }
                    }}
                  >
                    {item.label}
                  </a>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

export function DocsMobileMenu({ sections }: DocsNavigationProps) {
  const [activeLabel, setActiveLabel] = useState<string>("Jump to section");
  const [activeId, setActiveId] = useState<string>("");
  const detailsRef = useRef<HTMLDetailsElement | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const ids = sections.flatMap((section) => section.items.map((item) => item.href.replace("#", "")));
    const elements = ids.map((id) => document.getElementById(id)).filter(Boolean) as HTMLElement[];

    if (elements.length === 0) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          const sorted = [...visible].sort((a, b) => a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top);
          const matchedId = sorted[0].target.id;
          setActiveId(matchedId);
          // Find matching label
          for (const sec of sections) {
            const match = sec.items.find((item) => item.href === `#${matchedId}`);
            if (match) {
              setActiveLabel(match.label);
              break;
            }
          }
        }
      },
      {
        rootMargin: "-80px 0px -70% 0px",
        threshold: 0,
      }
    );

    elements.forEach((el) => observerRef.current?.observe(el));

    return () => {
      observerRef.current?.disconnect();
    };
  }, [sections]);

  const handleLinkClick = (id: string, label: string) => {
    if (detailsRef.current) {
      detailsRef.current.open = false;
    }
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      setActiveId(id);
      setActiveLabel(label);
    }
  };

  return (
    <details ref={detailsRef} className="group">
      <summary className="text-xs uppercase tracking-[0.15em] text-[#71717a] cursor-pointer list-none flex items-center justify-between">
        <span className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#e4f222]"></span>
          <span className="text-[#fafafa] font-semibold normal-case tracking-normal">{activeLabel}</span>
        </span>
        <svg className="w-3.5 h-3.5 transition-transform group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </summary>
      <div className="mt-4 space-y-4 pb-2 max-h-[60vh] overflow-y-auto pr-2">
        {sections.map((section) => (
          <div key={section.title}>
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#50545a] mb-1.5">
              {section.title}
            </h4>
            <div className="space-y-1">
              {section.items.map((item) => {
                const id = item.href.replace("#", "");
                const isActive = activeId === id;
                return (
                  <a
                    key={item.label}
                    href={item.href}
                    onClick={(e) => {
                      e.preventDefault();
                      handleLinkClick(id, item.label);
                    }}
                    className={`block text-xs py-1 transition-all pl-2 border-l border-transparent ${
                      isActive
                        ? "text-[#fafafa] font-semibold border-[#e4f222]/50 bg-white/[0.02]"
                        : "text-[#71717a] hover:text-[#fafafa]"
                    }`}
                  >
                    {item.label}
                  </a>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </details>
  );
}
