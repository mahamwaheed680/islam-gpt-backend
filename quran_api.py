"""
PROFESSIONAL QURAN API CLIENT WITH BATCH LOADING
NOW WITH URDU TRANSLATION!
"""

import requests
import json
import os
import time

class QuranAPIClient:
    """Professional client for Alquran.cloud API - 100% free"""
    
    BASE_URL = "https://api.alquran.cloud/v1"
    
    def __init__(self):
        # Create cache folder to store responses
        self.cache_dir = "quran_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        print("✅ Quran API Client ready (with caching & URDU support)")
    
    def _get_from_cache(self, key):
        """Check if we already have this data"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_to_cache(self, key, data):
        """Save data to avoid repeated API calls"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_surah(self, surah_number: int):
        """Get complete Surah with Arabic, English AND Urdu"""
        # Check cache first
        cached = self._get_from_cache(f"surah_{surah_number}")
        if cached:
            print(f"   📁 Using cached Surah {surah_number}")
            return cached
        
        print(f"   🌐 Fetching Surah {surah_number} from API (with Urdu)...")
        time.sleep(0.2)  # Be polite to API server
        
        try:
            # Arabic text
            arabic_url = f"{self.BASE_URL}/surah/{surah_number}/ar.alafasy"
            arabic_response = requests.get(arabic_url, timeout=10)
            
            # English translation
            english_url = f"{self.BASE_URL}/surah/{surah_number}/en.asad"
            english_response = requests.get(english_url, timeout=10)
            
            # URDU translation (Maududi)
            urdu_url = f"{self.BASE_URL}/surah/{surah_number}/ur.maududi"
            urdu_response = requests.get(urdu_url, timeout=10)
            
            if (arabic_response.status_code == 200 and 
                english_response.status_code == 200 and
                urdu_response.status_code == 200):
                
                arabic_data = arabic_response.json()
                english_data = english_response.json()
                urdu_data = urdu_response.json()
                
                # Combine data
                result = {
                    "success": True,
                    "surah_number": surah_number,
                    "arabic_name": arabic_data['data']['name'],
                    "english_name": arabic_data['data']['englishName'],
                    "verses_count": arabic_data['data']['numberOfAyahs'],
                    "revelation_type": arabic_data['data']['revelationType'],
                    "verses": []
                }
                
                # Combine Arabic, English AND Urdu verses
                for i in range(len(arabic_data['data']['ayahs'])):
                    verse = {
                        "number": i + 1,
                        "arabic": arabic_data['data']['ayahs'][i]['text'],
                        "english": english_data['data']['ayahs'][i]['text'],
                        "urdu": urdu_data['data']['ayahs'][i]['text']  # URDU ADDED!
                    }
                    result["verses"].append(verse)
                
                # Save to cache
                self._save_to_cache(f"surah_{surah_number}", result)
                print(f"   ✅ Saved Surah {surah_number} with Urdu")
                return result
                
        except Exception as e:
            print(f"   ⚠️ API error (with Urdu): {e}")
            print(f"   🔄 Falling back to English only...")
            
            # Fallback - without Urdu
            try:
                arabic_url = f"{self.BASE_URL}/surah/{surah_number}/ar.alafasy"
                english_url = f"{self.BASE_URL}/surah/{surah_number}/en.asad"
                arabic_response = requests.get(arabic_url, timeout=10)
                english_response = requests.get(english_url, timeout=10)
                
                if arabic_response.status_code == 200 and english_response.status_code == 200:
                    arabic_data = arabic_response.json()
                    english_data = english_response.json()
                    
                    result = {
                        "success": True,
                        "surah_number": surah_number,
                        "arabic_name": arabic_data['data']['name'],
                        "english_name": arabic_data['data']['englishName'],
                        "verses_count": arabic_data['data']['numberOfAyahs'],
                        "revelation_type": arabic_data['data']['revelationType'],
                        "verses": []
                    }
                    
                    for i in range(len(arabic_data['data']['ayahs'])):
                        verse = {
                            "number": i + 1,
                            "arabic": arabic_data['data']['ayahs'][i]['text'],
                            "english": english_data['data']['ayahs'][i]['text'],
                            "urdu": "اردو ترجمہ دستیاب نہیں"  # Urdu fallback message
                        }
                        result["verses"].append(verse)
                    
                    self._save_to_cache(f"surah_{surah_number}", result)
                    print(f"   ✅ Saved Surah {surah_number} (English only)")
                    return result
            except:
                pass
        
        return {"success": False, "message": "Could not fetch Surah"}
    
    def get_specific_verse(self, surah_number: int, verse_number: int):
        """Get ONE specific verse with Arabic, English AND Urdu"""
        # Check cache first
        cache_key = f"verse_{surah_number}_{verse_number}"
        cached = self._get_from_cache(cache_key)
        if cached:
            print(f"   📁 Using cached verse {surah_number}:{verse_number}")
            return cached
        
        print(f"   🌐 Fetching verse {surah_number}:{verse_number} from API (with Urdu)...")
        
        try:
            # Get specific verse with ALL THREE translations
            url = f"{self.BASE_URL}/ayah/{surah_number}:{verse_number}/editions/ar.alafasy,en.asad,ur.maududi"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200 and len(data['data']) >= 3:
                    verse_data = {
                        "success": True,
                        "surah_number": surah_number,
                        "verse_number": verse_number,
                        "arabic": data['data'][0]['text'],
                        "english": data['data'][1]['text'],
                        "urdu": data['data'][2]['text'],  # URDU ADDED!
                        "surah_name": data['data'][0]['surah']['englishName'],
                        "surah_name_arabic": data['data'][0]['surah']['name']
                    }
                    # Save to cache
                    self._save_to_cache(cache_key, verse_data)
                    print(f"   ✅ Saved verse {surah_number}:{verse_number} with Urdu")
                    return verse_data
        except Exception as e:
            print(f"   ⚠️ API error: {e}")
            
            # Fallback - without Urdu
            try:
                url = f"{self.BASE_URL}/ayah/{surah_number}:{verse_number}/editions/ar.alafasy,en.asad"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data['code'] == 200 and len(data['data']) >= 2:
                        verse_data = {
                            "success": True,
                            "surah_number": surah_number,
                            "verse_number": verse_number,
                            "arabic": data['data'][0]['text'],
                            "english": data['data'][1]['text'],
                            "urdu": "اردو ترجمہ دستیاب نہیں",
                            "surah_name": data['data'][0]['surah']['englishName'],
                            "surah_name_arabic": data['data'][0]['surah']['name']
                        }
                        self._save_to_cache(cache_key, verse_data)
                        return verse_data
            except:
                pass
        
        return {"success": False, "message": "Could not fetch verse"}
    
    def search_verses(self, query: str, limit: int = 5):
        """Search for verses containing keywords"""
        cache_key = f"search_{hash(query)}_{limit}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        print(f"   🔍 Searching Quran for: '{query}'")
        time.sleep(0.3)
        
        try:
            url = f"{self.BASE_URL}/search/{query}/en.asad"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200:
                    results = data['data']['matches'][:limit]
                    self._save_to_cache(cache_key, results)
                    return results
        except:
            pass
        
        return []
    
    # NEW METHOD: Get all available Urdu translations
    def get_urdu_editions(self):
        """Get list of available Urdu translations"""
        try:
            url = f"{self.BASE_URL}/edition?language=ur&type=translation"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200:
                    return data['data']
        except:
            pass
        return []
    
    # NEW METHOD: Load all Surahs
    def load_all_surahs(self, start=1, end=114):
        """Load multiple Surahs into cache at once"""
        print(f"🚀 Loading Surahs {start} to {end} with Urdu translations...")
        print("This will take 3-4 minutes. Please wait...")
        
        loaded_count = 0
        for surah_number in range(start, end + 1):
            print(f"   📖 [{surah_number:3d}/{end}] Loading...", end=" ")
            
            try:
                data = self.get_surah(surah_number)
                if data['success']:
                    loaded_count += 1
                    # Check if Urdu exists
                    if 'urdu' in data['verses'][0]:
                        print(f"✅ {data['arabic_name'][:15]}... (with Urdu)")
                    else:
                        print(f"✅ {data['arabic_name'][:15]}...")
                else:
                    print(f"❌ Failed")
                    
                # Small delay between requests
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:30]}")
                time.sleep(1)
        
        print(f"\n✅ Successfully loaded {loaded_count}/{end-start+1} Surahs!")
        return loaded_count
    
    def get_cache_stats(self):
        """Show statistics about cached Surahs"""
        import os
        cache_files = [f for f in os.listdir(self.cache_dir) 
                      if f.startswith('surah_') and f.endswith('.json')]
        
        print(f"\n📊 CACHE STATISTICS:")
        print(f"   Total cached Surahs: {len(cache_files)}/114")
        
        if cache_files:
            # Get Surah numbers
            numbers = []
            for file in cache_files:
                try:
                    num = int(file.replace('surah_', '').replace('.json', ''))
                    numbers.append(num)
                except:
                    pass
            
            numbers.sort()
            print(f"   Cached Surahs: {numbers[:10]}{'...' if len(numbers) > 10 else ''}")
            
            # Check if Urdu exists
            urdu_count = 0
            for file in cache_files[:5]:  # Check first 5 files
                try:
                    filepath = os.path.join(self.cache_dir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data['verses'] and 'urdu' in data['verses'][0]:
                            urdu_count += 1
                except:
                    pass
            
            if urdu_count > 0:
                print(f"   Urdu translation: ✅ Available")
            else:
                print(f"   Urdu translation: ⚠️ Not found (run load_all_surahs again)")
            
            # Calculate size
            total_size = 0
            for file in cache_files:
                filepath = os.path.join(self.cache_dir, file)
                total_size += os.path.getsize(filepath)
            
            print(f"   Total cache size: {total_size/1024/1024:.1f} MB")
            print(f"   Average per Surah: {total_size/len(cache_files)/1024:.0f} KB")

# Test if it works
if __name__ == "__main__":
    client = QuranAPIClient()
    
    print("\n" + "="*50)
    print("QURAN API CLIENT - TEST MENU")
    print("="*50)
    print("1. Test single Surah (with Urdu)")
    print("2. Load ALL 114 Surahs (with Urdu)")
    print("3. Load first 10 Surahs (quick test with Urdu)")
    print("4. Show cache statistics")
    print("5. Test specific verse (with Urdu)")
    print("6. List available Urdu translations")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        surah_num = input("Enter Surah number (1-114): ").strip()
        try:
            surah_num = int(surah_num)
            test_data = client.get_surah(surah_num)
            if test_data['success']:
                print(f"\n✅ API Test Successful!")
                print(f"Surah: {test_data['arabic_name']} ({test_data['english_name']})")
                print(f"Verses: {test_data['verses_count']}")
                print(f"\nFirst verse Arabic: {test_data['verses'][0]['arabic'][:50]}...")
                print(f"First verse English: {test_data['verses'][0]['english'][:50]}...")
                print(f"First verse Urdu: {test_data['verses'][0]['urdu'][:50]}...")
        except:
            print("Invalid input")
    
    elif choice == "2":
        loaded = client.load_all_surahs(1, 114)
        client.get_cache_stats()
    
    elif choice == "3":
        loaded = client.load_all_surahs(1, 10)
        client.get_cache_stats()
    
    elif choice == "4":
        client.get_cache_stats()
    
    elif choice == "5":
        surah = input("Enter Surah number: ").strip()
        verse = input("Enter Verse number: ").strip()
        try:
            surah = int(surah)
            verse = int(verse)
            verse_data = client.get_specific_verse(surah, verse)
            if verse_data['success']:
                print(f"\n✅ Verse {surah}:{verse}")
                print(f"Surah: {verse_data['surah_name_arabic']} ({verse_data['surah_name']})")
                print(f"\nArabic: {verse_data['arabic']}")
                print(f"\nEnglish: {verse_data['english']}")
                print(f"\nUrdu: {verse_data['urdu']}")
        except:
            print("Invalid input")
    
    elif choice == "6":
        editions = client.get_urdu_editions()
        if editions:
            print(f"\n✅ Found {len(editions)} Urdu translations:")
            for i, edition in enumerate(editions[:10], 1):
                print(f"   {i}. {edition['identifier']} - {edition['name']}")
        else:
            print("❌ No Urdu translations found")
    
    else:
        print("Invalid choice!")