"""
Pengelola Auto-Launch (Mulai Otomatis saat Windows Dinyalakan).
Menggunakan Windows Registry HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
sehingga tidak membutuhkan hak Administrator.
"""
import os
import sys

if sys.platform == "win32":
    import winreg
else:
    winreg = None

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "LiveSpeechToText_ADR"


def _get_launch_command() -> str:
    """Menentukan perintah launcher aplikasi untuk Windows Startup."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    vbs_path = os.path.join(project_root, "Live Speech to Text.vbs")
    if os.path.exists(vbs_path):
        return f'wscript.exe "{vbs_path}"'

    pythonw_path = os.path.join(project_root, "venv", "Scripts", "pythonw.exe")
    main_path = os.path.join(project_root, "main.py")
    if os.path.exists(pythonw_path) and os.path.exists(main_path):
        return f'"{pythonw_path}" "{main_path}"'

    fallback_pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    return f'"{fallback_pythonw}" "{main_path}"'


def is_autostart_enabled() -> bool:
    """Mengecek apakah aplikasi sudah terdaftar di Windows Startup Registry."""
    if sys.platform != "win32" or winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, APP_REG_NAME)
            return bool(val)
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"[Autostart] Gagal membaca registry startup: {e}", flush=True)
        return False


def set_autostart(enabled: bool) -> bool:
    """Mengaktifkan atau menonaktifkan auto-launch saat Windows dinyalakan."""
    if sys.platform != "win32" or winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                cmd = _get_launch_command()
                winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)
                print(f"[Autostart] Diaktifkan di registry: {cmd}", flush=True)
            else:
                try:
                    winreg.DeleteValue(key, APP_REG_NAME)
                    print("[Autostart] Dinonaktifkan dari registry startup.", flush=True)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"[Autostart] Gagal memperbarui registry startup: {e}", flush=True)
        return False
