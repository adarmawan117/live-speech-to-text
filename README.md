# Live Speech to Text (Floating Voice Typing)

Aplikasi Desktop Floating Helper untuk pengetikan suara (*Voice Typing*) langsung ke kursor aktif di aplikasi apa pun (WhatsApp, Telegram, Microsoft Word, Chrome, Notepad, Discord, dll.) secara *real-time* bertenaga Whisper AI dan akselerasi GPU NVIDIA RTX.

---

## Fitur Utama

- **Floating & Always on Top**:
  - Jendela ringkas melayang (*frameless & draggable*) yang selalu berada di atas jendela lain.
  - Desain modern bernuansa *Dark Navy* dengan sudut membulat elegan.
  - Dilengkapi animasi gelombang suara (*cyan neon waveform visualizer*) yang bergerak dinamis saat Anda berbicara.
- **Direct Typing ke Kursor Aktif**:
  - Mengetikkan kata-kata langsung ke posisi kursor yang sedang aktif di aplikasi lain tanpa perlu copy-paste.
  - Menggunakan algoritma *differential typing* cerdas berbasis *Longest Common Prefix* untuk meminimalkan penekanan tombol backspace jika ada revisi kata dari Whisper.
- **Pembersihan Tanda Baca Cerdas**:
  - Tanda baca otomatis yang dihasilkan oleh Whisper (seperti titik, koma, tanda tanya, tanda seru yang tidak diinginkan) otomatis dihilangkan.
  - Tanda hubung pada kata ulang bahasa Indonesia (misal: `teman-teman`, `jalan-jalan`) tetap dipertahankan.
- **Global Hotkey (Shortcut Bebas Sentuh Mouse)**:
  - Tekan tombol **`F8`** (atau tombol shortcut lain yang dikonfigurasi) dari aplikasi mana saja untuk langsung Mulai (*Start*) atau Berhenti (*End*) merekam tanpa kehilangan fokus kursor.
- **Popup Pengaturan Terpadu (Ikon ⚙)**:
  - Ganti tombol Shortcut Global (`F8`, `F9`, `F10`, `F12`, `Ctrl+Shift+Space`, dll).
  - Pilih Model Whisper (`small`, `base`, `medium`, `tiny`).
  - Pilih Bahasa (`id`, `en`, `auto`).
  - Pilih Perangkat Mikrofon yang diinginkan.
  - Pilih Mode Pengetikan (*Streaming per-kata* atau *Per-penggalan kalimat*).
- **Akselerasi GPU Mandiri (NVIDIA CUDA)**:
  - Latensi super instan di kartu grafis NVIDIA RTX (misal RTX 3050): hanya ~44ms (model `base`) dan ~140ms (model `small`).
  - Paket cuBLAS & cuDNN terpasang mandiri di virtual environment tanpa perlu instalasi CUDA Toolkit global.

---

## Struktur Folder Project

```text
live-speech-to-text/
├── main.py                             # Entry point aplikasi
├── run.bat                             # Script batch sekali klik untuk menjalankan aplikasi
├── requirements.txt                    # Daftar dependensi lengkap
├── README.md                           # Dokumentasi project
└── src/
    ├── core/
    │   ├── audio_capture.py            # Modul stream mikrofon (sounddevice)
    │   ├── config_manager.py           # Pengelola file konfigurasi config.json
    │   ├── cuda_setup.py               # Pengatur path DLL CUDA/cuDNN mandiri
    │   ├── focus_manager.py            # Manajemen fokus jendela & WS_EX_NOACTIVATE
    │   ├── hotkey_manager.py           # Pendengar shortcut keyboard global
    │   ├── live_worker.py              # QThread worker streaming per-kata & auto-commit
    │   ├── stt_engine.py               # Engine faster-whisper (transkripsi interim & final)
    │   ├── text_cleaner.py             # Pembersih tanda baca otomatis STT
    │   └── virtual_typist.py           # Pengetik virtual ke kursor aktif
    └── gui/
        ├── components/
        │   └── waveform_visualizer.py  # Animasi visualizer audio neon cyan
        ├── dialogs/
        │   ├── about_dialog.py         # Dialog tentang aplikasi & kredit pengembang
        │   └── settings_dialog.py      # Dialog popup pengaturan hotkey & audio
        ├── floating_window.py          # Jendela utama Floating App (Dual-State)
        └── main_window.py              # Jendela alternatif mode standalone
```

---

## Cara Menjalankan

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

1. Buka aplikasi via `run.bat`. Jendela melayang kecil akan tampil di layar Anda.
2. Posisikan kursor Anda di tempat Anda ingin mengetik (misal: kolom chat WhatsApp atau dokumen Word).
3. Mulai merekam dengan salah satu cara berikut:
   - Tekan tombol keyboard **`F8`** (kursor tetap aktif di aplikasi target).
   - Atau klik tombol **`▶ Start`** pada Floating App.
4. Tampilan aplikasi akan beralih ke mode **`Listening...`** dengan visualizer gelombang suara aktif.
5. Mulailah berbicara. Kata-kata yang Anda ucapkan akan langsung terketik secara *real-time* tepat di posisi kursor Anda.
6. Untuk berhenti, tekan tombol **`F8`** lagi atau klik tombol **`■ End`**.
7. Klik ikon gerigi (⚙) di pojok kiri bawah untuk mengatur shortcut, model, bahasa, atau mikrofon sesuai kenyamanan Anda.

---

Dikembangkan dengan ❤️ oleh [ADR Programming](https://www.instagram.com/adr_programming/)
