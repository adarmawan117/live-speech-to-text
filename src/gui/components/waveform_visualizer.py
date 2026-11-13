import math
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen

class WaveformVisualizer(QWidget):
    """
    Widget visualizer animasi gelombang audio berbentuk bar cyan neon
    seperti pada desain mode perekaman.
    """
    def __init__(self, num_bars: int = 19, parent=None):
        super().__init__(parent)
        self.num_bars = num_bars
        self.audio_level = 0.0
        self.phase = 0.0
        self.is_active = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.setMinimumHeight(65)
        self.setMaximumHeight(80)

    def start(self):
        """Memulai animasi gelombang."""
        self.is_active = True
        self.timer.start(33)  # ~30 FPS

    def stop(self):
        """Menghentikan animasi gelombang dan meratakan bar."""
        self.is_active = False
        self.timer.stop()
        self.audio_level = 0.0
        self.update()

    def set_level(self, level: float):
        """Mengatur level input audio (0.0 sampai 1.0)."""
        # Smoothing level
        self.audio_level = self.audio_level * 0.4 + level * 0.6

    def _on_tick(self):
        self.phase += 0.2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height / 2.0

        bar_width = 3.5
        spacing = (width - 40) / max(1, self.num_bars - 1)
        start_x = 20

        # Profil bell-curve (tengah lebih tinggi, samping lebih rendah)
        mid_idx = (self.num_bars - 1) / 2.0

        base_color = QColor("#00d2ff")
        glow_color = QColor(0, 210, 255, 60)

        for i in range(self.num_bars):
            # Faktor posisi gaussian dari tengah
            dist = abs(i - mid_idx) / mid_idx
            gaussian = math.exp(-2.2 * (dist ** 2))

            if self.is_active:
                wave = math.sin(self.phase + i * 0.4) * 0.25 + 0.75
                h = 8 + (height - 20) * gaussian * (self.audio_level * 0.7 + 0.3) * wave
            else:
                h = 4 + 6 * gaussian

            h = max(4.0, min(height - 8, h))

            x = start_x + i * spacing - bar_width / 2.0
            y = center_y - h / 2.0

            # Gambar glow effect
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawRoundedRect(int(x - 1), int(y - 1), int(bar_width + 2), int(h + 2), 2, 2)

            # Gambar bar utama
            painter.setBrush(QBrush(base_color))
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(h), 1.5, 1.5)

        painter.end()
