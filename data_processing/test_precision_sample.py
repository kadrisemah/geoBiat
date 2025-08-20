#!/usr/bin/env python3
"""
Test precise geocoding on a sample of doctors
to verify accuracy for distance calculations
"""
import csv
import requests
import time
import json

def test_precise_geocoding_sample():
    """Test precision geocoding on first 10 doctors"""
    
    input_path = 'app/medical_professionals/Data/doctors_geocoded.csv'
    
    print("Testing precise geocoding on sample doctors...")
    
    # Load first 10 doctors
    sample_doctors = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:  # Just first 10
                break
            sample_doctors.append(row)
    
    print(f"Testing {len(sample_doctors)} doctors for address-level precision:")
    
    for i, doctor in enumerate(sample_doctors):
        name = f"{doctor['nom']} {doctor['prenom']}"
        address = doctor['adresse']
        current_coords = f"{doctor['lat']}, {doctor['lon']}"
        
        print(f"\n{i+1}. {name}")
        print(f"   Address: {address}")
        print(f"   Current coords: {current_coords}")
        
        # Try precise geocoding
        try:
            geocode_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{address}, Tunisia",
                'format': 'json',
                'limit': 1,
                'countrycodes': 'tn',
                'addressdetails': 1
            }
            
            headers = {'User-Agent': 'GéoBiat-Test/1.0'}
            
            response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
            time.sleep(1.2)  # Rate limiting
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    result = results[0]
                    precise_lat = float(result['lat'])
                    precise_lon = float(result['lon'])
                    accuracy = result.get('place_rank', 99)
                    
                    print(f"   Precise coords: {precise_lat:.6f}, {precise_lon:.6f}")
                    print(f"   Accuracy level: {accuracy} (lower = better)")
                    
                    if accuracy <= 25:
                        print(f"   ✅ HIGH PRECISION - Ready for distance calculations")
                    elif accuracy <= 30:
                        print(f"   🟡 MEDIUM PRECISION - Good for distance calculations")
                    else:
                        print(f"   🔶 LOW PRECISION - May affect distance accuracy")
                        
                else:
                    print(f"   ❌ No geocoding result found")
            else:
                print(f"   ❌ Geocoding request failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n=== PRECISION TEST SUMMARY ===")
    print("This test shows the difference between:")
    print("• Current coordinates: City-level + small offset")  
    print("• Precise coordinates: Real street-level addresses")
    print("\nFor accurate distance calculations between doctors and banks,")
    print("we need the precise coordinates (building/street level).")

if __name__ == "__main__":
    test_precise_geocoding_sample()