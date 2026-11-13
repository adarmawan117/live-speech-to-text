import sounddevice as sd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QRadioButton, QButtonGroup, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.core.config_manager import load_config, save_config

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
        self.setFixedSize(360, 420)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d131f;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #c7d2e3;
                font-size: 12px;
            }
            QLabel#title {
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
            }
            QComboBox {
                background-color: #162035;
                color: #ffffff;
                border: 1px solid #2a3b5c;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #162035;
                color: #ffffff;
                selection-background-color: #1b68ff;
                border: 1px solid #2a3b5c;
            }
            QRadioButton {
                color: #c7d2e3;
                font-size: 12px;
                spacing: 6px;
            }
            QPushButton#btn_save {
                background-color: #1b68ff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#btn_save:hover {
                background-color: #2b78ff;
            }
            QPushButton#btn_cancel {
                background-color: transparent;
                color: #8fa0bc;
                border: 1px solid #2a3b5c;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton#btn_cancel:hover {
                background-color: #162035;
                color: #ffffff;
            }
        """)

        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(20, 20, 20, 20)
        self.layout_root.setSpacing(14)

        lbl_header = QLabel("Pengaturan STT & Hotkey", self)
        lbl_header.setObjectName("title")
        self.layout_root.addWidget(lbl_header)

        # 1. Hotkey Global
        lbl_hk = QLabel("Tombol Shortcut Global (Start / End):", self)
        self.combo_hotkey = QComboBox(self)
        self.combo_hotkey.addItems(["F8", "F9", "F10", "F12", "Ctrl+Shift+Space", "Alt+V", "F4"])
        self.combo_hotkey.setCurrentText(self.config.get("hotkey", "F8"))
        self.layout_root.addWidget(lbl_hk)
        self.layout_root.addWidget(self.combo_hotkey)

        # 2. Model Whisper
        lbl_mdl = QLabel("Model Whisper AI:", self)
        self.combo_model = QComboBox(self)
        self.combo_model.addItems(["small", "base", "medium", "tiny"])
        self.combo_model.setCurrentText(self.config.get("model_size", "small"))
        self.layout_root.addWidget(lbl_mdl)
        self.layout_root.addWidget(self.combo_model)

        # 3. Bahasa
        lbl_lang = QLabel("Bahasa Transkripsi:", self)
        self.combo_lang = QComboBox(self)
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
        layout_radio.setSpacing(6)
        layout_radio.addWidget(self.radio_streaming)
        layout_radio.addWidget(self.radio_sentence)
        self.layout_root.addLayout(layout_radio)

        self.layout_root.addStretch()

        # Tombol Aksi
        layout_btn = QHBoxLayout()
        layout_btn.setSpacing(10)

        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_save = QPushButton("Simpan", self)
        self.btn_save.setObjectName("btn_save")

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

