import threading
import time
from types import SimpleNamespace

from app import controller
from app.controller import RecordingState, RotaApp
from audio.recording_session import RecordingSession


class FakeTimer:
    def __init__(self):
        self.started_ms = None
        self.stopped = False

    def stop(self):
        self.stopped = True

    def start(self, ms):
        self.started_ms = ms


class FakeThread:
    def isRunning(self):
        return False


class FakeRunningThread:
    def isRunning(self):
        return True


class FakeMainWindow:
    def __init__(self):
        self.raw = None
        self.cleaned = None

    def update_state(self, *_args):
        pass

    def update_text_results(self, raw, cleaned):
        self.raw = raw
        self.cleaned = cleaned

    def update_timings(self, *_args):
        pass

    def update_metrics(self, *_args):
        pass

    def update_insight(self, *_args):
        pass

    def set_error_details(self, *_args):
        pass

    def refresh_history(self, *_args, **_kwargs):
        pass


def test_completed_processing_is_not_dropped_if_thread_cleanup_runs_first(monkeypatch):
    monkeypatch.setattr(controller.QTimer, "singleShot", lambda *_args, **_kwargs: None)

    app = RotaApp.__new__(RotaApp)
    session = RecordingSession(id="session-1")
    session.start_time = time.time() - 2.0
    app.state = RecordingState.PROCESSING
    app._state_lock = threading.RLock()
    app._processing_session_id = session.id
    app._processor_thread = FakeThread()
    app._retired_processor_threads = []
    app._processing_timeout_timer = FakeTimer()
    app._sessions = {session.id: session}
    app._last_session_id = session.id
    app._last_recording_seconds = 2.0
    app._latest_raw_text = ""
    app._latest_cleaned_text = ""
    app._latest_timings = {}
    app._active_session = None
    app.transcriber = SimpleNamespace(consume_backend_event=lambda: ("", ""))
    app.history = SimpleNamespace(entries=[], add_entry=lambda raw, cleaned, is_prompt: app.history.entries.append((raw, cleaned, is_prompt)))
    app.session_store = SimpleNamespace(
        records=[],
        add_session=lambda record: app.session_store.records.append(record),
        get_dashboard_metrics=lambda: {"today": {}, "lifetime": {}, "latest": None},
    )
    app.insights_service = SimpleNamespace(
        build_insight=lambda _text: SimpleNamespace(
            summary="Clear dictation",
            suggestion="",
            clarity_score=90,
            conciseness_score=88,
        )
    )
    app.main_window = FakeMainWindow()
    app.injector = SimpleNamespace(inject=lambda *_args, **_kwargs: (True, "ok"))
    app.snippets = SimpleNamespace(expand=lambda _text: None)
    app.auto_improvement = SimpleNamespace(track_injection=lambda *_args, **_kwargs: None)
    app.overlay = SimpleNamespace(show_success=lambda *_args: None, set_state=lambda *_args: None)
    app.show_toast = lambda *_args: None
    app._maybe_notify_backend_fallback = lambda: None
    app._refresh_debug_window = lambda: None
    app._update_metrics = lambda: None

    RotaApp._cleanup_processor_thread(app, session.id)
    assert app._processing_session_id == session.id

    RotaApp.on_processing_finished(
        app,
        "um raw transcript",
        "Raw transcript.",
        False,
        session.id,
        0.2,
        0.01,
        False,
        "groq",
    )

    assert app.state == RecordingState.SUCCESS
    assert app._latest_raw_text == "um raw transcript"
    assert app._latest_cleaned_text == "Raw transcript."
    assert app.history.entries == [("um raw transcript", "Raw transcript.", False)]
    assert app.session_store.records[0].transcript_text == "um raw transcript"
    assert app.session_store.records[0].backend_used == "groq"
    assert app._processing_session_id is None


def test_result_handler_keeps_running_processor_thread_alive():
    app = RotaApp.__new__(RotaApp)
    app._processing_timeout_timer = FakeTimer()
    app._processor_thread = FakeRunningThread()
    app._retired_processor_threads = []
    app._processing_session_id = "session-1"

    RotaApp._clear_processor_refs(app, "session-1")

    assert isinstance(app._processor_thread, FakeRunningThread)
    assert app._processing_session_id == "session-1"
    assert app._processing_timeout_timer.stopped is True
