"""
ISLAM-GPT PROFESSIONAL BACKEND
Now with Semantic Search for Quran Questions
"""

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from quran_api import QuranAPIClient  # Our professional client
from quran_search_engine import QuranSearchEngine  # NEW: Semantic search engine
import os
import re

# Initialize FastAPI
app = FastAPI(title="Islam-GPT Professional", version="2.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our Quran API client
print("🚀 Starting Islam-GPT Quran QA System...")
quran_client = QuranAPIClient()

# NEW: Initialize semantic search engine
print("🧠 Initializing Quran Semantic Search Engine...")
search_engine = QuranSearchEngine(quran_client)

# NEW: Check if embeddings already exist
EMBEDDINGS_FILE = "quran_embeddings.npz"
if os.path.exists(EMBEDDINGS_FILE):
    print("📂 Loading pre-computed embeddings...")
    search_engine.load_embeddings(EMBEDDINGS_FILE)
else:
    print("⚙️ Building search database for the first time...")
    print("This will take 2-3 minutes. Please wait...")
    search_engine.build_database()
    search_engine.save_embeddings(EMBEDDINGS_FILE)
    print("✅ Search database built and saved!")

print("✅ System ready! Quran QA engine loaded")

# Request model
class QuestionRequest(BaseModel):
    question: str

# Para/Juz metadata (30 Paras/Juz in Quran)
PARA_BOUNDARIES = {
    1: (1, 1),    # Al-Fatiha 1:1
    2: (2, 142),  # Al-Baqarah 2:142
    3: (2, 253),  # Al-Baqarah 2:253 (Ayat-ul-Kursi is in Para 3)
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
    """Get Para/Juz information for a verse"""
    for para in range(30, 0, -1):
        boundary_surah, boundary_verse = PARA_BOUNDARIES[para]
        
        if surah_number > boundary_surah:
            return {
                "para_number": para,
                "juz_number": para,
                "arabic_name": PARA_NAMES.get(para, ""),
                "display": f"Para {para} ({PARA_NAMES.get(para, '')}) • Juz {para}"
            }
        elif surah_number == boundary_surah and verse_number >= boundary_verse:
            return {
                "para_number": para,
                "juz_number": para,
                "arabic_name": PARA_NAMES.get(para, ""),
                "display": f"Para {para} ({PARA_NAMES.get(para, '')}) • Juz {para}"
            }
    
    return {
        "para_number": 1,
        "juz_number": 1,
        "arabic_name": PARA_NAMES.get(1, ""),
        "display": f"Para 1 ({PARA_NAMES.get(1, '')}) • Juz 1"
    }

# Helper functions
def detect_surah_number(question: str) -> int:
    """Detect which Surah the user is asking about - FIXED VERSION"""
    question_lower = question.lower()
    
    # ===== SPECIAL HANDLING FOR SIMILAR SURAH NAMES =====
    # Surah An-Nasr (110) - Help/Victory
    if "nasr" in question_lower or "نصر" in question_lower:
        # Make sure it's not just "nas"
        if "nasr" in question_lower or "نصر" in question_lower:
            print(f"   📍 Detected: Surah An-Nasr (110)")
            return 110
    
    # Surah An-Nas (114) - Mankind
    if "nas" in question_lower or "الناس" in question_lower:
        # Check if it's NOT "nasr"
        if "nasr" not in question_lower and "نصر" not in question_lower:
            print(f"   📍 Detected: Surah An-Nas (114)")
            return 114
    
    # Surah Al-Ikhlas (112)
    if "ikhlas" in question_lower or "الاخلاص" in question_lower or "sincerity" in question_lower:
        return 112
    
    # Surah Al-Falaq (113)
    if "falaq" in question_lower or "الفلق" in question_lower or "daybreak" in question_lower:
        return 113
    
    # ===== JUZZ 30 SURAHS (Common ones) =====
    juzz30_surahs = {
        "kafirun": 109, "الكافرون": 109, "disbelievers": 109,
        "kauthar": 108, "الكوثر": 108, "abundance": 108,
        "maun": 107, "الماعون": 107, "small kindness": 107,
        "quraish": 106, "قريش": 106,
        "fil": 105, "الفيل": 105, "elephant": 105,
        "humazah": 104, "الهمزة": 104, "slanderer": 104,
        "asr": 103, "العصر": 103, "time": 103,
        "takathur": 102, "التكاثر": 102, "rivalry": 102,
        "qariah": 101, "القارعة": 101, "calamity": 101,
        "adiyat": 100, "العاديات": 100, "chargers": 100,
        "zalzalah": 99, "الزلزلة": 99, "earthquake": 99,
        "bayyinah": 98, "البينة": 98, "clear evidence": 98,
        "qadr": 97, "القدر": 97, "power": 97,
        "alaq": 96, "العلق": 96, "clot": 96,
        "tin": 95, "التين": 95, "fig": 95,
        "sharh": 94, "الشرح": 94, "comfort": 94,
        "duha": 93, "الضحى": 93, "morning light": 93,
        "layl": 92, "الليل": 92, "night": 92,
        "shams": 91, "الشمس": 91, "sun": 91,
        "balad": 90, "البلد": 90, "city": 90,
        "fajr": 89, "الفجر": 89, "dawn": 89,
        "ghashiyah": 88, "الغاشية": 88, "overwhelming": 88,
        "ala": 87, "الأعلى": 87, "most high": 87,
        "tariq": 86, "الطارق": 86, "nightcomer": 86,
        "buruj": 85, "البروج": 85, "constellations": 85,
        "inshiqaq": 84, "الانشقاق": 84, "splitting open": 84,
        "mutaffifin": 83, "المطففين": 83, "defrauding": 83,
        "infitar": 82, "الانفطار": 82, "cleaving": 82,
        "takwir": 81, "التكوير": 81, "wrapping": 81,
        "abasa": 80, "عبس": 80, "he frowned": 80,
        "naziat": 79, "النازعات": 79, "those who drag": 79,
        "naba": 78, "النبأ": 78, "news": 78,
    }
    
    for pattern, surah_num in juzz30_surahs.items():
        if pattern in question_lower:
            return surah_num
    
    # ===== FAMOUS SURAHS =====
    famous_surahs = {
        "fatiha": 1, "الفاتحة": 1, "opening": 1,
        "baqarah": 2, "البقرة": 2, "cow": 2,
        "imran": 3, "عمران": 3,
        "nisa": 4, "النساء": 4, "women": 4,
        "maidah": 5, "المائدة": 5, "table": 5,
        "anaam": 6, "الأنعام": 6, "cattle": 6,
        "araf": 7, "الأعراف": 7,
        "anfal": 8, "الأنفال": 8,
        "tawbah": 9, "التوبة": 9, "repentance": 9,
        "yunus": 10, "يونس": 10,
        "hud": 11, "هود": 11,
        "yusuf": 12, "يوسف": 12, "joseph": 12,
        "raad": 13, "الرعد": 13, "thunder": 13,
        "ibrahim": 14, "إبراهيم": 14, "abraham": 14,
        "hijr": 15, "الحجر": 15,
        "nahl": 16, "النحل": 16, "bee": 16,
        "isra": 17, "الإسراء": 17, "night journey": 17,
        "kahf": 18, "الكهف": 18, "cave": 18,
        "maryam": 19, "مريم": 19, "mary": 19,
        "taha": 20, "طه": 20,
        "anbiya": 21, "الأنبياء": 21, "prophets": 21,
        "hajj": 22, "الحج": 22, "pilgrimage": 22,
        "muminun": 23, "المؤمنون": 23, "believers": 23,
        "nur": 24, "النور": 24, "light": 24,
        "furqan": 25, "الفرقان": 25, "criterion": 25,
        "shuara": 26, "الشعراء": 26, "poets": 26,
        "naml": 27, "النمل": 27, "ant": 27,
        "qasas": 28, "القصص": 28, "story": 28,
        "ankabut": 29, "العنكبوت": 29, "spider": 29,
        "rum": 30, "الروم": 30, "romans": 30,
        "luqman": 31, "لقمان": 31,
        "sajdah": 32, "السجدة": 32, "prostration": 32,
        "ahzab": 33, "الأحزاب": 33, "confederates": 33,
        "saba": 34, "سبأ": 34, "sheba": 34,
        "fatir": 35, "فاطر": 35, "originator": 35,
        "yaseen": 36, "يس": 36, "ya sin": 36,
        "saffat": 37, "الصافات": 37,
        "sad": 38, "ص": 38,
        "zumar": 39, "الزمر": 39,
        "ghafir": 40, "غافر": 40, "forgiver": 40,
        "fussilat": 41, "فصلت": 41,
        "shura": 42, "الشورى": 42,
        "zukhruf": 43, "الزخرف": 43,
        "dukhan": 44, "الدخان": 44,
        "jathiyah": 45, "الجاثية": 45,
        "ahqaf": 46, "الأحقاف": 46,
        "muhammad": 47, "محمد": 47,
        "fath": 48, "الفتح": 48, "victory": 48,
        "hujurat": 49, "الحجرات": 49,
        "qaf": 50, "ق": 50,
        "dhariyat": 51, "الذاريات": 51,
        "tur": 52, "الطور": 52,
        "najm": 53, "النجم": 53,
        "qamar": 54, "القمر": 54,
        "rahman": 55, "الرحمن": 55, "beneficent": 55,
        "waqiah": 56, "الواقعة": 56, "event": 56,
        "hadid": 57, "الحديد": 57,
        "mujadila": 58, "المجادلة": 58,
        "hashr": 59, "الحشر": 59,
        "mumtahina": 60, "الممتحنة": 60,
        "saff": 61, "الصف": 61,
        "jumuah": 62, "الجمعة": 62,
        "munafiqun": 63, "المنافقون": 63,
        "taghabun": 64, "التغابن": 64,
        "talaq": 65, "الطلاق": 65,
        "tahrim": 66, "التحريم": 66,
        "mulk": 67, "الملك": 67, "sovereignty": 67,
        "qalam": 68, "القلم": 68,
        "haqqah": 69, "الحاقة": 69,
        "maarij": 70, "المعارج": 70,
        "nuh": 71, "نوح": 71,
        "jinn": 72, "الجن": 72,
        "muzzammil": 73, "المزمل": 73,
        "muddaththir": 74, "المدثر": 74,
        "qiyamah": 75, "القيامة": 75,
        "insan": 76, "الإنسان": 76,
        "mursalat": 77, "المرسلات": 77,
    }
    
    for pattern, surah_num in famous_surahs.items():
        if pattern in question_lower:
            return surah_num
    
    # Try to extract number
    numbers = re.findall(r'\d+', question)
    if numbers:
        num = int(numbers[0])
        if 1 <= num <= 114:
            return num
    
    return 0

def extract_verse_range(question: str):
    """Extract verse range from question"""
    question_lower = question.lower()
    
    if "255" in question_lower:
        return (255, 255)
    
    patterns = [
        r'verse\s*(\d+)\s*[-–]\s*(\d+)',
        r'verses\s*(\d+)\s*[-–]\s*(\d+)',
        r'ayah\s*(\d+)\s*[-–]\s*(\d+)',
        r'ayat\s*(\d+)\s*[-–]\s*(\d+)',
        r'(\d+)\s*[-–]\s*(\d+)',
        r'verse\s*(\d+)\s*to\s*(\d+)',
        r'verses\s*(\d+)\s*to\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question_lower)
        if match:
            try:
                start = int(match.group(1))
                end = int(match.group(2))
                if start > 0 and end >= start:
                    return (start, end)
            except:
                pass
    
    single_patterns = [
        r'verse\s*(\d+)',
        r'ayah\s*(\d+)',
        r'ayat\s*(\d+)',
    ]
    
    for pattern in single_patterns:
        match = re.search(pattern, question_lower)
        if match:
            try:
                verse_num = int(match.group(1))
                if verse_num > 0:
                    return (verse_num, verse_num)
            except:
                pass
    
    return None

def format_surah_response(surah_data, question):
    """Create a beautiful, professional response"""
    if not surah_data['success']:
        return "I couldn't retrieve this Surah at the moment."
    
    response = f"# 📖 {surah_data['arabic_name']} ({surah_data['english_name']})\n\n"
    response += f"**Chapter {surah_data['surah_number']}** • "
    response += f"{surah_data['revelation_type']} Revelation • "
    response += f"{surah_data['verses_count']} Verses\n\n"
    
    verse_range = extract_verse_range(question)
    
    if verse_range:
        start_verse, end_verse = verse_range
        start_verse = max(1, start_verse)
        end_verse = min(surah_data['verses_count'], end_verse)
        
        if start_verse <= end_verse:
            para_info = get_para_info(surah_data['surah_number'], start_verse)
            response += f"**📍 {para_info['display']}**\n\n"
            response += f"## Verses {start_verse}-{end_verse}:\n\n"
            
            for verse in surah_data['verses'][start_verse-1:end_verse]:
                response += f"**{verse['number']}.** {verse['arabic']}\n"
                response += f"*English:* {verse['english'][:120]}...\n"
                if verse.get('urdu'):
                    response += f"*Urdu:* {verse.get('urdu', '')[:100]}...\n"
                response += "\n"
        else:
            para_info = get_para_info(surah_data['surah_number'], 1)
            response += f"**📍 {para_info['display']}**\n\n"
            response += "## Opening Verses:\n\n"
            for verse in surah_data['verses'][:3]:
                response += f"**{verse['number']}.** {verse['arabic']}\n"
                response += f"*English:* {verse['english'][:120]}...\n"
                if verse.get('urdu'):
                    response += f"*Urdu:* {verse.get('urdu', '')[:100]}...\n"
                response += "\n"
    else:
        para_info = get_para_info(surah_data['surah_number'], 1)
        response += f"**📍 {para_info['display']}**\n\n"
        response += "## Preview (First 3 verses):\n\n"
        for verse in surah_data['verses'][:3]:
            response += f"**{verse['number']}.** {verse['arabic']}\n"
            response += f"*English:* {verse['english'][:120]}...\n"
            if verse.get('urdu'):
                response += f"*Urdu:* {verse.get('urdu', '')[:100]}...\n"
            response += "\n"
        
        if surah_data['verses_count'] > 3:
            response += f"*This Surah has {surah_data['verses_count']} verses total.*\n"
            response += "*To see more, ask for specific verses.*\n"
    
    response += "---\n"
    response += "*Powered by Alquran.cloud API • Data cached for fast response*"
    
    return response

def format_semantic_response(question: str, results: list, confidence_threshold: float = 0.3):
    """Format semantic search results - SIMPLE CLEAN FORMAT"""
    
    # Show top 5 results
    display_results = results[:5] if results else []
    
    if not display_results:
        return f"No verses found for: '{question}'"
    
    response = f"Results for: '{question}'\n\n"
    response += "=" * 50 + "\n\n"
    
    for i, result in enumerate(display_results, 1):
        response += f"{i}. {result['reference']} (Relevance: {result['confidence_percent']})\n"
        response += f"   Arabic: {result['arabic']}\n"
        response += f"   English: {result['english'][:150]}...\n"
        
        if result.get('urdu') and result['urdu'] != "اردو ترجمہ دستیاب نہیں":
            response += f"   Urdu: {result['urdu'][:100]}...\n"
        
        response += "\n"
    
    response += "=" * 50 + "\n"
    response += f"Found {len(results)} relevant verses"
    
    return response
def format_low_confidence_preview(question: str, results):
    """Show preview even for low-confidence results"""
    if not results:
        return f"## 📖 About '{question}'\n\nNo related verses found in the Quran."
    
    response = f"## 📖 About '{question}'\n\n"
    response += "*The Quran doesn't contain explanatory verses like 'Surah X is...'. Here are some related verses:*\n\n"
    
    for i, result in enumerate(results[:3], 1):
        para_info = get_para_info(result['surah'], result['ayah'])
        
        response += f"**{i}. {result['reference']}** (Similarity: {result['confidence_percent']})\n"
        response += f"   *Location:* {para_info['display']}\n"
        response += f"   *Arabic:* {result['arabic'][:60]}...\n"
        response += f"   *English:* {result['english'][:80]}...\n\n"
    
    response += "---\n"
    response += f"*Showing top {len(results)} related verses (low confidence match)*\n"
    response += "*For specific verses, ask 'Show me Surah [name] verse [number]'*"
    
    return response

def format_keyword_response(question: str, results: list):
    """Fallback response for keyword search"""
    if not results:
        return "I couldn't find specific verses for your question. Try asking about a specific Surah or topic."
    
    response = f"## 🔍 Search Results for: '{question}'\n\n"
    
    for i, result in enumerate(results[:5], 1):
        verse_key = result.get('verse_key', '')
        if ':' in verse_key:
            surah_num, verse_num = verse_key.split(':')
            try:
                para_info = get_para_info(int(surah_num), int(verse_num))
                location = f" ({para_info['display']})"
            except:
                location = ""
        else:
            location = ""
        
        response += f"**{i}. {result.get('surah_name', 'Surah')} {verse_key}{location}**\n"
        response += f"{result.get('text', '')[:150]}...\n\n"
    
    response += "---\n"
    response += "*Search results from Quranic texts*"
    
    return response

# ==================== MAIN ASK ENDPOINT ====================
# ==================== MAIN ASK ENDPOINT ====================
@app.post("/ask")
def ask_question(request: QuestionRequest, confidence_threshold: float = 0.3):
    # Clean the question
    cleaned_question = request.question.strip().strip('"').strip("'")
    question_lower = cleaned_question.lower()
    
    print(f"\n📥 Question: '{cleaned_question}'")
    
    # ============ STEP 1: AYAT-UL-KURSI ============
    if ("ayat" in question_lower and "kursi" in question_lower) or \
       ("255" in question_lower and "baqarah" in question_lower) or \
       ("throne" in question_lower) or \
       ("ayatul" in question_lower):
        
        print(f"   🕌 SPECIAL: Ayat-ul-Kursi")
        verse_data = quran_client.get_specific_verse(2, 255)
        if verse_data['success']:
            para_info = get_para_info(2, 255)
            response = f"# 🕌 Ayat-ul-Kursi (The Throne Verse)\n\n**Surah Al-Baqarah (2), Verse 255**\n**📍 {para_info['display']}**\n\n**Arabic:**\n{verse_data['arabic']}\n\n**English:**\n{verse_data['english']}\n\n"
            if verse_data.get('urdu'):
                response += f"**Urdu:**\n{verse_data['urdu']}\n\n"
            response += "---\n*The greatest verse in the Quran*"
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "special",
                "surah_number": 2,
                "verse_number": 255,
                "timestamp": "2024"
            }
    
    # ============ RAMADAN SPECIAL ============
    if "ramadan" in question_lower or "fast" in question_lower or "صيام" in question_lower:
        verse_data = quran_client.get_specific_verse(2, 185)
        if verse_data['success']:
            para_info = get_para_info(2, 185)
            response = f"# 🌙 Ramadan in Islam\n\n"
            response += f"**Surah Al-Baqarah (2), Verse 185**\n"
            response += f"**📍 {para_info['display']}**\n\n"
            response += f"**Arabic:**\n{verse_data['arabic']}\n\n"
            response += f"**English:**\n{verse_data['english']}\n\n"
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "topic_special",
                "timestamp": "2024"
            }
    
    # ============ STEP 2: SURAH DETECTION ============
    surah_number = detect_surah_number(cleaned_question)
    
    # ============ STEP 3: WHAT IS SURAH X? ============
    if surah_number > 0 and ("what is surah" in question_lower or "tell me about surah" in question_lower or "explain surah" in question_lower):
        print(f"   📖 Showing Surah {surah_number} (What is Surah request)")
        surah_data = quran_client.get_surah(surah_number)
        if surah_data['success']:
            response = f"# 📖 {surah_data['arabic_name']} ({surah_data['english_name']})\n\n"
            response += f"**Chapter {surah_data['surah_number']}** • {surah_data['revelation_type']} Revelation • {surah_data['verses_count']} Verses\n\n"
            
            para_info = get_para_info(surah_number, 1)
            response += f"**📍 {para_info['display']}**\n\n"
            response += f"## Full Surah: {surah_data['english_name']}\n\n"
            
            for verse in surah_data['verses']:
                response += f"**{verse['number']}.** {verse['arabic']}\n"
                response += f"*English:* {verse['english']}\n"
                if verse.get('urdu'):
                    response += f"*Urdu:* {verse['urdu']}\n"
                response += "\n"
            
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "surah_explanation",
                "surah_number": surah_number,
                "timestamp": "2024"
            }
    
    # ============ STEP 4: SHOW ME SURAH X ============
    wants_to_see = any(word in question_lower for word in ["show me", "display", "view", "see", "verses"])
    if surah_number > 0 and wants_to_see:
        print(f"   📖 Showing Surah {surah_number} (full)")
        surah_data = quran_client.get_surah(surah_number)
        if surah_data['success']:
            # Get Para/Juz information
            para_info = get_para_info(surah_number, 1)
            
            # Build the response header
            response = f"""📖 سُورَةُ {surah_data['arabic_name']} ({surah_data['english_name']})
Chapter {surah_data['surah_number']} • {surah_data['revelation_type']} Revelation • {surah_data['verses_count']} Verses

📍 {para_info['display']}

"""
            # Add Bismillah on separate line with translation (for all Surahs except At-Tawbah 9)
            if surah_number != 9:
                response += """بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
In the name of Allah, the Entirely Merciful, the Especially Merciful

"""
            # Loop through ALL verses with complete text (no truncation)
            for verse in surah_data['verses']:
                response += f"{verse['number']}. {verse['arabic']}\n"
                response += f"English: {verse['english']}\n"
                if verse.get('urdu') and verse['urdu'] != "اردو ترجمہ دستیاب نہیں":
                    response += f"Urdu: {verse['urdu']}\n"
                response += "\n"
            
            # Add footer
            response += "---\n"
            response += "*Powered by Alquran.cloud API*"
            
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "full_surah",
                "surah_number": surah_number,
                "timestamp": "2024"
            }
    
    # ============ STEP 5: SPECIFIC VERSE (X:Y) ============
    pattern1 = re.search(r'(?:surah\s*)?(\d+)[:\s](\d+)', question_lower)
    if pattern1:
        s_num = int(pattern1.group(1))
        v_num = int(pattern1.group(2))
        print(f"   🎯 Verse: {s_num}:{v_num}")
        verse_data = quran_client.get_specific_verse(s_num, v_num)
        if verse_data['success']:
            response = f"# 📖 {verse_data['surah_name_arabic']} ({verse_data['surah_name']})\n\n**Verse {verse_data['verse_number']}**\n\n**Arabic:**\n{verse_data['arabic']}\n\n**English:**\n{verse_data['english']}\n\n"
            if verse_data.get('urdu'):
                response += f"**Urdu:**\n{verse_data['urdu']}\n\n"
            response += "---\n*Exact verse*"
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "exact_verse",
                "surah_number": s_num,
                "verse_number": v_num,
                "timestamp": "2024"
            }
    
    # ============ STEP 6: VERSE FROM SURAH NAME ============
    verse_range = extract_verse_range(cleaned_question)
    if surah_number > 0 and verse_range and verse_range[0] == verse_range[1]:
        v_num = verse_range[0]
        print(f"   🎯 Verse: {surah_number}:{v_num}")
        verse_data = quran_client.get_specific_verse(surah_number, v_num)
        if verse_data['success']:
            response = f"# 📖 {verse_data['surah_name_arabic']} ({verse_data['surah_name']})\n\n**Verse {verse_data['verse_number']}**\n\n**Arabic:**\n{verse_data['arabic']}\n\n**English:**\n{verse_data['english']}\n\n"
            if verse_data.get('urdu'):
                response += f"**Urdu:**\n{verse_data['urdu']}\n\n"
            response += "---\n*Exact verse*"
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "exact_verse",
                "surah_number": surah_number,
                "verse_number": v_num,
                "timestamp": "2024"
            }
    
    # ============ STEP 6.5: LAST PROPHET SPECIAL HANDLING ============
    if "last prophet" in question_lower or "final prophet" in question_lower or "seal of prophets" in question_lower:
        print(f"   🕌 SPECIAL: Last Prophet query")
        verse_data = quran_client.get_specific_verse(33, 40)
        if verse_data['success']:
            response = f"## The Last Prophet in Quran\n\n"
            response += f"**Surah Al-Ahzab (33), Verse 40**\n\n"
            response += f"Arabic: {verse_data['arabic']}\n\n"
            response += f"English: {verse_data['english']}\n\n"
            if verse_data.get('urdu'):
                response += f"Urdu: {verse_data['urdu']}\n\n"
            response += "This verse clearly states that Prophet Muhammad (ﷺ) is the last and final prophet."
            return {
                "question": cleaned_question,
                "answer": response,
                "type": "last_prophet",
                "timestamp": "2024"
            }
    
    # ============ STEP 7: SEMANTIC SEARCH ============
    print(f"   🔍 Semantic search...")
    try:
        semantic_results = search_engine.search(cleaned_question, top_k=20)
        if semantic_results:
            formatted = format_semantic_response(
                cleaned_question,
                semantic_results,
                confidence_threshold=0.3
            )
            return {
                "question": cleaned_question,
                "answer": formatted,
                "type": "semantic_search",
                "timestamp": "2024"
            }
    except Exception as e:
        print(f"Semantic search failed: {e}")
    
    # ============ STEP 8: KEYWORD SEARCH ============
    print(f"   🔍 Keyword search...")
    search_results = quran_client.search_verses(cleaned_question)
    if search_results:
        response = f"## 🔍 Search Results for: '{cleaned_question}'\n\n"
        for i, r in enumerate(search_results[:5], 1):
            verse_key = r.get('verse_key', '')
            response += f"**{i}. {r.get('surah_name', 'Surah')} {verse_key}**\n"
            response += f"{r.get('text', '')}\n\n"
        return {
            "question": cleaned_question,
            "answer": response,
            "type": "keyword_search",
            "timestamp": "2024"
        }
    
    # ============ STEP 9: NO RESULTS ============
    return {
        "question": cleaned_question,
        "answer": "No verses found. Try a different question.",
        "type": "no_results",
        "timestamp": "2024"
    }
@app.get("/")
def home():
    """Homepage with system info"""
    return {
        "system": "Islam-GPT Professional v2.0",
        "status": "✅ Operational",
        "features": [
            "Quran Semantic Search (AI-powered)",
            "Arabic text with English & Urdu translations",
            "Para/Juz information",
            "Smart Surah detection",
            "Exact verse lookup"
        ],
        "endpoints": {
            "ask_question": "POST /ask",
            "api_docs": "http://localhost:8000/docs",
            "test_surah": "GET /test/{surah_number}",
            "cache_stats": "GET /cache-stats"
        },
        "data_source": "Alquran.cloud API + Semantic AI"
    }

@app.get("/surah/{surah_number}")
def get_surah_endpoint(surah_number: int):
    """Return Surah data"""
    if 1 <= surah_number <= 114:
        data = quran_client.get_surah(surah_number)
        if data.get('success'):
            para_info = get_para_info(surah_number, 1)
            data['para_info'] = para_info
        return data
    return {"error": "Surah number must be between 1 and 114"}


@app.get("/para/{para_number}")
def get_para_info_endpoint(para_number: int):
    """Get information about a specific Para/Juz"""
    if 1 <= para_number <= 30:
        boundary_surah, boundary_verse = PARA_BOUNDARIES[para_number]
        next_boundary = PARA_BOUNDARIES.get(para_number + 1, (114, 6))
        
        return {
            "para_number": para_number,
            "juz_number": para_number,
            "arabic_name": PARA_NAMES.get(para_number, ""),
            "starts_at": f"{boundary_surah}:{boundary_verse}",
            "ends_before": f"{next_boundary[0]}:{next_boundary[1]}",
            "display": f"Para {para_number} ({PARA_NAMES.get(para_number, '')}) • Juz {para_number}"
        }
    return {"error": "Para number must be between 1 and 30"}

@app.get("/cache-stats")
def cache_stats():
    """Show cache statistics"""
    import os
    import json
    
    cache_dir = "quran_cache"
    if not os.path.exists(cache_dir):
        return {"status": "No cache found"}
    
    surah_files = [f for f in os.listdir(cache_dir) 
                  if f.startswith('surah_') and f.endswith('.json')]
    
    total_verses = 0
    total_size = 0
    
    for file in surah_files:
        filepath = os.path.join(cache_dir, file)
        total_size += os.path.getsize(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_verses += data.get('verses_count', 0)
        except:
            pass
    
    embeddings_info = {}
    if os.path.exists(EMBEDDINGS_FILE):
        embeddings_info = {
            "embeddings_file": "✅ Found",
            "embeddings_size": f"{os.path.getsize(EMBEDDINGS_FILE)/1024/1024:.1f} MB"
        }
    else:
        embeddings_info = {"embeddings_file": "❌ Not found"}
    
    return {
        **embeddings_info,
        "cached_surahs": len(surah_files),
        "total_surahs": 114,
        "percentage": f"{(len(surah_files)/114)*100:.1f}%",
        "total_verses": total_verses,
        "cache_size_mb": f"{total_size/1024/1024:.1f}",
        "semantic_search": "✅ Ready" if os.path.exists(EMBEDDINGS_FILE) else "⚠️ Needs building"
    }

@app.get("/test-search/{query}")
def test_semantic_search(query: str):
    """Test the semantic search engine"""
    results = search_engine.search(query, top_k=5)
    
    if results:
        formatted = format_semantic_response(query, results, confidence_threshold=0.25)
        return {
            "query": query,
            "results_count": len(results),
            "top_result": {
                "reference": results[0]['reference'],
                "confidence": results[0]['confidence_percent'],
                "arabic_preview": results[0]['arabic'][:50] + "..."
            },
            "formatted_response": formatted
        }
    else:
        return {"query": query, "results_count": 0, "message": "No results found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)