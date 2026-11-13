import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QGraphicsDropShadowEffect,
    QApplication, QSystemTrayIcon, QMenu
)
from PyQt5.QtCore import Qt, QPoint, QSize, QEvent
from PyQt5.QtGui import QFont, QColor, QIcon

from src.core.config_manager import load_config
from src.core.focus_manager import FocusManager
from src.core.virtual_typist import VirtualTypist
from src.core.hotkey_manager import HotkeyManager
from src.core.live_worker import LiveSTTWorker
from src.gui.components.waveform_visualizer import WaveformVisualizer
from src.gui.components.icons import get_svg_pixmap, get_svg_icon
from src.gui.dialogs.settings_dialog import SettingsDialog
from src.gui.dialogs.about_dialog import AboutDialog

ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icon.ico")

class FloatingSTTWindow(QWidget):
    """
    Floating App Window utama untuk Live Speech to Text.
    - Icon aplikasi premium berbasis vektor SVG.
    - Minimize ke System Tray (hanya bisa ketika tidak sedang merekam).
    - Menempel di atas (Always On Top) dan Frameless Draggable.
    - Mengetik langsung ke kursor aktif di aplikasi mana pun.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Inisialisasi eksplisit seluruh atribut (Standar PyQt5)
        self.config = load_config()
        self.worker = None
        self.virtual_typist = VirtualTypist()
        self.focus_manager = FocusManager()
        self.hotkey_manager = None
        self.tray_icon = None
        self.tray_menu = None
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
        self.btn_mic_start = None
        self.lbl_idle_title = None
        self.lbl_idle_subtitle = None
        self.btn_settings = None
        self.btn_info = None

        # Recording page widgets
        self.visualizer = None
        self.lbl_rec_title = None
        self.lbl_rec_subtitle = None
        self.btn_stop = None

        self._init_window()
        self._init_ui()
        self._init_tray()
        self._init_hotkey()

    def _init_window(self):
        """Konfigurasi properti jendela frameless, always-on-top, dan icon aplikasi."""
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(320, 270)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

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
        self.btn_minimize.setToolTip("Minimize ke System Tray")
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
        self.btn_close.setToolTip("Tutup Aplikasi")
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
        self.btn_minimize.clicked.connect(self.minimize_to_tray)
        self.btn_close.clicked.connect(self.close_application)

    def _build_idle_page(self):
        """Halaman Idle: Tombol Mic SVG besar di tengah, Teks Ready, Tombol Setting & Info SVG."""
        self.page_idle = QWidget()
        layout = QVBoxLayout(self.page_idle)
        layout.setContentsMargins(0, 10, 0, 4)
        layout.setSpacing(10)

        # Tombol Mikrofon Utama di Tengah (Circular Button dengan Mic SVG)
        self.btn_mic_start = QPushButton(self.page_idle)
        self.btn_mic_start.setFixedSize(86, 86)
        self.btn_mic_start.setIcon(get_svg_icon("mic_badge", color="#ffffff", size=42))
        self.btn_mic_start.setIconSize(QSize(42, 42))
        self.btn_mic_start.setCursor(Qt.PointingHandCursor)
        hotkey = self.config.get("hotkey", "F8")
        self.btn_mic_start.setToolTip(f"Mulai Merekam (atau tekan {hotkey})")
        self.btn_mic_start.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #101c33, stop:1 #142442);
                border: 2.5px solid #1e75ff;
                border-radius: 43px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a62f5, stop:1 #2779ff);
                border: 2.5px solid #00d2ff;
            }
            QPushButton:pressed {
                background: #1450d0;
                border: 2.5px solid #1652c4;
            }
        """)
        self.btn_mic_start.clicked.connect(self.start_recording)

        layout_badge = QHBoxLayout()
        layout_badge.addStretch()
        layout_badge.addWidget(self.btn_mic_start)
        layout_badge.addStretch()
        layout.addLayout(layout_badge)

        # Judul & Subtitle
        self.lbl_idle_title = QLabel("Ready to Transcribe", self.page_idle)
        self.lbl_idle_title.setAlignment(Qt.AlignCenter)
        self.lbl_idle_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")

        self.lbl_idle_subtitle = QLabel(f"Klik tombol mic atau tekan [{hotkey}]...", self.page_idle)
        self.lbl_idle_subtitle.setAlignment(Qt.AlignCenter)
        self.lbl_idle_subtitle.setStyleSheet("font-size: 11px; color: #8fa0bc;")

        layout.addWidget(self.lbl_idle_title)
        layout.addWidget(self.lbl_idle_subtitle)

        layout.addStretch()

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
            self.container.setStyleSheet("""
                QWidget#mainContainer {
                    background-color: #0c1322;
                    border: 1.5px solid #ff4757;
                    border-radius: 16px;
                }
            """)
        else:
            self.container.setStyleSheet("""
                QWidget#mainContainer {
                    background-color: #0c1322;
                    border: 1px solid #1b2e50;
                    border-radius: 16px;
                }
            """)

    def _init_tray(self):
        """Inisialisasi System Tray Icon dengan icon mikrofon cyan."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        tray_icon_img = QIcon(ICON_PATH) if os.path.exists(ICON_PATH) else get_svg_icon("mic", color="#00d2ff", size=32)
        self.tray_icon = QSystemTrayIcon(tray_icon_img, self)
        self.tray_icon.setToolTip("Live Speech to Text - ADR Programming")

        self.tray_menu = QMenu(self)
        self.tray_menu.setStyleSheet("""
            QMenu {
                background-color: #0d131f;
                color: #ffffff;
                border: 1px solid #2a3b5c;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1b68ff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2a3b5c;
                margin: 4px 0px;
            }
        """)

        action_show = self.tray_menu.addAction("Tampilkan Jendela")
        action_show.triggered.connect(self.restore_from_tray)

        action_settings = self.tray_menu.addAction("Pengaturan")
        action_settings.triggered.connect(self.open_settings)

        self.tray_menu.addSeparator()

        action_exit = self.tray_menu.addAction("Keluar")
        action_exit.triggered.connect(self.close_application)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        """Klik icon di system tray untuk menampilkan / menyembunyikan jendela."""
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                if not self.is_recording:
                    self.minimize_to_tray()
            else:
                self.restore_from_tray()

    def minimize_to_tray(self):
        """
        Minimize aplikasi ke System Tray.
        ATURAN KETAT: Aplikasi TIDAK BISA diminimize jika fitur transcribe sedang aktif (Start).
        """
        if self.is_recording:
            return

        self.hide()
        if self.tray_icon is not None and self.tray_icon.isVisible():
            hotkey = self.config.get("hotkey", "F8")
            self.tray_icon.showMessage(
                "Live Speech to Text",
                f"Aplikasi aktif di system tray. Tekan [{hotkey}] di keyboard untuk mulai bicara kapan saja.",
                QSystemTrayIcon.Information,
                2000
            )

    def restore_from_tray(self):
        """Mengembalikan jendela aplikasi dari system tray ke layar."""
        self.show()
        self.raise_()
        self.activateWindow()

    def changeEvent(self, event):
        """Mencegah minimize sistem dari OS jika sedang merekam."""
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                if self.is_recording:
                    # Tolak minimize jika sedang merekam
                    self.setWindowState(Qt.WindowNoState)
                    event.ignore()
                    return
                else:
                    self.minimize_to_tray()
                    event.ignore()
                    return
        super().changeEvent(event)

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

        # ATURAN: Matikan tombol minimize saat merekam
        self.btn_minimize.setEnabled(False)
        self.btn_minimize.setToolTip("Tidak dapat minimize saat sedang merekam")
        self.btn_minimize.setStyleSheet("background: transparent; border: none; opacity: 0.3;")

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

        # Aktifkan kembali tombol minimize saat idle
        self.btn_minimize.setEnabled(True)
        self.btn_minimize.setToolTip("Minimize ke System Tray")
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
            self.config = load_config()
            new_hotkey = self.config.get("hotkey", "F8")
            self.lbl_idle_subtitle.setText(f"Klik tombol mic atau tekan [{new_hotkey}]...")
            if self.btn_mic_start is not None:
                self.btn_mic_start.setToolTip(f"Mulai Merekam (atau tekan {new_hotkey})")
            if self.hotkey_manager is not None:
                self.hotkey_manager.register(new_hotkey)

    def open_about(self):
        """Membuka dialog tentang aplikasi."""
        dlg = AboutDialog(self)
        dlg.exec_()

    # --- Mouse Events untuk Draggable Frameless Window ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
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
        self.focus_manager.apply_no_activate(self)

    def close_application(self):
        """Keluar tuntas dari aplikasi dan menutup system tray."""
        self.close()

    def closeEvent(self, event):
        """Pembersihan bersih dan terminate event loop Qt saat jendela ditutup."""
        if self.worker is not None:
            self.worker.stop()
            self.worker = None
        if self.hotkey_manager is not None:
            self.hotkey_manager.unregister()
        if self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon = None
        event.accept()
        QApplication.quit()
