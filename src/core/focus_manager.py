import sys
import ctypes

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000

class FocusManager:
    """
    Mengelola fokus window Windows agar saat pengguna mengklik Floating App,
    fokus kursor di aplikasi target (WhatsApp, Word, Browser, dll.) tetap terjaga.
    """
    def __init__(self):
        self.last_target_hwnd = None
        self.user32 = ctypes.windll.user32 if sys.platform == "win32" else None

    def apply_no_activate(self, widget):
        """Menerapkan atribut WS_EX_NOACTIVATE ke jendela widget."""
        if not self.user32:
            return
        try:
            hwnd = int(widget.winId())
            style = self.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            self.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
        except Exception as e:
            print(f"Gagal menerapkan WS_EX_NOACTIVATE: {e}", flush=True)

    def capture_target(self, my_hwnd=None):
        """Menyimpan HWND jendela yang saat ini aktif (sebelum jendela kita disentuh)."""
        if not self.user32:
            return
        try:
            fg_hwnd = self.user32.GetForegroundWindow()
            if fg_hwnd != 0 and fg_hwnd != my_hwnd:
                self.last_target_hwnd = fg_hwnd
        except Exception:
            pass

    def restore_target(self):
        """Mengembalikan fokus ke jendela target."""
        if not self.user32 or not self.last_target_hwnd:
            return
        try:
            self.user32.SetForegroundWindow(self.last_target_hwnd)
        except Exception:
            pass
