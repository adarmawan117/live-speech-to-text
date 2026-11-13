from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    """
    Dialog Informasi Aplikasi & Kredit Pengembang bertema dark modern.
    Mengikuti aturan developer_credit.md.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tentang - Live Speech to Text")
        self.setFixedSize(320, 240)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d131f;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #c7d2e3;
            }
            QPushButton {
                background-color: #162035;
                color: #ffffff;
                border: 1px solid #2a3b5c;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1b68ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_app = QLabel("<b>Live Speech to Text</b>", self)
        lbl_app.setStyleSheet("font-size: 16px; color: #ffffff;")
        lbl_app.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_app)

        lbl_desc = QLabel("Aplikasi pengetikan suara instan (Voice Typing) ke kursor aktif Windows bertenaga Whisper AI.", self)
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet("font-size: 11px; color: #8fa0bc;")
        layout.addWidget(lbl_desc)

        layout.addSpacing(10)

        # Developer Credit Rule: Dikembangkan dengan ❤️ oleh ADR Programming
        lbl_credit = QLabel('<a href="https://www.instagram.com/adr_programming/" style="text-decoration:none; color:#00d2ff; font-weight:bold; font-size:12px;">Dikembangkan dengan ❤️ oleh ADR Programming</a>', self)
        lbl_credit.setAlignment(Qt.AlignCenter)
        lbl_credit.setOpenExternalLinks(True)
        layout.addWidget(lbl_credit)

        layout.addStretch()

        btn_ok = QPushButton("Tutup", self)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignCenter)
