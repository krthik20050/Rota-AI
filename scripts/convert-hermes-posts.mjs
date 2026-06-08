/**
 * Convert Hermes SEO blog posts to Rota AI website blog format.
 *
 * What this does:
 * 1. Maps frontmatter from Hermes format → BlogPost interface (fixes #1: no double-quoting)
 * 2. Fixes AI sloppiness: nd→and (fixes #3: context-aware), em dashes, AI transitions (fixes #4: more patterns)
 * 3. Removes number prefixes from titles
 * 4. Assigns categories (fixes #2: no more truncation)
 * 5. Writes converted posts to website/blog/ (overwrites if needed)
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const HERMES_DIR = path.join(ROOT, "Hermes SEO strategy", "BLOG_POSTS");
const OUTPUT_DIR = path.join(ROOT, "website", "blog");

// Existing posts to NEVER overwrite
const KEEP_EXISTING = new Set([
  "why-i-built-rota-ai.md",
  "rota-ai-free-voice-dictation-guide.md",
  "wispr-flow-alternatives-free-2026.md",
  "free-ai-tools-student-developer.md",
]);

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// ── AI Sloppiness Fixes (#3, #4) ─────────────────────────

/** Strip surrounding quotes from a string */
function stripQuotes(s) {
  if (!s) return s;
  s = s.trim();
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    s = s.slice(1, -1);
  }
  return s;
}

/**
 * Fix AI-generated patterns in markdown text.
 * Uses CONTEXT-AWARE replacement for "nd" → "and" to avoid corrupting words
 * like "sound", "backend", "second", "kind", "found" etc.
 */
function fixAISloppiness(text) {
  let result = text;

  // ── nd → and: context-aware (FIX #3: no more "souand") ──
  // Only replace "nd" when it's a standalone word with whitespace/punctuation around it
  result = result.replace(/(\s)nd(\s)/g, "$1and$2");
  result = result.replace(/(\s)nd([,;:.!?])/g, "$1and$2");
  result = result.replace(/([,;:.!?])nd(\s)/g, "$1and$2");
  result = result.replace(/^nd(\s)/gm, "and$1");           // start of line
  result = result.replace(/(\s)nd$/gm, "$1and");           // end of line

  // ── Fix double-spaced dash to em dash ──
  result = result.replace(/ — /g, " — ");
  result = result.replace(/ - /g, " — ");

  // ── Clean up triple-dot spacing ──
  result = result.replace(/\s+\.\.\.\s+/g, " ... ");

  // ── Remove self-deprecating AI transition phrases (FIX #4) ──
  const removePhrases = [
    /^Ok(?:ay)?,?\s+I\s+[a-z]+ be straight with you\.?\s*/gim,
    /^ok I am going to be straight with you\.?\s*/gim,
    /^Here is the thing\.?\s*/gim,
    /^Here's the thing\.?\s*/gim,
    /^Here is the deal\.?\s*/gim,
    /^Here's the deal\.?\s*/gim,
    /^Let me be real for a second\.?\s*/gim,
    /^Let's be real for a second\.?\s*/gim,
    /^Alright,?\s+let me be straight\.?\s*/gim,
    /^And honestly,?\s*/gim,
    /^Lowkey,?\s*/gim,
  ];

  for (const phrase of removePhrases) {
    while (phrase.test(result)) {
      result = result.replace(phrase, "");
    }
  }

  // ── Keep Gen Z slang as-is (tbh, fr) — user preference ──
  // Only expand YMMV since it's not commonly used slang
  result = result.replace(/\b(?:YMMV|ymmv)\b/g, "your mileage may vary");

  // ── Fix known Hermes typos ──
  result = result.replace(/awarendness/gi, "awareness");

  // ── Clean up awkward phrasing ──
  result = result.replace(/^That's it\.\s*/gm, "");

  // ── Fix "That is it." when it's clearly a concluding AI phrase ──
  result = result.replace(/^That is it\.\s*/gm, "");
  result = result.replace(/^That's it\.\s*/gm, "");

  return result;
}

/** Remove number prefix from title like "5. How to Run..." → "How to Run..." */
function cleanTitle(title) {
  return title.replace(/^\d+\.\s+/, "").trim();
}

/** Slugify a string for filename use */
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

// ── Frontmatter parsing (FIX #1: strip quotes) ───────────

function parseHermesFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, body: content };

  const rawFm = match[1];
  const body = match[2];

  const fm = {};
  const lines = rawFm.split("\n");
  let currentKey = null;

  for (const line of lines) {
    const keyMatch = line.match(/^(\w+):\s*(.*)/);
    if (keyMatch) {
      currentKey = keyMatch[1];
      // STRIP surrounding quotes from value (#1)
      fm[currentKey] = stripQuotes(keyMatch[2]);
    } else if (currentKey && line.startsWith("  ")) {
      // Handle multi-line values (like tags arrays)
      if (line.includes("[")) {
        const arrayMatch = line.match(/\[([^\]]*)\]/);
        if (arrayMatch) {
          fm[currentKey] = arrayMatch[1].split(",").map((s) => stripQuotes(s.trim()));
        }
      }
    }
  }

  return { frontmatter: fm, body };
}

// ── Frontmatter conversion (FIX #2: better categories) ───

const CATEGORY_MAP = {
  "comparison": "Comparisons",
  "guide": "Guides",
  "tutorial": "Guides",
  "how-to": "Guides",
  "privacy": "Privacy",
  "offline": "Offline",
  "student": "For Students",
  "students": "For Students",
  "developer": "For Developers",
  "developers": "For Developers",
  "tools": "For Developers",
  "windows": "Windows",
  "mac": "Mac",
  "linux": "Linux",
  "voice-dictation": "Voice Dictation",
  "transcription": "Voice Dictation",
  "vad": "Voice Dictation",
  "accuracy": "Voice Dictation",
  "open-source": "Open Source",
  "ai": "AI",
  "wispr-flow": "Comparisons",
  "superwhisper": "Comparisons",
  "otter": "Comparisons",
  "rota-ai": "Product Updates",
  "pricing": "Comparisons",
  "snippets": "Guides",
  "settings": "Guides",
  "setup": "Guides",
  "round-robin": "Technical",
};

function deriveCategory(hermesFm, tags) {
  // Try mapping from first tag
  if (tags && tags.length > 0) {
    const tag = tags[0].toLowerCase().trim();
    if (CATEGORY_MAP[tag]) return CATEGORY_MAP[tag];
  }

  // Try mapping from target_keyword parts
  const targetKw = (hermesFm.target_keyword || "").toLowerCase();
  for (const [key, val] of Object.entries(CATEGORY_MAP)) {
    if (targetKw.includes(key)) return val;
  }

  // Derive from title
  const title = (hermesFm.title || hermesFm.meta_title || "").toLowerCase();
  for (const [key, val] of Object.entries(CATEGORY_MAP)) {
    if (title.includes(key)) return val;
  }

  return "Voice Dictation";
}

function convertFrontmatter(hermesFm) {
  // Title: already stripped of quotes by parser
  let title = hermesFm.title || hermesFm.meta_title || "";
  title = cleanTitle(title);

  // Description: already stripped of quotes
  let description = hermesFm.description || hermesFm.meta_description || "";

  // Author
  let author = hermesFm.author || "Karthik Krishnan";

  // Date
  let date = hermesFm.date || "";

  // Tags
  let tags = [];
  if (Array.isArray(hermesFm.tags)) {
    tags = hermesFm.tags;
  } else if (typeof hermesFm.tags === "string") {
    tags = hermesFm.tags
      .replace(/[[\]']/g, "")
      .split(",")
      .map((t) => t.trim());
  }

  // Category (#2: smart mapping, no truncation)
  let category = deriveCategory(hermesFm, tags);

  return { title, description, author, date, tags, category };
}

function buildFrontmatterString(fm) {
  const lines = ["---"];
  if (fm.title) lines.push(`title: "${fm.title}"`);
  if (fm.description) lines.push(`description: "${fm.description}"`);
  if (fm.author) lines.push(`author: ${fm.author}`);
  if (fm.date) lines.push(`date: ${fm.date}`);
  if (fm.tags && fm.tags.length > 0) {
    lines.push(`tags: [${fm.tags.map((t) => t.trim()).join(", ")}]`);
  }
  if (fm.category) lines.push(`category: ${fm.category}`);
  lines.push("---");
  return lines.join("\n");
}

// ── Post-processing validation (#3) ──────────────────────

/** Known corrupted patterns to flag (should never appear) */
const CORRUPTED_PATTERNS = [
  "souand", "backeand", "secoand", "minuteand",
  "awarendness", "commanand", "commanands",
  "commmand", "aand", "theand", "thisand",
  "\\bnd[.,;:!?\\s]",  // any remaining standalone nd
];

function validateBody(body, title) {
  const issues = [];
  for (const pattern of CORRUPTED_PATTERNS) {
    const re = new RegExp(pattern, "gi");
    const matches = body.match(re);
    if (matches) {
      issues.push(`   ⚠️  Found corrupted pattern "${pattern}" (${matches.length}x): "${matches[0].substring(0, 50)}"`);
    }
  }
  return issues;
}

// ── Main ─────────────────────────────────────────────────

const files = fs
  .readdirSync(HERMES_DIR)
  .filter((f) => f.endsWith(".md"))
  .sort();

console.log(`\nFound ${files.length} Hermes blog posts to convert.\n`);

let converted = 0;
let skipped_existing = 0;
let skipped_failed = 0;
let total_issues = 0;

for (const file of files) {
  const filePath = path.join(HERMES_DIR, file);
  const rawContent = fs.readFileSync(filePath, "utf-8");

  // Parse and convert
  const { frontmatter: hermesFm, body } = parseHermesFrontmatter(rawContent);
  const newFm = convertFrontmatter(hermesFm);

  if (!newFm.title) {
    console.log(`  ⚠️  Skipped ${file}: no title found`);
    skipped_failed++;
    continue;
  }

  // Clean body AND description (fix AI sloppiness on both)
  let cleanBody = fixAISloppiness(body);
  newFm.description = fixAISloppiness(newFm.description);

  // Fix known edge cases from nd→and replacement
  cleanBody = cleanBody.replace(/If and you/g, "If you");
  cleanBody = cleanBody.replace(/if and you/g, "if you");

  // If no date, use file modification time
  if (!newFm.date) {
    const stats = fs.statSync(filePath);
    const mtime = stats.mtime;
    newFm.date = mtime.toISOString().split("T")[0];
  }

  // Build output filename from slug
  const slug = slugify(newFm.title);
  const outputFilename = `${slug}.md`;
  const outputPath = path.join(OUTPUT_DIR, outputFilename);

  // Check if this is an existing post to preserve
  if (KEEP_EXISTING.has(outputFilename)) {
    console.log(`  ● Kept existing: ${outputFilename}`);
    skipped_existing++;
    continue;
  }

  // Clean up body formatting
  cleanBody = cleanBody.replace(/\n{4,}/g, "\n\n\n");

  // Validate for corruption (#3)
  const issues = validateBody(cleanBody, newFm.title);
  for (const issue of issues) {
    console.log(issue);
    total_issues++;
  }

  // Build final content
  const frontmatterStr = buildFrontmatterString(newFm);
  const finalContent = frontmatterStr + "\n\n" + cleanBody.trim() + "\n";

  // Write (overwrite — we already cleaned old ones)
  fs.writeFileSync(outputPath, finalContent, "utf-8");
  console.log(`  ✅ ${file} → ${outputFilename}`);
  console.log(`     "${newFm.title}" | ${newFm.author} | ${newFm.date} | ${newFm.category}`);
  converted++;
}

console.log(`\nDone. ${converted} converted, ${skipped_existing} existing kept, ${skipped_failed} failed.`);
if (total_issues > 0) {
  console.log(`⚠️  ${total_issues} potential corruptions flagged — review manually.\n`);
} else {
  console.log("✅ No corruptions detected.\n");
}
