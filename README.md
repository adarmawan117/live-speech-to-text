# Live Speech to Text (STT)

Aplikasi Desktop Helper untuk transkripsi suara langsung menjadi teks secara *real-time* (*Voice Typing*) dengan pemrosesan kata demi kata secara mengalir seperti fitur pengetikan suara di smartphone. Dirancang agar Anda tidak perlu mengetik manual panjang lebar saat ingin mengirim pesan ke orang lain di WhatsApp, Telegram, email, maupun platform lainnya.

---

## Fitur Utama

- **Real-Time Streaming STT (Per-Kata / Interim Preview)**: Kata-kata yang Anda ucapkan langsung muncul seketika di layar tanpa perlu menunggu Anda berhenti bicara.
- **Auto-Commit Sentence (VAD)**: Begitu Anda jeda atau berhenti bicara sejenak (~0.7 detik), kalimat tersebut otomatis dikunci (*committed*) dan sistem langsung siap untuk kalimat berikutnya.
- **Murni Speech to Text (STT)**: Menghasilkan teks bersih tanpa penanda waktu (*timestamp*), siap langsung dikirim sebagai pesan.
- **Akselerasi GPU Mandiri (NVIDIA CUDA)**:
  - Mendukung GPU NVIDIA RTX (seperti RTX 3050) dengan komputasi `float16` berkecepatan tinggi (~140ms di model `small`, ~44ms di model `base`).
  - Dilengkapi library cuBLAS & cuDNN terintegrasi di virtual environment tanpa perlu instalasi CUDA Toolkit global yang rumit.
  - Fallback otomatis ke CPU (`int8`) jika dijalankan pada perangkat tanpa GPU NVIDIA.
- **Pilihan Model & Bahasa Fleksibel**:
  - Model Whisper: `small` (default, sangat responsif & akurat), `base` (ultra-cepat), `medium` (presisi tinggi), atau `tiny`.
  - Pilihan bahasa: Bahasa Indonesia (`id`), Bahasa Inggris (`en`), atau deteksi otomatis (`auto`).
- **Fitur Salin Cepat (Clipboard)**:
  - Opsi *Otomatis salin ke clipboard saat Berhenti*.
  - Tombol manual *Salin Teks (Clipboard)* untuk memudahkan *paste* instan (`Ctrl+V`) ke aplikasi chat.
- **Antarmuka Bersih & Responsif**:
  - GUI PyQt5 yang ringan dengan tombol *Start* (Mulai) dan *End* (Selesai).
  - Indikator bar level input suara untuk memastikan mic aktif.

---

## Struktur Folder Project

```text
live-speech-to-text/
├── main.py                     # Entry point aplikasi
├── run.bat                     # Script batch sekali klik untuk menjalankan aplikasi
├── requirements.txt            # Daftar dependensi lengkap
├── README.md                   # Dokumentasi project
└── src/
    ├── core/
    │   ├── audio_capture.py    # Modul stream mikrofon (sounddevice)
    │   ├── cuda_setup.py       # Pengatur path DLL CUDA/cuDNN mandiri
    │   ├── live_worker.py      # QThread worker streaming per-kata & auto-commit
    │   └── stt_engine.py       # Engine faster-whisper (transkripsi interim & final)
    └── gui/
        └── main_window.py      # Antarmuka GUI PyQt5
```

---

## Persyaratan Sistem

- **OS**: Windows 10 / 11 (64-bit)
- **Python**: Versi 3.10 – 3.13
- **Hardware**:
  - Mikrofon (internal atau eksternal)
  - Kartu grafis NVIDIA RTX / GTX (Sangat direkomendasikan untuk transkripsi instan dengan GPU) atau CPU multi-core.

---

## Cara Instalasi & Menjalankan

### 1. Buat Virtual Environment & Install Dependensi
Buka terminal / PowerShell di folder project ini:

```powershell
# 1. Buat virtual environment
python -m venv venv

# 2. Install seluruh dependensi
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Menjalankan Aplikasi
Cukup klik ganda (double-click) file:
```text
run.bat
```
Atau melalui terminal:
```powershell
.\venv\Scripts\python.exe main.py
```

---

## Panduan Penggunaan

1. Buka aplikasi via `run.bat`.
2. Model default yang dipilih adalah `small` (sangat direkomendasikan untuk streaming kata-per-kata yang cepat dan akurat).
3. Pastikan bahasa terpilih adalah `Indonesia (id)`.
4. Klik tombol **Mulai Mendengarkan (Start)**.
5. Mulailah berbicara ke mikrofon. Kata-kata yang Anda ucapkan akan langsung muncul seketika secara mengalir di layar.
6. Saat Anda berhenti bicara sejenak, kalimat otomatis dikunci.
7. Setelah selesai seluruh pesan, klik tombol **Selesai / Berhenti (End)**.
8. Teks secara otomatis disalin ke clipboard, Anda tinggal menekan `Ctrl + V` pada aplikasi chat.

---

Dikembangkan dengan ❤️ oleh [ADR Programming](https://www.instagram.com/adr_programming/)
