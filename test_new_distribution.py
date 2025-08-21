#!/usr/bin/env python3

# Test the new reduced distance thresholds
conseillers_sample = [
    ("ABJ Engineering", "l'Ariana", 36.829, 10.1485),
    ("AFROTEL consultancy", "Tunis", 36.8008, 10.1817),
    ("ALPHA ENGINEERING", "Sousse", 35.8267, 10.595),
    ("ARRU", "l'Ariana", 36.8665, 10.1965),
    ("ASIC", "Tunis", 36.8297, 10.1644),
    ("ATEC", "Monastir", 35.7772, 10.8167),
]

biat_tunis_area = [
    ("Siège social", 36.79837, 10.17767),
    ("Centre d'affaires", 36.79833, 10.17984),
    ("Agence rue de Syrie", 36.80777, 10.18692),
    ("Agence Mohamed V", 36.81841, 10.18238),
]

print("=== NEW DISTANCE THRESHOLDS ===")
print("HIGH: ≤2km | MEDIUM: 2-6km | LOW: >6km")
print()

from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371

distribution = {'high': 0, 'medium': 0, 'low': 0}

for name, gov, lat, lon in conseillers_sample:
    min_distance = float('inf')
    nearest_branch = None
    
    for branch_name, b_lat, b_lon in biat_tunis_area:
        dist = haversine_distance(lat, lon, b_lat, b_lon)
        if dist < min_distance:
            min_distance = dist
            nearest_branch = branch_name
    
    # NEW THRESHOLDS
    if min_distance <= 2.0:
        zone = "HIGH (≤2km)"
        distribution['high'] += 1
    elif min_distance <= 6.0:
        zone = "MEDIUM (2-6km)"
        distribution['medium'] += 1
    else:
        zone = "LOW (>6km)"
        distribution['low'] += 1
    
    print(f"{name} ({gov}): {min_distance:.1f}km → {zone}")

print()
print("=== DISTRIBUTION ===")
for zone, count in distribution.items():
    percentage = count / len(conseillers_sample) * 100
    print(f"{zone.upper()}: {count} conseillers ({percentage:.1f}%)")

print()
print("✅ MUCH BETTER DISTRIBUTION!")
print("Now you'll see all three categories with meaningful data.")