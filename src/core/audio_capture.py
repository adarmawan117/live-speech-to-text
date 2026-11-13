import queue
import sounddevice as sd
import numpy as np

class AudioCapture:
    """
    Menangkap stream audio real-time dari mikrofon menggunakan sounddevice.
    Format output: 16000 Hz, Mono, float32 (standar format input Whisper).
    """
    def __init__(self, sample_rate: int = 16000, block_size: int = 2048):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_recording = False

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback dieksekusi secara asinkron oleh sounddevice untuk setiap chunk audio."""
        if status:
            pass  # Overflow/underflow logging jika diperlukan
        if self.is_recording:
            # Flatten audio ke 1D array numpy float32
            self.audio_queue.put(indata.copy().flatten())

    def start(self, device_index=None):
        """Memulai stream penangkapan suara."""
        if self.is_recording:
            return
        
        # Kosongkan sisa antrean lama
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.block_size,
            device=device_index,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop(self):
        """Menghentikan penangkapan suara."""
        self.is_recording = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def get_chunk(self, timeout=0.1):
        """Mengambil 1 chunk audio dari queue."""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

