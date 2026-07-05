from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QWidgetItem


class FlowLayout(QLayout):
    """Wraps child widgets horizontally (like CSS flex-wrap).

    CRITICAL NOTE: Custom QLayout subclasses in PySide6 risk access violations
    because Qt destroys child QWidgetItem C++ objects during parent cleanup,
    but the Python _item_list still holds references to them. All item iteration
    is wrapped in try-except guards to handle this gracefully.
    """

    def __init__(self, parent=None, margin=0, hspacing=6, vspacing=6):
        super().__init__(parent)
        self._item_list = []
        self._h_space = hspacing
        self._v_space = vspacing
        self.setContentsMargins(margin, margin, margin, margin)

    # NO __del__ — Qt's parent-child ownership already handles cleanup of
    # child items. A custom __del__ risks double-free / use-after-free.

    def addItem(self, item):
        self._item_list.append(item)

    def addWidget(self, widget, stretch=0, alignment=None):
        _ = stretch
        _ = alignment
        item = QWidgetItem(widget)
        self.addItem(item)

    def setSpacing(self, spacing: int):
        self._h_space = spacing
        self._v_space = spacing

    def horizontalSpacing(self):
        return self._h_space

    def verticalSpacing(self):
        return self._v_space

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        try:
            return self._do_layout(QRect(0, 0, width, 0), True)
        except Exception:
            return 0

    def setGeometry(self, rect):
        super().setGeometry(rect)
        try:
            self._do_layout(rect, False)
        except Exception:
            pass

    def sizeHint(self):
        try:
            size = QSize()
            for item in list(self._item_list):
                try:
                    size = size.expandedTo(item.sizeHint())
                except Exception:
                    continue
            margins = self.contentsMargins()
            size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
            return size
        except Exception:
            return QSize(200, 100)

    def minimumSize(self):
        try:
            size = QSize()
            for item in list(self._item_list):
                try:
                    size = size.expandedTo(item.minimumSize())
                except Exception:
                    continue
            margins = self.contentsMargins()
            size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
            return size
        except Exception:
            return QSize(100, 50)

    def _do_layout(self, rect, test_only):
        try:
            margins = self.contentsMargins()
            effective_rect = rect.adjusted(
                +margins.left(), +margins.top(), -margins.right(), -margins.bottom()
            )
            x = effective_rect.x()
            y = effective_rect.y()
            line_height = 0

            for item in list(self._item_list):
                try:
                    widget = item.widget()
                    if widget and not widget.isVisible():
                        continue
                    sh = item.sizeHint()
                    space_x = self.horizontalSpacing()
                    space_y = self.verticalSpacing()
                    next_x = x + sh.width() + space_x
                    if next_x - space_x > effective_rect.right() and line_height > 0:
                        x = effective_rect.x()
                        y = y + line_height + space_y
                        next_x = x + sh.width() + space_x
                        line_height = 0

                    if not test_only:
                        item.setGeometry(QRect(QPoint(x, y), sh))

                    x = next_x
                    line_height = max(line_height, sh.height())
                except Exception:
                    continue

            return y + line_height - rect.y() + margins.bottom()
        except Exception:
            return 0
