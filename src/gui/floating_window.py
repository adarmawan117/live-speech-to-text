import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QFont, QColor

from src.core.config_manager import load_config
from src.core.focus_manager import FocusManager
from src.core.virtual_typist import VirtualTypist
from src.core.hotkey_manager import HotkeyManager
from src.core.live_worker import LiveSTTWorker
from src.gui.components.waveform_visualizer import WaveformVisualizer
from src.gui.components.icons import get_svg_pixmap, get_svg_icon
from src.gui.dialogs.settings_dialog import SettingsDialog
from src.gui.dialogs.about_dialog import AboutDialog

class FloatingSTTWindow(QWidget):
    """
    Floating App Window utama untuk Live Speech to Text.
    - Menggunakan icon premium berbasis vektor SVG.
    - Menempel di atas (Always On Top) dan Frameless Draggable.
    - Mengetik langsung ke kursor aktif di aplikasi mana pun.
    - Otomatis keluar tuntas dan menutup CMD saat jendela ditutup.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Inisialisasi eksplisit seluruh instance variables (Standar PyQt5)
        self.config = load_config()
        self.worker = None
        self.virtual_typist = VirtualTypist()
        self.focus_manager = FocusManager()
        self.hotkey_manager = None
        self.is_recording = False
        self._drag_position = QPoint()

        # Widget references
        self.container = None
        self.layout_root = None
        self.layout_header = None
        self.lbl_header_icon = None
        self.lbl_header_title = None
        self.btn_minimize = None
        self.btn_close = None

        self.stacked_widget = None
        self.page_idle = None
        self.page_recording = None

        # Idle page widgets
        self.lbl_mic_badge = None
        self.lbl_idle_title = None
        self.lbl_idle_subtitle = None
        self.btn_start = None
        self.btn_settings = None
        self.btn_info = None

        # Recording page widgets
        self.visualizer = None
        self.lbl_rec_title = None
        self.lbl_rec_subtitle = None
        self.btn_stop = None

        self._init_window()
        self._init_ui()
        self._init_hotkey()

    def _init_window(self):
        """Konfigurasi properti jendela frameless & always-on-top."""
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(320, 310)

    def _init_ui(self):
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(10, 10, 10, 10)

        # Kontainer utama dengan border radius & shadow
        self.container = QWidget(self)
        self.container.setObjectName("mainContainer")
        self._update_container_style(is_recording=False)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        layout_container = QVBoxLayout(self.container)
        layout_container.setContentsMargins(16, 12, 16, 16)
        layout_container.setSpacing(10)

        # 1. Header Bar (Icon SVG, Title, Minimize SVG, Close SVG)
        self.layout_header = QHBoxLayout()
        self.layout_header.setSpacing(8)

        self.lbl_header_icon = QLabel(self.container)
        self.lbl_header_icon.setPixmap(get_svg_pixmap("mic", color="#00d2ff", size=16))

        self.lbl_header_title = QLabel("Live Speech to Text", self.container)
        self.lbl_header_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffffff;")

        self.btn_minimize = QPushButton(self.container)
        self.btn_minimize.setIcon(get_svg_icon("minimize", color="#8fa0bc", size=14))
        self.btn_minimize.setIconSize(QSize(14, 14))
        self.btn_minimize.setFixedSize(26, 26)
        self.btn_minimize.setCursor(Qt.PointingHandCursor)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)

        self.btn_close = QPushButton(self.container)
        self.btn_close.setIcon(get_svg_icon("close", color="#8fa0bc", size=13))
        self.btn_close.setIconSize(QSize(13, 13))
        self.btn_close.setFixedSize(26, 26)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #e63946;
            }
        """)

        self.layout_header.addWidget(self.lbl_header_icon)
        self.layout_header.addWidget(self.lbl_header_title)
        self.layout_header.addStretch()
        self.layout_header.addWidget(self.btn_minimize)
        self.layout_header.addWidget(self.btn_close)
        layout_container.addLayout(self.layout_header)

        # 2. Stacked Pages (Idle vs Recording)
        self.stacked_widget = QStackedWidget(self.container)

        self._build_idle_page()
        self._build_recording_page()

        self.stacked_widget.addWidget(self.page_idle)
        self.stacked_widget.addWidget(self.page_recording)
        self.stacked_widget.setCurrentWidget(self.page_idle)

        layout_container.addWidget(self.stacked_widget)
        self.layout_root.addWidget(self.container)

        # Hubungkan tombol window
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_close.clicked.connect(self.close_application)

    def _build_idle_page(self):
        """Halaman Idle: Badge Mic SVG besar, Teks Ready, Tombol Start SVG, Tombol Setting & Info SVG."""
        self.page_idle = QWidget()
        layout = QVBoxLayout(self.page_idle)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(10)

        # Circular Badge Microphone dengan SVG Premium
        self.lbl_mic_badge = QLabel(self.page_idle)
        self.lbl_mic_badge.setFixedSize(76, 76)
        self.lbl_mic_badge.setAlignment(Qt.AlignCenter)
        self.lbl_mic_badge.setPixmap(get_svg_pixmap("mic_badge", color="#ffffff", size=38))
        self.lbl_mic_badge.setStyleSheet("""
            QLabel {
                background-color: #101c33;
                border: 2px solid #1e75ff;
                border-radius: 38px;
            }
        """)

        layout_badge = QHBoxLayout()
        layout_badge.addStretch()
        layout_badge.addWidget(self.lbl_mic_badge)
        layout_badge.addStretch()
        layout.addLayout(layout_badge)

        # Judul & Subtitle
        self.lbl_idle_title = QLabel("Ready to Transcribe", self.page_idle)
        self.lbl_idle_title.setAlignment(Qt.AlignCenter)
        self.lbl_idle_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")

        hotkey = self.config.get("hotkey", "F8")
        self.lbl_idle_subtitle = QLabel(f"Tekan Start atau tombol [{hotkey}]...", self.page_idle)
        self.lbl_idle_subtitle.setAlignment(Qt.AlignCenter)
        self.lbl_idle_subtitle.setStyleSheet("font-size: 11px; color: #8fa0bc;")

        layout.addWidget(self.lbl_idle_title)
        layout.addWidget(self.lbl_idle_subtitle)

        # Tombol Start dengan Icon Play SVG
        self.btn_start = QPushButton("Start", self.page_idle)
        self.btn_start.setIcon(get_svg_icon("play", color="#ffffff", size=16))
        self.btn_start.setIconSize(QSize(16, 16))
        self.btn_start.setFixedHeight(44)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a62f5, stop:1 #2779ff);
                color: #ffffff;
                border: none;
                border-radius: 22px;
                font-size: 14px;
                font-weight: bold;
                padding-left: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2570ff, stop:1 #3b88ff);
            }
            QPushButton:pressed {
                background: #1450d0;
            }
        """)
        self.btn_start.clicked.connect(self.start_recording)
        layout.addWidget(self.btn_start)

        # Baris Bawah (Gear SVG & Info SVG)
        layout_footer = QHBoxLayout()
        layout_footer.setContentsMargins(4, 4, 4, 0)

        self.btn_settings = QPushButton(self.page_idle)
        self.btn_settings.setIcon(get_svg_icon("gear", color="#8fa0bc", size=17))
        self.btn_settings.setIconSize(QSize(17, 17))
        self.btn_settings.setFixedSize(28, 28)
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        self.btn_settings.clicked.connect(self.open_settings)

        self.btn_info = QPushButton(self.page_idle)
        self.btn_info.setIcon(get_svg_icon("info", color="#8fa0bc", size=17))
        self.btn_info.setIconSize(QSize(17, 17))
        self.btn_info.setFixedSize(28, 28)
        self.btn_info.setCursor(Qt.PointingHandCursor)
        self.btn_info.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        self.btn_info.clicked.connect(self.open_about)

        layout_footer.addWidget(self.btn_settings)
        layout_footer.addStretch()
        layout_footer.addWidget(self.btn_info)
        layout.addLayout(layout_footer)

    def _build_recording_page(self):
        """Halaman Recording: Waveform Visualizer cyan, Listening text, Tombol End SVG merah."""
        self.page_recording = QWidget()
        layout = QVBoxLayout(self.page_recording)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(12)

        # Visualizer Audio Cyan
        self.visualizer = WaveformVisualizer(num_bars=19, parent=self.page_recording)
        layout.addWidget(self.visualizer)

        # Status Teks
        self.lbl_rec_title = QLabel("Listening...", self.page_recording)
        self.lbl_rec_title.setAlignment(Qt.AlignCenter)
        self.lbl_rec_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")

        self.lbl_rec_subtitle = QLabel("Speak now", self.page_recording)
        self.lbl_rec_subtitle.setAlignment(Qt.AlignCenter)
        self.lbl_rec_subtitle.setStyleSheet("font-size: 11px; color: #8fa0bc;")

        layout.addWidget(self.lbl_rec_title)
        layout.addWidget(self.lbl_rec_subtitle)

        # Tombol End dengan Icon Stop SVG
        self.btn_stop = QPushButton("End", self.page_recording)
        self.btn_stop.setIcon(get_svg_icon("stop", color="#ffffff", size=15))
        self.btn_stop.setIconSize(QSize(15, 15))
        self.btn_stop.setFixedHeight(44)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e63946, stop:1 #ff4757);
                color: #ffffff;
                border: none;
                border-radius: 22px;
                font-size: 14px;
                font-weight: bold;
                padding-left: 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f04855, stop:1 #ff5e6c);
            }
            QPushButton:pressed {
                background: #c92a37;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_recording)
        layout.addWidget(self.btn_stop)

    def _update_container_style(self, is_recording: bool):
        """Memperbarui warna border & gradient kontainer utama."""
        if is_recording:
            # Border merah aksen saat merekam
            self.container.setStyleSheet("""
                QWidget#mainContainer {
                    background-color: #0c1322;
                    border: 1.5px solid #ff4757;
                    border-radius: 16px;
                }
            """)
        else:
            # Border biru elegan saat idle
            self.container.setStyleSheet("""
                QWidget#mainContainer {
                    background-color: #0c1322;
                    border: 1px solid #1b2e50;
                    border-radius: 16px;
                }
            """)

    def _init_hotkey(self):
        """Mendaftarkan shortcut global."""
        hotkey = self.config.get("hotkey", "F8")
        self.hotkey_manager = HotkeyManager(hotkey=hotkey, parent=self)
        self.hotkey_manager.hotkey_triggered.connect(self.toggle_recording)

    def toggle_recording(self):
        """Toggle antara mulai dan selesai rekam via Hotkey."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Mulai mendengarkan suara & mengetik ke kursor aktif."""
        if self.is_recording:
            return

        # 1. Simpan jendela target dan kembalikan fokus ke kursor aplikasi target
        self.focus_manager.capture_target(int(self.winId()))
        self.focus_manager.restore_target()

        self.is_recording = True
        self._update_container_style(is_recording=True)
        self.stacked_widget.setCurrentWidget(self.page_recording)
        self.visualizer.start()

        # 2. Reset buffer pengetik virtual
        self.virtual_typist.reset()

        # 3. Jalankan STT Worker di background
        model_name = self.config.get("model_size", "small")
        language = self.config.get("language", "id")

        self.worker = LiveSTTWorker(model_size=model_name, language=language, parent=self)
        self.worker.interim_text_ready.connect(self.on_interim_text_ready)
        self.worker.final_text_ready.connect(self.on_final_text_ready)
        self.worker.audio_level.connect(self.visualizer.set_level)
        self.worker.start()

    def stop_recording(self):
        """Berhenti mendengarkan & menyelesaikan kalimat terakhir."""
        if not self.is_recording:
            return

        self.is_recording = False
        self.visualizer.stop()
        self._update_container_style(is_recording=False)
        self.stacked_widget.setCurrentWidget(self.page_idle)

        if self.worker is not None:
            self.worker.stop()
            self.worker = None

        self.virtual_typist.reset()

    def on_interim_text_ready(self, interim_text: str):
        """Menerima potongan kata live dan mengetikkan secara langsung ke kursor aktif."""
        typing_mode = self.config.get("typing_mode", "streaming")
        if typing_mode == "streaming" and self.is_recording:
            self.virtual_typist.type_interim(interim_text)

    def on_final_text_ready(self, final_text: str):
        """Menerima kalimat final saat ada jeda dan menguncinya di kursor aktif."""
        if self.is_recording or not self.virtual_typist.last_interim:
            self.virtual_typist.commit_phrase(final_text)

    def open_settings(self):
        """Membuka dialog popup pengaturan."""
        dlg = SettingsDialog(self)
        if dlg.exec_():
            # Muat ulang konfigurasi setelah disimpan
            self.config = load_config()
            new_hotkey = self.config.get("hotkey", "F8")
            self.lbl_idle_subtitle.setText(f"Tekan Start atau tombol [{new_hotkey}]...")
            if self.hotkey_manager is not None:
                self.hotkey_manager.register(new_hotkey)

    def open_about(self):
        """Membuka dialog tentang aplikasi."""
        dlg = AboutDialog(self)
        dlg.exec_()

    # --- Mouse Events untuk Draggable Frameless Window ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Simpan jendela target sebelum jendela kita diklik
            self.focus_manager.capture_target(int(self.winId()))
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self._drag_position.isNull():
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = QPoint()

    def showEvent(self, event):
        super().showEvent(event)
        # Terapkan WS_EX_NOACTIVATE agar klik tombol tidak mencuri fokus kursor
        self.focus_manager.apply_no_activate(self)

    def close_application(self):
        """Keluar tuntas dari aplikasi."""
        self.close()

    def closeEvent(self, event):
        """Pembersihan bersih dan terminate event loop Qt saat jendela ditutup."""
        if self.worker is not None:
            self.worker.stop()
            self.worker = None
        if self.hotkey_manager is not None:
            self.hotkey_manager.unregister()
        event.accept()
        QApplication.quit()
