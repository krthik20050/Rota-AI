import Link from "next/link";
import { getAllPosts } from "@/lib/blog";

export const metadata = {
  title: "Blog - Rota AI",
  description: "Voice dictation, open source AI, and building Rota AI.",
};

export default function BlogPage() {
  const posts = getAllPosts();

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
        <Link href="/" className="flex items-center gap-2.5">
          <div
            className="w-6 h-6 flex items-center justify-center"
            style={{ background: "#e4f222", borderRadius: 2 }}
          >
            <svg className="w-3 h-3 text-black" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
          </div>
          <span className="text-sm font-semibold tracking-[0.12em] uppercase text-[#fafafa]">
            Rota AI
          </span>
        </Link>
        <Link
          href="/"
          className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors"
        >
          ← Back to home
        </Link>
      </nav>

      <div className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4"
          style={{ fontSize: "clamp(40px, 6vw, 64px)", color: "#fafafa" }}
        >
          Blog
        </h1>
        <p className="text-sm text-[#a1a1aa] mb-16">
          Voice dictation, open source AI, and building Rota AI.
        </p>

        <div className="space-y-0">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${encodeURIComponent(post.slug)}`}
              className="block py-8 border-b border-white/[.06] group"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs text-[#71717a] font-mono">{post.date}</span>
                {post.tags.slice(0, 2).map((tag) => (
                  <span
                    key={tag}
                    className="text-xs px-2 py-0.5 rounded-sm"
                    style={{
                      background: "rgba(228,242,34,0.06)",
                      color: "#e4f222",
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <h2 className="text-xl font-semibold text-[#fafafa] mb-2 group-hover:text-[#e4f222] transition-colors">
                {post.title}
              </h2>
              <p className="text-sm text-[#a1a1aa] leading-relaxed">
                {post.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
