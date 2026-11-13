import keyboard
from PyQt5.QtCore import QObject, pyqtSignal

class HotkeyManager(QObject):
    """
    Manajer Hotkey global untuk memicu Start / End dari aplikasi apa pun di Windows.
    """
    hotkey_triggered = pyqtSignal()

    def __init__(self, hotkey="F8", parent=None):
        super().__init__(parent)
        self.current_hotkey = hotkey
        self.is_registered = False
        self.register(self.current_hotkey)

    def register(self, hotkey: str):
        """Mendaftarkan hotkey baru."""
        self.unregister()
        try:
            self.current_hotkey = hotkey.strip()
            if self.current_hotkey:
                keyboard.add_hotkey(self.current_hotkey, self._on_hotkey)
                self.is_registered = True
        except Exception as e:
            print(f"Gagal mendaftarkan hotkey '{hotkey}': {e}", flush=True)

    def unregister(self):
        """Membatalkan pendaftaran hotkey aktif."""
        if self.is_registered and self.current_hotkey:
            try:
                keyboard.remove_hotkey(self.current_hotkey)
            except Exception:
                pass
            self.is_registered = False

    def _on_hotkey(self):
        """Callback saat hotkey ditekan di Windows."""
        self.hotkey_triggered.emit()
