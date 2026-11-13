import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from src.core.audio_capture import AudioCapture
from src.core.stt_engine import get_stt_engine

class LiveSTTWorker(QThread):
    """
    Worker background QThread streaming audio real-time:
    - Menghasilkan live interim transcription per-kata saat pengguna sedang bicara.
    - Mengunci kalimat (final commit) ketika mendeteksi jeda napas/berhenti bicara.
    """
    status_changed = pyqtSignal(str)
    interim_text_ready = pyqtSignal(str)   # Kata-kata live yang sedang diucapkan
    final_text_ready = pyqtSignal(str)     # Kalimat yang sudah selesai/dikunci
    audio_level = pyqtSignal(float)
    engine_ready = pyqtSignal(str)
    auto_timeout = pyqtSignal()            # Dipicu jika 60 detik tidak ada input suara

    def __init__(self, model_size: str = "small", language: str = "id", timeout_sec: float = 60.0, parent=None):
        super().__init__(parent)
        self.model_size = model_size
        self.language = language
        self.no_speech_timeout_sec = float(timeout_sec)
        self.audio_capture = None
        self.engine = None
        self.is_running = False
        self.silence_threshold = 0.015   # Ambang batas energi suara (RMS)
        self.silence_limit_sec = 0.75     # Jeda hening sebelum kalimat dikunci
        self.interim_interval_sec = 0.35  # Interval pembaruan preview per-kata (~350ms)
        self.max_phrase_sec = 12.0        # Batas durasi frase maksimal sebelum dipotong

    def run(self):
        self.is_running = True
        try:
            self.status_changed.emit(f"Menyiapkan model Whisper '{self.model_size}'...")
            self.engine = get_stt_engine(model_size=self.model_size, language=self.language)

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
            last_interim_time = 0.0
            last_interim_text = ""
            last_speech_time = time.time()  # Waktu terakhir terdeteksi input suara

            sample_rate = 16000

            while self.is_running:
                chunk = self.audio_capture.get_chunk(timeout=0.04)
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
                    last_speech_time = current_time
                    if not is_speaking:
                        is_speaking = True
                        phrase_start_time = current_time
                    silence_start_time = None
                    speech_buffer.append(chunk)

                    # Pembaruan streaming per-kata (Interim Preview)
                    if (current_time - last_interim_time) >= self.interim_interval_sec:
                        last_interim_time = current_time
                        total_audio = np.concatenate(speech_buffer)
                        # Hanya proses jika durasi suara sudah minimal ~0.25 detik
                        if len(total_audio) / sample_rate >= 0.25:
                            interim = self.engine.transcribe_interim(total_audio)
                            if interim:
                                last_interim_text = interim
                                self.interim_text_ready.emit(interim)

                else:
                    if is_speaking:
                        speech_buffer.append(chunk)
                        if silence_start_time is None:
                            silence_start_time = current_time
                        elif (current_time - silence_start_time) >= self.silence_limit_sec:
                            # Pengguna berhenti bicara sejenak -> Kunci kalimat (Final Commit)
                            self._commit_phrase(speech_buffer, sample_rate, last_interim_text)
                            speech_buffer = []
                            is_speaking = False
                            silence_start_time = None
                            last_interim_text = ""
                            self.interim_text_ready.emit("")

                    # Cek batas waktu hening tanpa suara (Auto-Timeout 60 detik)
                    elif (current_time - last_speech_time) >= self.no_speech_timeout_sec:
                        print(f"[LiveSTTWorker] Auto-timeout tercapai ({self.no_speech_timeout_sec}s hening). Menghentikan engine...", flush=True)
                        self.status_changed.emit("Otomatis berhenti: tidak ada input suara selama 1 menit.")
                        self.auto_timeout.emit()
                        break

                # Jika pengguna bicara tanpa henti melebihi durasi batas, kunci segmen
                if is_speaking and phrase_start_time and (current_time - phrase_start_time) >= self.max_phrase_sec:
                    self._commit_phrase(speech_buffer, sample_rate, last_interim_text)
                    speech_buffer = []
                    phrase_start_time = current_time
                    silence_start_time = None
                    last_interim_text = ""
                    self.interim_text_ready.emit("")

            # Jika worker dihentikan dan masih ada sisa buffer bicara
            if speech_buffer:
                self._commit_phrase(speech_buffer, sample_rate, last_interim_text)
                self.interim_text_ready.emit("")

        except Exception as e:
            print(f"Error pada thread LiveSTTWorker: {e}", flush=True)
            self.status_changed.emit(f"Error: {e}")
        finally:
            if self.audio_capture is not None:
                self.audio_capture.stop()
                self.audio_capture = None
            self.status_changed.emit("Siap")

    def _commit_phrase(self, buffer_chunks, sample_rate, fallback_text):
        """Memproses transkripsi final untuk mengunci kalimat."""
        if not buffer_chunks or self.engine is None:
            return

        total_audio = np.concatenate(buffer_chunks)
        duration = len(total_audio) / sample_rate

        if duration < 0.35:
            return

        try:
            final_text = self.engine.transcribe_audio(total_audio)
            # Jika transkripsi final kosong (misal terfilter VAD), gunakan teks interim terakhir
            commit_text = final_text if final_text else fallback_text
            if commit_text:
                self.final_text_ready.emit(commit_text)
        except Exception as e:
            print(f"Error saat commit transkripsi: {e}", flush=True)
            if fallback_text:
                self.final_text_ready.emit(fallback_text)

    def stop(self):
        """Menghentikan worker secara aman dan non-blocking."""
        self.is_running = False
        if not self.wait(1500):
            try:
                self.terminate()
            except Exception:
                pass
