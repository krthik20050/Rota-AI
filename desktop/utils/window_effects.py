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

# Accent States
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4  # RS4 1803
ACCENT_ENABLE_HOSTBACKDROP = 5        # RS5 1809
ACCENT_INVALID_STATE = 6

def apply_blur(hwnd, color=0x99111111):
    """
    Applies the Acrylic blur effect to a window handle (HWND).
    Color is in ABGR hex format (0x7f000000 = 50% transparent black).
    """
    user32 = ctypes.windll.user32
    
    accent = ACCENTPOLICY()
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.GradientColor = color
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19  # WCA_ACCENT_POLICY
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)
    
    user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))
