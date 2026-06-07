import { notFound } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getPostBySlug, getAllPosts, extractTocHeadings, headingId } from "@/lib/blog";
import { TocSidebar, TocMobile } from "@/components/TocSidebar";
import type { ReactNode } from "react";

interface Props {
  params: Promise<{ slug: string }>;
}

const AUTHOR_SOCIALS = [
  {
    name: "X / Twitter",
    href: "https://x.com/itsurkk05",
    icon: (
      <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
    ),
  },
  {
    name: "Instagram",
    href: "https://www.instagram.com/karthikkrishnan000/",
    icon: (
      <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
    ),
  },
  {
    name: "YouTube",
    href: "https://www.youtube.com/@Krthikk",
    icon: (
      <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
    ),
  },
];

/** Recursively extract plain text from React children */
function flattenText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(flattenText).join("");
  if (node && typeof node === "object" && "props" in node) {
    return flattenText((node as any).props.children);
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

const proseClasses =
  "prose prose-invert max-w-none " +
  "prose-headings:text-[#fafafa] prose-headings:font-semibold prose-headings:mt-14 prose-headings:mb-6 " +
  "prose-h2:text-[24px] prose-h2:tracking-tight prose-h2:leading-snug " +
  "prose-h3:text-[18px] prose-h3:mt-10 prose-h3:mb-5 " +
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

            {/* Author info */}
            <div className="flex items-center justify-between flex-wrap gap-4 mb-14 pb-6">
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
                <ShareLink href={`https://twitter.com/intent/tweet?text=${shareText}&url=${encodeURIComponent(postUrl)}`} label="Share on X"
                  icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>} />
                <ShareLink href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(postUrl)}`} label="Share on LinkedIn"
                  icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>} />
                <ShareLink href={`https://wa.me/?text=${encodeURIComponent(post.title + " " + postUrl)}`} label="Share on WhatsApp"
                  icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>} />
                <ShareLink href={`mailto:?subject=${shareText}&body=${encodeURIComponent(postUrl)}`} label="Share via Email"
                  icon={<svg viewBox="0 0 24 24" className="w-3 h-3 fill-current text-[#71717a]"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>} />
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

      {/* Author bio */}
      <section className="max-w-3xl mx-auto px-6 sm:px-10 pb-16 pt-6">
        <div className="flex items-start gap-4 p-6 sm:p-8 rounded-sm"
          style={{ background: "rgba(255,255,255,0.02)" }}>
          <div className="w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold uppercase shrink-0"
            style={{ background: "rgba(228,242,34,0.1)", color: "#e4f222" }}>
            {post.author.split(" ").map(n => n[0]).join("").slice(0, 2)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-[#fafafa] mb-0.5">{post.author}</div>
            {post.authorRole && (
              <p className="text-[10px] text-[#71717a] uppercase tracking-wider mb-2">{post.authorRole}</p>
            )}
            <p className="text-xs text-[#71717a] leading-relaxed mb-4">
              {post.author === "Karthik Krishnan"
                ? "Built Rota AI because no student should pay $15/month for a dictation tool. Writes about open source, voice technology, and building things that matter."
                : "Contributor to Rota AI. Writing about voice dictation, AI, and open source software."}
            </p>
            <div className="flex items-center gap-2.5 flex-wrap">
              {AUTHOR_SOCIALS.map((social) => (
                <a key={social.name} href={social.href} target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] uppercase tracking-wider text-[#71717a] hover:text-[#e4f222] hover:bg-white/[0.04] transition-all rounded-sm"
                  style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
                  {social.icon}
                  <span>{social.name}</span>
                </a>
              ))}
              {post.authorTwitter && (
                <a href={`https://x.com/${post.authorTwitter}`} target="_blank" rel="noopener noreferrer"
                  className="text-[10px] text-[#50545a] hover:text-[#e4f222] transition-colors uppercase tracking-wider font-mono">X/Twitter</a>
              )}
              {post.authorLinkedin && (
                <a href={`https://linkedin.com/in/${post.authorLinkedin}`} target="_blank" rel="noopener noreferrer"
                  className="text-[10px] text-[#50545a] hover:text-[#e4f222] transition-colors uppercase tracking-wider font-mono">LinkedIn</a>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Related posts */}
      {shownRelated.length > 0 && (
        <section className="max-w-4xl mx-auto px-6 sm:px-10 pb-20 pt-4">
          <h3 className="text-[10px] uppercase tracking-[0.2em] text-[#50545a] mb-8 font-mono">Related articles</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {shownRelated.map((related) => (
              <Link key={related.slug} href={`/blog/${encodeURIComponent(related.slug)}`}
                className="group block p-5 transition-all duration-200 hover:bg-[#0c0c0e] rounded-sm"
                style={{ background: "rgba(255,255,255,0.02)" }}>
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
