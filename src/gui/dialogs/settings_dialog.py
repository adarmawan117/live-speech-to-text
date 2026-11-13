import os
import sounddevice as sd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QRadioButton
)
from PyQt5.QtCore import Qt
from src.core.config_manager import load_config, save_config

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets")).replace("\\", "/")

class SettingsDialog(QDialog):
    """
    Dialog Pengaturan Floating App bertema dark modern.
    Mengikuti standar PyQt5: explicit attribute initialization & descriptive naming.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()

        self.layout_root = None
        self.combo_hotkey = None
        self.combo_model = None
        self.combo_lang = None
        self.combo_device = None
        self.radio_streaming = None
        self.radio_sentence = None
        self.btn_save = None
        self.btn_cancel = None

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Pengaturan - Live Speech to Text")
        self.setFixedSize(400, 530)
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
        self.layout_root.setContentsMargins(24, 22, 24, 22)
        self.layout_root.setSpacing(14)

        lbl_header = QLabel("Pengaturan STT & Hotkey", self)
        lbl_header.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold; margin-bottom: 2px;")
        self.layout_root.addWidget(lbl_header)

        # 1. Hotkey Global
        lbl_hk = QLabel("Tombol Shortcut Global (Start / End):", self)
        self.combo_hotkey = QComboBox(self)
        self.combo_hotkey.setFixedHeight(38)
        self.combo_hotkey.addItems(["F8", "F9", "F10", "F12", "Ctrl+Shift+Space", "Alt+V", "F4"])
        self.combo_hotkey.setCurrentText(self.config.get("hotkey", "F8"))
        self.layout_root.addWidget(lbl_hk)
        self.layout_root.addWidget(self.combo_hotkey)

        # 2. Model Whisper
        lbl_mdl = QLabel("Model Whisper AI:", self)
        self.combo_model = QComboBox(self)
        self.combo_model.setFixedHeight(38)
        self.combo_model.addItems(["small", "base", "medium", "tiny"])
        self.combo_model.setCurrentText(self.config.get("model_size", "small"))
        self.layout_root.addWidget(lbl_mdl)
        self.layout_root.addWidget(self.combo_model)

        # 3. Bahasa
        lbl_lang = QLabel("Bahasa Transkripsi:", self)
        self.combo_lang = QComboBox(self)
        self.combo_lang.setFixedHeight(38)
        self.combo_lang.addItem("Indonesia (id)", "id")
        self.combo_lang.addItem("English (en)", "en")
        self.combo_lang.addItem("Otomatis (Auto-Detect)", None)
        curr_lang = self.config.get("language", "id")
        idx = self.combo_lang.findData(curr_lang)
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        self.layout_root.addWidget(lbl_lang)
        self.layout_root.addWidget(self.combo_lang)

        # 4. Mikrofon
        lbl_mic = QLabel("Perangkat Mikrofon:", self)
        self.combo_device = QComboBox(self)
        self.combo_device.setFixedHeight(38)
        self._populate_audio_devices()
        self.layout_root.addWidget(lbl_mic)
        self.layout_root.addWidget(self.combo_device)

        # 5. Mode Pengetikan
        lbl_mode = QLabel("Mode Pengetikan ke Kursor Aktif:", self)
        self.layout_root.addWidget(lbl_mode)

        self.radio_streaming = QRadioButton("Streaming Kata demi Kata (Live)", self)
        self.radio_sentence = QRadioButton("Per Penggalan Kalimat (Saat Jeda)", self)
        
        mode = self.config.get("typing_mode", "streaming")
        if mode == "sentence":
            self.radio_sentence.setChecked(True)
        else:
            self.radio_streaming.setChecked(True)

        layout_radio = QVBoxLayout()
        layout_radio.setSpacing(8)
        layout_radio.setContentsMargins(4, 2, 4, 4)
        layout_radio.addWidget(self.radio_streaming)
        layout_radio.addWidget(self.radio_sentence)
        self.layout_root.addLayout(layout_radio)

        self.layout_root.addStretch()

        # Tombol Aksi
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
        """Menyimpan konfigurasi baru."""
        self.config["hotkey"] = self.combo_hotkey.currentText()
        self.config["model_size"] = self.combo_model.currentText()
        self.config["language"] = self.combo_lang.currentData()
        self.config["audio_device"] = self.combo_device.currentData()
        self.config["typing_mode"] = "sentence" if self.radio_sentence.isChecked() else "streaming"

        save_config(self.config)
        self.accept()

