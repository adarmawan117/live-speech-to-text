# 🤖 AI Developer Context: Live Speech to Text (Floating Voice Typing)

**ATTENTION FUTURE AI:** Baca dokumen ini dengan seksama sebelum memodifikasi atau memperluas codebase ini. Dokumen ini merangkum seluruh keputusan arsitektural, bug/quirks sistem operasi Windows, tata kelola thread, manipulasi kursor, parameter audio pipeline, trik rendering, dan *hints* teknis yang ditemukan selama pengembangan agar tidak terjadi regresi (*breaking changes*).

---

## 1. Tech Stack & Core Libraries

*   **Runtime:** Python 3.13 (64-bit Windows).
*   **GUI Framework:** `PyQt5` (Frameless, Always On Top, Translucent Background, QStackedWidget, QTabWidget, QGraphicsDropShadowEffect).
*   **Speech-to-Text Engine:** `faster-whisper` (CTranslate2 backend bertenaga Whisper AI).
*   **GPU Acceleration:** NVIDIA CUDA 12 (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12`, `nvidia-cuda-nvrtc-cu12`) terintegrasi mandiri di virtual environment (`venv`).
*   **Audio Capture:** `sounddevice` (PortAudio wrapper, 16kHz mono float32, block-sliding buffer).
*   **Virtual Input / Direct Typing:** Win32 API via `keyboard` & `ctypes` (`SendInput`, `VK_BACK`, `KEYEVENTF_UNICODE`).
*   **Global Hotkey Listener:** `keyboard` (Win32 low-level keyboard hooks).
*   **Inter-Process Communication (IPC):** Qt `QLocalServer` & `QLocalSocket` (Windows Named Pipes untuk Single Instance enforcement).
*   **Windows Startup Management:** `winreg` (Windows Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` untuk auto-launch user-level tanpa UAC).
*   **Icon & Graphic Rendering:** `PyQt5.QtSvg` (`QSvgRenderer`) dan `QPainter` anti-aliased rendering.
*   **Packaging & Distribution:**
    *   `Live Speech to Text.vbs` (Silent launcher via `pythonw.exe`).
    *   `Setup.bat` (Automated 1-click shortcut installer ke Desktop & Start Menu).
    *   `installer.iss` + `build_installer.bat` (Inno Setup 6 standalone compiler).

---

## 2. Global Architecture & File Structure

```text
live-speech-to-text/
├── .docs/
│   └── AI_CONTEXT.md                   # Dokumen ini (AI Developer Guidelines)
├── assets/
│   ├── icon.ico                        # Multi-res application icon (16px - 256px)
│   ├── icon.png                        # PNG icon cyan mic badge
│   ├── chevron_down.png                # Dropdown arrow anti-aliased
│   ├── radio_checked.png               # Active radio indicator glowing ring & dot
│   └── radio_unchecked.png             # Inactive radio indicator border
├── src/
│   ├── core/
│   │   ├── audio_capture.py            # Stream mikrofon via sounddevice (sliding window buffer)
│   │   ├── autostart_manager.py        # Pengelola Windows Startup Registry (HKCU Run auto-launch hening)
│   │   ├── config_manager.py           # Single source of truth untuk config.json
│   │   ├── cuda_setup.py               # Setup environment path DLL CUDA/cuDNN dari venv
│   │   ├── focus_manager.py            # Windows API: WS_EX_NOACTIVATE & restore active HWND
│   │   ├── hotkey_manager.py           # Listener shortcut keyboard global (F8, unhook on exit)
│   │   ├── live_worker.py              # QThread worker: streaming interim, final commit & auto-timeout
│   │   ├── single_instance.py          # IPC Named Pipe controller untuk single instance aplikasi
│   │   ├── stt_engine.py               # faster-whisper engine wrapper & _ENGINE_CACHE VRAM residency
│   │   ├── text_cleaner.py             # Sanitasi tanda baca STT & preservasi kata ulang
│   │   └── virtual_typist.py           # LCP differential typist ke kursor Windows aktif
│   └── gui/
│       ├── components/
│       │   ├── icons.py                # Generator icon vektor SVG murni (mic, mic_badge, stop, stop_badge, dll.)
│       │   └── waveform_visualizer.py  # 19-bar cyan neon dynamic audio waveform
│       ├── dialogs/
│       │   ├── about_dialog.py         # Modal kredit developer ADR Programming
│       │   └── settings_dialog.py      # Modal pengaturan dua tab ringkas (Audio, Sistem)
│       └── floating_window.py          # Jendela utama dual-state (Idle vs Recording) + System Tray + Dynamic Icons
├── main.py                             # Entry point aplikasi (URUTAN IMPORT SANGAT KRUSIAL!)
├── run.bat                             # Launcher terminal CMD (auto-close exit code 0)
├── Live Speech to Text.vbs             # Launcher hening tanpa jendela hitam CMD
├── Setup.bat                           # Installer shortcut Desktop & Start Menu
├── build_installer.bat                 # Script kompilasi Inno Setup compiler (ISCC.exe)
├── installer.iss                       # Inno Setup 6 compilation blueprint
├── requirements.txt                    # Dependensi runtime lengkap
└── README.md                           # Dokumentasi resmi pengguna & instalasi
```

---

## 3. Notable Quirks & Critical Hints (DO NOT BREAK)

### A. Windows DLL Collision & Import Order di `main.py`
*   **The Bug:** Jika modul `PyQt5` di-import sebelum modul C++ CUDA/CTranslate2 (`ctranslate2`, `faster_whisper`), Windows akan mengalami DLL collision atau crash *silent access violation (exit code 1)* saat model Whisper dimuat atau audio stream dibuka.
*   **The Fix:** Di baris paling atas `main.py`, WAJIB memanggil `setup_cuda_environment()`, disusul `import ctranslate2`, dan `import faster_whisper` **SEBELUM** ada modul PyQt5 yang di-import:
    ```python
    from src.core.cuda_setup import setup_cuda_environment
    setup_cuda_environment()
    import ctranslate2
    import faster_whisper
    # Baru setelah ini modul PyQt5 dan modul lainnya boleh di-import!
    from PyQt5.QtWidgets import QApplication
    ```

### B. High-DPI Scaling & Console Suppression di `main.py`
*   `QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)` dan `Qt.AA_UseHighDpiPixmaps` **WAJIB dipanggil SEBELUM `QApplication(sys.argv)` dibuat**. Jika dipanggil sesudahnya, scaling DPI layar monitor 2K/4K akan pecah atau memunculkan error Qt runtime.
*   `os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"` meredam spam log Windows DirectWrite font warnings di konsol.
*   `sys.stdout.reconfigure(encoding="utf-8")` mencegah `UnicodeEncodeError` pada terminal Windows dengan codepage CP1252/CP437.

### C. Dynamic CUDA/cuDNN Discovery (`cuda_setup.py`)
*   **The Problem:** Pengguna tidak perlu menginstal NVIDIA CUDA Toolkit secara global di sistem Windows mereka. Modul cuBLAS dan cuDNN sudah terpasang mandiri sebagai pip wheels di `venv\Lib\site-packages\nvidia\`.
*   **The Fix:** Pada Python $\ge 3.8$ di Windows, DLL tidak bisa lagi ditemukan hanya dengan memodifikasi `os.environ["PATH"]`. Fungsi `setup_cuda_environment()` di [cuda_setup.py](../src/core/cuda_setup.py) secara dinamis memindai direktori `nvidia/*/bin` dan mendaftarkannya dengan API Win32:
    ```python
    os.add_dll_directory(bin_path)
    os.environ["PATH"] = bin_path + os.pathsep + os.environ.get("PATH", "")
    ```

### D. Audio Pipeline & Parameter Dua-Fase (Streaming vs Commit)
Transkripsi suara real-time mengimplementasikan arsitektur dua fase (*dual-phase transcription*) di [live_worker.py](../src/core/live_worker.py) dan [stt_engine.py](../src/core/stt_engine.py):

| Parameter | Nilai | Tujuan & Rasional |
| :--- | :--- | :--- |
| **Sample Rate** | `16000` Hz | Standar mutlak format input Whisper (Mono, `float32`). |
| **Block Size** | `2048` samples | Ukuran buffer chunk per callback `sounddevice` (~128ms). |
| **Silence Threshold** | `0.015` RMS | Ambang energi suara: $\text{rms} = \sqrt{\frac{1}{N}\sum x_i^2}$. Di atas nilai ini = bicara. |
| **Interim Interval** | `0.35` detik | Throttle pembaruan kata live (~350ms). Durasi audio minimal $\ge 0.25$ detik. |
| **Interim Engine** | `beam_size=1`, `vad=False` | Greedy search super instan (~40-140ms). VAD dinonaktifkan agar buntut kalimat tidak terpangkas. |
| **Silence Limit** | `0.75` detik | Batas hening (jeda napas) untuk mentrigger **Final Commit**. |
| **Max Phrase Duration** | `12.0` detik | Batas frase maksimal sebelum auto-commit jika pengguna bicara tanpa henti. |
| **Final Commit Engine** | `beam_size=3`, `vad=True` | Akurasi tinggi dengan VAD filtering (`min_silence_duration_ms=300`). |
| **Fallback Mechanism** | `fallback_text` | Jika VAD commit memotong kalimat secara agresif, gunakan teks interim terakhir agar kata tidak lenyap. |

### E. VRAM Model Caching (`_ENGINE_CACHE`)
*   Untuk mencegah jeda *freeze* 2-4 detik setiap kali pengguna menekan Start/End, `stt_engine.py` menyimpan instance model Whisper di memori GPU melalui kamus global `_ENGINE_CACHE[(model_size, language)]`.
*   Model tetap menetap di VRAM selama sesi berlangsung, sehingga penekanan tombol mic berikutnya menghasilkan transkripsi instan dengan latensi nol. Model baru hanya dimuat jika user mengganti model/bahasa di menu pengaturan.

### F. Real-Time Streaming Typing & LCP (Longest Common Prefix)
*   **The Problem:** Dalam mode *streaming per-kata*, Whisper menghasilkan kata-kata tentatif (*interim transcript*) yang bisa direvisi di tengah kalimat ketika konteks baru terdengar. Menghapus seluruh kalimat dengan backspace lalu mengetik ulang menimbulkan *screen flickering/jitter* parah pada aplikasi target (seperti Word atau WhatsApp).
*   **The Fix:** Menggunakan algoritma **Longest Common Prefix (LCP)** di [virtual_typist.py](../src/core/virtual_typist.py):
    1. Bandingkan `last_interim` dengan `new_interim` untuk mencari karakter awal yang identik (*common prefix*).
    2. Hanya tekan tombol `VK_BACK` sebanyak sisa karakter lama: `len(last_interim) - lcp_len`.
    3. Ketikkan hanya potongan karakter baru: `new_interim[lcp_len:]` dengan delay `delay=0.003` (3ms per karakter) agar antrean pesan Windows tidak drop keystroke.
    4. Saat pengguna berhenti berbicara (*VAD silence detected*), panggil `commit_phrase(final_text)`: ketikkan spasi penutup, lalu **reset `last_interim`** agar kalimat sebelumnya tidak terhapus oleh kalimat berikutnya.

### G. Pembersihan Tanda Baca Cerdas (Preservasi Kata Ulang)
*   **The Rule:** Whisper sering menambahkan tanda baca otomatis (titik, koma, tanda tanya) yang tidak diinginkan user saat berkirim pesan. Namun tanda hubung `-` pada kata ulang bahasa Indonesia (misal `teman-teman`, `jalan-jalan`, `hati-hati`) **HARUS TETAP DIPERTAHANKAN**.
*   **The Fix:** Fungsi `clean_stt_punctuation(text)` di [text_cleaner.py](../src/core/text_cleaner.py) menggunakan regex:
    ```python
    # Ganti ellipsis dan dash terpisah/panjang dengan spasi
    cleaned = re.sub(r'[\u2014\u2013\u2026]', ' ', text)
    # Hapus dash yang berdiri sendiri (bukan di antara kata berulang)
    cleaned = re.sub(r'(?<=\s)-(?=\s)|(?<=\s)-|-(?=\s)', ' ', cleaned)
    # Hapus semua tanda baca umum lainnya
    cleaned = _PUNCTUATION_PATTERN.sub('', cleaned)
    ```

### H. Window Focus & Non-Activating Window (`WS_EX_NOACTIVATE`)
*   **The Bug:** Jika jendela floating diklik atau digeser, Windows secara default memindahkan keyboard focus ke jendela floating. Akibatnya, kursor di WhatsApp/Word hilang dan teks tidak bisa terketik ke aplikasi tujuan.
*   **The Fix:**
    1. Terapkan flag Win32 `WS_EX_NOACTIVATE` via `SetWindowLongPtr` di [focus_manager.py](../src/core/focus_manager.py).
    2. Pada event `mousePressEvent` jendela floating, tangkap `HWND` aplikasi aktif sebelumnya via `GetForegroundWindow()`.
    3. Saat mulai merekam (`start_recording`), kembalikan fokus ke target via `SetForegroundWindow(target_hwnd)` sebelum pengetikan dimulai.
    4. Window flags jendela utama harus: `Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint`. **JANGAN gunakan `Qt.SubWindow`** karena mematahkan mekanisme shutdown event loop `QApplication.quit()`.

### I. Drop Shadow Padding Bleed pada Jendela Frameless
*   `FloatingSTTWindow` menggunakan latar transparan (`Qt.WA_TranslucentBackground`).
*   Bayangan gelap dirender menggunakan `QGraphicsDropShadowEffect(blur=20, offset=(0,4))` pada `container`.
*   Layout terluar (`layout_root`) sengaja diberi `setContentsMargins(10, 10, 10, 10)`. **JANGAN diubah ke 0**, karena margin 10px ini adalah area kanvas untuk merender efek blur bayangan agar tidak terpotong garis tepi jendela (*clipping*).

### J. Windows UIPI (User Interface Privilege Isolation)
*   **The Quirk:** Windows mencegah aplikasi tanpa privilege Administrator mengirim `SendInput` atau menangkap tombol keyboard global jika aplikasi target yang sedang aktif berjalan sebagai Administrator (misal: elevated CMD, PowerShell, Task Manager, Regedit).
*   **The Solution:** Jika user memerlukan pengetikan suara ke aplikasi dengan hak Administrator, `Live Speech to Text` harus dijalankan dengan opsi *"Run as Administrator"*.

### K. Cross-Thread Hotkey Event Marshaling
*   Library `keyboard` memicu callback `_on_hotkey` di thread latar belakang OS miliknya sendiri.
*   Di [hotkey_manager.py](../src/core/hotkey_manager.py), pemanggilan langsung ke fungsi GUI dihindari. Callback hanya memancarkan sinyal PyQt: `self.hotkey_triggered.emit()`.
*   Mekanisme *Queued Connection* internal Qt secara otomatis membawa eksekusi sinyal ke Main GUI Thread dengan aman.

### L. Terminal CMD Auto-Close & Thread Termination
*   **The Bug:** GUI sudah ditutup, namun jendela Command Prompt (`run.bat`) tetap menggantung karena background thread dari library `keyboard` masih aktif.
*   **The Fix:**
    1. Di `FloatingSTTWindow.closeEvent()`, panggil `self.hotkey_manager.unregister()` yang mengeksekusi `keyboard.unhook_all()`, hentikan `worker.stop()`, sembunyikan tray icon, dan panggil `QApplication.quit()`.
    2. Di `run.bat`, gunakan `if errorlevel 1 pause`. Jika exit code normal (0), CMD otomatis menutup tuntas.
    3. Untuk pengguna umum, sediakan `Live Speech to Text.vbs` yang meluncurkan aplikasi via `pythonw.exe` (`IMAGE_SUBSYSTEM_WINDOWS_GUI`) tanpa membuka konsol sama sekali.

### M. System Tray & Strict Minimize Protection (Tray vs Taskbar)
*   **The Rule:**
    *   Pengguna dapat memilih perilaku tombol minimize (`—`) melalui pengaturan: **Masuk ke System Tray** (default) atau **Minimize ke Taskbar (Icon Biasa)**.
    *   **Ikon Status Dinamis Terpadu**:
        - Saat Idle: Ikon header bar berupa mikrofon cyan (`#00d2ff`), ikon taskbar/tray berupa `icon_idle` (badge mikrofon cyan). Tooltip tray: `"Live Speech to Text - ADR Programming"`.
        - Saat Merekam (`start_recording`): Ikon header bar otomatis berganti menjadi ikon stop merah (`stop`, `#ff4757`), ikon taskbar dan System Tray berganti menjadi badge stop merah (`stop_badge`, bulatan merah `#e63946` dengan kotak putih rounded di tengahnya). Tooltip tray berubah menjadi `"Live Speech to Text - Merekam (Listening...)"`.
        - Saat Selesai / Auto-Timeout (`stop_recording`): Seluruh ikon dan tooltip otomatis dipulihkan kembali ke status idle.
    *   **Ikon Status Dinamis Terpadu**:
        - Saat Idle: Ikon header bar berupa mikrofon cyan (`#00d2ff`), ikon taskbar/tray berupa `icon_idle` (badge mikrofon cyan). Tooltip tray: `"Live Speech to Text - ADR Programming"`.
        - Saat Merekam (`start_recording`): Ikon header bar otomatis berganti menjadi ikon stop merah (`stop`, `#ff4757`), ikon taskbar dan System Tray berganti menjadi badge stop merah (`stop_badge`, bulatan merah `#e63946` dengan kotak putih rounded di tengahnya). Tooltip tray berubah menjadi `"Live Speech to Text - Merekam (Listening...)"`.
        - Saat Selesai / Auto-Timeout (`stop_recording`): Seluruh ikon dan tooltip otomatis dipulihkan kembali ke status idle.
    *   **DILARANG BISA DIMINIMIZE saat fitur transkripsi sedang aktif (`Start`/Recording)**, apa pun mode minimize yang dipilih.
    *   Minimize hanya boleh dilakukan saat mode Idle/tidak merekam.
*   **The Fix:** Diimplementasikan 3 lapis di [floating_window.py](../src/gui/floating_window.py):
    1. UI Level: `self.btn_minimize.setEnabled(False)` saat `start_recording()`, diaktifkan kembali saat `stop_recording()`. Tooltip tombol disesuaikan dinamis ("Minimize ke System Tray" vs "Minimize ke Taskbar").
    2. Method Level: `handle_minimize()` dan `minimize_to_tray()` langsung `return` jika `self.is_recording == True`.
    3. OS Event Level: `changeEvent(QEvent.WindowStateChange)` mengintersepsi event minimize dari sistem OS. Jika `self.is_recording`, tolak dengan `self.setWindowState(Qt.WindowNoState)` dan `event.ignore()`. Jika idle dan `minimize_to_tray` aktif, alihkan ke tray; jika idle dan taskbar mode aktif, izinkan minimize standar OS.

### N. Form Element Sizing & Font Clipping di PyQt5 (QSS Quirk & Compact Tab Styling)
*   **The Bug:** Di Qt Stylesheet, menerapkan `padding` pada `QComboBox`, `QPushButton`, atau `QTabBar::tab` tanpa menentukan ukuran minimum menyebabkan teks terpotong (*clipped*), baik secara vertikal (huruf 'g', 'j', 'p', 'y') maupun horizontal pada tab bar.
*   **The Fix:**
    1. Semua input `QComboBox` dan action `QPushButton` wajib memiliki `setFixedHeight(38)` atau `min-height: 38px`.
    2. Atur padding horizontal saja: `padding-left: 12px; padding-right: 32px;`.
    3. Dialog pengaturan [settings_dialog.py](../src/gui/dialogs/settings_dialog.py) menggunakan `QTabWidget` modern dua tab berdimensi lapang **`440 × 560 px`** dengan label ringkas satu kata (**Audio** dan **Sistem**).
    4. Tab styling diatur kompak dan proporsional dengan `min-width: 68px; min-height: 28px; padding: 3px 14px;` serta inisialisasi font `QFont("Segoe UI", 9)` langsung pada `tabBar()` untuk memastikan ukuran text metrics akurat tanpa memotong teks tab.
    5. Indikator radio button di QSS: Gunakan PNG anti-aliased beresolusi pas yang di-load via path absolut: `image: url("{radio_checked_path}");`.
    6. Dropdown dinamis: saat auto-stop diubah ke nonaktif, combo batas waktu timeout otomatis di-disable (`setEnabled(False)`) dan label diberi warna teks redup (`#4f627d`).

### O. Waveform Visualizer Mathematics (`waveform_visualizer.py`)
Visualizer 19-bar cyan neon menggunakan formula kurva Gaussian dan modulasi sinus 30 FPS:
*   **Gaussian Bell Curve:** Bar tengah lebih tinggi, bar samping lebih rendah:
    $$\text{gaussian} = \exp\left(-2.2 \times \text{dist}^2\right), \quad \text{dist} = \frac{|i - \text{mid}|}{\text{mid}}$$
*   **Sine Phase Motion:**
    $$\text{wave} = \sin(\text{phase} + i \times 0.4) \times 0.25 + 0.75$$
*   **Smoothing Level Audio:**
    $$\text{audio\_level} = \text{audio\_level} \times 0.4 + \text{level} \times 0.6$$
*   **Double-pass Rendering:** Menggambar glow rectangle transparan `QColor(0, 210, 255, 60)` di lapisan belakang sebelum menggambar core bar `QColor("#00d2ff")`.

### P. Audio Device Disconnection & Fallback
*   Dalam [settings_dialog.py](../src/gui/dialogs/settings_dialog.py), perangkat mic disimpan sebagai indeks integer.
*   Jika mic USB dicabut atau Windows berganti audio endpoint, `sounddevice` bisa melempar `PortAudioError: Invalid device`.
*   Sistem menangani ini secara elegan: jika nilai yang disimpan `None` atau gagal terhubung, engine otomatis fallback ke default endpoint audio sistem operasi Windows.

### Q. Inno Setup Compiler (`installer.iss`)
*   Gunakan parameter `Excludes: "*__pycache__*,*.pyc"` (dengan huruf 's' di akhir), bukan `Exclude`.
*   Gunakan `compiler:Default.isl` untuk bahasa default. Jangan merujuk `Indonesian.isl` kecuali filenya disertakan secara manual karena Inno Setup 6 standar tidak menyertakan modul bahasa Indonesia bawaan.
*   Folder `Output/` dan file binary setup `.exe` wajib dikarantina di `.gitignore`.
*   `PrivilegesRequired=lowest` dipasang agar instalasi tidak memicu popup UAC Windows Administrator jika diinstal di tingkat pengguna.

### R. Auto-Stop Silence Timeout (Resource Saver)
*   **The Problem:** Jika pengguna lupa menekan tombol Stop/End atau shortcut global, proses audio recording dan model Whisper tetap aktif di background, membebani utilisasi GPU/CPU komputer pengguna.
*   **The Fix:**
    1. Di [live_worker.py](../src/core/live_worker.py), catat `last_speech_time = time.time()` setiap kali amplitudo `rms > silence_threshold` terdeteksi.
    2. Pengguna dapat mengaktifkan/menonaktifkan fitur ini melalui `"auto_stop_enabled": True/False` dan memilih durasi timeout `"auto_stop_timeout_sec": 30/45/60/120/180/300`.
    3. Saat kondisi hening (`not is_speaking`), `auto_stop_enabled == True`, dan `(current_time - last_speech_time) >= self.no_speech_timeout_sec`:
       - Pancarkan sinyal `self.auto_timeout.emit()`.
       - Update status info `"Otomatis berhenti: tidak ada input suara selama X detik."`.
       - Break dari audio loop dan hentikan stream PortAudio secara tuntas.
    4. Di [floating_window.py](../src/gui/floating_window.py), slot `on_auto_timeout()` memanggil `self.stop_recording()`, mengembalikan tampilan ke halaman Idle (ikon mic bulat biru), mengaktifkan kembali tombol minimize, dan memunculkan notifikasi balon tray `showMessage()` di Windows dengan format durasi ramah pengguna (`X menit` atau `X detik`).

### S. Single Instance Application & IPC Named Pipe (`single_instance.py`)
*   **The Goal:** Mencegah pengguna membuka lebih dari satu instance aplikasi yang dapat menyebabkan perebutan port audio mikrofon, duplikasi global keyboard hook `F8`, dan pemborosan VRAM GPU Whisper.
*   **The Mechanism:**
    1. Menggunakan protokol **Windows Named Pipe** via `QLocalServer` dan `QLocalSocket` di [single_instance.py](../src/core/single_instance.py) dengan server identifier `LiveSpeechToText_SingleInstance_Server`.
    2. Saat aplikasi baru diluncurkan (`main.py`):
       - Hubungkan `QLocalSocket` ke server.
       - Jika terhubung (`waitForConnected(500) == True`), berarti ada instance yang sudah aktif.
       - Panggil Win32 API `ctypes.windll.user32.AllowSetForegroundWindow(-1)` agar OS mengizinkan instance pertama memunculkan jendelanya ke depan.
       - Kirim sinyal `b"ACTIVATE\n"`, lalu instance kedua langsung keluar secara bersih (`sys.exit(0)`).
    3. Di instance pertama:
       - `SingleInstanceController.message_received` terhubung ke `window.restore_from_tray()`.
       - Jika jendela sedang diminimize (`isMinimized()`), kembalikan status jendela dengan `setWindowState`.
       - Tampilkan jendela (`show()`), angkat ke tumpukan teratas (`raise_()`), aktifkan (`activateWindow()`), serta panggil `ShowWindow(hwnd, SW_RESTORE)` dan `SetForegroundWindow(hwnd)` via Win32 API untuk memastikan jendela tampil di layar pengguna.

### T. Windows Startup Registry (Auto-Launch Boot Management)
*   **The Goal:** Memungkinkan pengguna menyalakan aplikasi secara otomatis ketika Windows boot tanpa menampilkan jendela CMD terminal yang mengganggu.
*   **The Mechanism:**
    1. Menggunakan Windows Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` melalui modul [autostart_manager.py](../src/core/autostart_manager.py) dengan registry key `LiveSpeechToText_ADR`.
    2. Berjalan di tingkat pengguna (`HKEY_CURRENT_USER`), sehingga **TIDAK memerlukan elevasi Administrator (UAC)**.
    3. Perintah eksekusi mengarah ke launcher VBScript: `wscript.exe "{path}\Live Speech to Text.vbs"`, menjamin aplikasi mulai sepenuhnya hening di latar belakang tanpa kilatan konsol Command Prompt.
    4. Status registry otomatis disinkronisasi ketika pengguna menekan tombol "Simpan" di dialog Pengaturan.

---

## 4. Multi-Threading & Concurrency Architecture

Aplikasi ini menggunakan model multi-threading non-blocking yang ketat:

```text
[OS Audio Driver (PortAudio)]
       │ (16kHz float32 audio callback)
       ▼
[AudioCapture Queue (queue.Queue)]
       │ (chunk retrieval timeout=0.04s)
       ▼
[LiveSTTWorker (QThread)]
   ├── WhisperModel (CUDA float16 / CPU int8 via _ENGINE_CACHE)
   ├── RMS Audio Level Calculation
   ├── Dual-phase Transcription (Interim vs Commit)
   └── Configurable Silence Timeout Watchdog (30s-300s or disabled)
       │
       │ (PyQt Signals: interim_text_ready, final_text_ready, audio_level, auto_timeout)
       ▼
[Main GUI Thread (QApplication)]
   ├── FloatingSTTWindow (Dual-state: Hero Mic Idle vs Waveform Recording)
   ├── WaveformVisualizer (Update cyan neon animation at 30 FPS)
   ├── FocusManager (Preserve & restore target application HWND, WS_EX_NOACTIVATE)
   ├── VirtualTypist (Win32 LCP differential keystroke execution via SendInput)
   ├── SingleInstanceController (QLocalServer IPC: restore_from_tray on duplicate launch)
   ├── AutostartManager (HKCU Run Windows Registry synchronization)
   ├── SettingsDialog (Two-Tab QTabWidget: Audio, Sistem)
   └── SystemTrayIcon (QSystemTrayIcon: minimize-to-tray & auto-stop balloon alerts)
       │
       ▼
[Active Windows Application (WhatsApp / Word / Chrome)]
```

*   **Penting:** Komponen GUI **hanya boleh disentuh dari Main Thread**. Komunikasi dari `LiveSTTWorker` ke GUI wajib menggunakan **PyQt Signals/Slots** untuk menjamin thread-safety tanpa deadlock.

---

## 5. Configuration Schema (`config.json`)

File `config.json` bertindak sebagai *single source of truth* untuk pengaturan persisten pengguna:

```json
{
    "hotkey": "F8",
    "model_size": "small",
    "language": "id",
    "audio_device": null,
    "typing_mode": "streaming",
    "auto_start_on_boot": false,
    "minimize_to_tray": true,
    "auto_stop_enabled": true,
    "auto_stop_timeout_sec": 60
}
```

*   `hotkey`: String tombol shortcut (`"F8"`, `"F9"`, `"F10"`, `"Ctrl+Shift+Space"`, dll).
*   `model_size`: Ukuran model Whisper (`"tiny"`, `"base"`, `"small"`, `"medium"`).
*   `language`: Kode bahasa ISO 639-1 (`"id"` untuk Indonesia, `"en"` untuk Inggris, `null` untuk auto-detect).
*   `audio_device`: Indeks integer mic dari `sounddevice.query_devices()` atau `null` untuk default sistem.
*   `typing_mode`: `"streaming"` (pengetikan live kata demi kata) atau `"sentence"` (ketik per-frase saat jeda).
*   `auto_start_on_boot`: Boolean (`true` / `false`) untuk menjalankan aplikasi otomatis saat Windows boot.
*   `minimize_to_tray`: Boolean (`true`: sembunyi ke System Tray, `false`: minimize ke Taskbar biasa).
*   `auto_stop_enabled`: Boolean (`true` / `false`) untuk mengaktifkan/menonaktifkan fitur auto-stop saat hening.
*   `auto_stop_timeout_sec`: Integer durasi hening dalam detik sebelum engine berhenti (`30`, `45`, `60`, `120`, `180`, `300`).

---

## 6. Whisper Models Matrix & GPU Requirements

Faster-whisper menyimpan model di direktori cache default:
`%USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-*`

| Model Size | Parameter Count | VRAM (CUDA float16) | Latensi Rata-rata | Karakteristik & Rekomendasi |
| :--- | :--- | :--- | :--- | :--- |
| **`tiny`** | 39 M | ~1.0 GB | ~20 ms | Sangat cepat, namun akurasi bahasa Indonesia rendah. |
| **`base`** | 74 M | ~1.2 GB | ~44 ms | Ringan, cukup baik untuk perintah pendek. |
| **`small`** | 244 M | ~2.0 GB | ~140 ms | **Default & Recommended**: Titik temu optimal kecepatan & akurasi tata bahasa Indonesia. |
| **`medium`** | 769 M | ~4.5 GB | ~350 ms | Akurasi tertinggi, cocok untuk GPU 6GB+ VRAM (RTX 3060/4060). |

---

## 7. Design System & Visual Guidelines

Jika diminta menambahkan dialog baru, komponen, atau styling:

1.  **Color Palette:**
    *   Dark Navy Root: `#0c1322`
    *   Card / Input Background: `#141e33` (Hover: `#18253e`)
    *   Border Stroke: `#253858` (Hover: `#3b5a8c`, Active Focus: `#1b68ff`)
    *   Cyan Accent / Waveform: `#00d2ff`
    *   Primary Blue Gradient: `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a62f5, stop:1 #2779ff)`
    *   Recording Red Gradient: `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e63946, stop:1 #ff4757)`
    *   Primary Text: `#ffffff`, Secondary Text: `#8fa0bc` / `#94a3b8`, Disabled Text: `#4f627d`

2.  **No Emojis Rule & Pure Inline SVG Icons:**
    *   **DILARANG KERAS** menggunakan emoji teks (misal 🎙️, ⚙️, ℹ️, ▶️, ⏹️) di antarmuka pengguna!
    *   Semua icon adalah string inline SVG di [icons.py](../src/gui/components/icons.py) yang dirender transparan via `QSvgRenderer`. Pola ini menjamin tidak ada aset file eksternal yang hilang dan memungkinkan injeksi warna heksadesimal dinamis saat runtime.

3.  **Hero Circular Mic Button:**
    *   Tombol utama di layar Idle adalah icon mikrofon melingkar (`86 × 86 px`, `border-radius: 43px`) di tengah jendela, bukan tombol bar memanjang.
    *   Dimensi default Floating Window: **`320 × 270 px`**.
    *   Dimensi default Settings Dialog: **`440 × 560 px`** (terbagi atas dua tab ringkas: **Audio** dan **Sistem**).

4.  **Dual-State Status Indicators:**
    *   Mode Idle: Aksen cyan neon (`#00d2ff`), ikon mikrofon di header & taskbar/tray.
    *   Mode Merekam: Aksen border merah glowing (`#ff4757`), animasi gelombang suara aktif, dan ikon berganti otomatis menjadi badge stop merah (`stop_badge`).

---

## 8. Verification & Debugging Playbook untuk AI

Jika di masa depan Anda perlu memodifikasi atau menguji fungsi tertentu secara terisolasi tanpa membuka GUI:

1.  **Uji Coba Sanitasi Tanda Baca:**
    ```powershell
    .\venv\Scripts\python.exe -c "from src.core.text_cleaner import clean_stt_punctuation; print(clean_stt_punctuation('Halo... apa kabar? teman-teman! kita jalan-jalan yuk.'))"
    # Ekspektasi: "Halo apa kabar teman-teman kita jalan-jalan yuk"
    ```
2.  **Uji Coba CTranslate2 & Akselerasi GPU CUDA:**
    ```powershell
    .\venv\Scripts\python.exe -c "from src.core.cuda_setup import setup_cuda_environment; setup_cuda_environment(); import ctranslate2; print('CUDA Drivers Available:', ctranslate2.get_cuda_device_count())"
    # Ekspektasi: CUDA Drivers Available: 1 (atau jumlah GPU RTX)
    ```
3.  **Uji Coba Tangkap Audio Mikrofon:**
    ```powershell
    .\venv\Scripts\python.exe -c "import sounddevice as sd; print(sd.query_devices())"
    ```
4.  **Uji Coba Single Instance IPC Controller:**
    ```powershell
    .\venv\Scripts\python.exe -c "from src.core.single_instance import SingleInstanceController; s = SingleInstanceController(); print('Another instance running:', s.is_another_instance_running())"
    # Ekspektasi: False (jika tidak ada instance) atau True (jika aplikasi sedang berjalan)
    ```
5.  **Uji Coba Konfigurasi Konfigurasi Lengkap (config.json):**
    ```powershell
    .\venv\Scripts\python.exe -c "from src.core.config_manager import load_config; cfg = load_config(); print('Autostart:', cfg.get('auto_start_on_boot')); print('Minimize Tray:', cfg.get('minimize_to_tray')); print('Auto-Stop:', cfg.get('auto_stop_enabled'), cfg.get('auto_stop_timeout_sec'), 'detik')"
    ```
6.  **Uji Coba Ketersediaan System Tray Windows:**
    ```powershell
    .\venv\Scripts\python.exe -c "from PyQt5.QtWidgets import QApplication, QSystemTrayIcon; import sys; app = QApplication(sys.argv); print('System Tray Available:', QSystemTrayIcon.isSystemTrayAvailable())"
    # Ekspektasi: System Tray Available: True
    ```
7.  **Uji Coba Auto-Start Windows Registry (Write, Read, & Delete):**
    ```powershell
    .\venv\Scripts\python.exe -c "from src.core.autostart_manager import is_autostart_enabled, set_autostart; print('Initial:', is_autostart_enabled()); set_autostart(True); print('Set True:', is_autostart_enabled()); set_autostart(False); print('Set False:', is_autostart_enabled())"
    ```
8.  **Uji Coba Kompilasi Seluruh Kode:**
    ```powershell
    .\venv\Scripts\python.exe -m compileall src main.py
    ```

---

## 9. Developer Credit & Workspace Standards

*   **Developer Credit Rule:** Mengikuti aturan `developer_credit.md`:
    *   Label teks: `"Dikembangkan dengan ❤️ oleh ADR Programming"`
    *   Link tautan: `https://www.instagram.com/adr_programming/`
*   **PyQt5 Architecture Rule:** Mengikuti aturan `gui_pyqt5.md`:
    *   Inisialisasi semua atribut widget secara eksplisit di `__init__` (`self.btn_mic_start = None`, dll).
    *   Hindari `setObjectName` berlebih yang tidak digunakan untuk selektor QSS.
    *   Dilarang introspeksi defensif `hasattr`/`getattr` pada atribut yang didefinisikan sendiri.
*   **Git Workflow Rule:** Mengikuti `git_workflow.md` (Commit hanya saat diminta oleh user secara eksplisit).
*   **Security Rule:** Mengikuti `sensitive_data_protection.md` (Zero credential leak, resolusi path Windows dinamis `%USERPROFILE%` / `%APPDATA%`, karantina build folder di `.gitignore`).

---
*Dokumentasi ini dibuat sebagai referensi mutlak untuk pengembangan masa depan Live Speech to Text.*
