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
}

const BLOG_DIR = path.join(process.cwd(), "blog");

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
    };
  } catch {
    return null;
  }
}
