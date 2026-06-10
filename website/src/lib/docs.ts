import fs from "fs";
import path from "path";
import matter from "gray-matter";

const DOCS_DIR = path.join(process.cwd(), "docs");

export function getDocContent(slug: string): { content: string; title: string } {
  try {
    const fullPath = path.join(DOCS_DIR, `${slug}.md`);
    if (!fs.existsSync(fullPath)) {
      return { content: "", title: "" };
    }
    const fileContents = fs.readFileSync(fullPath, "utf8");
    const { data, content } = matter(fileContents);
    return {
      content,
      title: data.title || "",
    };
  } catch (e) {
    console.error(`Error reading doc ${slug}:`, e);
    return { content: "", title: "" };
  }
}
