import sys

if sys.platform == "win32":
    import ctypes
    from ctypes.wintypes import HWND, DWORD

    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", DWORD),
            ("AccentFlags", DWORD),
            ("GradientColor", DWORD),
            ("AnimationId", DWORD)
        ]

    class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", DWORD),
            ("Data", ctypes.POINTER(ACCENTPOLICY)),
            ("SizeOfData", DWORD)
        ]

    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

    def apply_blur(hwnd, color=0x99111111):
        """Apply Acrylic blur effect (Windows only). No-op on Linux."""
        user32 = ctypes.windll.user32

        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = color

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)

        user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))

else:
    def apply_blur(hwnd, color=0x99111111):
        """No-op on Linux. Blur is handled by the compositor."""
        pass
