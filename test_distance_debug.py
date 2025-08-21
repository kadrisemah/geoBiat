#!/usr/bin/env python3
"""
Quick test to debug distance-based precision system
"""

import pandas as pd
from math import radians, cos, sin, asin, sqrt
import os
import sys

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return float('inf')
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return c * 6371  # Earth radius in km

def calculate_distance_based_precision(conseiller_lat, conseiller_lon, biat_branches):
    """Calculate precision based on distance to nearest BIAT branch"""
    if pd.isna(conseiller_lat) or pd.isna(conseiller_lon):
        return "no_coords", "Pas de Coordonnées", 0.0, None, float('inf')
    
    # Find nearest BIAT branch
    min_distance = float('inf')
    nearest_branch = None
    
    for _, branch in biat_branches.iterrows():
        if pd.notna(branch['lat']) and pd.notna(branch['long']):
            distance = haversine_distance(conseiller_lat, conseiller_lon, branch['lat'], branch['long'])
            if distance < min_distance:
                min_distance = distance
                nearest_branch = branch['agence']
    
    # Assign precision based on distance
    if min_distance <= 5.0:
        return "high", f"Haute Précision (≤5km de BIAT)", 0.9, nearest_branch, min_distance
    elif min_distance <= 15.0:
        return "medium", f"Précision Moyenne (5-15km de BIAT)", 0.7, nearest_branch, min_distance
    else:
        return "low", f"Précision Faible (>15km de BIAT)", 0.3, nearest_branch, min_distance

def test_distance_system():
    """Test the distance-based precision system"""
    
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load data
    conseillers_file = os.path.join(current_dir, 'app', 'conseillers', 'Data', 'conseillers_geocoded.csv')
    banks_file = os.path.join(current_dir, 'app', 'base_prospection', 'Data', 'geo_banks.csv')
    
    print(f"Loading conseillers from: {conseillers_file}")
    print(f"Loading banks from: {banks_file}")
    
    try:
        df_conseillers = pd.read_csv(conseillers_file, encoding='utf-8')
        df_banks = pd.read_csv(banks_file, encoding='utf-8')
        
        print(f"Loaded {len(df_conseillers)} conseillers")
        print(f"Loaded {len(df_banks)} banks")
        
        # Filter BIAT branches
        biat_branches = df_banks[df_banks['banque'].str.upper() == 'BIAT'].copy()
        print(f"Found {len(biat_branches)} BIAT branches")
        
        if len(biat_branches) == 0:
            print("ERROR: No BIAT branches found!")
            return
        
        # Test with first 10 conseillers
        test_conseillers = df_conseillers.head(10)
        
        print("\n=== TESTING DISTANCE CALCULATIONS ===")
        
        precision_counts = {'high': 0, 'medium': 0, 'low': 0, 'no_coords': 0}
        
        for index, conseiller in test_conseillers.iterrows():
            precision_level, precision_label, confidence, nearest_branch, distance = calculate_distance_based_precision(
                conseiller['latitude'], conseiller['longitude'], biat_branches
            )
            
            precision_counts[precision_level] += 1
            
            print(f"\n{conseiller['nom']}")
            print(f"  Coordinates: ({conseiller['latitude']}, {conseiller['longitude']})")
            print(f"  Distance: {distance:.1f}km" if distance != float('inf') else "  Distance: No coordinates")
            print(f"  Nearest BIAT: {nearest_branch}")
            print(f"  Precision: {precision_level} - {precision_label}")
        
        print(f"\n=== PRECISION DISTRIBUTION ===")
        for level, count in precision_counts.items():
            percentage = count / len(test_conseillers) * 100
            print(f"{level}: {count} ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_distance_system()