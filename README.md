# Live Speech to Text (Floating Voice Typing)

Aplikasi Desktop Floating Helper untuk pengetikan suara (*Voice Typing*) langsung ke kursor aktif di aplikasi apa pun (WhatsApp, Telegram, Microsoft Word, Chrome, Notepad, Discord, dll.) secara *real-time* bertenaga Whisper AI dan akselerasi GPU NVIDIA RTX.

---

## Fitur Utama

- **Hero Mic Button Interaktif**:
  - Tombol mikrofon melingkar modern (`86 × 86 px`) tepat di tengah jendela menggantikan tombol konvensional, dilengkapi efek hover gradien biru menyala dan tooltip hotkey dinamis.
- **Floating & Always on Top**:
  - Jendela ringkas melayang (*frameless & draggable*) yang selalu berada di atas jendela lain.
  - Desain modern bernuansa *Dark Navy* dengan sudut membulat elegan.
  - Ikon aplikasi vektor premium SVG tajam tanpa pixelation pada resolusi apa pun.
  - Dilengkapi animasi gelombang suara (*cyan neon waveform visualizer*) yang bergerak dinamis saat Anda berbicara.
- **System Tray & Fleksibilitas Minimize**:
  - Pilihan perilaku tombol minimize (`—`) pada menu pengaturan:
    - **Masuk ke System Tray**: Jendela disembunyikan sepenuhnya ke tray pojok kanan taskbar Windows dengan notifikasi balon informatif.
    - **Minimize ke Taskbar (Icon Biasa)**: Jendela diminimalkan ke taskbar biasa seperti aplikasi desktop standar.
  - **Proteksi Rekam Mutlak**: Aplikasi dilarang dan tidak bisa diminimize saat fitur transkripsi sedang aktif (*Listening.../Recording*). Tombol minimize otomatis dinonaktifkan untuk mencegah jendela terminimize secara tidak sengaja di tengah sesi pengetikan. Minimize hanya dapat dilakukan saat mode santai/idle.
  - Klik atau double-click icon tray untuk memunculkan kembali jendela ke layar.
- **Single Instance Application**:
  - Mencegah aplikasi terbuka ganda. Jika aplikasi sedang berjalan dan pengguna membukanya kembali (misal dari shortcut Desktop, Start Menu, atau launcher), aplikasi tidak akan membuka jendela baru melainkan otomatis mengaktifkan dan memunculkan kembali jendela yang sedang berjalan ke layar depan via IPC Windows Named Pipe (`QLocalServer` & `QLocalSocket`).
- **Auto-Launch Windows Startup**:
  - Opsi aktivasi langsung dari menu pengaturan agar aplikasi berjalan otomatis saat Windows dinyalakan.
  - Berjalan di tingkat *User Registry* (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`), sehingga tidak memerlukan hak Administrator (UAC).
  - Meluncur secara hening di latar belakang via VBScript (`Live Speech to Text.vbs`) tanpa kilatan jendela konsol CMD hitam.
- **Direct Typing ke Kursor Aktif**:
  - Mengetikkan kata-kata langsung ke posisi kursor yang sedang aktif di aplikasi lain tanpa perlu copy-paste.
  - Menggunakan algoritma *differential typing* cerdas berbasis *Longest Common Prefix (LCP)* untuk meminimalkan penekanan tombol backspace jika ada revisi kata dari Whisper.
- **Pembersihan Tanda Baca Cerdas**:
  - Tanda baca otomatis yang dihasilkan oleh Whisper (seperti titik, koma, tanda tanya, tanda seru yang tidak diinginkan) otomatis dihilangkan.
  - Tanda hubung pada kata ulang bahasa Indonesia (misal: `teman-teman`, `jalan-jalan`, `hati-hati`) tetap dipertahankan secara cerdas.
- **Global Hotkey (Shortcut Bebas Sentuh Mouse)**:
  - Tekan tombol **`F8`** (atau tombol shortcut lain yang dikonfigurasi) dari aplikasi mana saja untuk langsung Mulai (*Start*) atau Berhenti (*End*) merekam tanpa kehilangan fokus kursor aktif.
- **Auto-Stop Timeout Hemat Resource**:
  - Mencegah CPU/GPU bekerja terus-menerus jika pengguna lupa menekan tombol Stop/End setelah selesai berbicara.
  - Dapat diaktifkan/dinonaktifkan (*Toggle On/Off*) dengan pilihan durasi hening fleksibel: **30 detik**, **45 detik**, **1 menit (default)**, **2 menit**, **3 menit**, dan **5 menit**.
  - Saat waktu hening tercapai, engine transkripsi otomatis berhenti, visualizer berhenti, jendela kembali ke mode idle, dan notifikasi balon tray muncul memberi tahu pengguna.
- **Popup Pengaturan Terpadu Dua Tab (Ikon ⚙)**:
  - Desain modal lapang modern (`440 × 560 px`) dengan tab navigasi ringkas satu kata (**Audio** & **Sistem**):
    - **Tab Audio**: Ganti Model Whisper (`small`, `base`, `medium`, `tiny`), Bahasa (`id`, `en`, `auto`), Perangkat Mikrofon, dan Mode Pengetikan (*Streaming kata demi kata (Live)* atau *Per penggalan kalimat (Saat jeda)*).
    - **Tab Sistem**: Ganti Tombol Shortcut Global (`F8`, `F9`, `F10`, `F12`, `Ctrl+Shift+Space`, dll.), Mulai Otomatis saat Windows Dinyalakan (Aktif/Nonaktif), Perilaku Tombol Minimize (System Tray vs Taskbar biasa), serta Auto-Stop Saat Hening (Aktif/Nonaktif dan durasi waktu dinamis).
- **Akselerasi GPU Mandiri (NVIDIA CUDA)**:
  - Latensi super instan di kartu grafis NVIDIA RTX (misal RTX 3050): hanya ~44ms (model `base`) dan ~140ms (model `small`).
  - Paket cuBLAS & cuDNN terpasang mandiri di virtual environment tanpa perlu instalasi CUDA Toolkit global di sistem Windows.

---

## Struktur Folder Project

```text
live-speech-to-text/
├── .docs/
│   └── AI_CONTEXT.md                   # Panduan teknis komprehensif arsitektur & quirks untuk AI Agent
├── assets/
│   ├── icon.ico                        # Ikon aplikasi multi-resolusi Windows (16px - 256px)
│   ├── icon.png                        # Asset PNG ikon cyan mic badge
│   ├── chevron_down.png                # Panah dropdown anti-aliased
│   ├── radio_checked.png               # Indikator radio button aktif
│   └── radio_unchecked.png             # Indikator radio button nonaktif
├── main.py                             # Entry point utama aplikasi (Single Instance, CUDA setup & GUI)
├── run.bat                             # Launcher terminal CMD (auto-close exit code 0)
├── Live Speech to Text.vbs             # Launcher hening tanpa jendela hitam CMD (via pythonw.exe)
├── Setup.bat                           # Installer shortcut 1-klik ke Desktop & Start Menu
├── build_installer.bat                 # Script kompilasi installer Inno Setup (.exe)
├── installer.iss                       # Blueprint Inno Setup 6 compiler
├── requirements.txt                    # Daftar dependensi library Python lengkap
├── README.md                           # Dokumentasi resmi project
└── src/
    ├── core/
    │   ├── audio_capture.py            # Modul stream mikrofon (sounddevice sliding window buffer)
    │   ├── autostart_manager.py        # Pengatur auto-launch Windows startup registry (HKCU Run)
    │   ├── config_manager.py           # Pengelola file konfigurasi persisten config.json
    │   ├── cuda_setup.py               # Pengatur path DLL CUDA/cuDNN mandiri di virtual environment
    │   ├── focus_manager.py            # Manajemen fokus jendela target & WS_EX_NOACTIVATE
    │   ├── hotkey_manager.py           # Pendengar shortcut keyboard global (low-level hook)
    │   ├── live_worker.py              # QThread worker streaming per-kata, commit & auto-timeout
    │   ├── single_instance.py          # IPC Single Instance controller (Windows Named Pipe)
    │   ├── stt_engine.py               # Engine faster-whisper (transkripsi interim & final commit)
    │   ├── text_cleaner.py             # Pembersih tanda baca otomatis STT & preservasi kata ulang
    │   └── virtual_typist.py           # Pengetik virtual ke kursor aktif berbasis LCP
    └── gui/
        ├── components/
        │   ├── icons.py                # Generator ikon vektor inline SVG murni (anti-pixelation)
        │   └── waveform_visualizer.py  # Animasi visualizer audio neon cyan (19-bar Gaussian curve)
        ├── dialogs/
        │   ├── about_dialog.py         # Dialog tentang aplikasi & kredit pengembang ADR Programming
        │   └── settings_dialog.py      # Dialog popup pengaturan dua tab ringkas (Audio, Sistem)
        └── floating_window.py          # Jendela utama Floating App (Dual-State) + System Tray integration
```

---

## Instalasi & Cara Menjalankan

### 1. Instalasi Shortcut Instan (Disarankan)
Cukup jalankan file:
```text
Setup.bat
```
Script ini akan otomatis:
- Memverifikasi virtual environment `venv`.
- Membuat shortcut di **Desktop**: `Live Speech to Text.lnk` lengkap dengan ikon mikrofon cyan.
- Membuat shortcut di **Start Menu**: Folder `ADR Programming > Live Speech to Text`.
- Mengarahkan launcher ke `Live Speech to Text.vbs` sehingga aplikasi terbuka hening tanpa jendela CMD.

### 2. Menjalankan Manual
- **Hening (Disarankan)**: Klik ganda file `Live Speech to Text.vbs` (aplikasi langsung melayang tanpa jendela konsol hitam CMD).
- **Mode Diagnostik**: Klik ganda `run.bat` (dengan tampilan konsol CMD untuk melihat log proses; CMD otomatis tertutup saat aplikasi ditutup).
- **Via Terminal**:
```powershell
.\venv\Scripts\python.exe main.py
```

### 3. Build Installer Setup (.exe)
Jika ingin membuat file installer mandiri berbasis Inno Setup 6:
```text
build_installer.bat
```
File installer setup berekstensi `.exe` akan dibuat di folder `Output\LiveSpeechToText_Setup.exe`.

---

## Panduan Penggunaan

1. **Membuka Aplikasi**:
   - Jalankan aplikasi melalui shortcut Desktop / Start Menu, atau klik ganda `Live Speech to Text.vbs`.
   - Jendela melayang ringkas (*floating window*) bernuansa Dark Navy akan tampil di layar.
2. **Posisikan Kursor**:
   - Posisikan kursor mouse Anda pada kolom teks tempat Anda ingin mengetik (misal: ruang chat WhatsApp, dokumen Microsoft Word, Google Docs, Notepad, Telegram, dll.).
3. **Mulai Merekam Suara**:
   - Tekan tombol shortcut keyboard **`F8`** (kursor tetap aktif di aplikasi target tanpa berpindah fokus).
   - Atau klik **tombol mikrofon besar** melingkar di tengah jendela Floating App.
4. **Mode Mendengarkan (*Listening...*)**:
   - Tampilan jendela otomatis beralih menampilkan visualizer gelombang suara neon cyan yang bergerak dinamis mengikuti desibel suara Anda.
5. **Berbicara Secara Alami**:
   - Mulailah berbicara. Kata-kata yang Anda ucapkan akan langsung terketik secara *real-time* tepat di posisi kursor aktif Anda.
   - Algoritma diferensial *Longest Common Prefix (LCP)* memastikan proses pengetikan halus tanpa kedipan (*flickering*).
6. **Selesai / Menghentikan Rekam**:
   - Tekan tombol **`F8`** kembali, atau klik tombol **`■ End`** pada jendela floating.
   - Jendela kembali ke mode idle dan kalimat terakhir terkunci rapi di posisi kursor.
7. **Menu Pengaturan Terpadu (Ikon ⚙)**:
   - Klik ikon gerigi (⚙) di pojok kiri bawah jendela untuk membuka modal pengaturan dua tab:
     - **Tab Audio**: Atur Model Whisper (`small`, `base`, `medium`, `tiny`), Bahasa Transkripsi (`id`, `en`, atau Auto-Detect), Perangkat Mikrofon, dan Mode Pengetikan (*Streaming* per kata atau *Per penggalan kalimat*).
     - **Tab Sistem**: Ubah Shortcut Global (`F8`, `F9`, `F10`, dll.), aktifkan/nonaktifkan Auto-Launch saat Windows boot, tentukan perilaku minimize (System Tray vs Taskbar biasa), serta atur Auto-Stop saat hening.
8. **Fleksibilitas Tombol Minimize (`—`)**:
   - **Mode System Tray (Default)**: Klik tombol minimize (`—`) di pojok kanan atas jendela saat mode idle. Jendela akan disembunyikan ke System Tray di pojok kanan taskbar. Anda tetap bisa menekan tombol `F8` kapan saja dari aplikasi mana pun untuk merekam langsung tanpa perlu membuka jendela, atau klik/double-click icon tray untuk menampilkan kembali jendela.
   - **Mode Taskbar (Icon Biasa)**: Jika preferensi diubah ke Taskbar, jendela akan diminimalkan ke taskbar biasa seperti jendela Windows standar.
9. **Proteksi Rekam Mutlak**:
   - Saat sedang merekam suara (*Listening...*), tombol minimize otomatis dinonaktifkan dan event minimize dari sistem OS diabaikan. Ini menjamin sesi transkripsi Anda tidak terhenti atau tersembunyi secara tidak sengaja di tengah pembicaraan penting.
10. **Auto-Stop Hemat Daya & Komputasi**:
    - Jika Anda lupa menekan tombol `End` setelah selesai berbicara, sistem otomatis menghentikan engine transkripsi saat mendeteksi keheningan (default 1 menit, dapat disesuaikan: 30 detik, 45 detik, 1 menit, 2 menit, 3 menit, 5 menit, atau dinonaktifkan di tab Sistem).
    - Beban komputasi GPU/CPU komputer Anda langsung dilepaskan, dan notifikasi balon informatif akan muncul di System Tray.
11. **Single Instance Controller**:
    - Anda tidak perlu khawatir membuka aplikasi dua kali. Jika aplikasi sudah berjalan di layar atau di tray dan Anda membukanya kembali dari shortcut, sistem otomatis mendeteksi instance yang ada via Windows Named Pipe, memulihkan jendela, dan membawanya ke tumpukan paling depan.
12. **Mulai Otomatis Saat Booting Windows**:
    - Anda dapat mengaktifkan opsi *Mulai Otomatis Saat Windows Dinyalakan* pada tab *Sistem*. Aplikasi akan otomatis berjalan di latar belakang setiap kali Anda menyalakan komputer secara hening dan siap digunakan kapan pun Anda menekan tombol shortcut `F8`.

---

Dikembangkan dengan ❤️ oleh [ADR Programming](https://www.instagram.com/adr_programming/)
