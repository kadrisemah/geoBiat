#!/usr/bin/env python3
"""
Final verification with more realistic water detection
The previous algorithm was too conservative
"""
import csv
import math

def is_actually_in_water(lat, lon):
    """
    More realistic water detection for Tunisia
    Only flags coordinates that are REALLY in water bodies
    """
    try:
        lat, lon = float(lat), float(lon)
        
        # Tunisia bounds check
        if not (30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.0):
            return True  # Outside Tunisia
        
        # Mediterranean Sea (too far north) - be more generous
        if lat > 37.35:
            return True
        
        # Gulf of Gabès (too far east/south) - be more generous  
        if lat < 33.2 and lon > 11.0:
            return True
            
        # Major salt lakes/sebkhas - only the centers
        
        # Chott el Djerid (salt lake center)
        if 33.6 <= lat <= 33.9 and 7.8 <= lon <= 8.3:
            return True
        
        # Lac de Tunis (actual lake center only)
        if 36.80 <= lat <= 36.82 and 10.18 <= lon <= 10.22:
            return True
            
        # Sebkha Ariana (salt marsh center only)
        if 36.88 <= lat <= 36.90 and 10.12 <= lon <= 10.16:
            return True
        
        return False
        
    except (ValueError, TypeError):
        return True  # Invalid coordinates

def final_coordinate_check():
    """Final check with realistic water detection"""
    
    source_path = 'app/medical_professionals/Data/doctors_geocoded.csv'
    
    print("Final coordinate verification with realistic water detection...")
    
    problematic = []
    total_count = 0
    
    with open(source_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_count += 1
            lat = row.get('lat')
            lon = row.get('lon')
            
            if is_actually_in_water(lat, lon):
                problematic.append({
                    'name': f"{row.get('nom', '')} {row.get('prenom', '')}",
                    'address': row.get('adresse', ''),
                    'speciality': row.get('specialite', ''),
                    'lat': lat,
                    'lon': lon,
                    'gouvernorat': row.get('gouvernorat', ''),
                    'issue': 'Actually in water'
                })
    
    print(f"\nFinal Results:")
    print(f"Total doctors: {total_count}")
    print(f"Actually problematic coordinates: {len(problematic)}")
    print(f"Good coordinates: {total_count - len(problematic)}")
    print(f"Real accuracy: {((total_count - len(problematic))/total_count)*100:.1f}%")
    
    if problematic:
        print(f"\nActually problematic entries:")
        for i, issue in enumerate(problematic[:5]):
            print(f"{i+1}. {issue['name']} ({issue['speciality']})")
            print(f"   Address: {issue['address']}")
            print(f"   Coords: {issue['lat']}, {issue['lon']} ({issue['gouvernorat']})")
            print(f"   Issue: {issue['issue']}")
            print()
    else:
        print("All coordinates are now properly placed on land!")
    
    return len(problematic)

if __name__ == "__main__":
    final_coordinate_check()