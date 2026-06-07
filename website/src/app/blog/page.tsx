import Link from "next/link";
import { getAllPosts } from "@/lib/blog";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blog - Rota AI",
  description: "Voice dictation, open source AI, and building Rota AI.",
};

export default function BlogPage() {
  const posts = getAllPosts();
  const latestPosts = posts.slice(0, 5);
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

      {/* Hero — minimal, like Wispr Flow's "Inside Flow: Blog" */}
      <div className="px-6 sm:px-10 pt-28 pb-16">
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
        <div className="flex flex-col lg:flex-row gap-16">
          {/* Main content */}
          <div className="flex-1 min-w-0">
            {/* Category filter tabs — subtle, like Wispr Flow */}
            {categories.length > 1 && (
              <div className="flex items-center gap-4 mb-10 overflow-x-auto pb-2">
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

            {/* Blog list — text-only cards with hairline dividers */}
            {posts.map((post, i) => (
              <Link
                key={post.slug}
                href={`/blog/${encodeURIComponent(post.slug)}`}
                className={`group block py-8 ${
                  i > 0 ? "border-t border-white/[0.06]" : ""
                } transition-colors hover:bg-[#0c0c0e] -mx-6 sm:-mx-8 px-6 sm:px-8`}
              >
                <div className="flex items-start gap-3 mb-3">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-[#71717a]">
                    {post.category}
                  </span>
                  <span className="text-[10px] font-mono text-[#50545a]" aria-hidden="true">·</span>
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

            {/* Load more — placeholder for future pagination */}
            {posts.length > 10 && (
              <div className="pt-10 text-center">
                <button className="text-[11px] font-mono uppercase tracking-[0.2em] text-[#71717a] hover:text-[#fafafa] transition-colors cursor-pointer bg-transparent border-none">
                  Load more
                </button>
              </div>
            )}
          </div>

          {/* Sidebar — Latest Articles */}
          <aside className="w-full lg:w-64 shrink-0">
            <div className="lg:sticky lg:top-24">
              <h3 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] mb-5 font-mono">Latest articles</h3>
              <div className="space-y-0">
                {latestPosts.map((post, i) => (
                  <div key={post.slug} className={`py-3 ${i > 0 ? "border-t border-white/[0.04]" : ""}`}>
                    <Link
                      href={`/blog/${encodeURIComponent(post.slug)}`}
                      className="group block"
                    >
                      <h4 className="text-xs font-medium text-[#a1a1aa] group-hover:text-[#fafafa] transition-colors leading-snug line-clamp-2 mb-1.5">
                        {post.title}
                      </h4>
                      <div className="flex items-center gap-1.5 text-[10px] text-[#50545a] font-mono">
                        <span>{post.date}</span>
                        <span aria-hidden="true">·</span>
                        <span>{post.readTime}</span>
                      </div>
                    </Link>
                  </div>
                ))}
              </div>

              {/* Subscribe — minimal inline form */}
              <div className="mt-8">
                <h4 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] mb-3 font-mono">Stay in the loop</h4>
                <p className="text-[11px] text-[#71717a] leading-relaxed mb-4">
                  New posts, no spam, unsubscribe anytime.
                </p>
                <form action="/api/subscribe" method="POST" className="flex flex-col gap-2">
                  <input
                    type="email"
                    name="email"
                    placeholder="your@email.com"
                    required
                    className="w-full px-3 py-2 text-xs outline-none transition-all bg-transparent rounded-sm"
                    style={{ border: "1px solid rgba(255,255,255,0.1)", color: "#fafafa" }}
                  />
                  <button
                    type="submit"
                    className="w-full px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90 rounded-sm"
                    style={{ background: "#e4f222", color: "#000", border: "none", cursor: "pointer" }}
                  >
                    Subscribe
                  </button>
                </form>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
