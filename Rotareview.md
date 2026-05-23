# Rota AI — Prompts v2 Deep Review & Wispr Flow Gap Analysis

You are acting as a senior prompt engineer, product auditor, and AI systems reviewer.
Your job is to do a complete, research-backed audit of `prompts.py` against Wispr Flow's
capabilities. Be brutally honest. Do not skip steps.

---

## STEP 1 — Read the source file first

Read `prompts.py` in full. Understand every export:
- `_BASE_SYSTEM_PROMPT`
- `_CONTEXT_RULES` (7 keys)
- `_MODE_PROMPTS` (6 keys)
- `_COMMAND_PATTERNS`
- `_AUTO_STRUCTURE_PROMPT`
- `_REGISTER_DETECT_BLOCK`
- `build_final_system_prompt()`
- `should_run_structure_pass()`
- `extract_command_snippet()`

---

## STEP 2 — Research Wispr Flow deeply (web search required)

Search the web for ALL of the following. Read actual pages, not just snippets.

Search queries to run (run each separately for thorough coverage):
1. "Wispr Flow AI auto edit feature how it works"
2. "Wispr Flow voice dictation text formatting intelligence"
3. "Wispr Flow app review 2024 2025 features"
4. "Wispr Flow vs alternatives text cleanup quality"
5. "Wispr Flow system prompt leaked OR shared OR reverse engineered"
6. "how does Wispr Flow know when to use bullet points"
7. "Wispr Flow context detection how it works"
8. "voice dictation post processing LLM prompt engineering best practices"
9. "Wispr Flow AI pipeline architecture"
10. "Wispr Flow review accuracy formatting natural language"

From your research, document:
- Exactly what Wispr Flow's "AI Auto-Edit" feature does step by step
- How it detects context (email vs chat vs code editor)
- How it decides structure (bullets vs prose vs numbered)
- What makes its output feel non-AI — why it doesn't feel robotic
- Any known limitations or failure modes users complain about
- Any technical details about their processing pipeline

---

## STEP 3 — Run feature verification tests

For each feature below, write a test input, call the LLM using the prompt from
`prompts.py`, get a real output, and PASS/FAIL based on criteria.

Use `build_final_system_prompt(context, mode)` to assemble prompts.
Use the Groq or OpenAI API (whichever is configured in this project) for actual calls.
If no API is configured, simulate the call by evaluating the prompt quality manually
against the test input — document exactly what the output SHOULD be.

### TEST SUITE A — Auto Bullet / Numbered List Detection

**Test A1 — Sequential steps should become numbered list**
Input: `"um so uh to deploy the app you first need to run npm install then you
run npm run build and then you do npm start and that's it"`
Expected: Numbered list with 3 clean steps. No "um", "uh", "so".
PASS criteria: output has "1." "2." "3." format, no fillers.

**Test A2 — Parallel items should become bullet list**
Input: `"so the features we're adding are like real time sync and uh offline mode
and also push notifications and I think dark mode too"`
Expected: Bullet list with • character, 4 items.
PASS criteria: uses • not numbers (unordered), no fillers.

**Test A3 — Short text protection — should NOT become bullets**
Input: `"hey can you check the PR I sent you"`
Expected: Single clean sentence. "Hey, can you check the PR I sent you?"
FAIL criteria: any bullet points or paragraph breaks in this output.

**Test A4 — Mixed format — prose intro + numbered steps**
Input: `"so basically the onboarding flow has a problem and here's how to fix it
first we remove the email confirmation step second we add a progress bar and third
we pre-fill the user's name from their Google account"`
Expected: One prose sentence, then a numbered list of 3 fixes.
PASS criteria: prose + numbered list, clean language.

---

### TEST SUITE B — Smart Paragraph Breaks

**Test B1 — Single topic = single paragraph**
Input: `"so the API is returning a 404 error and I've checked the endpoint and it
looks correct but the base URL might be wrong so I need to double check the
environment variables and make sure production is pointing to the right server"`
Expected: Single paragraph, no breaks, clean and connected.
FAIL criteria: paragraph breaks in the middle of this connected thought.

**Test B2 — Topic shift = paragraph break**
Input: `"the login page is done and working great. separately I need to talk about
the payment integration because we're using Stripe and there's a webhook issue
that's blocking the whole checkout flow"`
Expected: Two paragraphs. One for login, one for Stripe/payment issue.
PASS criteria: blank line between the two topics.

**Test B3 — No paragraph-per-sentence anti-pattern**
Input: `"I woke up and had coffee. Then I checked my email. There were three
important messages. I replied to all of them. Then I started working on the feature.
It took about two hours. Then I pushed the code."`
Expected: One or two paragraphs MAX. NOT seven single-sentence paragraphs.
FAIL criteria: more than 2 paragraph breaks in this output.

---

### TEST SUITE C — Auto Register Detection

**Test C1 — Formal vocabulary → professional output**
Input: `"I wanted to circle back regarding the Q3 deliverables and ensure alignment
on the timeline with all key stakeholders before we proceed to the next phase"`
Expected: Formal prose, no contractions, no casual language.
PASS criteria: output reads like a business email body.

**Test C2 — Casual vocabulary → relaxed output**
Input: `"yo can you tell mike the build is gonna be done by friday and we're
probably gonna push it saturday morning if everything looks good"`
Expected: Casual message, contractions preserved, short and punchy.
FAIL criteria: "I wanted to inform you that the build will be completed..."
style formalization of casual speech.

**Test C3 — Technical vocabulary → technical register**
Input: `"we need to update the useEffect hook to depend on the userId prop and
also fix the async await issue in the fetchUserData function"`
Expected: Preserves "useEffect", "userId", "async/await", "fetchUserData" exactly.
FAIL criteria: any simplification of these technical terms.

---

### TEST SUITE D — AI Auto-Edit Behavior (No-AI-Feel Test)

This is the most important test suite. The output must not feel AI-generated.

**Test D1 — No AI vocabulary in output**
Run the following raw transcript through `build_final_system_prompt("other", "clean")`:
Input: `"so uh the app needs to be faster and uh it should also be easier to use
you know and we should probably think about the mobile experience too"`
Check output for these banned words: "Additionally", "Furthermore", "It is worth
noting", "It should be noted", "In conclusion", "Leveraging", "Utilize",
"Streamline", "Enhance", "Ensure seamless", "Holistic", "Robust", "Paradigm",
"Cutting-edge", "Revolutionary", "Delve", "Showcasing", "Fostering", "Pivotal",
"Testament to", "Tapestry", "Vibrant", "Underscores", "Serves as a", "Stands as".
FAIL criteria: ANY of these words appearing in the output.

**Test D2 — No sycophantic openers**
Check that output never starts with: "Certainly!", "Of course!", "Sure!", "Great!",
"Absolutely!", "Here is the cleaned text:", "Here's what you said:", or any preamble.
FAIL criteria: output starts with anything other than the actual cleaned content.

**Test D3 — No unfinished thought completion**
Input: `"I was thinking we could maybe do"`
Expected: "I was thinking we could maybe do" (or the closest clean version)
The model must NOT complete this thought with its own ideas.
FAIL criteria: any content added after what the speaker said.

**Test D4 — No content invention**
Input: `"email john about the meeting"`
Expected: "Email John about the meeting."
FAIL criteria: output invents "Hi John, I wanted to reach out about..." style content.

---

### TEST SUITE E — Self-Correction Resolution

**Test E1 — Immediate correction resolved**
Input: `"the server costs two hundred dollars a month. no wait, three hundred."`
Expected: "The server costs $300 a month."
PASS criteria: only $300, not $200.

**Test E2 — Topic transition NOT treated as correction**
Input: `"so the backend is done. okay moving on, we still need to finish the
frontend and the onboarding flow is also incomplete"`
Expected: Both "backend is done" AND "frontend/onboarding incomplete" preserved.
FAIL criteria: "backend is done" gets dropped because speaker moved on.

**Test E3 — Multi-topic ramble — all preserved**
Input: `"ugh I'm so stressed today and I've been drinking too much coffee anyway
that's not important the point is we need to push the release by Thursday and
also we need to update the documentation before we do that"`
Expected: Something like: "We need to push the release by Thursday. We also need
to update the documentation before doing that."
Note: The stress/coffee intro may be dropped (off-topic) but the two action items
MUST be preserved.
PASS criteria: Thursday deadline AND documentation update both in output.

---

### TEST SUITE F — Number / Date / Currency Formatting

**Test F1 — Spoken numbers to digits**
Input: `"the latency is two hundred and fifty milliseconds and we have about
forty five percent of users on mobile and it costs us three thousand rupees a month"`
Expected: "250ms", "45%", "₹3,000"
PASS criteria: all three formatted as digits.

**Test F2 — Dates**
Input: `"let's set the deadline for march fifteen twenty twenty five"`
Expected: "March 15, 2025"
PASS criteria: proper capitalization and digit format.

---

## STEP 4 — Run the `should_run_structure_pass` function tests

Test the Python function directly. Do NOT call the LLM for these — just run Python.

```python
import sys
sys.path.insert(0, '.')
from prompts import should_run_structure_pass, extract_command_snippet, _COMMAND_PATTERNS

# Test should_run_structure_pass
assert should_run_structure_pass("Hey can you check the PR") == False, \
    "Short text should return False"

assert should_run_structure_pass(
    "We need to do this first, second, and third. " * 10
) == True, "Long text with list signals should return True"

assert should_run_structure_pass("• Item one\n• Item two\n• Item three") == False, \
    "Already structured text should return False"

assert should_run_structure_pass(
    "The team is growing. We also need to hire. Another thing is the budget."
) == True, "List signals present, should return True"

# Test extract_command_snippet — leading fillers stripped
result = extract_command_snippet("um, uh, so like... make this professional please")
assert "make this professional" in result, f"Filler not stripped: got '{result}'"

result2 = extract_command_snippet("okay so basically um summarize this for me")
assert "summarize" in result2, f"Command not detected after filler strip: '{result2}'"

# Test _COMMAND_PATTERNS against filler-prefixed inputs
def detect_mode(transcript):
    snippet = extract_command_snippet(transcript)
    for pattern, mode in _COMMAND_PATTERNS:
        if pattern.search(snippet):
            return mode
    return "clean"

assert detect_mode("um so like make this professional") == "professional"
assert detect_mode("uh summarize this for me") == "summarize"
assert detect_mode("basically convert this to bullets") == "bullets"
assert detect_mode("hmm make it casual") == "casual"
assert detect_mode("mail this to the team") == "email"
assert detect_mode("just clean this up") == "clean"  # No command match

print("ALL PYTHON UNIT TESTS PASSED")
```

Run this code. Report which tests pass and which fail. Fix any failures directly
in `prompts.py` without breaking existing exports.

---

## STEP 5 — Wispr Flow vs Rota AI v2 Capability Matrix

After completing all research and tests, produce a scored matrix:

| Capability | Wispr Flow | Rota AI v2 | Gap | Fix Required? |
|---|---|---|---|---|
| Filler/disfluency removal | /10 | /10 | | |
| Stutter resolution | /10 | /10 | | |
| Self-correction resolution | /10 | /10 | | |
| False start handling | /10 | /10 | | |
| Auto punctuation from intonation | /10 | /10 | | |
| Spoken punctuation commands | /10 | /10 | | |
| Proper noun capitalization | /10 | /10 | | |
| Tech name exact casing | /10 | /10 | | |
| Number/date/currency formatting | /10 | /10 | | |
| Paragraph intelligence | /10 | /10 | | |
| Auto numbered list detection | /10 | /10 | | |
| Auto bullet list detection | /10 | /10 | | |
| Short text protection | /10 | /10 | | |
| Context auto-detection (email/chat/code) | /10 | /10 | | |
| Register auto-detection (formal/casual/technical) | /10 | /10 | | |
| AI Auto-Edit / second structural pass | /10 | /10 | | |
| No AI-sounding vocabulary in output | /10 | /10 | | |
| No content hallucination | /10 | /10 | | |
| Anti-injection guardrails | /10 | /10 | | |
| Mixed format (prose + list) | /10 | /10 | | |
| **TOTAL** | **/200** | **/200** | | |

Score honestly based on what the prompts instruct vs what Wispr Flow actually does.
Do not inflate Rota AI scores. The goal is to find gaps, not to feel good.

---

## STEP 6 — Wispr Flow AI Auto-Edit: How it actually works

Based on your web research, write a detailed technical explanation of:

1. What triggers the AI Auto-Edit pass in Wispr Flow (length? content type?)
2. What decisions it makes (format, structure, paragraph, bullets)
3. How it avoids making output sound AI-generated
4. What model(s) it uses (if known)
5. Approximate latency it adds
6. What it does differently from a single-pass cleanup

Then compare to what `_AUTO_STRUCTURE_PROMPT` in Rota AI's `prompts.py` currently does.
Identify any gaps in how the second pass is implemented.

---

## STEP 7 — No-AI-Feel Audit

This is a pass/fail audit of the current prompts against producing human-sounding output.

Check `_BASE_SYSTEM_PROMPT`, `_AUTO_STRUCTURE_PROMPT`, and all `_MODE_PROMPTS` for:

**Banned vocabulary in the PROMPTS THEMSELVES** (if the prompt uses AI vocabulary,
the model will mirror it in outputs):
- "Additionally", "Furthermore", "Moreover"
- "It is worth noting", "It should be noted"
- "Ensure seamless", "Streamline", "Leverage", "Utilize"
- "Holistic", "Robust", "Paradigm", "Cutting-edge"
- "Delve", "Showcasing", "Fostering", "Pivotal", "Tapestry"
- Em-dash overuse in the prompt text itself
- Rule-of-three forcing in examples

Check the prompts for these patterns and flag every instance.

Then verify that the prompts contain explicit instructions to the model to:
- NOT use any of the above vocabulary
- Prefer plain, direct language
- Match the speaker's natural vocabulary level
- Produce output a real human would type

If any of these instructions are missing or weak, rewrite those sections.

---

## STEP 8 — Final fixes to prompts.py

Based on everything found in steps 1–7:

1. List every issue found (numbered)
2. For each issue, make the targeted fix directly in `prompts.py`
3. Do NOT refactor or rename any existing exports
4. Only add content — never remove unless something is actively harmful
5. After each fix, note: what changed and why

---

## STEP 9 — Final report

Produce a clean summary:

```
ROTA AI PROMPTS v2 — AUDIT REPORT
===================================

PYTHON UNIT TESTS: X/Y passed
LLM FEATURE TESTS: X/Y passed (or X/Y evaluated if no API configured)

WISPR FLOW GAP SCORE: Rota AI v2 [X/200] vs Wispr Flow [estimated Y/200]
REMAINING GAP: [Z points]

TOP 3 GAPS TO CLOSE:
1. [gap] — [fix applied / still open]
2. [gap] — [fix applied / still open]
3. [gap] — [fix applied / still open]

AI-FEEL AUDIT: [PASS / FAIL — N issues found, M fixed]

WISPR FLOW AI AUTO-EDIT — KEY INSIGHT:
[2-3 sentences on how it works and how close Rota AI v2 is]

VERDICT:
[Honest 2-3 sentence assessment of where Rota AI v2 stands vs Wispr Flow]
```

---

## Execution order

Run these steps in sequence. Do not skip any step.
Steps 1 and 4 can run without API access.
Steps 3 and 6 require web search and/or LLM calls — do those properly.
Step 8 edits the actual file — do it carefully and verify exports are intact after.

The prompts.py file is at: `./prompts.py`