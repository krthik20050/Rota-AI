import { notFound } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
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
  return {
    title: `${post.title} - Rota AI`,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      images: [
        {
          url: `/api/og?title=${encodeURIComponent(post.title)}&description=${encodeURIComponent(post.description)}`,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.description,
    },
  };
}

function ShareLink({ href, label, icon }: { href: string; label: string; icon: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center justify-center w-8 h-8 rounded-sm transition-all duration-200 hover:scale-110"
      style={{ border: "1px solid rgba(255,255,255,0.08)" }}
      title={label}
    >
      {icon}
    </a>
  );
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  const allPosts = getAllPosts();

  if (!post) notFound();

  // Related posts: same category first, then fallback to shared tags
  const relatedPosts = allPosts
    .filter((p) => p.slug !== slug && p.category === post.category)
    .length > 0
    ? allPosts.filter((p) => p.slug !== slug && p.category === post.category)
    : allPosts.filter((p) => p.slug !== slug && p.tags.some((t) => post.tags.includes(t)));
  const shownRelated = relatedPosts.slice(0, 3);

  const siteUrl = "https://rota.software";
  const postUrl = `${siteUrl}/blog/${encodeURIComponent(slug)}`;
  const shareText = encodeURIComponent(post.title);

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
        <Link
          href="/blog"
          className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors"
        >
          All posts
        </Link>
      </nav>

      <article className="max-w-2xl mx-auto px-6 sm:px-10 pt-28 pb-8">
        {/* Category & meta */}
        <div className="flex items-center gap-3 mb-6">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#71717a]">
            {post.category}
          </span>
          <span className="text-[8px] text-[#50545a]" aria-hidden="true">·</span>
          <span className="text-[10px] font-mono text-[#50545a]">{post.readTime}</span>
        </div>

        {/* Title */}
        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-8"
          style={{ fontSize: "clamp(28px, 4vw, 44px)", color: "#fafafa" }}
        >
          {post.title}
        </h1>

        {/* Author info row — text only, no avatar box */}
        <div className="flex items-center justify-between flex-wrap gap-4 mb-14 pb-8"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
          <div>
            <div className="text-sm font-medium text-[#fafafa]">{post.author}</div>
            <div className="flex items-center gap-2 text-[11px] text-[#50545a] font-mono">
              <span>{post.date}</span>
              <span aria-hidden="true">·</span>
              <span>{post.readTime}</span>
            </div>
          </div>

          {/* Share links */}
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] uppercase tracking-[0.15em] text-[#50545a] font-mono mr-1">Share</span>
            <ShareLink
              href={`https://twitter.com/intent/tweet?text=${shareText}&url=${encodeURIComponent(postUrl)}`}
              label="Share on X"
              icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>}
            />
            <ShareLink
              href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(postUrl)}`}
              label="Share on LinkedIn"
              icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>}
            />
            <ShareLink
              href={`https://wa.me/?text=${encodeURIComponent(post.title + " " + postUrl)}`}
              label="Share on WhatsApp"
              icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>}
            />
            <ShareLink
              href={`mailto:?subject=${shareText}&body=${encodeURIComponent(postUrl)}`}
              label="Share via Email"
              icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>}
            />
          </div>
        </div>

        {/* Content — clean prose, proper hierarchy */}
        <div className="prose prose-invert max-w-none
          prose-headings:text-[#fafafa] prose-headings:font-semibold prose-headings:mt-12 prose-headings:mb-5
          prose-h2:text-[22px] prose-h2:tracking-tight prose-h2:leading-snug prose-h2:border-none prose-h2:pb-0
          prose-h3:text-[17px] prose-h3:mt-8 prose-h3:mb-4
          prose-p:text-[#d4d4d8] prose-p:leading-[1.75] prose-p:mb-6 prose-p:text-[16px]
          prose-strong:text-[#fafafa] prose-strong:font-semibold
          prose-em:text-[#d4d4d8] prose-em:not-italic prose-em:font-semibold
          prose-a:text-[#e4f222] prose-a:no-underline hover:prose-a:underline
          prose-code:text-[#e4f222] prose-code:bg-[#111113] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-sm prose-code:text-sm prose-code:font-mono prose-code:before:content-none prose-code:after:content-none
          prose-pre:bg-[#111113] prose-pre:border prose-pre:border-white/[.06] prose-pre:rounded-sm prose-pre:p-4
          prose-pre:overflow-x-auto
          prose-blockquote:border-l-[#e4f222] prose-blockquote:text-[#a1a1aa] prose-blockquote:pl-5 prose-blockquote:italic
          prose-li:text-[#d4d4d8] prose-li:mb-2 prose-li:text-[16px] prose-li:leading-[1.7]
          prose-ul:my-6 prose-ol:my-6
          prose-hr:border-white/[.06] prose-hr:my-14
          prose-img:rounded-sm prose-img:my-10
          prose-table:text-sm prose-table:my-8
          prose-th:text-[#fafafa] prose-th:font-medium prose-th:py-2.5 prose-th:px-4 prose-th:border-b prose-th:border-white/[.08] prose-th:text-left
          prose-td:text-[#d4d4d8] prose-td:py-2.5 prose-td:px-4 prose-td:border-b prose-td:border-white/[.04]
        ">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {post.content}
          </ReactMarkdown>
        </div>
      </article>

      {/* Author bio — hairline divider, no box */}
      <section className="max-w-2xl mx-auto px-6 sm:px-10 pb-16 pt-8"
        style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="flex items-start gap-4 pt-8">
          <div className="w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold uppercase shrink-0"
            style={{ background: "rgba(228,242,34,0.1)", color: "#e4f222" }}>
            {post.author.split(" ").map(n => n[0]).join("").slice(0, 2)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-[#fafafa] mb-0.5">{post.author}</div>
            {post.authorRole && (
              <p className="text-[10px] text-[#71717a] uppercase tracking-wider mb-2">{post.authorRole}</p>
            )}
            <p className="text-xs text-[#71717a] leading-relaxed">
              {post.author === "Karthik Krishnan"
                ? "Built Rota AI because no student should pay $15/month for a dictation tool. Writes about open source, voice technology, and building things that matter."
                : "Contributor to Rota AI. Writing about voice dictation, AI, and open source software."}
            </p>
            {post.authorTwitter || post.authorLinkedin || post.authorWebsite ? (
              <div className="flex items-center gap-3 mt-3">
                {post.authorTwitter && (
                  <a href={`https://x.com/${post.authorTwitter}`} target="_blank" rel="noopener noreferrer"
                    className="text-[10px] text-[#71717a] hover:text-[#e4f222] transition-colors uppercase tracking-wider font-mono">
                    X / Twitter
                  </a>
                )}
                {post.authorLinkedin && (
                  <a href={`https://linkedin.com/in/${post.authorLinkedin}`} target="_blank" rel="noopener noreferrer"
                    className="text-[10px] text-[#71717a] hover:text-[#e4f222] transition-colors uppercase tracking-wider font-mono">
                    LinkedIn
                  </a>
                )}
                {post.authorWebsite && (
                  <a href={post.authorWebsite} target="_blank" rel="noopener noreferrer"
                    className="text-[10px] text-[#71717a] hover:text-[#e4f222] transition-colors uppercase tracking-wider font-mono">
                    GitHub
                  </a>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </section>

      {/* Related posts — hairline links, no boxes */}
      {shownRelated.length > 0 && (
        <section className="max-w-4xl mx-auto px-6 sm:px-10 pb-20">
          <div className="pt-12" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
            <h3 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] mb-6 font-mono">Related articles</h3>
            <div className="divide-y divide-white/[0.04]">
              {shownRelated.map((related) => (
                <Link
                  key={related.slug}
                  href={`/blog/${encodeURIComponent(related.slug)}`}
                  className="group block py-5 transition-colors hover:bg-[#0c0c0e] -mx-4 px-4"
                >
                  <div className="flex items-center gap-2 text-[10px] font-mono text-[#50545a] mb-2">
                    <span>{related.category}</span>
                    <span aria-hidden="true">·</span>
                    <span>{related.date}</span>
                    <span aria-hidden="true">·</span>
                    <span>{related.readTime}</span>
                  </div>
                  <h4 className="text-sm font-medium text-[#fafafa] group-hover:text-[#e4f222] transition-colors leading-snug mb-1">
                    {related.title}
                  </h4>
                  <p className="text-[12px] text-[#71717a] leading-relaxed line-clamp-1">
                    {related.description}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-12 px-6 sm:px-10" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-5 h-5 flex items-center justify-center rounded-sm" style={{ background: "#e4f222" }}>
              <svg className="w-2.5 h-2.5 text-black" viewBox="0 0 24 24" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/></svg>
            </div>
            <span className="text-xs font-semibold tracking-[0.12em] uppercase text-[#fafafa]">Rota AI</span>
          </div>
          <p className="text-[10px] uppercase tracking-widest text-[#71717a]">&copy; 2026 Rota AI &middot; MIT License</p>
        </div>
      </footer>
    </div>
  );
}
