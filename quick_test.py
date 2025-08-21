#!/usr/bin/env python3
from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return c * 6371  # Earth radius in km

# Test calculation
conseiller_lat, conseiller_lon = 36.829, 10.1485  # ABJ Engineering
biat_lat, biat_lon = 36.79836654663086, 10.17767238616943  # BIAT Siège

distance = haversine_distance(conseiller_lat, conseiller_lon, biat_lat, biat_lon)

print(f"Distance from ABJ Engineering to BIAT Siège: {distance:.2f} km")

if distance <= 5.0:
    zone = "HIGH (≤5km)"
elif distance <= 15.0:
    zone = "MEDIUM (5-15km)"
else:
    zone = "LOW (>15km)"

print(f"Zone classification: {zone}")

# Test a few more BIAT branches
biat_branches = [
    ("Siège social", 36.79836654663086, 10.17767238616943),
    ("Centre d'affaires", 36.7983283996582, 10.17984199523926),
    ("Agence rue el Jazira 2", 36.7945671081543, 10.1763334274292),
    ("Agence rue de Syrie", 36.80777359008789, 10.18692207336426),
]

min_distance = float('inf')
nearest_branch = None

print(f"\n=== Testing all BIAT branches ===")
for branch_name, lat, lon in biat_branches:
    dist = haversine_distance(conseiller_lat, conseiller_lon, lat, lon)
    print(f"{branch_name}: {dist:.2f} km")
    if dist < min_distance:
        min_distance = dist
        nearest_branch = branch_name

print(f"\nNearest BIAT branch: {nearest_branch} at {min_distance:.2f} km")

if min_distance <= 5.0:
    final_zone = "HIGH (≤5km)"
elif min_distance <= 15.0:
    final_zone = "MEDIUM (5-15km)" 
else:
    final_zone = "LOW (>15km)"

print(f"Final zone: {final_zone}")