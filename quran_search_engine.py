# quran_search_engine.py
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class QuranSearchEngine:
    def __init__(self, quran_client):
        self.client = quran_client
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, effective model
        self.verses = []
        self.embeddings = None
        print("🧠 Initializing Quran Search Engine...")
        
    def build_database(self):
        """Load all Quran verses and prepare for semantic search"""
        print("📚 Building verse database...")
        
        all_verses = []
        for surah_num in range(1, 115):  # All 114 surahs
            surah_data = self.client.get_surah(surah_num)
            if surah_data['success']:
                for verse in surah_data['verses']:
                    # Create searchable text: Combine Arabic + English + Urdu for better understanding
                    search_text = f"{verse['arabic']} {verse['english']} {verse.get('urdu', '')}"
                    all_verses.append({
                        'surah': surah_num,
                        'ayah': verse['number'],
                        'arabic': verse['arabic'],
                        'english': verse['english'],
                        'urdu': verse.get('urdu', ''),
                        'search_text': search_text,
                        'reference': f"{surah_num}:{verse['number']}"
                    })
        
        self.verses = all_verses
        print(f"✅ Loaded {len(self.verses)} verses")
        
        # Create embeddings (numerical representations of text meaning)
        print("🔢 Creating semantic embeddings...")
        texts = [v['search_text'] for v in self.verses]
        self.embeddings = self.model.encode(texts)
        print("🚀 Quran Search Engine is ready!")
    
    def search(self, question: str, top_k: int = 5):
        """Find the most semantically similar verses to the question"""
        # Convert question to embedding
        question_embedding = self.model.encode([question])
        
        # Calculate similarity scores
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        # Get indices of top matches
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Prepare results
        results = []
        for idx in top_indices:
            verse = self.verses[idx]
            results.append({
                **verse,
                'similarity_score': float(similarities[idx]),
                'confidence_percent': f"{similarities[idx] * 100:.1f}%"
            })
        
        return results
    
    # ADD THESE TWO NEW METHODS BELOW:
    def save_embeddings(self, path='quran_embeddings.npz'):
        """Save embeddings to file for fast loading later"""
        if self.embeddings is None:
            print("❌ No embeddings to save. Build database first.")
            return False
            
        verses_json = json.dumps(self.verses, ensure_ascii=False)
        
        np.savez_compressed(
            path,
            embeddings=self.embeddings,
            verses=verses_json
        )
        print(f"💾 Saved {len(self.verses)} verse embeddings to {path}")
        return True
    
    def load_embeddings(self, path='quran_embeddings.npz'):
        """Load embeddings from file"""
        try:
            data = np.load(path, allow_pickle=True)
            self.embeddings = data['embeddings']
            
            verses_json = str(data['verses'])
            self.verses = json.loads(verses_json)
            
            print(f"📂 Loaded {len(self.verses)} verses with pre-computed embeddings")
            return True
        except Exception as e:
            print(f"❌ Could not load embeddings: {e}")
            return False