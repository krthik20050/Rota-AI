"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useState, useMemo } from "react";

interface PostSummary {
  slug: string;
  title: string;
  description: string;
  date: string;
  author: string;
  category?: string;
  readTime?: string;
}

export function BlogFilterableContent({
  posts,
  categories,
}: {
  posts: PostSummary[];
  categories: string[];
}) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const filteredPosts = useMemo(() => {
    if (!activeCategory) return posts;
    return posts.filter((p) => p.category === activeCategory);
  }, [activeCategory, posts]);

  const featured = filteredPosts[0];
  const rest = filteredPosts.slice(1);

  return (
    <>
      {/* Category filter */}
      {categories.length > 1 && (
        <div className="flex items-center gap-4 mb-12 overflow-x-auto pb-2">
          <span className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono shrink-0">Browse</span>
          <button
            onClick={() => setActiveCategory(null)}
            className={`text-[11px] font-mono whitespace-nowrap transition-all duration-200 px-3 py-1 rounded-sm ${
              activeCategory === null
                ? "text-[#e4f222] bg-[#e4f222]/10"
                : "text-[#71717a] hover:text-[#fafafa]"
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`text-[11px] font-mono whitespace-nowrap transition-all duration-200 px-3 py-1 rounded-sm ${
                activeCategory === cat
                  ? "text-[#e4f222] bg-[#e4f222]/10"
                  : "text-[#71717a] hover:text-[#fafafa]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Featured post */}
      {featured && (
        <Link
          href={`/blog/${encodeURIComponent(featured.slug)}`}
          className="group block mb-14 p-8 sm:p-10 transition-all duration-300 hover:bg-[#0c0c0e] rounded-sm -mx-6 sm:-mx-8 px-6 sm:px-8"
          style={{ background: "rgba(255,255,255,0.02)" }}
        >
          <div className="flex items-center gap-3 mb-4">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#e4f222]">
              {featured.category}
            </span>
            <span className="text-[8px] text-[#50545a]" aria-hidden="true">·</span>
            <span className="text-[10px] font-mono text-[#50545a]">{featured.readTime}</span>
          </div>
          <h2
            className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4 group-hover:text-[#e4f222] transition-colors"
            style={{ fontSize: "clamp(24px, 3.5vw, 40px)", color: "#fafafa" }}
          >
            {featured.title}
          </h2>
          <p className="text-sm text-[#71717a] leading-relaxed max-w-3xl mb-6">
            {featured.description}
          </p>
          <div className="flex items-center gap-2 text-[11px] text-[#50545a] font-mono">
            <span>{featured.author}</span>
            <span aria-hidden="true">·</span>
            <span>{featured.date}</span>
          </div>
        </Link>
      )}

      {/* Remaining posts */}
      <div className="space-y-8">
        {rest.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${encodeURIComponent(post.slug)}`}
            className="group block p-6 sm:p-8 transition-all duration-300 hover:bg-[#0c0c0e] rounded-sm -mx-6 sm:-mx-8 px-6 sm:px-8"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#71717a]">
                {post.category}
              </span>
              <span className="text-[8px] text-[#50545a]" aria-hidden="true">·</span>
              <span className="text-[10px] font-mono text-[#50545a]">{post.readTime}</span>
            </div>
            <h2
              className="font-display uppercase tracking-[0.02em] leading-[0.95] mb-3 group-hover:text-[#e4f222] transition-colors"
              style={{ fontSize: "clamp(18px, 2.5vw, 28px)", color: "#fafafa" }}
            >
              {post.title}
            </h2>
            <p className="text-sm text-[#71717a] leading-relaxed max-w-2xl mb-5">
              {post.description}
            </p>
            <div className="flex items-center gap-2 text-[11px] text-[#50545a] font-mono">
              <span>{post.author}</span>
              <span aria-hidden="true">·</span>
              <span>{post.date}</span>
            </div>
          </Link>
        ))}
      </div>

      {/* Load more */}
      {posts.length > 10 && (
        <div className="pt-12 text-center">
          <button className="text-[11px] font-mono uppercase tracking-[0.2em] text-[#71717a] hover:text-[#fafafa] transition-colors cursor-pointer bg-transparent border-none">
            Load more
          </button>
        </div>
      )}

      {/* Subscribe - client-side with micro-animation */}
      <div className="mt-12">
        <BlogSubscribeForm />
      </div>
    </>
  );
}

/* Subscribe Form (client-side, with micro-animation) */

function BlogSubscribeForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setStatus("loading");
    setMessage("");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus("success");
        setMessage("You are on the list!");
        setEmail("");
      } else {
        setStatus("error");
        setMessage(data.error || "Something went wrong.");
      }
    } catch {
      setStatus("error");
      setMessage("Network error.");
    }
  };

  if (status === "success") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="flex items-center gap-3 p-6 sm:p-8 rounded-sm"
        style={{ background: "rgba(228,242,34,0.04)", border: "1px solid rgba(228,242,34,0.15)" }}
      >
        <div className="w-8 h-8 flex items-center justify-center rounded-full bg-[#e4f222]/10">
          <svg className="w-4 h-4 text-[#e4f222]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div>
          <p className="text-sm text-[#e4f222] font-medium">Subscribed!</p>
          <p className="text-xs text-[#71717a] mt-0.5">{message}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 p-6 sm:p-8 rounded-sm"
      style={{ background: "rgba(255,255,255,0.02)" }}>
      <div className="flex-1">
        <h4 className="text-xs font-medium text-[#fafafa] mb-1">Stay in the loop</h4>
        <p className="text-[11px] text-[#71717a]">New posts, no spam, unsubscribe anytime.</p>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          className="px-3 py-2 text-xs outline-none transition-all bg-transparent rounded-sm w-full sm:w-48"
          style={{ border: "1px solid rgba(255,255,255,0.1)", color: "#fafafa" }}
          onFocus={(e) => e.target.style.borderColor = "rgba(228,242,34,0.4)"}
          onBlur={(e) => e.target.style.borderColor = "rgba(255,255,255,0.1)"}
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 rounded-sm whitespace-nowrap disabled:opacity-50"
          style={{ background: "#e4f222", color: "#000", border: "none", cursor: "pointer" }}
        >
          {status === "loading" ? (
            <span className="flex items-center gap-2">
              <svg className="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Sending
            </span>
          ) : (
            "Subscribe"
          )}
        </button>
      </form>
      {status === "error" && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs text-red-400 mt-2"
        >
          {message}
        </motion.p>
      )}
    </div>
  );
}
