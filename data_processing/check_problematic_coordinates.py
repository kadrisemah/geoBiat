#!/usr/bin/env python3
"""
Quick check for problematic coordinates (points in sea, sabkha, etc.)
Identifies doctors placed in water or uninhabitable areas
"""
import csv
import math

def distance_to_coast(lat, lon):
    """
    Estimate distance to nearest coast - simplified calculation
    Returns approximate distance in km
    """
    # Major coastal reference points in Tunisia
    coastal_points = [
        (37.2759, 9.8734),   # Bizerte
        (36.8529, 10.3312),  # Carthage/Sidi Bou Said
        (36.8065, 10.1815),  # Tunis (Lac de Tunis)
        (36.4000, 10.6167),  # Hammamet
        (35.8256, 10.6367),  # Sousse
        (35.5047, 10.7461),  # Monastir
        (34.7406, 10.7609),  # Sfax
        (33.8815, 10.0982),  # Gabès
        (33.5067, 11.0183),  # Djerba
    ]
    
    min_distance = float('inf')
    for coast_lat, coast_lon in coastal_points:
        # Haversine distance
        dlat = math.radians(lat - coast_lat)
        dlon = math.radians(lon - coast_lon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(coast_lat)) * math.cos(math.radians(lat)) * math.sin(dlon/2)**2
        distance = 2 * math.asin(math.sqrt(a)) * 6371  # Earth radius in km
        min_distance = min(min_distance, distance)
    
    return min_distance

def is_likely_in_water(lat, lon):
    """
    Check if coordinates are likely in water/sea/sabkha
    """
    try:
        lat, lon = float(lat), float(lon)
        
        # Tunisia bounds
        if not (30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.0):
            return True  # Outside Tunisia
        
        # Mediterranean Sea (too far north)
        if lat > 37.3:
            return True
        
        # Gulf of Gabès (too far east/south)
        if lat < 33.5 and lon > 10.8:
            return True
            
        # Chott el Djerid (salt lake area)
        if 33.5 <= lat <= 34.2 and 7.5 <= lon <= 8.5:
            return True
        
        # Too close to major coastlines (likely in sea)
        coast_distance = distance_to_coast(lat, lon)
        if coast_distance < 0.5:  # Less than 500m from coast
            return True
            
        # Specific problematic water bodies
        
        # Lac de Tunis
        if 36.7 <= lat <= 36.85 and 10.15 <= lon <= 10.25:
            return True
            
        # Sebkha Ariana
        if 36.85 <= lat <= 36.9 and 10.1 <= lon <= 10.2:
            return True
        
        return False
        
    except (ValueError, TypeError):
        return True  # Invalid coordinates

def check_all_coordinates():
    """Check all doctor coordinates for problematic placements"""
    
    source_path = 'app/medical_professionals/Data/doctors_geocoded.csv'
    
    print("Checking for problematic coordinates...")
    
    problematic = []
    total_count = 0
    
    with open(source_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_count += 1
            lat = row.get('lat')
            lon = row.get('lon')
            
            if is_likely_in_water(lat, lon):
                coast_dist = distance_to_coast(float(lat), float(lon)) if lat and lon else 0
                
                problematic.append({
                    'name': f"{row.get('nom', '')} {row.get('prenom', '')}",
                    'address': row.get('adresse', ''),
                    'speciality': row.get('specialite', ''),
                    'lat': lat,
                    'lon': lon,
                    'gouvernorat': row.get('gouvernorat', ''),
                    'coast_distance_km': round(coast_dist, 2),
                    'issue': 'Likely in water/sea/sabkha'
                })
    
    print(f"\nResults:")
    print(f"Total doctors: {total_count}")
    print(f"Problematic coordinates: {len(problematic)}")
    print(f"Good coordinates: {total_count - len(problematic)}")
    print(f"Accuracy: {((total_count - len(problematic))/total_count)*100:.1f}%")
    
    if problematic:
        print(f"\nFirst 10 problematic entries:")
        for i, issue in enumerate(problematic[:10]):
            print(f"{i+1}. {issue['name']} ({issue['speciality']})")
            print(f"   Address: {issue['address']}")
            print(f"   Coords: {issue['lat']}, {issue['lon']} ({issue['gouvernorat']})")
            print(f"   Coast distance: {issue['coast_distance_km']} km")
            print(f"   Issue: {issue['issue']}")
            print()
        
        # Save problematic entries for fixing
        with open('data_processing/problematic_coordinates.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'address', 'speciality', 'lat', 'lon', 'gouvernorat', 'coast_distance_km', 'issue']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(problematic)
        
        print(f"Problematic entries saved to: data_processing/problematic_coordinates.csv")
    else:
        print("No problematic coordinates found!")
    
    return len(problematic)

if __name__ == "__main__":
    check_all_coordinates()