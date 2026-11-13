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
from src.core.single_instance import SingleInstanceController
from src.gui.floating_window import FloatingSTTWindow

def main():
    # Standar High-DPI: harus dipanggil SEBELUM QApplication diinisialisasi
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass

    app = QApplication(sys.argv)

    # 5. Cek Single Instance: jika aplikasi sudah berjalan, buka jendela yang ada & keluar
    single_instance = SingleInstanceController()
    if single_instance.is_another_instance_running():
        print("[SingleInstance] Aplikasi sudah berjalan. Mengaktifkan jendela instance yang ada...", flush=True)
        sys.exit(0)

    # Jalankan server lokal untuk mendengarkan jika ada instance baru yang dibuka nanti
    single_instance.start_server()

    window = FloatingSTTWindow()
    single_instance.message_received.connect(lambda msg: window.restore_from_tray())
    window.show()

    exit_code = app.exec_()
    single_instance.cleanup()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
