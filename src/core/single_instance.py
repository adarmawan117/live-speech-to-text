import sys
import ctypes
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

SINGLE_INSTANCE_SERVER_NAME = "LiveSpeechToText_SingleInstance_Server"

class SingleInstanceController(QObject):
    """
    Manajer Single Instance menggunakan QLocalServer & QLocalSocket (Windows Named Pipes).
    Memastikan hanya ada satu proses Live Speech to Text yang berjalan di sistem.
    Jika instance baru dijalankan saat aplikasi sudah aktif:
    1. Memberi tahu instance pertama untuk membuka & mengangkat jendela ke depan.
    2. Instance kedua langsung keluar secara bersih.
    """
    message_received = pyqtSignal(str)

    def __init__(self, server_name: str = SINGLE_INSTANCE_SERVER_NAME, parent=None):
        super().__init__(parent)
        self.server_name = server_name
        self.server = None

    def is_another_instance_running(self) -> bool:
        """
        Mengecek apakah sudah ada instance aplikasi yang sedang aktif berjalan.
        Jika ada, kirim perintah 'ACTIVATE' ke instance tersebut dan return True.
        """
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(500):
            # Izinkan proses utama memanggil SetForegroundWindow di Windows
            if sys.platform == "win32":
                try:
                    ctypes.windll.user32.AllowSetForegroundWindow(-1)
                except Exception:
                    pass

            socket.write(b"ACTIVATE\n")
            socket.waitForBytesWritten(1000)
            socket.flush()
            socket.disconnectFromServer()
            return True
        return False

    def start_server(self) -> bool:
        """
        Memulai server lokal (Windows Named Pipe) untuk mendengarkan panggilan instance baru.
        """
        # Bersihkan sisa server dari crash lama jika ada
        QLocalServer.removeServer(self.server_name)
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self._handle_new_connection)
        return self.server.listen(self.server_name)

    def _handle_new_connection(self):
        """Menangani koneksi dari instance kedua yang baru diluncurkan."""
        client = self.server.nextPendingConnection()
        if not client:
            return

        # Langsung pancarkan sinyal aktivasi agar instance pertama tampil tanpa jeda
        self.message_received.emit("ACTIVATE")

        def _cleanup():
            try:
                client.readAll()
            except Exception:
                pass
            client.deleteLater()

        client.readyRead.connect(_cleanup)
        client.disconnected.connect(_cleanup)

    def cleanup(self):
        """Menutup server lokal saat aplikasi berhenti."""
        if self.server is not None:
            self.server.close()
            QLocalServer.removeServer(self.server_name)
            self.server = None
