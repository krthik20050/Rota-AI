import { notFound } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getPostBySlug, getAllPosts, extractTocHeadings, headingId } from "@/lib/blog";
import { TocSidebar, TocMobile } from "@/components/TocSidebar";
import { ScrollProgress } from "@/components/ScrollProgress";
import type { ReactNode } from "react";

interface Props {
  params: Promise<{ slug: string }>;
}

/** Recursively extract plain text from React children */
function flattenText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(flattenText).join("");
  if (node && typeof node === "object" && "props" in node) {
    const el = node as { props: { children?: ReactNode } };
    return flattenText(el.props.children);
  }
  return "";
}

export async function generateStaticParams() {
  const posts = getAllPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) return { title: "Post not found — Rota AI" };
  return {
    title: `${post.title} — Rota AI`,
    description: post.description,
    alternates: {
      canonical: `https://rota.software/blog/${slug}`,
    },
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      publishedTime: post.date,
      authors: [post.author],
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

const proseClasses =
  "prose prose-invert max-w-none " +
  "prose-headings:text-[#fafafa] prose-headings:font-semibold prose-headings:mt-16 prose-headings:mb-6 prose-headings:scroll-mt-24 " +
  "prose-h2:text-[30px] prose-h2:tracking-tight prose-h2:leading-[1.15] " +
  "prose-h3:text-[21px] prose-h3:mt-12 prose-h3:mb-5 prose-h3:leading-snug " +
  "prose-p:text-[#d4d4d8] prose-p:leading-[1.85] prose-p:mb-7 prose-p:text-[16.5px] " +
  "prose-strong:text-[#fafafa] prose-strong:font-semibold " +
  "prose-em:text-[#d4d4d8] prose-em:not-italic prose-em:font-semibold " +
  "prose-a:text-[#e4f222] prose-a:no-underline hover:prose-a:underline " +
  "prose-code:text-[#e4f222] prose-code:bg-[#111113] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-sm prose-code:text-sm prose-code:font-mono prose-code:before:content-none prose-code:after:content-none " +
  "prose-pre:bg-[#111113] prose-pre:border prose-pre:border-white/[.06] prose-pre:rounded-sm prose-pre:p-5 " +
  "prose-pre:overflow-x-auto " +
  "prose-blockquote:border-l-[#e4f222] prose-blockquote:text-[#a1a1aa] prose-blockquote:pl-6 prose-blockquote:italic " +
  "prose-li:text-[#d4d4d8] prose-li:mb-2.5 prose-li:text-[16px] prose-li:leading-[1.8] " +
  "prose-ul:my-8 prose-ol:my-8 " +
  "prose-hr:border-white/[.06] prose-hr:my-16 " +
  "prose-img:rounded-sm prose-img:my-12 " +
  "prose-table:text-sm prose-table:my-10 " +
  "prose-th:text-[#fafafa] prose-th:font-medium prose-th:py-3 prose-th:px-5 prose-th:border-b prose-th:border-white/[.08] prose-th:text-left " +
  "prose-td:text-[#d4d4d8] prose-td:py-3 prose-td:px-5 prose-td:border-b prose-td:border-white/[.04]";

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  const allPosts = getAllPosts();

  if (!post) notFound();

  const headings = extractTocHeadings(post.content);

  // Related posts
  const relatedPosts = allPosts
    .filter((p) => p.slug !== slug && p.category === post.category)
    .length > 0
    ? allPosts.filter((p) => p.slug !== slug && p.category === post.category)
    : allPosts.filter((p) => p.slug !== slug && p.tags.some((t) => post.tags.includes(t)));
  const shownRelated = relatedPosts.slice(0, 3);

  const isKarthik = post.author === "Karthik Krishnan";

  // Format ISO date like "2026-05-25" → "May 25, 2026"
  const formattedDate = (() => {
    try {
      const d = new Date(post.date);
      if (isNaN(d.getTime())) return post.date;
      return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
    } catch {
      return post.date;
    }
  })();

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Scroll progress indicator */}
      <ScrollProgress />

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
          className="text-xs uppercase tracking-[0.15em] text-[#71717a] hover:text-[#fafafa] transition-colors link-underline"
        >
          All posts
        </Link>
      </nav>

      <div className="max-w-6xl mx-auto px-6 sm:px-10 pt-28 pb-8">
        <div className="flex gap-16">
          {/* Desktop TOC sidebar */}
          {headings.length > 0 && (
            <aside className="hidden lg:block w-56 shrink-0">
              <div className="sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto">
                <TocSidebar items={headings} />
              </div>
            </aside>
          )}

          <article className="flex-1 min-w-0 max-w-3xl">
            {/* Article JSON-LD Schema */}
            <script
              type="application/ld+json"
              dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                  "@context": "https://schema.org",
                  "@type": "Article",
                  "headline": post.title,
                  "description": post.description,
                  "author": {
                    "@type": "Person",
                    "name": post.author,
                    "url": "https://rota.software/blog"
                  },
                  "datePublished": post.date || undefined,
                  "dateModified": post.date || undefined,
                  "image": `https://rota.software/api/og?title=${encodeURIComponent(post.title)}&description=${encodeURIComponent(post.description)}`,
                  "publisher": {
                    "@type": "Organization",
                    "name": "Rota AI",
                    "logo": {
                      "@type": "ImageObject",
                      "url": "https://rota.software/logo.svg"
                    }
                  },
                  "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": `https://rota.software/blog/${slug}`
                  }
                }),
              }}
            />
            {/* BreadcrumbList JSON-LD Schema */}
            <script
              type="application/ld+json"
              dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                  "@context": "https://schema.org",
                  "@type": "BreadcrumbList",
                  "itemListElement": [
                    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://rota.software/" },
                    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://rota.software/blog" },
                    { "@type": "ListItem", "position": 3, "name": post.title, "item": `https://rota.software/blog/${slug}` }
                  ]
                }),
              }}
            />
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
              className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-10"
              style={{ fontSize: "clamp(32px, 4.5vw, 52px)", color: "#fafafa" }}
            >
              {post.title}
            </h1>

            {/* Author row: photo + name/date/role + social profile links */}
            <div
              className="flex items-center justify-between flex-wrap gap-4 mb-14 pb-6"
              style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full overflow-hidden shrink-0 ring-2 ring-white/[0.06]">
                  <img
                    src="/author.jpg"
                    alt={post.author}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-[#fafafa]">{post.author}</span>
                    {isKarthik && (
                      <span className="text-[9px] uppercase tracking-wider text-[#e4f222] font-mono bg-[#e4f222]/10 px-2 py-0.5 rounded-sm">
                        Founder
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-[#50545a] font-mono">
                    <span>{formattedDate}</span>
                    <span aria-hidden="true">·</span>
                    <span>{post.readTime}</span>
                  </div>
                </div>
              </div>
              {/* Social profile links only - no share button */}
              <div className="flex items-center gap-1.5">
                <a
                  href="https://x.com/itsurkk05"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-icon-btn flex items-center justify-center w-8 h-8 rounded-sm text-[#71717a] hover:text-[#fafafa]"
                  style={{ border: "1px solid rgba(255,255,255,0.08)" }}
                  title="Follow on X / Twitter"
                >
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                </a>
                <a
                  href="https://www.instagram.com/karthikkrishnan000/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-icon-btn flex items-center justify-center w-8 h-8 rounded-sm text-[#71717a] hover:text-[#fafafa]"
                  style={{ border: "1px solid rgba(255,255,255,0.08)" }}
                  title="Follow on Instagram"
                >
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                </a>
                <a
                  href="https://www.linkedin.com/in/karthik-krishnan-/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-icon-btn flex items-center justify-center w-8 h-8 rounded-sm text-[#71717a] hover:text-[#fafafa]"
                  style={{ border: "1px solid rgba(255,255,255,0.08)" }}
                  title="Follow on LinkedIn"
                >
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                </a>
              </div>
            </div>

            {/* Mobile TOC (collapsible, shown on small screens) */}
            <TocMobile items={headings} />

            {/* Content with heading IDs for TOC navigation */}
            <div className={proseClasses}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h2: ({ children, ...rest }) => {
                    const text = flattenText(children);
                    const id = headingId(text);
                    return <h2 id={id} {...rest}>{children}</h2>;
                  },
                  h3: ({ children, ...rest }) => {
                    const text = flattenText(children);
                    const id = headingId(text);
                    return <h3 id={id} {...rest}>{children}</h3>;
                  },
                }}
              >
                {post.content}
              </ReactMarkdown>
            </div>
          </article>
        </div>
      </div>

      {/* Author bio - Enhanced profile card */}
      <section className="max-w-3xl mx-auto px-6 sm:px-10 pb-16 pt-6">
        <div
          className="p-6 sm:p-8 rounded-sm animate-fade-slide-up"
          style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)" }}
        >
          <div className="flex items-center gap-1.5 mb-6">
            <span className="text-[9px] uppercase tracking-[0.2em] text-[#50545a] font-mono">About the Author</span>
            <div className="flex-1 h-px bg-white/[.04]" />
          </div>

          <div className="flex flex-col sm:flex-row items-start gap-5">
            <div className="w-16 h-16 rounded-full overflow-hidden shrink-0 ring-2 ring-[#e4f222]/20">
              <img
                src="/author.jpg"
                alt={post.author}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2.5 mb-1">
                <span className="text-sm font-medium text-[#fafafa]">{post.author}</span>
                {isKarthik && (
                  <span className="text-[9px] uppercase tracking-wider text-[#e4f222] font-mono bg-[#e4f222]/10 px-2 py-0.5 rounded-sm">
                    Founder
                  </span>
                )}
              </div>
              {isKarthik && (
                <p className="text-[10px] text-[#71717a] uppercase tracking-wider mb-3">Founder &amp; Developer</p>
              )}
              {post.authorRole && !isKarthik && (
                <p className="text-[10px] text-[#71717a] uppercase tracking-wider mb-3">{post.authorRole}</p>
              )}
              <p className="text-xs text-[#71717a] leading-relaxed mb-5 max-w-lg">
                {isKarthik
                  ? "I built Rota because I didn't have $15 to pay for a dictation tool per month, so I built my own."
                  : "Contributor to Rota AI. Writing about voice dictation, AI, and open source software."}
              </p>
              <div className="flex items-center gap-2.5 flex-wrap">
                <a href="https://x.com/itsurkk05" target="_blank" rel="noopener noreferrer"
                  className="social-icon-btn flex items-center gap-1.5 px-4 py-2 text-[10px] uppercase tracking-wider text-[#71717a] hover:text-[#fafafa] rounded-sm"
                  style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                  Follow on X
                </a>
                <a href="https://www.instagram.com/karthikkrishnan000/" target="_blank" rel="noopener noreferrer"
                  className="social-icon-btn flex items-center gap-1.5 px-4 py-2 text-[10px] uppercase tracking-wider text-[#71717a] hover:text-[#fafafa] rounded-sm"
                  style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                  Follow on IG
                </a>
                <a href="https://www.linkedin.com/in/karthik-krishnan-/" target="_blank" rel="noopener noreferrer"
                  className="social-icon-btn flex items-center gap-1.5 px-4 py-2 text-[10px] uppercase tracking-wider text-[#71717a] hover:text-[#fafafa] rounded-sm"
                  style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                  Follow on LinkedIn
                </a>
                <a href="https://www.youtube.com/@Krthikk" target="_blank" rel="noopener noreferrer"
                  className="social-icon-btn flex items-center gap-1.5 px-4 py-2 text-[10px] uppercase tracking-wider text-[#71717a] hover:text-[#fafafa] rounded-sm"
                  style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                  YouTube
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Related posts */}
      {shownRelated.length > 0 && (
        <section className="max-w-4xl mx-auto px-6 sm:px-10 pb-20 pt-4">
          <h3 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] mb-8 font-mono">Related articles</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {shownRelated.map((related, i) => (
              <Link
                key={related.slug}
                href={`/blog/${encodeURIComponent(related.slug)}`}
                className="group block p-5 transition-all duration-300 hover:bg-[#0c0c0e] rounded-sm"
                style={{ background: "rgba(255,255,255,0.02)", animation: `fadeSlideUp 0.5s ease-out ${i * 0.1}s forwards` }}
              >
                <div className="flex items-center gap-2 text-[10px] font-mono text-[#50545a] mb-3">
                  <span>{related.category}</span>
                  <span aria-hidden="true">·</span>
                  <span>{related.readTime}</span>
                </div>
                <h4 className="text-sm font-medium text-[#fafafa] group-hover:text-[#e4f222] transition-colors leading-snug mb-2 line-clamp-2">{related.title}</h4>
                <p className="text-[11px] text-[#71717a] leading-relaxed line-clamp-2">{related.description}</p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="py-12 px-6 sm:px-10">
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
