import re

# Karakter tanda baca umum yang sering dihasilkan Whisper secara otomatis
# Titik, koma, tanda tanya, tanda seru, titik dua, titik koma, kutip, ellipsis, kurung, garis miring
_PUNCTUATION_PATTERN = re.compile(r'[\.,\?!:;"\'“”‘’/\\(){}\[\]<>~`@#$%^&*+=|_]')

def clean_stt_punctuation(text: str) -> str:
    """
    Menghilangkan tanda baca dari hasil live transcribe Whisper.
    - Menghilangkan titik, koma, tanda tanya, tanda seru, tanda kutip, dll.
    - Mempertahankan kata berulang dengan tanda hubung (misal: 'teman-teman', 'jalan-jalan').
    - Merapikan spasi ganda.
    """
    if not text:
        return ""

    # Ganti ellipsis dan dash panjang/terpisah dengan spasi
    cleaned = re.sub(r'[\u2014\u2013\u2026]', ' ', text)
    
    # Hapus dash yang berdiri sendiri (bukan di antara kata)
    cleaned = re.sub(r'(?<=\s)-(?=\s)|(?<=\s)-|-(?=\s)', ' ', cleaned)

    # Hapus semua tanda baca umum
    cleaned = _PUNCTUATION_PATTERN.sub('', cleaned)

    # Rapikan spasi ganda
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

