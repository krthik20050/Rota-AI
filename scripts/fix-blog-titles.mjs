/**
 * Fix corrupted blog post titles and use a simple, reliable approach:
 * Just append " — Rota AI" to titles that don't mention the brand.
 * Except for comparison posts which get natural embedding.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const BLOG_DIR = path.join(ROOT, "website", "blog");

const files = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith(".md"));

// Manual mappings for posts that need specific treatment
const TITLE_MAP = {
  "5-free-voice-dictation-apps-for-windows-ranked.md": "5 Free Voice Dictation Apps for Windows (Ranked) — Rota AI",
  "best-free-dictation-software-for-students-in-2026.md": "Best Free Dictation Software for Students in 2026 — Rota AI",
  "best-open-source-voice-dictation-software-in-2026.md": "Best Open Source Voice Dictation Software in 2026 — Rota AI",
  "best-voice-dictation-app-for-windows-11-in-2026.md": "Best Voice Dictation App for Windows 11 in 2026 — Rota AI",
  "what-is-voice-activity-detection-vad-and-why-does-it-matter.md": "What Is Voice Activity Detection (VAD) and Why Does It Matter? — Rota AI",
  "otter-ai-alternatives-that-are-free-and-actually-good.md": "Otter.ai vs Rota AI: Free & Private Voice Dictation Alternative",
  "superwhisper-alternatives-that-are-free-and-open-source.md": "SuperWhisper vs Rota AI: Free & Open Source Voice Dictation",
  "how-i-built-a-free-wispr-flow-alternative-as-a-student.md": "How I Built Rota AI: A Free Wispr Flow Alternative as a Student",
  "wispr-flow-alternatives-free-2026.md": "Rota AI vs Wispr Flow: The Best Free Alternative (2026)",
  "wispr-flow-alternatives-that-are-actually-free-in-2026.md": "Rota AI vs Wispr Flow: The Free Alternative in 2026",
  "is-wispr-flow-worth-15-month-my-honest-take-after-using-it.md": "Rota AI vs Wispr Flow: Is It Worth $15/Month?",
  "openai-whisper-dictation-apps-the-complete-list.md": "Rota AI & OpenAI Whisper: The Complete Dictation Apps Guide",
  "voice-dictation-vs-typing-i-tracked-my-speed-for-2-weeks.md": "Rota AI: Voice Dictation vs Typing — I Tracked My Speed for 2 Weeks",
  "how-voice-snippets-save-me-30-minutes-a-day.md": "Rota AI: How Voice Snippets Save Me 30 Minutes a Day",
  "how-i-improved-voice-dictation-accuracy-from-70-to-95.md": "How I Improved Voice Dictation Accuracy from 70% to 95% — Rota AI",
  "how-ai-voice-dictation-actually-works-the-full-pipeline.md": "How AI Voice Dictation Actually Works (The Full Pipeline) — Rota AI",
  "why-privacy-matters-more-than-you-think-in-voice-dictation.md": "Why Privacy Matters More Than You Think in Voice Dictation — Rota AI",
  "wispr-flow-pricing-in-2026-is-it-worth-15-month.md": "Wispr Flow Pricing in 2026: Is It Worth $15/Month? — Rota AI",
  "7-free-ai-tools-i-use-as-a-student-developer.md": "7 Free AI Tools I Use as a Developer (including Rota AI)",
  "free-ai-tools-student-developer.md": "7 Free AI Tools I Use as a Developer (including Rota AI)",
};

// Posts that already mention Rota AI (skip)
const ALREADY_HAS_BRAND = [
  "how-to-customize-rota-ai-settings-for-your-workflow.md",
  "i-tried-voice-coding-with-cursor-using-rota-ai-here-is-what-happened.md",
  "rota-ai-free-voice-dictation-guide.md",
  "rota-ai-vs-superwhisper-which-one-should-you-actually-use.md",
  "rota-ai-vs-wispr-flow-an-honest-comparison-from-someone-who-built-the-alternative.md",
  "why-i-built-rota-ai.md",
];

// Posts that just need " — Rota AI" appended
const APPEND_SUFFIX = [
  "how-to-choose-a-voice-dictation-app-without-wasting-money.md",
  "how-to-dictate-text-into-any-windows-application.md",
  "how-to-run-ai-voice-dictation-completely-offline-on-windows.md",
  "how-to-set-up-a-free-groq-api-key-for-voice-dictation.md",
  "how-to-transcribe-audio-files-with-whisper-on-windows.md",
  "the-student-s-guide-to-hands-free-typing-no-subscriptions.md",
  "why-voice-dictation-will-replace-typing-for-developers.md",
  "how-round-robin-scheduling-saves-my-api-rates.md",
];

let updated = 0;
let skipped = 0;

for (const file of files) {
  const filePath = path.join(BLOG_DIR, file);

  let content = fs.readFileSync(filePath, "utf-8");
  const titleMatch = content.match(/^title:\s*"(.+)"\s*$/m);
  if (!titleMatch) {
    console.log(`  ⚠️  ${file}: no title found`);
    continue;
  }

  const currentTitle = titleMatch[1];

  // Skip if already has Rota AI
  if (ALREADY_HAS_BRAND.includes(file)) {
    console.log(`  ● ${file}: already has Rota AI — skipped`);
    skipped++;
    continue;
  }

  let newTitle;

  // Manual override
  if (TITLE_MAP[file]) {
    newTitle = TITLE_MAP[file];
  }
  // Append suffix
  else if (APPEND_SUFFIX.includes(file)) {
    newTitle = currentTitle.replace(/ \| Rota AI$/, ""); // strip any existing suffix
    if (!newTitle.includes("Rota AI")) {
      newTitle = newTitle + " — Rota AI";
    }
  }
  // Others: just ensure it has Rota AI somewhere
  else {
    newTitle = currentTitle.replace(/ \| Rota AI$/, "");
    if (!newTitle.includes("Rota AI")) {
      newTitle = newTitle + " — Rota AI";
    }
  }

  if (newTitle === currentTitle) {
    console.log(`  ● ${file}: no change needed — "${currentTitle}"`);
    skipped++;
    continue;
  }

  content = content.replace(`title: "${currentTitle}"`, `title: "${newTitle}"`);
  fs.writeFileSync(filePath, content, "utf-8");
  console.log(`  ✅ ${file}: "${currentTitle}"`);
  console.log(`     → "${newTitle}"`);
  updated++;
}

console.log(`\nDone. ${updated} fixed, ${skipped} skipped.\n`);
