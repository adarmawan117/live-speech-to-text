import sys
import os

# 1. Pastikan penekanan warning font Qt dan HuggingFace symlinks di Windows
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# 2. Pastikan UTF-8 encoding
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

# 3. PENTING: Inisialisasi environment CUDA dan import CTranslate2 / faster-whisper
# HARUS dilakukan SEBELUM PyQt5 di-import untuk mencegah konflik runtime DLL C++ di Windows
from src.core.cuda_setup import setup_cuda_environment
setup_cuda_environment()
import ctranslate2
import faster_whisper

# 4. Inisialisasi modul GUI PyQt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.gui.floating_window import FloatingSTTWindow

def main():
    # Standar High-DPI: harus dipanggil SEBELUM QApplication diinisialisasi
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass

    app = QApplication(sys.argv)
    window = FloatingSTTWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
