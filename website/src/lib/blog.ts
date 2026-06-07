import fs from "fs";
import path from "path";
import matter from "gray-matter";

export interface BlogPost {
  slug: string;
  title: string;
  date: string;
  description: string;
  tags: string[];
  content: string;
  author: string;
  authorRole?: string;
  authorImage?: string;
  authorTwitter?: string;
  authorLinkedin?: string;
  authorWebsite?: string;
  image?: string;
  readTime?: string;
  category?: string;
}

const BLOG_DIR = path.join(process.cwd(), "blog");

function estimateReadTime(content: string): string {
  const wordsPerMinute = 200;
  const words = content.split(/\s+/).length;
  const minutes = Math.max(1, Math.ceil(words / wordsPerMinute));
  return `${minutes} min read`;
}

export function getAllPosts(): BlogPost[] {
  if (!fs.existsSync(BLOG_DIR)) return [];
  const files = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith(".md"));

  return files
    .map((file) => {
      const slug = file.replace(/\.md$/, "").replace(/[^a-zA-Z0-9_-]/g, "-");
      const raw = fs.readFileSync(path.join(BLOG_DIR, file), "utf-8");
      const { data, content } = matter(raw);
      return {
        slug,
        title: data.title || slug,
        date: data.date || "",
        description: data.description || "",
        tags: data.tags || [],
        content,
        author: data.author || "Rota AI Team",
        authorRole: data.authorRole,
        authorImage: data.authorImage,
        authorTwitter: data.authorTwitter,
        authorLinkedin: data.authorLinkedin,
        authorWebsite: data.authorWebsite,
        image: data.image,
        readTime: data.readTime || estimateReadTime(content),
        category: data.category || (data.tags?.[0]) || "General",
      };
    })
    .sort((a, b) => (a.date > b.date ? -1 : 1));
}

export function getPostBySlug(slug: string): BlogPost | null {
  try {
    const raw = fs.readFileSync(path.join(BLOG_DIR, `${slug}.md`), "utf-8");
    const { data, content } = matter(raw);
    return {
      slug,
      title: data.title || slug,
      date: data.date || "",
      description: data.description || "",
      tags: data.tags || [],
      content,
      author: data.author || "Rota AI Team",
      authorRole: data.authorRole,
      authorImage: data.authorImage,
      authorTwitter: data.authorTwitter,
      authorLinkedin: data.authorLinkedin,
      authorWebsite: data.authorWebsite,
      image: data.image,
      readTime: data.readTime || estimateReadTime(content),
      category: data.category || (data.tags?.[0]) || "General",
    };
  } catch {
    return null;
  }
}
