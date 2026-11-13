import time
import keyboard

class VirtualTypist:
    """
    Melakukan pengetikan virtual secara real-time ke jendela yang sedang aktif.
    Menggunakan algoritma Longest Common Prefix untuk meminimalkan penekanan Backspace.
    """
    def __init__(self):
        self.last_interim = ""

    def type_interim(self, new_text: str):
        """
        Mengetik kata per kata secara streaming.
        Hanya menghapus bagian akhiran jika ada revisi dari Whisper,
        lalu mengetik kata baru.
        """
        if not new_text:
            return

        common_len = 0
        min_len = min(len(self.last_interim), len(new_text))
        while common_len < min_len and self.last_interim[common_len] == new_text[common_len]:
            common_len += 1

        backspaces = len(self.last_interim) - common_len
        to_type = new_text[common_len:]

        # Hapus hanya karakter yang berbeda
        if backspaces > 0:
            for _ in range(backspaces):
                keyboard.send("backspace")
                time.sleep(0.003)

        # Ketik karakter baru
        if to_type:
            keyboard.write(to_type, delay=0.003)

        self.last_interim = new_text

    def commit_phrase(self, final_text: str):
        """
        Mengunci kalimat saat jeda hening terdeteksi.
        Mengetik sisa koreksi, menambahkan spasi, dan mereset buffer interim.
        """
        target_text = final_text.strip() if final_text else self.last_interim.strip()
        if target_text:
            self.type_interim(target_text)
            # Berikan spasi pemisah antar kalimat
            keyboard.write(" ", delay=0.003)

        self.last_interim = ""

    def reset(self):
        """Mereset state pengetikan."""
        self.last_interim = ""

