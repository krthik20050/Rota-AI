import Link from "next/link";
import { getAllPosts } from "@/lib/blog";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blog - Rota AI",
  description: "Voice dictation, open source AI, and building Rota AI.",
};

const SOCIAL_LINKS = [
  {
    name: "X / Twitter",
    href: "https://x.com/itsurkk05",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
    ),
  },
  {
    name: "Instagram",
    href: "https://www.instagram.com/karthikkrishnan000/",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
    ),
  },
  {
    name: "YouTube",
    href: "https://www.youtube.com/@Krthikk",
    icon: (
      <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
    ),
  },
];

export default function BlogPage() {
  const posts = getAllPosts();
  const featured = posts[0];
  const rest = posts.slice(1);
  const categories = [...new Set(posts.map((p) => p.category).filter(Boolean))] as string[];

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Nav */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14"
        style={{
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(9,9,11,0.92)",
          backdropFilter: "blur(16px)",
        }}
      >
        <Link href="/" className="flex items-center">
          <img src="/logo.svg" alt="Rota AI" className="h-8 w-auto" />
        </Link>
        <div className="flex items-center gap-6 text-xs uppercase tracking-[0.15em] text-[#71717a]">
          <Link href="/" className="hover:text-[#fafafa] transition-colors">Home</Link>
          <span className="text-[#fafafa]">Blog</span>
          <Link href="/#download" className="px-4 py-2 text-xs font-semibold tracking-[0.15em] uppercase transition-all hover:opacity-90 rounded-sm"
            style={{ background: "#e4f222", color: "#000" }}>Download</Link>
        </div>
      </nav>

      {/* Hero */}
      <div className="px-6 sm:px-10 pt-28 pb-12">
        <div className="max-w-6xl mx-auto">
          <p className="text-[11px] uppercase tracking-[0.2em] text-[#e4f222] font-mono mb-4">Inside Rota</p>
          <h1
            className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4"
            style={{ fontSize: "clamp(36px, 6vw, 64px)", color: "#fafafa" }}
          >
            Blog
          </h1>
          <p className="text-sm text-[#71717a] max-w-lg leading-relaxed">
            Open source voice dictation, AI tools, student stories, and building Rota AI in the open.
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 sm:px-10 pb-20">
        {/* Category filter */}
        {categories.length > 1 && (
          <div className="flex items-center gap-4 mb-12 overflow-x-auto pb-2">
            <span className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] font-mono shrink-0">Browse</span>
            {categories.map((cat) => (
              <span
                key={cat}
                className="text-[11px] font-mono text-[#71717a] hover:text-[#fafafa] transition-colors whitespace-nowrap cursor-default"
              >
                {cat}
              </span>
            ))}
          </div>
        )}

        {/* Featured post — spacious hero card, no borders */}
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

        {/* Remaining posts — text-only, spacious, no borders */}
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

        {/* Social links — follow the author */}
        <div className="mt-20 pt-12" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            <div>
              <h3 className="text-sm font-display uppercase tracking-[0.02em] text-[#fafafa] mb-1">
                Follow the author
              </h3>
              <p className="text-xs text-[#71717a]">
                Karthik Krishnan on social media
              </p>
            </div>
            <div className="flex items-center gap-3 sm:ml-auto">
              {SOCIAL_LINKS.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2.5 text-xs uppercase tracking-wider transition-all duration-200 hover:bg-white/[0.06] rounded-sm"
                  style={{
                    border: "1px solid rgba(255,255,255,0.08)",
                    color: "#a1a1aa",
                  }}
                >
                  {social.icon}
                  <span>{social.name}</span>
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Subscribe */}
        <div className="mt-12">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 p-6 sm:p-8 rounded-sm"
            style={{ background: "rgba(255,255,255,0.02)" }}>
            <div className="flex-1">
              <h4 className="text-xs font-medium text-[#fafafa] mb-1">Stay in the loop</h4>
              <p className="text-[11px] text-[#71717a]">New posts, no spam, unsubscribe anytime.</p>
            </div>
            <form action="/api/subscribe" method="POST" className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
              <input
                type="email"
                name="email"
                placeholder="your@email.com"
                required
                className="px-3 py-2 text-xs outline-none transition-all bg-transparent rounded-sm w-full sm:w-48"
                style={{ border: "1px solid rgba(255,255,255,0.1)", color: "#fafafa" }}
              />
              <button
                type="submit"
                className="px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 rounded-sm whitespace-nowrap"
                style={{ background: "#e4f222", color: "#000", border: "none", cursor: "pointer" }}
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
