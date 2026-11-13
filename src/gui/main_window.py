import webbrowser
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox,
    QProgressBar, QCheckBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor
from src.core.live_worker import LiveSTTWorker

class MainWindow(QMainWindow):
    """
    Jendela Utama Live Speech to Text.
    Mengikuti panduan arsitektur PyQt5:
    - Inisialisasi atribut eksplisit di __init__
    - Penamaan widget semantik (btn_*, txt_*, lbl_*, dll.)
    - Tanpa setObjectName berlebih dan tanpa hasattr/getattr defensif
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inisialisasi eksplisit seluruh atribut
        self.worker = None
        self.layout_root = None
        self.layout_controls = None
        self.layout_actions = None
        self.layout_options = None
        self.central_widget = None

        self.lbl_title = None
        self.lbl_status = None
        self.lbl_device = None
        self.lbl_credit = None

        self.combo_model = None
        self.combo_language = None
        self.checkbox_auto_copy = None

        self.btn_start = None
        self.btn_stop = None
        self.btn_copy = None
        self.btn_clear = None

        self.progress_audio = None
        self.txt_transcription = None

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Live Speech to Text - ADR Programming")
        self.resize(750, 550)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout_root = QVBoxLayout(self.central_widget)
        self.layout_root.setContentsMargins(15, 15, 15, 15)
        self.layout_root.setSpacing(10)

        # Baris Judul & Status
        self.lbl_title = QLabel("Live Speech to Text", self)
        font_title = QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        self.lbl_title.setFont(font_title)
        self.layout_root.addWidget(self.lbl_title)

        # Pengaturan Model & Bahasa
        self.layout_options = QHBoxLayout()
        self.layout_options.setSpacing(10)

        lbl_model_tag = QLabel("Model:", self)
        self.combo_model = QComboBox(self)
        self.combo_model.addItems(["medium", "small", "base", "tiny"])
        self.combo_model.setCurrentText("medium")  # Prioritas hasil bagus

        lbl_lang_tag = QLabel("Bahasa:", self)
        self.combo_language = QComboBox(self)
        self.combo_language.addItem("Indonesia (id)", "id")
        self.combo_language.addItem("English (en)", "en")
        self.combo_language.addItem("Otomatis (Auto-Detect)", None)

        self.layout_options.addWidget(lbl_model_tag)
        self.layout_options.addWidget(self.combo_model)
        self.layout_options.addWidget(lbl_lang_tag)
        self.layout_options.addWidget(self.combo_language)
        self.layout_options.addStretch()

        self.lbl_device = QLabel("Akselerasi: Menunggu...", self)
        self.layout_options.addWidget(self.lbl_device)

        self.layout_root.addLayout(self.layout_options)

        # Baris Tombol Kontrol (Start & End)
        self.layout_controls = QHBoxLayout()
        self.layout_controls.setSpacing(10)

        self.btn_start = QPushButton("Mulai Mendengarkan (Start)", self)
        self.btn_start.setMinimumHeight(40)
        font_btn = QFont()
        font_btn.setBold(True)
        self.btn_start.setFont(font_btn)

        self.btn_stop = QPushButton("Selesai / Berhenti (End)", self)
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setFont(font_btn)
        self.btn_stop.setEnabled(False)

        self.layout_controls.addWidget(self.btn_start)
        self.layout_controls.addWidget(self.btn_stop)
        self.layout_root.addLayout(self.layout_controls)

        # Level Audio & Status Label
        self.lbl_status = QLabel("Status: Siap (Klik 'Mulai Mendengarkan' untuk mulai bicara)", self)
        self.layout_root.addWidget(self.lbl_status)

        self.progress_audio = QProgressBar(self)
        self.progress_audio.setRange(0, 100)
        self.progress_audio.setValue(0)
        self.progress_audio.setTextVisible(False)
        self.progress_audio.setMaximumHeight(8)
        self.layout_root.addWidget(self.progress_audio)

        # Text Area Hasil Transcribe
        self.txt_transcription = QTextEdit(self)
        font_text = QFont()
        font_text.setPointSize(11)
        self.txt_transcription.setFont(font_text)
        self.txt_transcription.setPlaceholderText("Hasil transkripsi suara Anda akan langsung muncul di sini secara berurutan...")
        self.layout_root.addWidget(self.txt_transcription, stretch=1)

        # Tombol Aksi Tambahan (Salin & Hapus)
        self.layout_actions = QHBoxLayout()
        self.layout_actions.setSpacing(10)

        self.checkbox_auto_copy = QCheckBox("Otomatis salin ke clipboard saat Berhenti", self)
        self.checkbox_auto_copy.setChecked(True)
        self.layout_actions.addWidget(self.checkbox_auto_copy)

        self.layout_actions.addStretch()

        self.btn_copy = QPushButton("Salin Teks (Clipboard)", self)
        self.btn_clear = QPushButton("Bersihkan Teks", self)

        self.layout_actions.addWidget(self.btn_copy)
        self.layout_actions.addWidget(self.btn_clear)
        self.layout_root.addLayout(self.layout_actions)

        # Developer Credit Footer
        self.lbl_credit = QLabel('<a href="https://www.instagram.com/adr_programming/" style="text-decoration:none; color:#555;">Dikembangkan dengan ❤️ oleh ADR Programming</a>', self)
        self.lbl_credit.setAlignment(Qt.AlignCenter)
        self.lbl_credit.setOpenExternalLinks(True)
        self.layout_root.addWidget(self.lbl_credit)

        # Hubungkan Signals & Slots
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_copy.clicked.connect(self.on_copy_clicked)
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        self.combo_model.currentTextChanged.connect(self.on_model_changed)

    def on_model_changed(self, model_name: str):
        """Memberi informasi status ketika pilihan model diubah."""
        self.lbl_status.setText(f"Status: Model '{model_name}' dipilih. Klik 'Mulai Mendengarkan' untuk mulai.")

    def on_start_clicked(self):
        """Memulai sesi perekaman & live STT."""
        if self.worker is not None and self.worker.isRunning():
            return

        model_name = self.combo_model.currentText()
        selected_lang = self.combo_language.currentData()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.combo_model.setEnabled(False)
        self.combo_language.setEnabled(False)
        self.lbl_status.setText(f"Status: Menyiapkan model '{model_name}'...")

        self.worker = LiveSTTWorker(model_size=model_name, language=selected_lang, parent=self)
        self.worker.status_changed.connect(self.on_status_changed)
        self.worker.text_segment_ready.connect(self.on_text_segment_ready)
        self.worker.audio_level.connect(self.on_audio_level)
        self.worker.engine_ready.connect(self.on_engine_ready)
        self.worker.start()

    def on_stop_clicked(self):
        """Menghentikan sesi perekaman & live STT."""
        if self.worker is not None:
            self.lbl_status.setText("Status: Menghentikan & menyelesaikan segmen terakhir...")
            self.worker.stop()
            self.worker = None

        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.combo_model.setEnabled(True)
        self.combo_language.setEnabled(True)
        self.progress_audio.setValue(0)
        self.lbl_status.setText("Status: Selesai")

        # Otomatis salin ke clipboard jika dicentang
        if self.checkbox_auto_copy.isChecked():
            self.on_copy_clicked()

    def on_status_changed(self, status_text: str):
        self.lbl_status.setText(f"Status: {status_text}")

    def on_engine_ready(self, device_text: str):
        self.lbl_device.setText(f"Akselerasi: {device_text}")

    def on_audio_level(self, level: float):
        try:
            val = int(max(0.0, min(1.0, level)) * 100)
            self.progress_audio.setValue(val)
        except Exception:
            pass

    def on_text_segment_ready(self, text: str):
        """Menambahkan teks hasil transkripsi ke text area secara rapi."""
        current_text = self.txt_transcription.toPlainText().strip()
        if current_text:
            new_text = current_text + " " + text
        else:
            new_text = text

        self.txt_transcription.setPlainText(new_text)
        cursor = self.txt_transcription.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.txt_transcription.setTextCursor(cursor)

    def on_copy_clicked(self):
        """Menyalin teks hasil transcribe ke clipboard sistem."""
        text = self.txt_transcription.toPlainText().strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.lbl_status.setText("Status: Teks berhasil disalin ke clipboard! Siap dipaste ke pesan.")

    def on_clear_clicked(self):
        """Bersihkan text area."""
        self.txt_transcription.clear()
        self.lbl_status.setText("Status: Teks dibersihkan.")

    def closeEvent(self, event):
        """Pastikan worker dihentikan saat jendela ditutup."""
        if self.worker is not None:
            self.worker.stop()
            self.worker = None
        event.accept()
