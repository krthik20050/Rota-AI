/**
 * Add "Rota AI" to blog post titles that don't already mention it.
 * This strengthens the brand association in Google's index.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const BLOG_DIR = path.join(ROOT, "website", "blog");

const files = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith(".md"));

let updated = 0;
let skipped = 0;

for (const file of files) {
  const filePath = path.join(BLOG_DIR, file);
  let content = fs.readFileSync(filePath, "utf-8");

  // Extract current title from frontmatter
  const titleMatch = content.match(/^title:\s*"(.+)"\s*$/m);
  if (!titleMatch) {
    console.log(`  ⚠️  ${file}: no title found`);
    continue;
  }

  const currentTitle = titleMatch[1];

  // Skip if already mentions Rota AI
  if (/rota\s*ai/i.test(currentTitle)) {
    console.log(`  ● ${file}: already mentions Rota AI — skipped`);
    skipped++;
    continue;
  }

  // Determine the best way to add "Rota AI"
  let newTitle;

  const titleLower = currentTitle.toLowerCase();

  // Comparison posts: embed "Rota AI vs X" or "X vs Rota AI" naturally
  if (titleLower.includes("vs") || titleLower.includes("alternative") || titleLower.includes("alternatives")) {
    if (titleLower.includes("wispr flow")) {
      // "Wispr Flow Alternatives..." → "Rota AI vs Wispr Flow: The Free Alternative"
      newTitle = currentTitle
        .replace(/Wispr Flow Alternatives/i, "Rota AI vs Wispr Flow")
        .replace(/That Are Actually Free/i, "The Free Alternative");
    } else if (titleLower.includes("superwhisper")) {
      // "SuperWhisper Alternatives..." → "SuperWhisper vs Rota AI: Free & Open Source Alternative"
      newTitle = currentTitle
        .replace(/SuperWhisper Alternatives/i, "SuperWhisper vs Rota AI")
        .replace(/That Are Free and Open Source/i, "Free & Open Source Alternative");
    } else if (titleLower.includes("otter")) {
      // "Otter.ai Alternatives..." → "Otter.ai vs Rota AI: Free & Private Alternative"
      newTitle = currentTitle
        .replace(/Otter\.?ai Alternatives/i, "Otter.ai vs Rota AI")
        .replace(/That Are Free and Actually Good/i, "Free & Private Alternative");
    } else if (titleLower.includes("whisper")) {
      // "OpenAI Whisper Dictation Apps..." → "Rota AI & OpenAI Whisper: Best Dictation Apps"
      if (titleLower.includes("openai")) {
        newTitle = `Rota AI & OpenAI Whisper: The Complete List of Dictation Apps`;
      } else {
        newTitle = `Rota AI: How to Transcribe Audio Files with Whisper on Windows`;
      }
    } else if (titleLower.includes("wispr")) {
      // "Is Wispr Flow Worth $15?" → "Rota AI vs Wispr Flow: Is It Worth $15/Month?"
      newTitle = currentTitle.replace(/^Is Wispr Flow/i, "Rota AI vs Wispr Flow");
    } else {
      newTitle = `${currentTitle} — Rota AI`;
    }
  }
  // Tool roundup posts: embed Rota AI naturally
  else if (titleLower.includes("free voice dictation apps") || titleLower.includes("best voice dictation") || titleLower.includes("best open source") || titleLower.includes("best free dictation")) {
    newTitle = currentTitle.replace(/(for|in|of|on)/i, (match) => {
      if (titleLower.includes("best voice dictation app for windows")) {
        return `Rota AI: Best Voice Dictation App ${match}`;
      }
      if (titleLower.includes("best open source voice dictation")) {
        return `Rota AI: Best Open Source Voice Dictation ${match}`;
      }
      if (titleLower.includes("best free dictation software")) {
        return `Rota AI: Best Free Dictation Software ${match}`;
      }
      if (titleLower.includes("free voice dictation apps")) {
        return `Rota AI: Top Free Voice Dictation Apps ${match}`;
      }
      return match;
    });
    if (newTitle === currentTitle) {
      newTitle = `${currentTitle} — Rota AI`;
    }
  }
  // "7 Free AI Tools" → "7 Free AI Tools I Use as a Developer (including Rota AI)"
  else if (titleLower.includes("7 free ai tools") || titleLower.includes("free ai tools")) {
    newTitle = currentTitle.replace(/I Use/i, "I Use (including Rota AI)");
  }
  // Voice dictation vs typing → add Rota AI
  else if (titleLower.includes("voice dictation vs typing")) {
    newTitle = `Rota AI: Voice Dictation vs Typing — I Tracked My Speed for 2 Weeks`;
  }
  // How-to guides about general voice dictation → add "with Rota AI"
  else if (titleLower.startsWith("how to")) {
    if (titleLower.includes("choose")) {
      newTitle = `Rota AI: How to Choose a Voice Dictation App (Without Wasting Money)`;
    } else if (titleLower.includes("dictate text")) {
      newTitle = `Rota AI: How to Dictate Text Into Any Windows Application`;
    } else if (titleLower.includes("run")) {
      newTitle = `Rota AI: How to Run AI Voice Dictation Completely Offline on Windows`;
    } else if (titleLower.includes("set up") || titleLower.includes("groq")) {
      newTitle = `Rota AI: How to Set Up a Free Groq API Key for Voice Dictation`;
    } else if (titleLower.includes("transcribe") || titleLower.includes("whisper")) {
      newTitle = `Rota AI: How to Transcribe Audio Files with Whisper on Windows`;
    } else if (titleLower.includes("snippet") || titleLower.includes("voice snippet")) {
      newTitle = `Rota AI: How Voice Snippets Save Me 30 Minutes a Day`;
    } else {
      newTitle = `Rota AI Guide: ${currentTitle}`;
    }
  }
  // Student/guides
  else if (titleLower.includes("student")) {
    newTitle = `Rota AI: The Student's Guide to Hands-Free Typing (No Subscriptions)`;
  }
  // Privacy posts
  else if (titleLower.includes("privacy")) {
    newTitle = `${currentTitle} — Rota AI`;
  }
  // What-is / explainer posts
  else if (titleLower.startsWith("what is") || titleLower.startsWith("what does")) {
    newTitle = currentTitle.replace(/^What/i, "What (and How Rota AI Uses It)");
  }
  // The future / why posts
  else if (titleLower.includes("future") || titleLower.includes("will replace")) {
    newTitle = `Rota AI: Why Voice Dictation Will Replace Typing for Developers`;
  }
  // Round robin / technical
  else if (titleLower.includes("round robin")) {
    newTitle = `Rota AI: How Round Robin Scheduling Saves My API Rates`;
  }
  // Default: append " | Rota AI"
  else {
    newTitle = `${currentTitle} | Rota AI`;
  }

  // Replace title in frontmatter
  const oldLine = `title: "${currentTitle}"`;
  const newLine = `title: "${newTitle}"`;

  if (!content.includes(oldLine)) {
    console.log(`  ⚠️  ${file}: could not find title line to replace`);
    continue;
  }

  content = content.replace(oldLine, newLine);
  fs.writeFileSync(filePath, content, "utf-8");
  console.log(`  ✅ ${file}: "${currentTitle}" → "${newTitle}"`);
  updated++;
}

console.log(`\nDone. ${updated} updated, ${skipped} already had Rota AI.\n`);
