/**
 * Fix blog post formatting issues for production readiness:
 * 1. Spread dates across 2026-01 to 2026-06 (not all same day)
 * 2. Replace em dashes (—) with regular hyphens in blog body content
 * 3. Remove emojis from blog content (keep only in frontmatter)
 * 4. Fix any other formatting inconsistencies
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const BLOG_DIR = path.join(ROOT, "website", "blog");

const files = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith(".md"));

// Date distribution: spread 29 posts from 2026-01-10 to 2026-05-15
// That's roughly 125 days / 29 posts ≈ 4.3 days between each
const NEW_DATES = {
  "5-free-voice-dictation-apps-for-windows-ranked.md": "2026-01-10",
  "how-i-built-a-free-wispr-flow-alternative-as-a-student.md": "2026-01-17",
  "the-student-s-guide-to-hands-free-typing-no-subscriptions.md": "2026-01-25",
  "what-is-voice-activity-detection-vad-and-why-does-it-matter.md": "2026-02-02",
  "how-to-set-up-a-free-groq-api-key-for-voice-dictation.md": "2026-02-10",
  "how-to-run-ai-voice-dictation-completely-offline-on-windows.md": "2026-02-18",
  "best-free-dictation-software-for-students-in-2026.md": "2026-02-22",
  "best-open-source-voice-dictation-software-in-2026.md": "2026-02-26",
  "best-voice-dictation-app-for-windows-11-in-2026.md": "2026-03-02",
  "how-ai-voice-dictation-actually-works-the-full-pipeline.md": "2026-03-06",
  "how-i-improved-voice-dictation-accuracy-from-70-to-95.md": "2026-03-10",
  "how-to-choose-a-voice-dictation-app-without-wasting-money.md": "2026-03-14",
  "how-to-dictate-text-into-any-windows-application.md": "2026-03-18",
  "how-to-transcribe-audio-files-with-whisper-on-windows.md": "2026-03-22",
  "how-voice-snippets-save-me-30-minutes-a-day.md": "2026-03-26",
  "voice-dictation-vs-typing-i-tracked-my-speed-for-2-weeks.md": "2026-03-30",
  "why-privacy-matters-more-than-you-think-in-voice-dictation.md": "2026-04-03",
  "why-voice-dictation-will-replace-typing-for-developers.md": "2026-04-07",
  "how-round-robin-scheduling-saves-my-api-rates.md": "2026-04-11",
  "7-free-ai-tools-i-use-as-a-student-developer.md": "2026-04-15",
  "i-tried-voice-coding-with-cursor-using-rota-ai-here-is-what-happened.md": "2026-04-19",
  "how-to-customize-rota-ai-settings-for-your-workflow.md": "2026-04-23",
  "openai-whisper-dictation-apps-the-complete-list.md": "2026-04-27",
  "wispr-flow-pricing-in-2026-is-it-worth-15-month.md": "2026-05-01",
  "rota-ai-vs-superwhisper-which-one-should-you-actually-use.md": "2026-05-05",
  "rota-ai-vs-wispr-flow-an-honest-comparison-from-someone-who-built-the-alternative.md": "2026-05-09",
  "superwhisper-alternatives-that-are-free-and-open-source.md": "2026-05-11",
  "otter-ai-alternatives-that-are-free-and-actually-good.md": "2026-05-13",
  "wispr-flow-alternatives-that-are-actually-free-in-2026.md": "2026-05-15",
};

// Posts that should NOT be touched (original posts with intentional dates)
const SKIP_DATES = new Set([
  "why-i-built-rota-ai.md",        // 2026-05-25 (intentional)
  "wispr-flow-alternatives-free-2026.md",  // 2026-05-26 (intentional)
  "free-ai-tools-student-developer.md",    // 2026-05-28 (intentional)
  "rota-ai-free-voice-dictation-guide.md", // 2026-05-28 (intentional)
]);

let datesFixed = 0;
let dashesFixed = 0;
let emojisFixed = 0;

// Emoji removal regex - matches common emoji patterns
const EMOJI_REGEX = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{200D}\u{2934}\u{2935}\u{25AA}\u{25AB}\u{25FB}\u{25FC}\u{25FD}\u{25FE}\u{2B05}\u{2B06}\u{2B07}\u{2B1B}\u{2B1C}\u{2B50}\u{2B55}\u{3030}\u{303D}\u{3297}\u{3299}]/gu;

for (const file of files) {
  const filePath = path.join(BLOG_DIR, file);
  let content = fs.readFileSync(filePath, "utf-8");
  let changed = false;

  // ── Fix dates ──
  if (NEW_DATES[file]) {
    const newDate = NEW_DATES[file];
    const dateMatch = content.match(/^date:\s*(\S+)/m);
    if (dateMatch && dateMatch[1] !== newDate && !SKIP_DATES.has(file)) {
      content = content.replace(/^date:\s*\S+$/m, `date: ${newDate}`);
      console.log(`  📅 ${file}: ${dateMatch[1]} → ${newDate}`);
      datesFixed++;
      changed = true;
    }
  }

  // Extract frontmatter and body for separate processing
  const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!fmMatch) continue;

  let [, frontmatter, body] = fmMatch;
  let bodyChanged = false;

  // ── Fix em dashes in body content (but not in frontmatter) ──
  const dashCount = (body.match(/—/g) || []).length;
  if (dashCount > 0) {
    // Replace em dashes with regular hyphens in body text
    body = body.replace(/—/g, "-");
    console.log(`  ➖ ${file}: replaced ${dashCount} em dash(es)`);
    dashesFixed += dashCount;
    bodyChanged = true;
  }

  // ── Fix en dashes in body content ──
  const enDashCount = (body.match(/–/g) || []).length;
  if (enDashCount > 0) {
    body = body.replace(/–/g, "-");
    console.log(`  ➖ ${file}: replaced ${enDashCount} en dash(es)`);
    dashesFixed += enDashCount;
    bodyChanged = true;
  }

  // ── Remove emojis from body content ──
  const emojiCount = (body.match(EMOJI_REGEX) || []).length;
  if (emojiCount > 0) {
    body = body.replace(EMOJI_REGEX, "");
    console.log(`  😊 ${file}: removed ${emojiCount} emoji character(s)`);
    emojisFixed += emojiCount;
    bodyChanged = true;
  }

  if (changed || bodyChanged) {
    const newContent = `---\n${frontmatter}\n---\n\n${body}`;
    fs.writeFileSync(filePath, newContent, "utf-8");
  }
}

console.log(`\n✅ Done: ${datesFixed} dates fixed, ${dashesFixed} dashes replaced, ${emojisFixed} emojis removed.\n`);
