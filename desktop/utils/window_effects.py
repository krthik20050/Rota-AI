import sys

_DWMWA_WINDOW_CORNER_PREFERENCE = 33
_DWMWCP_ROUND = 2  # Round the corners of the window


if sys.platform == "win32":
    import ctypes
    from ctypes.wintypes import DWORD

    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", DWORD),
            ("AccentFlags", DWORD),
            ("GradientColor", DWORD),
            ("AnimationId", DWORD),
        ]

    class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", DWORD),
            ("Data", ctypes.POINTER(ACCENTPOLICY)),
            ("SizeOfData", DWORD),
        ]

    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

    def apply_blur(hwnd, color=0x99111111):
        """Apply Acrylic blur effect (Windows only). No-op on macOS/Linux."""
        user32 = ctypes.windll.user32

        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = color

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)

        user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))

    def apply_win11_rounded_corners(hwnd: int) -> None:
        """
        Tell Windows 11 to round the window corners natively via DWM.

        This sets DWMWA_WINDOW_CORNER_PREFERENCE to DWMWCP_ROUND so that
        DWM applies its own native rounded corners — even on frameless windows.
        Works on Windows 11 build 22000+. No-op on older Windows.
        """
        try:
            policy = ctypes.c_int(_DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd),
                _DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(policy),
                ctypes.sizeof(policy),
            )
        except Exception:
            pass  # Older Windows or missing dwmapi — safe to ignore

else:

    def apply_blur(hwnd, color=0x99111111):
        """No-op on macOS/Linux. Blur is handled by the compositor/WM."""
        pass

    def apply_win11_rounded_corners(hwnd: int) -> None:
        """No-op on non-Windows platforms."""
        pass
