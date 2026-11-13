import os
import sys

def setup_cuda_environment():
    """
    Menambahkan DLL CUDA/cuDNN dari paket pip nvidia di virtual environment
    ke path pencarian DLL Windows agar CTranslate2 / faster-whisper dapat
    memanfaatkan akselerasi GPU NVIDIA RTX secara otomatis.
    """
    if sys.platform != "win32":
        return

    # Cari direktori site-packages
    base_dirs = []
    # 1. Site-packages di Python aktif / venv
    for p in sys.path:
        if "site-packages" in p and os.path.exists(p):
            base_dirs.append(p)
            
    # 2. Site-packages relatif terhadap root project
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_site_packages = os.path.join(current_dir, "venv", "Lib", "site-packages")
    if os.path.exists(project_site_packages) and project_site_packages not in base_dirs:
        base_dirs.append(project_site_packages)

    for sp in base_dirs:
        nvidia_dir = os.path.join(sp, "nvidia")
        if os.path.exists(nvidia_dir):
            for root, dirs, _ in os.walk(nvidia_dir):
                if "bin" in dirs:
                    bin_path = os.path.join(root, "bin")
                    try:
                        os.add_dll_directory(bin_path)
                    except Exception:
                        pass
                    if bin_path not in os.environ.get("PATH", ""):
                        os.environ["PATH"] = bin_path + os.pathsep + os.environ.get("PATH", "")
