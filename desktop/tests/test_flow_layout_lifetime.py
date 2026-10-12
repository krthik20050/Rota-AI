"""Exercise Qt ownership, including the installed-app timer crash pattern."""

import gc

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from shiboken6 import isValid

from ui.components.flow_layout import FlowLayout
from ui.components.trend_chart import SpeechTrendChart


def test_real_desktop_navigation_and_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    from app.desktop_smoke import run_desktop_smoke

    assert run_desktop_smoke() == 0


@pytest.mark.parametrize("attach_first", [True, False])
def test_flow_card_survives_builder_scope_and_remains_embedded(attach_first):
    app = QApplication.instance() or QApplication([])
    host = QWidget()
    outer = QVBoxLayout(host)
    flow = FlowLayout()
    if attach_first:
        outer.addLayout(flow)
    card = QWidget()
    inner = QVBoxLayout(card)
    chart = SpeechTrendChart()
    inner.addWidget(chart)
    flow.addWidget(card, 1)
    if not attach_first:
        outer.addLayout(flow)
    del card, inner
    gc.collect()
    try:
        assert isValid(chart)
        assert chart.parentWidget().parentWidget() is host
        host.show()
        app.processEvents()
        for _ in range(5):
            chart.setTrendData(["Mon", "Tue"], [100, 120], [90, 95])
            chart.setTrendDataAnimated(["Mon", "Tue"], [100, 120], [90, 95])
            app.processEvents()
        assert not chart.parentWidget().isWindow()
        host.hide()
        host.show()
        app.processEvents()
        assert chart.isVisible()
    finally:
        host.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
