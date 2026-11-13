import os
import sys

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np
from src.core.cuda_setup import setup_cuda_environment
setup_cuda_environment()

import ctranslate2
from faster_whisper import WhisperModel
from src.core.text_cleaner import clean_stt_punctuation

_ENGINE_CACHE = {}

def get_stt_engine(model_size: str = "small", language: str = "id") -> "STTEngine":
    """Mengambil atau membuat engine STT dari cache agar tidak reload model berkali-kali."""
    key = (model_size, language)
    if key not in _ENGINE_CACHE:
        _ENGINE_CACHE[key] = STTEngine(model_size=model_size, language=language)
    return _ENGINE_CACHE[key]

class STTEngine:
    """
    Engine Speech to Text menggunakan faster-whisper dengan akselerasi GPU (CUDA)
    dan fallback otomatis ke CPU. Menghasilkan teks murni tanpa tanda baca otomatis.
    """
    def __init__(self, model_size: str = "small", device: str = "auto", language: str = "id"):
        setup_cuda_environment()
        self.model_size = model_size
        self.device = device
        self.language = language
        self.model = None
        self.active_device = "cpu"
        self._load_model()

    def _load_model(self):
        """Memuat model Whisper dengan prioritas GPU CUDA."""
        if self.device in ("auto", "cuda"):
            try:
                print(f"Memuat model Whisper '{self.model_size}' pada GPU (CUDA float16)...", flush=True)
                self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
                self.active_device = "cuda (GPU)"
                print(f"Model '{self.model_size}' siap di GPU CUDA!", flush=True)
                return
            except Exception as e:
                print(f"Gagal inisialisasi CUDA ({e}). Menggunakan CPU...", flush=True)

        threads = min(os.cpu_count() or 4, 6)
        print(f"Memuat model Whisper '{self.model_size}' pada CPU (int8, threads={threads})...", flush=True)
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8", cpu_threads=threads)
        self.active_device = f"cpu ({threads} threads)"

    def transcribe_interim(self, audio_data: np.ndarray) -> str:
        """
        Transkripsi super cepat (beam_size=1) untuk streaming kata demi kata.
        Tanda baca otomatis langsung dihilangkan.
        """
        if self.model is None or len(audio_data) == 0:
            return ""

        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        transcribe_kwargs = {
            "beam_size": 1,
            "vad_filter": False,
            "without_timestamps": True,
            "no_speech_threshold": 0.6
        }
        if self.language:
            transcribe_kwargs["language"] = self.language

        try:
            segments, _ = self.model.transcribe(audio_data, **transcribe_kwargs)
            texts = [s.text.strip() for s in segments if s.no_speech_prob < 0.6 and s.text.strip()]
            raw_text = " ".join(texts)
            return clean_stt_punctuation(raw_text)
        except Exception:
            return ""

    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transkripsi final saat jeda bicara (beam_size=3 dengan VAD filter).
        Tanda baca otomatis langsung dihilangkan.
        """
        if self.model is None or len(audio_data) == 0:
            return ""

        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        transcribe_kwargs = {
            "beam_size": 3,
            "vad_filter": True,
            "vad_parameters": dict(min_silence_duration_ms=300),
            "without_timestamps": True
        }
        if self.language:
            transcribe_kwargs["language"] = self.language

        try:
            segments, _ = self.model.transcribe(audio_data, **transcribe_kwargs)
            texts = [s.text.strip() for s in segments if s.text.strip()]
            raw_text = " ".join(texts)
            return clean_stt_punctuation(raw_text)
        except Exception:
            return ""
