import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")

DEFAULT_CONFIG = {
    "hotkey": "F8",
    "model_size": "small",
    "language": "id",
    "audio_device": None,
    "typing_mode": "streaming",  # 'streaming' (per-kata) atau 'sentence' (per-kalimat)
    "auto_stop_timeout_sec": 60  # Batas waktu hening (detik) sebelum auto-stop
}

def load_config() -> dict:
    """Memuat konfigurasi dari config.json atau mengembalikan konfigurasi default."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> bool:
    """Menyimpan konfigurasi ke config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception:
        return False

