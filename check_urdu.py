"""
Script to check if the Alquran.cloud API has Urdu translations.
"""
import requests

def check_urdu_availability():
    """Checks available Urdu translation editions."""
    BASE_URL = "https://api.alquran.cloud/v1"
    
    print("🔍 Checking Alquran.cloud for Urdu translations...")
    
    # This endpoint lists all available 'editions' (translations/recitations)
    editions_url = f"{BASE_URL}/edition?language=ur&type=translation"
    
    try:
        response = requests.get(editions_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            urdu_editions = data.get('data', [])
            
            if urdu_editions:
                print(f"✅ SUCCESS: Found {len(urdu_editions)} Urdu edition(s).\n")
                print("Available Urdu editions (identifier - name):")
                print("-" * 40)
                for edition in urdu_editions:
                    # The 'identifier' is what you use in the API URL (e.g., ur.maududi)
                    print(f"  • {edition['identifier']:20} -> {edition['name']}")
                print(f"\n💡 You can use an identifier like: '{urdu_editions[0]['identifier']}'")
                return True, urdu_editions
            else:
                print("❌ No Urdu translation editions found in Alquran.cloud.")
                return False, []
        else:
            print(f"⚠️ Could not reach the editions API. Status: {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")
        return False, []

if __name__ == "__main__":
    available, editions = check_urdu_availability()