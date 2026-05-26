"""
WisprFlow-grade AI text processor for Rota AI.

Architecture:
  Raw Whisper transcript
    → Spoken punctuation pre-processing
    → Dynamic context-aware LLM cleanup (Gemini primary, Groq fallback)
    → Auto-learning personal dictionary extraction
    → Final polished intent-based text

Key design decisions:
  - Gemini is the PRIMARY cleanup engine (generous rate limits, excellent formatting)
  - Groq is the FALLBACK (ultra-fast but rate-limited)
  - Prompts are dynamically constructed per-dictation with app context + tone
  - Personal dictionary auto-grows from every processed text
"""

import json
import os
import re
import time as _time
import urllib.error
import urllib.request

import structlog
from groq import Groq

from ai.personal_dictionary import PersonalDictionary
from ai.prompts import _AUTO_STRUCTURE_PROMPT, _COMMAND_PATTERNS, should_run_structure_pass
from ai.rate_limiter import (
    _INJECTION_PATTERNS,
    _MAX_PERSONAL_TERMS,
    _MAX_SYSTEM_PROMPT_LENGTH,
    _MAX_TRANSCRIPT_LENGTH,
    _gemini_rate_limiter,
    _groq_rate_limiter,
)
from ai.text_utils import (
    _build_dynamic_prompt,
    _is_too_different,
    _preprocess_spoken_punctuation,
    _rule_based_clean,
    _sanitize_llm_output,
)

logger = structlog.get_logger(__name__)

WRITING_MODES = {"raw", "clean", "professional", "casual", "bullets", "email", "summarize"}


# ---------------------------------------------------------------------------
# Main AI Processor
# ---------------------------------------------------------------------------


class AIProcessor:
    """
    WisprFlow-grade semantic voice dictation processor with context awareness.

    Architecture:
      - Primary: Gemini 2.0 Flash Lite (generous rate limits, excellent at formatting)
      - Fallback 1: Groq Llama 3.3 70B versatile (ultra-fast)
      - Fallback 2: Groq Llama 3.1 8B instant (fast, lower quality)
      - Fallback 3: Rule-based regex cleanup (always available, no API)
    """

    def __init__(
        self,
        writing_mode: str = "clean",
        ai_provider: str = "gemini",
        ollama_model: str = "llama3.2:1b",
        ollama_url: str = "http://localhost:11434",
        **kwargs,
    ):
        if writing_mode not in WRITING_MODES:
            logger.warning("unknown_writing_mode", mode=writing_mode, fallback="clean")
            writing_mode = "clean"

        self.writing_mode = writing_mode
        self.ai_provider = ai_provider
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url.rstrip("/")
        self.last_error = False

        # Load API keys from environment
        self._groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self._gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self._groq_client = None  # Lazy-initialized, cached

        # Round-robin state: rotate starting model so load spreads across all slots
        self._rr_idx: int = 0
        self._cooldowns: dict[str, float] = {}  # model_id → monotonic ts when cooldown expires

        # Auto-learning personal dictionary
        self.personal_dict = PersonalDictionary()

    def update_api_keys(self, groq_key: str = "", gemini_key: str = "") -> None:
        """Update API keys at runtime (e.g. after onboarding saves new keys)."""
        if groq_key:
            self._groq_api_key = groq_key
            self._groq_client = None  # Invalidate cached client
        if gemini_key:
            self._gemini_api_key = gemini_key

    @property
    def is_configured(self) -> bool:
        return True

    @property
    def active_backend(self) -> str:
        provider = self.ai_provider
        if provider == "gemini" and self._gemini_api_key:
            return "gemini"
        elif provider == "groq" and self._groq_api_key:
            return "groq"
        elif provider == "ollama":
            return "ollama"
        # Smart auto-selection: try Gemini first, then Groq
        if provider == "auto":
            if self._gemini_api_key:
                return "gemini"
            if self._groq_api_key:
                return "groq"
        return "rule-based"

    @property
    def model(self) -> str:
        backend = self.active_backend
        if backend == "gemini":
            return "gemini-2.0-flash"
        elif backend == "groq":
            return "llama-3.3-70b-versatile"
        elif backend == "ollama":
            return self.ollama_model
        return "rule-based"

    def should_generate_prompt(self, text):
        return False, None

    def detect_command(self, text: str) -> tuple[str, str]:
        """
        Check if the transcribed text begins with a voice command phrase.
        Returns (command_mode, content_text) or ("", original_text).
        """
        sample = text[:120]
        for pattern, mode in _COMMAND_PATTERNS:
            m = pattern.search(sample)
            if m:
                remaining = text[: m.start()] + text[m.end() :]
                remaining = re.sub(r"^[\s,.\-–—]+", "", remaining).strip()
                if remaining:
                    logger.debug("command_detected", mode=mode, content_preview=remaining[:40])
                    return mode, remaining
        return "", text

    def process_text(
        self,
        text: str,
        correlation_id=None,
        writing_mode: str = None,
        app_context=None,
        field_text: str = "",
    ) -> str:
        """
        Clean and transform transcribed text using the configured AI backend.

        Args:
            text: raw transcription from Whisper
            correlation_id: for log tracing
            writing_mode: override instance writing_mode for this call
            app_context: AppContext from field_detector — informs formatting
            field_text: existing text in the input field for continuity
        """
        text = (text or "").strip()
        if not text:
            return ""

        # SECURITY: Reject overly long inputs
        if len(text) > _MAX_TRANSCRIPT_LENGTH:
            logger.warning("transcript_too_long", length=len(text), cid=correlation_id)
            return _rule_based_clean(text)

        # SECURITY: Check for prompt injection patterns
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning(
                    "prompt_injection_detected", cid=correlation_id, pattern=pattern.pattern[:40]
                )
                return _rule_based_clean(text)

        # SECURITY: Strip triple-quote sequences that could break prompt structure
        text = text.replace('"""', '" " "').replace("'''", "' ' '")

        mode = writing_mode if writing_mode and writing_mode in WRITING_MODES else self.writing_mode

        if mode == "raw":
            return text

        # Pre-process spoken punctuation before LLM call
        text = _preprocess_spoken_punctuation(text)

        backend = self.active_backend
        if backend == "rule-based":
            return _rule_based_clean(text)

        # Build context-aware dynamic prompt
        personal_terms = self.personal_dict.get_terms()[:_MAX_PERSONAL_TERMS]  # SECURITY: cap terms
        system_prompt = _build_dynamic_prompt(
            writing_mode=mode,
            app_context=app_context,
            field_text=field_text,
            personal_terms=personal_terms if personal_terms else None,
        )

        # SECURITY: Cap system prompt length
        if len(system_prompt) > _MAX_SYSTEM_PROMPT_LENGTH:
            system_prompt = system_prompt[:_MAX_SYSTEM_PROMPT_LENGTH]

        # Try primary backend, then cascade through fallbacks
        result = None
        wrapped_text = f'RAW TRANSCRIPT TO CLEAN:\n"""\n{text}\n"""'

        if backend == "ollama":
            result = self._ollama_process(wrapped_text, system_prompt, mode, correlation_id)
        else:
            # Round-robin across all available cloud models (Gemini + Groq).
            # Each 429 marks a 60s cooldown on that model so the next call skips it.
            result = self._cloud_cascade(wrapped_text, system_prompt, mode, correlation_id)
            if result is None:
                # All cloud models exhausted — try local Ollama before giving up
                logger.info("cloud_cascade_exhausted_trying_ollama", cid=correlation_id)
                result = self._ollama_process(wrapped_text, system_prompt, mode, correlation_id)

        if result is not None:
            # Safety net: strip any code blocks / markdown the LLM may have generated
            result = _sanitize_llm_output(result, text)
            if mode == "clean" and _is_too_different(result, text):
                logger.warning("ai_cleanup_too_different", cid=correlation_id)
                return _rule_based_clean(text)

            # AI Auto-Edit: second structural pass (Wispr Flow-style two-pass)
            # Only run for clean mode on long-enough text with list/structure signals
            if mode == "clean" and should_run_structure_pass(result):
                structured = self._run_structure_pass(result, correlation_id)
                if structured:
                    result = structured

            # Auto-learn from the polished output
            self.personal_dict.learn_from_text(result)
            return result

        # Final fallback: rule-based clean
        return _rule_based_clean(text)

    # ------------------------------------------------------------------
    # AI Auto-Edit: second structural pass (Wispr Flow two-pass architecture)
    # ------------------------------------------------------------------

    def _run_structure_pass(self, text: str, correlation_id) -> str | None:
        """
        Run the structural second pass on already-cleaned text.
        Only converts unstructured content to lists/paragraphs — never rephrases.
        Uses the same round-robin cascade so any available model can handle it.
        """
        wrapped = f'TEXT TO STRUCTURE:\n"""\n{text}\n"""'
        result = self._cloud_cascade(wrapped, _AUTO_STRUCTURE_PROMPT, "clean", correlation_id)
        if result:
            result = _sanitize_llm_output(result, text)
            if not _is_too_different(result, text):
                logger.debug("structure_pass_ok", cid=correlation_id)
                return result
            logger.warning("structure_pass_too_different", cid=correlation_id)
        return None

    # ------------------------------------------------------------------
    # Gemini REST integration (PRIMARY — generous rate limits)
    # ------------------------------------------------------------------

    def _gemini_call(
        self,
        model_name: str,
        text: str,
        system_prompt: str,
        correlation_id,
        _acquire_rl: bool = True,
    ) -> str | None:
        """Call one specific Gemini model. Marks 60s cooldown on 429.

        Pass _acquire_rl=False when the caller (_cloud_cascade) has already
        acquired a rate-limit token for the entire Gemini provider group so we
        don't burn multiple tokens per cascade for the same provider.
        """
        if not self._gemini_api_key:
            return None
        if _acquire_rl:
            allowed, retry_after = _gemini_rate_limiter.acquire()
            if not allowed:
                logger.warning(
                    "gemini_rate_limited", retry_after_s=round(retry_after, 1), cid=correlation_id
                )
                return None
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        )
        payload = json.dumps(
            {
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json", "x-goog-api-key": self._gemini_api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                candidates = body.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        cleaned = parts[0].get("text", "").strip()
                        if cleaned:
                            logger.debug("gemini_ok", model=model_name, cid=correlation_id)
                            return cleaned
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                self._mark_cooldown(model_name)
                logger.warning("gemini_429_cooldown", model=model_name, cid=correlation_id)
            else:
                logger.error(
                    "gemini_http_error", code=exc.code, model=model_name, cid=correlation_id
                )
        except Exception as exc:
            logger.error("gemini_failed", model=model_name, error=str(exc), cid=correlation_id)
        return None

    # ------------------------------------------------------------------
    # Groq integration (FALLBACK — ultra-fast but rate-limited)
    # ------------------------------------------------------------------

    def _get_groq_client(self) -> "Groq":
        """Return a cached Groq client, re-creating if the API key changed."""
        if self._groq_client is None:
            self._groq_client = Groq(api_key=self._groq_api_key)
        return self._groq_client

    # ------------------------------------------------------------------
    # Round-robin helpers
    # ------------------------------------------------------------------

    def _in_cooldown(self, model_id: str) -> bool:
        return _time.monotonic() < self._cooldowns.get(model_id, 0.0)

    def _mark_cooldown(self, model_id: str, seconds: float = 60.0) -> None:
        self._cooldowns[model_id] = _time.monotonic() + seconds
        logger.info("model_cooldown_set", model=model_id, cooldown_seconds=int(seconds))

    def _cloud_cascade(
        self, wrapped_text: str, system_prompt: str, mode: str, correlation_id
    ) -> str | None:
        """
        Try all available cloud models in round-robin order.
        Skips models in 429 cooldown. Advances the rotation index after each success
        so the next call starts at the next slot — spreading load evenly.

        Ordering: respects ai_provider preference (groq-first or gemini-first),
        then round-robins within that order so no single model gets all the load.
        """
        # Four Gemini models × free-tier quota = ~6 000 req/day combined capacity.
        # Order: balanced first, fastest second, proven third, most-capable last.
        gemini_slots = (
            [
                ("gemini", "gemini-2.0-flash"),
                ("gemini", "gemini-1.5-flash"),
                ("gemini", "gemini-2.0-flash-lite"),
                ("gemini", "gemini-2.5-flash"),
            ]
            if self._gemini_api_key
            else []
        )
        groq_slots = (
            [("groq", "llama-3.3-70b-versatile"), ("groq", "llama-3.1-8b-instant")]
            if self._groq_api_key
            else []
        )

        # Honor preferred provider: put it first so it anchors the rotation
        if self.ai_provider == "groq":
            slots = groq_slots + gemini_slots
        else:
            slots = gemini_slots + groq_slots

        if not slots:
            return None

        n = len(slots)
        start = self._rr_idx % n
        ordered = slots[start:] + slots[:start]

        # Acquire one rate-limit token per provider for the entire cascade so
        # trying multiple models of the same provider doesn't burn N tokens.
        gemini_rl_ok: bool | None = None  # None = not yet checked
        groq_rl_ok: bool | None = None

        for provider, model_id in ordered:
            if self._in_cooldown(model_id):
                logger.debug("rr_skip_cooldown", model=model_id, cid=correlation_id)
                continue

            result = None
            if provider == "gemini":
                if gemini_rl_ok is None:
                    allowed, retry_after = _gemini_rate_limiter.acquire()
                    gemini_rl_ok = allowed
                    if not allowed:
                        logger.warning(
                            "gemini_rate_limited_cascade",
                            retry_after_s=round(retry_after, 1),
                            cid=correlation_id,
                        )
                if gemini_rl_ok:
                    result = self._gemini_call(
                        model_id, wrapped_text, system_prompt, correlation_id, _acquire_rl=False
                    )
            elif provider == "groq":
                if groq_rl_ok is None:
                    allowed, retry_after = _groq_rate_limiter.acquire()
                    groq_rl_ok = allowed
                    if not allowed:
                        logger.warning(
                            "groq_rate_limited_cascade",
                            retry_after_s=round(retry_after, 1),
                            cid=correlation_id,
                        )
                if groq_rl_ok:
                    result = self._groq_call(
                        model_id, wrapped_text, system_prompt, correlation_id, _acquire_rl=False
                    )

            if result is not None:
                self._rr_idx = (slots.index((provider, model_id)) + 1) % n
                return result

        logger.warning("cloud_cascade_all_unavailable", cid=correlation_id)
        return None

    def _groq_call(
        self,
        model_name: str,
        text: str,
        system_prompt: str,
        correlation_id,
        _acquire_rl: bool = True,
    ) -> str | None:
        """Call one specific Groq model. Marks 60s cooldown on rate-limit errors."""
        if not self._groq_api_key:
            return None
        if _acquire_rl:
            allowed, retry_after = _groq_rate_limiter.acquire()
            if not allowed:
                logger.warning(
                    "groq_rate_limited", retry_after_s=round(retry_after, 1), cid=correlation_id
                )
                return None
        try:
            client = self._get_groq_client()
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
                max_tokens=2048,
                timeout=6,
            )
            cleaned = response.choices[0].message.content.strip()
            if cleaned:
                logger.debug("groq_ok", model=model_name, cid=correlation_id)
                return cleaned
            return None
        except Exception as exc:
            err_str = str(exc).lower()
            if "429" in err_str or "rate limit" in err_str or "ratelimit" in err_str:
                self._mark_cooldown(model_name)
                logger.warning("groq_429_cooldown", model=model_name, cid=correlation_id)
            else:
                logger.error(
                    "groq_failed",
                    model=model_name,
                    error=f"{type(exc).__name__}: {str(exc)[:120]}",
                    cid=correlation_id,
                )
            return None

    # ------------------------------------------------------------------
    # Ollama integration (local LLM)
    # ------------------------------------------------------------------

    def _ollama_process(
        self, text: str, system_prompt: str, mode: str, correlation_id
    ) -> str | None:
        payload = json.dumps(
            {
                "model": self.ollama_model,
                "system": system_prompt,
                "prompt": text,
                "stream": False,
            }
        ).encode()

        url = f"{self.ollama_url}/api/generate"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode())
                cleaned = (body.get("response") or "").strip()
                if cleaned:
                    self.last_error = False
                    logger.debug(
                        "ollama_ok",
                        mode=mode,
                        model=self.ollama_model,
                        cid=correlation_id,
                    )
                    return cleaned
                return None
        except Exception as exc:
            self.last_error = True
            logger.warning("ollama_unavailable", error=str(exc), cid=correlation_id)
            return None
