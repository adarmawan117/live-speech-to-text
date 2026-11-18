import os
import sys
import sounddevice as sd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QRadioButton, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.core.config_manager import load_config, save_config
from src.core.autostart_manager import is_autostart_enabled, set_autostart

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets")).replace("\\", "/")


class SettingsDialog(QDialog):
    """
    Dialog Pengaturan Floating App bertema dark modern dengan tab terorganisir.
    Mengikuti standar PyQt5: explicit attribute initialization & descriptive naming.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()

        # Inisialisasi eksplisit seluruh atribut (Standar PyQt5)
        self.layout_root = None
        self.tabs = None
        self.tab_transcription = None
        self.tab_system = None

        # Tab 1: Transkripsi & Audio
        self.combo_model = None
        self.combo_lang = None
        self.combo_device = None
        self.radio_streaming = None
        self.radio_sentence = None

        # Tab 2: Sistem & Otomasi
        self.combo_hotkey = None
        self.combo_autostart = None
        self.combo_minimize = None
        self.combo_autostop = None
        self.combo_timeout = None
        self.lbl_timeout = None

        # Action buttons
        self.btn_save = None
        self.btn_cancel = None

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Pengaturan - Live Speech to Text")
        self.setFixedSize(440, 560)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        chevron_path = f"{ASSETS_DIR}/chevron_down.png"
        radio_checked_path = f"{ASSETS_DIR}/radio_checked.png"
        radio_unchecked_path = f"{ASSETS_DIR}/radio_unchecked.png"

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0c1322;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }}
            QLabel {{
                color: #94a3b8;
                font-size: 12px;
                font-weight: 500;
            }}
            QTabWidget::pane {{
                border: 1px solid #253858;
                border-radius: 8px;
                background-color: #0c1322;
                top: -1px;
                padding: 14px 10px;
            }}
            QTabBar::tab {{
                background-color: #141e33;
                color: #8fa0bc;
                border: 1px solid #253858;
                border-bottom: none;
                min-width: 68px;
                min-height: 28px;
                padding: 3px 14px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }}
            QTabBar::tab:hover {{
                background-color: #18253e;
                color: #ffffff;
            }}
            QTabBar::tab:selected {{
                background-color: #1b68ff;
                color: #ffffff;
                border-color: #1b68ff;
            }}
            QComboBox {{
                background-color: #141e33;
                color: #ffffff;
                border: 1px solid #253858;
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 32px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: #3b5a8c;
                background-color: #18253e;
            }}
            QComboBox:focus {{
                border-color: #1b68ff;
            }}
            QComboBox:disabled {{
                background-color: #0d1422;
                color: #4f627d;
                border-color: #1a283e;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 34px;
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url("{chevron_path}");
                width: 14px;
                height: 14px;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #141e33;
                color: #ffffff;
                selection-background-color: #1b68ff;
                selection-color: #ffffff;
                border: 1px solid #253858;
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 34px;
                padding: 4px 12px;
            }}
            QRadioButton {{
                color: #cbd5e1;
                font-size: 13px;
                spacing: 10px;
                min-height: 26px;
            }}
            QRadioButton:hover {{
                color: #ffffff;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            QRadioButton::indicator:checked {{
                image: url("{radio_checked_path}");
            }}
            QRadioButton::indicator:unchecked {{
                image: url("{radio_unchecked_path}");
            }}
        """)

        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(20, 18, 20, 18)
        self.layout_root.setSpacing(12)

        lbl_header = QLabel("Pengaturan STT, Sistem & Hotkey", self)
        lbl_header.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 2px;")
        self.layout_root.addWidget(lbl_header)

        # Tab Widget Utama
        self.tabs = QTabWidget(self)
        self.tabs.tabBar().setFont(QFont("Segoe UI", 9))

        self._build_transcription_tab()
        self._build_system_tab()

        self.tabs.addTab(self.tab_transcription, "Audio")
        self.tabs.addTab(self.tab_system, "Sistem")
        self.layout_root.addWidget(self.tabs)

        # Tombol Aksi Bawah (Batal & Simpan)
        layout_btn = QHBoxLayout()
        layout_btn.setSpacing(12)

        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setFixedHeight(38)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #141e33;
                color: #94a3b8;
                border: 1px solid #253858;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1e2c47;
                color: #ffffff;
                border-color: #3b5a8c;
            }
            QPushButton:pressed {
                background-color: #111a2c;
            }
        """)

        self.btn_save = QPushButton("Simpan", self)
        self.btn_save.setFixedHeight(38)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a62f5, stop:1 #2779ff);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 24px;
                min-width: 90px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2570ff, stop:1 #3b88ff);
            }
            QPushButton:pressed {
                background: #1450d0;
            }
        """)

        layout_btn.addStretch()
        layout_btn.addWidget(self.btn_cancel)
        layout_btn.addWidget(self.btn_save)
        self.layout_root.addLayout(layout_btn)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.on_save)

    def _build_transcription_tab(self):
        """Membangun tab Transkripsi: Model Whisper, Bahasa, Mic, Mode Pengetikan."""
        self.tab_transcription = QWidget()
        layout = QVBoxLayout(self.tab_transcription)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # 1. Model Whisper
        lbl_mdl = QLabel("Model Whisper AI:", self.tab_transcription)
        self.combo_model = QComboBox(self.tab_transcription)
        self.combo_model.setFixedHeight(38)
        self.combo_model.addItems(["small", "base", "medium", "tiny"])
        self.combo_model.setCurrentText(self.config.get("model_size", "small"))
        layout.addWidget(lbl_mdl)
        layout.addWidget(self.combo_model)

        # 2. Bahasa
        lbl_lang = QLabel("Bahasa Transkripsi:", self.tab_transcription)
        self.combo_lang = QComboBox(self.tab_transcription)
        self.combo_lang.setFixedHeight(38)
        self.combo_lang.addItem("Indonesia (id)", "id")
        self.combo_lang.addItem("English (en)", "en")
        self.combo_lang.addItem("Otomatis (Auto-Detect)", None)
        curr_lang = self.config.get("language", "id")
        idx = self.combo_lang.findData(curr_lang)
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        layout.addWidget(lbl_lang)
        layout.addWidget(self.combo_lang)

        # 3. Mikrofon
        lbl_mic = QLabel("Perangkat Mikrofon:", self.tab_transcription)
        self.combo_device = QComboBox(self.tab_transcription)
        self.combo_device.setFixedHeight(38)
        self._populate_audio_devices()
        layout.addWidget(lbl_mic)
        layout.addWidget(self.combo_device)

        # 4. Mode Pengetikan
        lbl_mode = QLabel("Mode Pengetikan ke Kursor Aktif:", self.tab_transcription)
        layout.addWidget(lbl_mode)

        self.radio_streaming = QRadioButton("Streaming Kata demi Kata (Live)", self.tab_transcription)
        self.radio_sentence = QRadioButton("Per Penggalan Kalimat (Saat Jeda)", self.tab_transcription)

        mode = self.config.get("typing_mode", "streaming")
        if mode == "sentence":
            self.radio_sentence.setChecked(True)
        else:
            self.radio_streaming.setChecked(True)

        layout_radio = QVBoxLayout()
        layout_radio.setSpacing(6)
        layout_radio.setContentsMargins(4, 2, 4, 2)
        layout_radio.addWidget(self.radio_streaming)
        layout_radio.addWidget(self.radio_sentence)
        layout.addLayout(layout_radio)

        layout.addStretch()

    def _build_system_tab(self):
        """Membangun tab Sistem: Shortcut Global, Auto-Launch Windows, Minimize ke Tray, Auto-Stop Hening."""
        self.tab_system = QWidget()
        layout = QVBoxLayout(self.tab_system)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(11)

        # 1. Hotkey Global
        lbl_hk = QLabel("Tombol Shortcut Global (Start / End):", self.tab_system)
        self.combo_hotkey = QComboBox(self.tab_system)
        self.combo_hotkey.setFixedHeight(38)
        self.combo_hotkey.addItems(["F8", "F9", "F10", "F12", "Ctrl+Shift+Space", "Alt+V", "F4"])
        self.combo_hotkey.setCurrentText(self.config.get("hotkey", "F8"))
        layout.addWidget(lbl_hk)
        layout.addWidget(self.combo_hotkey)

        # 2. Auto-Launch saat Windows dinyalakan
        lbl_autostart = QLabel("Mulai Otomatis Saat Windows Dinyalakan:", self.tab_system)
        self.combo_autostart = QComboBox(self.tab_system)
        self.combo_autostart.setFixedHeight(38)
        self.combo_autostart.addItem("Nonaktif (Buka manual)", False)
        self.combo_autostart.addItem("Aktif (Jalankan saat booting Windows)", True)
        # Ambil status aktual dari registry Windows jika di Windows
        curr_autostart = is_autostart_enabled() if sys.platform == "win32" else self.config.get("auto_start_on_boot", False)
        idx_autostart = self.combo_autostart.findData(curr_autostart)
        if idx_autostart >= 0:
            self.combo_autostart.setCurrentIndex(idx_autostart)
        layout.addWidget(lbl_autostart)
        layout.addWidget(self.combo_autostart)

        # 3. Minimize ke Tray vs Icon Biasa
        lbl_minimize = QLabel("Perilaku Tombol Minimize (_):", self.tab_system)
        self.combo_minimize = QComboBox(self.tab_system)
        self.combo_minimize.setFixedHeight(38)
        self.combo_minimize.addItem("Masuk ke System Tray (Sembunyi ke Tray)", True)
        self.combo_minimize.addItem("Minimize ke Taskbar (Icon Biasa)", False)
        curr_min = self.config.get("minimize_to_tray", True)
        idx_min = self.combo_minimize.findData(curr_min)
        if idx_min >= 0:
            self.combo_minimize.setCurrentIndex(idx_min)
        layout.addWidget(lbl_minimize)
        layout.addWidget(self.combo_minimize)

        # 4. Auto-Stop Ketika Tidak Ada Suara (On / Off)
        lbl_autostop = QLabel("Auto-Stop Saat Hening Tanpa Suara:", self.tab_system)
        self.combo_autostop = QComboBox(self.tab_system)
        self.combo_autostop.setFixedHeight(38)
        self.combo_autostop.addItem("Aktif (Otomatis Berhenti Saat Hening)", True)
        self.combo_autostop.addItem("Nonaktif (Tetap Merekam Terus)", False)
        curr_autostop = self.config.get("auto_stop_enabled", True)
        idx_stop = self.combo_autostop.findData(curr_autostop)
        if idx_stop >= 0:
            self.combo_autostop.setCurrentIndex(idx_stop)
        layout.addWidget(lbl_autostop)
        layout.addWidget(self.combo_autostop)

        # 5. Durasi Waktu Auto-Stop
        self.lbl_timeout = QLabel("Batas Waktu Hening Tanpa Suara:", self.tab_system)
        self.combo_timeout = QComboBox(self.tab_system)
        self.combo_timeout.setFixedHeight(38)
        self.combo_timeout.addItem("30 Detik", 30)
        self.combo_timeout.addItem("45 Detik", 45)
        self.combo_timeout.addItem("1 Menit (Default)", 60)
        self.combo_timeout.addItem("2 Menit", 120)
        self.combo_timeout.addItem("3 Menit", 180)
        self.combo_timeout.addItem("5 Menit", 300)
        curr_timeout = int(self.config.get("auto_stop_timeout_sec", 60))
        idx_timeout = self.combo_timeout.findData(curr_timeout)
        if idx_timeout >= 0:
            self.combo_timeout.setCurrentIndex(idx_timeout)
        else:
            self.combo_timeout.addItem(f"{curr_timeout} Detik", curr_timeout)
            self.combo_timeout.setCurrentIndex(self.combo_timeout.count() - 1)

        layout.addWidget(self.lbl_timeout)
        layout.addWidget(self.combo_timeout)

        # Sambungkan sinyal perubahan auto-stop untuk enable/disable combo timeout
        self.combo_autostop.currentIndexChanged.connect(self._on_autostop_changed)
        self._on_autostop_changed()

        layout.addStretch()

    def _on_autostop_changed(self):
        """Mengaktifkan/menonaktifkan combo durasi timeout sesuai opsi auto-stop."""
        is_active = self.combo_autostop.currentData()
        self.combo_timeout.setEnabled(bool(is_active))
        if is_active:
            self.lbl_timeout.setStyleSheet("color: #94a3b8;")
        else:
            self.lbl_timeout.setStyleSheet("color: #4f627d;")

    def _populate_audio_devices(self):
        """Memuat daftar mikrofon yang tersedia."""
        self.combo_device.addItem("Default Sistem", None)
        try:
            devices = sd.query_devices()
            for idx, dev in enumerate(devices):
                if dev.get("max_input_channels", 0) > 0:
                    name = f"[{idx}] {dev.get('name', 'Mic')}"
                    self.combo_device.addItem(name, idx)
        except Exception:
            pass

        saved_dev = self.config.get("audio_device")
        if saved_dev is not None:
            found = self.combo_device.findData(saved_dev)
            if found >= 0:
                self.combo_device.setCurrentIndex(found)

    def on_save(self):
        """Menyimpan konfigurasi baru ke file dan sistem."""
        self.config["hotkey"] = self.combo_hotkey.currentText()
        self.config["model_size"] = self.combo_model.currentText()
        self.config["language"] = self.combo_lang.currentData()
        self.config["audio_device"] = self.combo_device.currentData()
        self.config["typing_mode"] = "sentence" if self.radio_sentence.isChecked() else "streaming"

        # Simpan pengaturan sistem & otomasi
        autostart_enabled = bool(self.combo_autostart.currentData())
        self.config["auto_start_on_boot"] = autostart_enabled
        set_autostart(autostart_enabled)

        self.config["minimize_to_tray"] = bool(self.combo_minimize.currentData())
        self.config["auto_stop_enabled"] = bool(self.combo_autostop.currentData())
        self.config["auto_stop_timeout_sec"] = int(self.combo_timeout.currentData())

        save_config(self.config)
        self.accept()
