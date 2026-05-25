from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from ai.ai_processor import AIProcessor
from audio.recorder import AudioRecorder
from data.config import ConfigManager
from data.history import HistoryManager
from plat import get_injector as _get_injector
from services.enhanced_insights import EnhancedInsightsService
from services.insights_service import InsightsService
from services.session_store import SessionStore


@dataclass
class AppServices:
    config: ConfigManager
    history: HistoryManager
    session_store: SessionStore
    insights_service: InsightsService
    enhanced_insights: EnhancedInsightsService
    recorder: AudioRecorder
    ai_processor: AIProcessor
    injector: object  # TextInjector (OS-appropriate)


def _inject_api_keys(config: ConfigManager) -> None:
    """Push API keys from config into env so all modules pick them up via os.environ."""
    for env_var, config_key in [
        ("GROQ_API_KEY", "groq_api_key"),
        ("GEMINI_API_KEY", "gemini_api_key"),
    ]:
        val = config.get(config_key, "")
        if val and not os.environ.get(env_var):
            os.environ[env_var] = val


def _get_appdata_dir() -> str:
    """Return the OS-appropriate app data directory."""
    if sys.platform == "win32":
        return os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/RotaAI
        return os.path.join(os.path.expanduser("~/Library/Application Support"), "RotaAI")
    # Linux: follow XDG Base Directory Specification
    xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(xdg_data, "rota-ai")


def build_app_services() -> AppServices:
    config = ConfigManager()
    _inject_api_keys(config)
    history = HistoryManager()
    appdata_dir = _get_appdata_dir()
    os.makedirs(appdata_dir, exist_ok=True)
    recorder = AudioRecorder()
    session_store = SessionStore(os.path.join(appdata_dir, "sessions.db"))
    insights_service = InsightsService()
    enhanced_insights = EnhancedInsightsService(session_store)
    ai_processor = AIProcessor(
        writing_mode=config.get("writing_mode", "clean"),
        ai_provider=config.get("ai_provider", "gemini"),
        ollama_model=config.get("ollama_model", "llama3.2:1b"),
        ollama_url=config.get("ollama_url", "http://localhost:11434"),
    )
    # Use the platform-appropriate injector (Linux: clipboard+xdotool/wtype, Windows: clipboard+keybd_event)
    InjectorClass = _get_injector()
    injector = InjectorClass()
    return AppServices(
        config=config,
        history=history,
        session_store=session_store,
        insights_service=insights_service,
        enhanced_insights=enhanced_insights,
        recorder=recorder,
        ai_processor=ai_processor,
        injector=injector,
    )
