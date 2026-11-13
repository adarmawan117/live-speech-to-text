# Live Speech to Text (Floating Voice Typing)

Aplikasi Desktop Floating Helper untuk pengetikan suara (*Voice Typing*) langsung ke kursor aktif di aplikasi apa pun (WhatsApp, Telegram, Microsoft Word, Chrome, Notepad, Discord, dll.) secara *real-time* bertenaga Whisper AI dan akselerasi GPU NVIDIA RTX.

---

## Fitur Utama

- **Hero Mic Button Interaktif**:
  - Tombol mikrofon melingkar modern (`86 × 86 px`) tepat di tengah jendela menggantikan tombol konvensional, dilengkapi efek hover gradien biru menyala dan tooltip hotkey dinamis.
- **Floating & Always on Top**:
  - Jendela ringkas melayang (*frameless & draggable*) yang selalu berada di atas jendela lain.
  - Desain modern bernuansa *Dark Navy* dengan sudut membulat elegan.
  - Ikon aplikasi vektor premium SVG tajam tanpa pixelation.
  - Dilengkapi animasi gelombang suara (*cyan neon waveform visualizer*) yang bergerak dinamis saat Anda berbicara.
- **System Tray & Minimize Protection**:
  - Minimize otomatis menyembunyikan aplikasi ke System Tray (Taskbar pojok kanan).
  - **Proteksi Rekam**: Aplikasi dilarang / tidak bisa diminimize saat fitur transkripsi sedang aktif (*Start*). Minimize hanya dapat dilakukan saat mode santai/idle.
  - Klik atau double-click icon tray untuk menampilkan kembali jendela.
- **Single Instance Application**:
  - Mencegah aplikasi terbuka ganda. Jika aplikasi sedang berjalan dan pengguna membukanya kembali (misal dari shortcut Desktop atau Start Menu), aplikasi tidak akan membuka jendela baru melainkan otomatis mengaktifkan dan memunculkan kembali jendela yang sedang berjalan ke layar depan via IPC Windows Named Pipe.
- **Direct Typing ke Kursor Aktif**:
  - Mengetikkan kata-kata langsung ke posisi kursor yang sedang aktif di aplikasi lain tanpa perlu copy-paste.
  - Menggunakan algoritma *differential typing* cerdas berbasis *Longest Common Prefix* untuk meminimalkan penekanan tombol backspace jika ada revisi kata dari Whisper.
- **Pembersihan Tanda Baca Cerdas**:
  - Tanda baca otomatis yang dihasilkan oleh Whisper (seperti titik, koma, tanda tanya, tanda seru yang tidak diinginkan) otomatis dihilangkan.
  - Tanda hubung pada kata ulang bahasa Indonesia (misal: `teman-teman`, `jalan-jalan`) tetap dipertahankan.
- **Global Hotkey (Shortcut Bebas Sentuh Mouse)**:
  - Tekan tombol **`F8`** (atau tombol shortcut lain yang dikonfigurasi) dari aplikasi mana saja untuk langsung Mulai (*Start*) atau Berhenti (*End*) merekam tanpa kehilangan fokus kursor.
- **Auto-Stop Timeout Hemat Resource**:
  - Jika selama 1 menit (60 detik) tidak ada input suara yang terdeteksi, engine transkripsi otomatis berhenti (*End*), visualizer berhenti, jendela kembali ke mode idle, dan notifikasi balon tray muncul. Fitur ini mencegah GPU/CPU bekerja terus-menerus jika pengguna lupa menekan tombol Stop.
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
├── .docs/
│   └── AI_CONTEXT.md                   # Panduan teknis komprehensif untuk AI Agent
├── assets/
│   ├── icon.ico                        # Ikon aplikasi multi-resolusi Windows
│   ├── icon.png                        # Asset PNG ikon cyan mic badge
│   ├── chevron_down.png                # Panah dropdown anti-aliased
│   ├── radio_checked.png               # Indikator radio button aktif
│   └── radio_unchecked.png             # Indikator radio button nonaktif
├── main.py                             # Entry point utama aplikasi (Single Instance & CUDA setup)
├── run.bat                             # Launcher terminal CMD (auto-close exit code 0)
├── Live Speech to Text.vbs             # Launcher hening tanpa jendela hitam CMD
├── Setup.bat                           # Installer shortcut 1-klik ke Desktop & Start Menu
├── build_installer.bat                 # Script kompilasi installer Inno Setup (.exe)
├── installer.iss                       # Blueprint Inno Setup 6 compiler
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
    │   ├── single_instance.py          # IPC Single Instance controller (Windows Named Pipe)
    │   ├── stt_engine.py               # Engine faster-whisper (transkripsi interim & final)
    │   ├── text_cleaner.py             # Pembersih tanda baca otomatis STT
    │   └── virtual_typist.py           # Pengetik virtual ke kursor aktif (LCP)
    └── gui/
        ├── components/
        │   ├── icons.py                # Generator ikon vektor inline SVG murni
        │   └── waveform_visualizer.py  # Animasi visualizer audio neon cyan
        ├── dialogs/
        │   ├── about_dialog.py         # Dialog tentang aplikasi & kredit pengembang ADR Programming
        │   └── settings_dialog.py      # Dialog popup pengaturan hotkey & audio
        └── floating_window.py          # Jendela utama Floating App (Dual-State) + System Tray
```

---

## Instalasi & Cara Menjalankan

### 1. Instalasi Shortcut Instan (Disarankan)
Cukup jalankan file:
```text
Setup.bat
```
Script ini akan otomatis membuat:
- Shortcut di **Desktop**: `Live Speech to Text.lnk` dengan ikon mikrofon cyan.
- Shortcut di **Start Menu**: Folder `ADR Programming > Live Speech to Text`.
- Menjalankan aplikasi langsung tanpa menampilkan konsol CMD hitam (via `Live Speech to Text.vbs`).

### 2. Menjalankan Manual
- Klik ganda file `Live Speech to Text.vbs` (tanpa jendela konsol hitam CMD).
- Atau klik ganda `run.bat` (dengan tampilan konsol untuk diagnosa).
- Atau via terminal:
```powershell
.\venv\Scripts\python.exe main.py
```

### 3. Build Installer Setup (.exe)
Jika ingin membuat file installer Inno Setup `.exe`:
```text
build_installer.bat
```
File installer setup mandiri akan dibuat di folder `Output\LiveSpeechToText_Setup.exe`.

---

## Panduan Penggunaan

1. Buka aplikasi via `run.bat`. Jendela melayang kecil akan tampil di layar Anda.
2. Posisikan kursor Anda di tempat Anda ingin mengetik (misal: kolom chat WhatsApp atau dokumen Word).
3. Mulai merekam dengan salah satu cara berikut:
   - Tekan tombol keyboard **`F8`** (kursor tetap aktif di aplikasi target).
   - Atau klik **tombol mikrofon besar** di tengah Floating App.
4. Tampilan aplikasi akan beralih ke mode **`Listening...`** dengan visualizer gelombang suara aktif.
5. Mulailah berbicara. Kata-kata yang Anda ucapkan akan langsung terketik secara *real-time* tepat di posisi kursor Anda.
6. Untuk berhenti, tekan tombol **`F8`** lagi atau klik tombol **`■ End`**.
7. Klik ikon gerigi (⚙) di pojok kiri bawah untuk mengatur shortcut, model, bahasa, atau mikrofon sesuai kenyamanan Anda.
8. **Minimize ke System Tray**: Klik tombol minimize (`—`) di pojok kanan atas jendela saat mode idle. Jendela akan tersembunyi ke System Tray. Anda tetap bisa menekan `F8` kapan saja dari aplikasi mana pun untuk langsung merekam, atau klik icon tray untuk memunculkan kembali jendela ke layar.
9. **Proteksi Rekam**: Saat sedang merekam suara (*Listening...*), tombol minimize otomatis dinonaktifkan untuk mencegah jendela terminimize secara tidak sengaja di tengah sesi transkripsi.
10. **Auto-Stop Hemat Baterai & Daya**: Jika Anda lupa menekan tombol `End` setelah selesai berbicara, sistem otomatis menghentikan engine transkripsi setelah 1 menit hening untuk melepaskan beban GPU/CPU komputer Anda.

---

Dikembangkan dengan ❤️ oleh [ADR Programming](https://www.instagram.com/adr_programming/)
