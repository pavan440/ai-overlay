import ctypes

_user32 = ctypes.windll.user32

_WDA_EXCLUDEFROMCAPTURE = 0x00000011
_HWND_TOPMOST           = -1
_SWP_NOMOVE             = 0x0002
_SWP_NOSIZE             = 0x0001
_GWL_EXSTYLE            = -20
_WS_EX_TOOLWINDOW       = 0x00000080   # hides from taskbar & Alt+Tab
_WS_EX_APPWINDOW        = 0x00040000   # forces onto taskbar (we remove this)


def apply_overlay(hwnd: int) -> None:
    # Exclude from all screen capture (OBS, Teams, Zoom, Win+PrintScreen, etc.)
    _user32.SetWindowDisplayAffinity(hwnd, _WDA_EXCLUDEFROMCAPTURE)

    # Always on top
    _user32.SetWindowPos(hwnd, _HWND_TOPMOST, 0, 0, 0, 0, _SWP_NOMOVE | _SWP_NOSIZE)

    # Hide from taskbar and Alt+Tab switcher
    style = _user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
    style = (style | _WS_EX_TOOLWINDOW) & ~_WS_EX_APPWINDOW
    _user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, style)
