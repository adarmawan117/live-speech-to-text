import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from src.core.audio_capture import AudioCapture
from src.core.stt_engine import get_stt_engine

class LiveSTTWorker(QThread):
    """
    Worker background QThread yang menangkap audio real-time dan melakukan
    deteksi jeda bicara (voice activity detection), lalu mentranskripsikannya
    menggunakan STTEngine tanpa memblokir GUI.
    """
    status_changed = pyqtSignal(str)
    text_segment_ready = pyqtSignal(str)
    audio_level = pyqtSignal(float)
    engine_ready = pyqtSignal(str)

    def __init__(self, model_size: str = "medium", language: str = "id", parent=None):
        super().__init__(parent)
        self.model_size = model_size
        self.language = language
        self.audio_capture = None
        self.engine = None
        self.is_running = False
        self.silence_threshold = 0.015  # Ambang batas energi suara (RMS)
        self.silence_limit_sec = 0.8     # Jeda hening sebelum transkripsi dipicu
        self.max_phrase_sec = 15.0       # Batas durasi frase sebelum dipaksa transkripsi

    def run(self):
        self.is_running = True
        try:
            self.status_changed.emit(f"Menyiapkan model Whisper '{self.model_size}'...")
            self.engine = get_stt_engine(model_size=self.model_size, language=self.language)
            
            # Jika user sudah menekan Stop saat model sedang disiapkan
            if not self.is_running:
                return

            self.engine_ready.emit(self.engine.active_device)

            self.audio_capture = AudioCapture(sample_rate=16000, block_size=2048)
            self.audio_capture.start()
            self.status_changed.emit("Mendengarkan suara...")

            speech_buffer = []
            silence_start_time = None
            is_speaking = False
            phrase_start_time = None

            sample_rate = 16000

            while self.is_running:
                chunk = self.audio_capture.get_chunk(timeout=0.05)
                if chunk is None:
                    continue

                # Hitung RMS energi suara
                sq_mean = np.mean(chunk**2)
                rms = float(np.sqrt(sq_mean)) if sq_mean >= 0 else 0.0
                if np.isnan(rms):
                    rms = 0.0

                self.audio_level.emit(min(rms * 10, 1.0))

                current_time = time.time()

                if rms > self.silence_threshold:
                    if not is_speaking:
                        is_speaking = True
                        phrase_start_time = current_time
                    silence_start_time = None
                    speech_buffer.append(chunk)
                else:
                    if is_speaking:
                        speech_buffer.append(chunk)
                        if silence_start_time is None:
                            silence_start_time = current_time
                        elif (current_time - silence_start_time) >= self.silence_limit_sec:
                            # Jeda bicara terdeteksi! Lakukan transkripsi
                            self._process_speech_buffer(speech_buffer, sample_rate)
                            speech_buffer = []
                            is_speaking = False
                            silence_start_time = None

                # Jika pengguna bicara tanpa henti melebihi batas waktu, potong sebagian
                if is_speaking and phrase_start_time and (current_time - phrase_start_time) >= self.max_phrase_sec:
                    self._process_speech_buffer(speech_buffer, sample_rate)
                    speech_buffer = []
                    phrase_start_time = current_time
                    silence_start_time = None

            # Jika dihentikan dan masih ada sisa buffer bicara
            if speech_buffer and self.is_running:
                self._process_speech_buffer(speech_buffer, sample_rate)

        except Exception as e:
            print(f"Error pada thread LiveSTTWorker: {e}", flush=True)
            self.status_changed.emit(f"Error: {e}")
        finally:
            if self.audio_capture is not None:
                self.audio_capture.stop()
                self.audio_capture = None
            self.status_changed.emit("Siap")

    def _process_speech_buffer(self, buffer_chunks, sample_rate):
        if not buffer_chunks or self.engine is None:
            return

        total_audio = np.concatenate(buffer_chunks)
        duration = len(total_audio) / sample_rate

        # Abaikan noise klik / batuk singkat di bawah 0.4 detik
        if duration < 0.4:
            return

        self.status_changed.emit("Mentranskripsikan...")
        try:
            text = self.engine.transcribe_audio(total_audio)
            if text:
                self.text_segment_ready.emit(text)
        except Exception as e:
            print(f"Error transkripsi: {e}", flush=True)
        finally:
            if self.is_running:
                self.status_changed.emit("Mendengarkan suara...")

    def stop(self):
        """Menghentikan worker secara aman dan non-blocking."""
        self.is_running = False
        # Gunakan timeout wait 1500ms agar GUI tidak pernah freeze
        if not self.wait(1500):
            try:
                self.terminate()
            except Exception:
                pass
