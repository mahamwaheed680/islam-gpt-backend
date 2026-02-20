"""
QURAN PARA/JUZ METADATA
Mapping of verses to their Para/Juz numbers
"""

# Para/Juz boundaries in the Quran
# Format: {para_number: (surah, verse_start)}
PARA_BOUNDARIES = {
    1: (1, 1),    # Al-Fatiha 1:1
    2: (2, 142),  # Al-Baqarah 2:142
    3: (2, 253),  # Al-Baqarah 2:253
    4: (3, 93),   # Al-Imran 3:93
    5: (4, 24),   # An-Nisa 4:24
    6: (4, 148),  # An-Nisa 4:148
    7: (5, 82),   # Al-Ma'idah 5:82
    8: (6, 111),  # Al-An'am 6:111
    9: (7, 88),   # Al-A'raf 7:88
    10: (8, 41),  # Al-Anfal 8:41
    11: (9, 93),  # At-Tawbah 9:93
    12: (11, 6),  # Hud 11:6
    13: (12, 53), # Yusuf 12:53
    14: (15, 1),  # Al-Hijr 15:1
    15: (17, 1),  # Al-Isra 17:1
    16: (18, 75), # Al-Kahf 18:75
    17: (21, 1),  # Al-Anbiya 21:1
    18: (23, 1),  # Al-Mu'minun 23:1
    19: (25, 21), # Al-Furqan 25:21
    20: (27, 56), # An-Naml 27:56
    21: (29, 46), # Al-Ankabut 29:46
    22: (33, 31), # Al-Ahzab 33:31
    23: (36, 28), # Ya-Sin 36:28
    24: (39, 32), # Az-Zumar 39:32
    25: (41, 47), # Fussilat 41:47
    26: (46, 1),  # Al-Ahqaf 46:1
    27: (51, 31), # Adh-Dhariyat 51:31
    28: (58, 1),  # Al-Mujadila 58:1
    29: (67, 1),  # Al-Mulk 67:1
    30: (78, 1),  # An-Naba 78:1
}

# Reverse lookup: Find which Para a verse belongs to
def find_para_for_verse(surah_number: int, verse_number: int) -> int:
    """Find which Para/Juz a verse belongs to"""
    for para in range(30, 0, -1):  # Check from Para 30 down to 1
        boundary_surah, boundary_verse = PARA_BOUNDARIES[para]
        
        if surah_number > boundary_surah:
            return para
        elif surah_number == boundary_surah and verse_number >= boundary_verse:
            return para
    
    return 1  # Default to Para 1

# Para names in Urdu/Arabic/English
PARA_NAMES = {
    1: "آلَیْت",  # Alif Lam Meem
    2: "سَيَقُولُ",  # Sayaqool
    3: "تِلْكَ الرُّسُلُ",  # Tilkar Rusul
    4: "لَنْ تَنَالُوا",  # Lan Tana Loo
    5: "وَالْمُحْصَنَاتُ",  # Wal Mohsanat
    6: "لَا يُحِبُّ اللَّهُ",  # La Yuhibbullah
    7: "وَإِذَا سَمِعُوا",  # Wa Iza Samiu
    8: "وَلَوْ أَنَّنَا",  # Wa Lau Annana
    9: "قَالَ الْمَلَأُ",  # Qalal Malao
    10: "وَاعْلَمُوا",  # Wa A'lamu
    11: "يَعْتَذِرُونَ",  # Ya'taziroon
    12: "وَمَا مِنْ دَابَّةٍ",  # Wa Ma Min Da'abbah
    13: "وَمَا أُبَرِّئُ",  # Wa Ma Ubri
    14: "رُبَمَا",  # Rubama
    15: "سُبْحَانَ الَّذِي",  # Subhanallazi
    16: "قَالَ أَلَمْ",  # Qal Alam
    17: "اقْتَرَبَ",  # Iqtaraba
    18: "قَدْ أَفْلَحَ",  # Qad Aflaha
    19: "وَقَالَ الَّذِينَ",  # Wa Qalallazina
    20: "أَمَّنْ خَلَقَ",  # A'man Khalaq
    21: "اتْلُ مَا أُوحِيَ",  # Utlu Ma Oohi
    22: "وَمَنْ يَقْنُتْ",  # Wa Manyaqnut
    23: "وَمَا لِيَ",  # Wa Mali
    24: "فَمَنْ أَظْلَمُ",  # Faman Azlam
    25: "إِلَيْهِ يُرَدُّ",  # Elahe Yuruddo
    26: "حم",  # Ha'a Meem
    27: "قَالَ فَمَا خَطْبُكُمْ",  # Qala Fama Khatbukum
    28: "قَدْ سَمِعَ اللَّهُ",  # Qad Sami Allah
    29: "تَبَارَكَ",  # Tabarak
    30: "عَمَّ",  # Amma
}

def get_para_info(surah_number: int, verse_number: int):
    """Get complete Para information for a verse"""
    para_number = find_para_for_verse(surah_number, verse_number)
    
    return {
        "para_number": para_number,
        "para_name_arabic": PARA_NAMES.get(para_number, ""),
        "juz_number": para_number,  # Juz = Para in Quran
        "display": f"Para {para_number} ({PARA_NAMES.get(para_number, '')}) • Juz {para_number}"
    }

# Test function
if __name__ == "__main__":
    # Test some verses
    test_cases = [
        (1, 1),    # Para 1
        (2, 142),  # Para 2
        (2, 255),  # Ayat-ul-Kursi - Para 3
        (36, 1),   # Ya-Sin - Para 23
        (78, 1),   # An-Naba - Para 30
    ]
    
    for surah, verse in test_cases:
        info = get_para_info(surah, verse)
        print(f"Surah {surah}:{verse} → {info['display']}")