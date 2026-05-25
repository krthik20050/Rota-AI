import { notFound } from "next/navigation";
import Link from "next/link";
import { getPostBySlug, getAllPosts } from "@/lib/blog";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const posts = getAllPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) return { title: "Post not found - Rota AI" };
  return { title: `${post.title} - Rota AI` };
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug(slug);

  if (!post) notFound();

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
          href="/blog"
          className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors"
        >
          ← All posts
        </Link>
      </nav>

      <article className="max-w-3xl mx-auto px-6 sm:px-10 pt-28 pb-20">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-xs text-[#71717a] font-mono">{post.date}</span>
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-sm"
              style={{ background: "rgba(228,242,34,0.06)", color: "#e4f222" }}
            >
              {tag}
            </span>
          ))}
        </div>

        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.95] mb-8"
          style={{ fontSize: "clamp(32px, 5vw, 52px)", color: "#fafafa" }}
        >
          {post.title}
        </h1>

        <div
          className="prose prose-invert prose-sm max-w-none
            prose-headings:text-[#fafafa] prose-headings:font-semibold prose-headings:mt-8 prose-headings:mb-4
            prose-p:text-[#a1a1aa] prose-p:leading-relaxed prose-p:mb-4
            prose-strong:text-[#fafafa] prose-strong:font-medium
            prose-a:text-[#e4f222] prose-a:no-underline hover:prose-a:underline
            prose-code:text-[#e4f222] prose-code:bg-[#111113] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-sm prose-code:text-xs prose-code:font-mono
            prose-pre:bg-[#111113] prose-pre:border prose-pre:border-white/[.06] prose-pre:rounded-sm
            prose-li:text-[#a1a1aa] prose-li:mb-1
            prose-h2:text-2xl prose-h2:mt-12 prose-h2:mb-4
            prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
            prose-table:text-sm
            prose-th:text-[#fafafa] prose-th:font-medium prose-th:py-2 prose-th:px-3 prose-th:border-b prose-th:border-white/[.08]
            prose-td:text-[#a1a1aa] prose-td:py-2 prose-td:px-3 prose-td:border-b prose-td:border-white/[.04]"
          dangerouslySetInnerHTML={{
            __html: post.content
              .replace(/^# .+$/gm, "")
              .replace(/^## /gm, "<h2>")
              .replace(/^### /gm, "<h3>")
              .replace(/\n\n/g, "</p><p>")
              .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
              .replace(/`(.+?)`/g, "<code>$1</code>")
              .replace(/^- (.+)$/gm, "<li>$1</li>")
              .replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>")
              .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
              .trim(),
          }}
        />
      </article>
    </div>
  );
}
