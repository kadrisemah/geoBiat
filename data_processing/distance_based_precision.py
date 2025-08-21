#!/usr/bin/env python3
"""
Distance-Based Precision System for Conseillers
Calculate precision based on actual distance to nearest BIAT branch
- High Precision: Within 5km of BIAT branch (strategic zone)
- Medium Precision: 5-15km from BIAT branch (expansion zone) 
- Low Precision: >15km from BIAT branch (remote zone)
"""

import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import os

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def find_nearest_biat_distance(conseiller_lat, conseiller_lon, biat_branches):
    """Find distance to nearest BIAT branch"""
    if pd.isna(conseiller_lat) or pd.isna(conseiller_lon):
        return float('inf')
    
    min_distance = float('inf')
    nearest_branch = None
    
    for _, branch in biat_branches.iterrows():
        if pd.notna(branch['lat']) and pd.notna(branch['long']):
            distance = haversine_distance(
                conseiller_lat, conseiller_lon, 
                branch['lat'], branch['long']
            )
            if distance < min_distance:
                min_distance = distance
                nearest_branch = branch['agence']
    
    return min_distance, nearest_branch

def calculate_distance_based_precision(distance_km):
    """
    Calculate precision level based on distance to nearest BIAT branch
    
    Business Logic:
    - 0-5km: High Precision (strategic zone for direct competition)
    - 5-15km: Medium Precision (expansion opportunity zone)
    - >15km: Low Precision (remote zone, lower priority)
    """
    if distance_km <= 5.0:
        return "high", "Haute Précision (≤5km de BIAT)", 0.9
    elif distance_km <= 15.0:
        return "medium", "Précision Moyenne (5-15km de BIAT)", 0.7
    else:
        return "low", "Précision Faible (>15km de BIAT)", 0.3

def process_distance_based_precision():
    """Process conseillers with distance-based precision"""
    
    # Get project paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Load data
    conseillers_file = os.path.join(project_root, 'app', 'conseillers', 'Data', 'conseillers_geocoded.csv')
    banks_file = os.path.join(project_root, 'app', 'base_prospection', 'Data', 'geo_banks.csv')
    
    print("Loading conseillers and banks data...")
    df_conseillers = pd.read_csv(conseillers_file, encoding='utf-8')
    df_banks = pd.read_csv(banks_file, encoding='utf-8')
    
    # Filter only BIAT branches
    biat_branches = df_banks[df_banks['banque'].str.upper() == 'BIAT'].copy()
    print(f"Found {len(biat_branches)} BIAT branches")
    print(f"Processing {len(df_conseillers)} conseillers")
    
    # Calculate distances and precision
    results = []
    
    for index, conseiller in df_conseillers.iterrows():
        if pd.notna(conseiller['latitude']) and pd.notna(conseiller['longitude']):
            # Find nearest BIAT branch
            distance_km, nearest_branch = find_nearest_biat_distance(
                conseiller['latitude'], conseiller['longitude'], biat_branches
            )
            
            # Calculate precision based on distance
            precision_level, precision_label, confidence = calculate_distance_based_precision(distance_km)
            
            results.append({
                'distance_to_nearest_biat': round(distance_km, 2),
                'nearest_biat_branch': nearest_branch,
                'precision_level': precision_level,
                'precision_label': precision_label,
                'distance_based_confidence': confidence
            })
        else:
            # No coordinates available
            results.append({
                'distance_to_nearest_biat': None,
                'nearest_biat_branch': None,
                'precision_level': 'no_coords',
                'precision_label': 'Pas de Coordonnées',
                'distance_based_confidence': 0.0
            })
        
        if (index + 1) % 50 == 0:
            print(f"Processed {index + 1}/{len(df_conseillers)} conseillers...")
    
    # Add results to dataframe
    results_df = pd.DataFrame(results)
    df_enhanced = pd.concat([df_conseillers, results_df], axis=1)
    
    # Analysis
    print("\n=== DISTANCE-BASED PRECISION ANALYSIS ===")
    
    valid_coords = df_enhanced[df_enhanced['distance_to_nearest_biat'].notna()]
    total_valid = len(valid_coords)
    
    if total_valid > 0:
        high_precision = len(valid_coords[valid_coords['precision_level'] == 'high'])
        medium_precision = len(valid_coords[valid_coords['precision_level'] == 'medium'])
        low_precision = len(valid_coords[valid_coords['precision_level'] == 'low'])
        
        print(f"Total with coordinates: {total_valid}")
        print(f"High Precision (≤5km): {high_precision} ({high_precision/total_valid*100:.1f}%)")
        print(f"Medium Precision (5-15km): {medium_precision} ({medium_precision/total_valid*100:.1f}%)")
        print(f"Low Precision (>15km): {low_precision} ({low_precision/total_valid*100:.1f}%)")
        
        # Distance statistics
        print(f"\nDistance Statistics:")
        print(f"Average distance to BIAT: {valid_coords['distance_to_nearest_biat'].mean():.1f}km")
        print(f"Median distance to BIAT: {valid_coords['distance_to_nearest_biat'].median():.1f}km")
        print(f"Min distance: {valid_coords['distance_to_nearest_biat'].min():.1f}km")
        print(f"Max distance: {valid_coords['distance_to_nearest_biat'].max():.1f}km")
        
        # Business insights
        strategic_zone = high_precision + medium_precision
        print(f"\n=== BUSINESS INSIGHTS ===")
        print(f"Strategic Zone (≤15km): {strategic_zone} conseillers ({strategic_zone/total_valid*100:.1f}%)")
        print(f"Direct Competition Zone (≤5km): {high_precision} conseillers ({high_precision/total_valid*100:.1f}%)")
        
        # Top governorates in strategic zone
        strategic_conseillers = valid_coords[valid_coords['distance_to_nearest_biat'] <= 15.0]
        if len(strategic_conseillers) > 0:
            print(f"\n=== TOP GOVERNORATES IN STRATEGIC ZONE (≤15km) ===")
            gov_counts = strategic_conseillers['gouvernorat'].value_counts()
            for gov, count in gov_counts.head(5).items():
                print(f"{gov}: {count} conseillers")
    
    # Save enhanced data
    output_file = os.path.join(project_root, 'app', 'conseillers', 'Data', 'conseillers_distance_precision.csv')
    df_enhanced.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nDistance-based precision data saved to: {output_file}")
    
    return df_enhanced

def show_nearest_branches_sample():
    """Show sample of conseillers with their nearest BIAT branches"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    output_file = os.path.join(project_root, 'app', 'conseillers', 'Data', 'conseillers_distance_precision.csv')
    
    if os.path.exists(output_file):
        df = pd.read_csv(output_file, encoding='utf-8')
        
        print("\n=== SAMPLE: CONSEILLERS AND NEAREST BIAT BRANCHES ===")
        
        # Show 10 high precision examples
        high_precision = df[(df['precision_level'] == 'high') & (df['distance_to_nearest_biat'].notna())].head(10)
        
        for _, conseiller in high_precision.iterrows():
            print(f"\n{conseiller['nom']}")
            print(f"  Distance: {conseiller['distance_to_nearest_biat']}km")
            print(f"  Nearest BIAT: {conseiller['nearest_biat_branch']}")
            print(f"  Precision: {conseiller['precision_label']}")
            print(f"  Location: {conseiller['gouvernorat']}")

if __name__ == "__main__":
    print("=== DISTANCE-BASED PRECISION SYSTEM ===")
    print("Calculating precision based on distance to BIAT branches...")
    print("High: ≤5km | Medium: 5-15km | Low: >15km")
    print("="*50)
    
    df_result = process_distance_based_precision()
    show_nearest_branches_sample()
    
    print("\nDistance-based precision calculation completed!")
    print("This provides real business value for strategic planning.")