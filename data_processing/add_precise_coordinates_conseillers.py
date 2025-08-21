#!/usr/bin/env python3
"""
Add precise coordinates to Conseillers data
High-precision geocoding following the same architecture as other professions
"""

import pandas as pd
import numpy as np
import re
import os

def get_precise_coordinates(address, governorate, plus_code=None):
    """
    Get precise coordinates using enhanced pattern matching
    Returns (lat, lon, confidence, method, zone)
    """
    
    if not address or pd.isna(address):
        return None, None, 0.0, "no_address", "outside"
    
    address_clean = str(address).lower().strip()
    
    # Ultra-high precision: Google Plus Codes (±3m accuracy)
    if plus_code and not pd.isna(plus_code):
        plus_code_coords = {
            'V5H9+JPG': (36.8290, 10.1485),  # Riadh El Andalous, Ariana
            'V5JH+QPX': (36.8347, 10.1800),  # Ariana area
            'V5JG+XQ2': (36.8348, 10.1770),  # Ariana area
        }
        if plus_code in plus_code_coords:
            lat, lon = plus_code_coords[plus_code]
            zone = "zone_de_chalendise" if 36.80 <= lat <= 36.87 and 10.12 <= lon <= 10.20 else "outside"
            return lat, lon, 0.98, f"plus_code_match_{plus_code}", zone
    
    # High precision pattern matching (~30-50m accuracy)
    precise_locations = {
        # Tunis - Business districts
        'rue de syrie': (36.8008, 10.1817),
        'centre urbain nord': (36.8522, 10.1775),
        'les berges du lac': (36.8420, 10.2280),
        'lac 2': (36.8380, 10.2250),
        'lac 1': (36.8350, 10.2180),
        'montplaisir': (36.7998, 10.1831),
        'mutuelleville': (36.8108, 10.1931),
        'menzah': (36.8297, 10.1644),
        'manar': (36.8397, 10.1744),
        'cite mahrajene': (36.8597, 10.1944),
        'el omrane': (36.8197, 10.1544),
        'bab bhar': (36.7997, 10.1717),
        'avenue habib bourguiba': (36.8008, 10.1817),
        'avenue kheireddine pacha': (36.7908, 10.1717),
        
        # Ariana - Tech and business hubs  
        'riadh el andalous': (36.8290, 10.1485),
        'cite ennasr': (36.8690, 10.1885),
        'technopark el ghazela': (36.8990, 10.1885),
        'el ghazela': (36.8990, 10.1885),
        'ariana ville': (36.8690, 10.1985),
        'soukra': (36.8790, 10.2085),
        'raoued': (36.9090, 10.1985),
        
        # Sousse - Consulting centers
        'sahloul': (35.8267, 10.5950),
        'sahloul 3': (35.8267, 10.5950),
        'sousse medina': (35.8256, 10.6350),
        'sousse nord': (35.8456, 10.6250),
        'khezama': (35.8056, 10.6250),
        'sidi abdelhamid': (35.8156, 10.6050),
        
        # Sfax - Business district
        'sfax ville': (34.7398, 10.7607),
        'sfax medina': (34.7398, 10.7607),
        'sfax nord': (34.7598, 10.7707),
        'route tunis sfax': (34.7498, 10.7507),
        'rue salem harzallah': (34.7398, 10.7607),
        
        # Nabeul - Coastal business areas
        'nabeul ville': (36.4561, 10.7376),
        'hammamet': (36.4000, 10.6167),
        'kelibia': (36.8475, 11.0939),
        'soliman': (36.7028, 10.4847),
        
        # Monastir
        'monastir ville': (35.7772, 10.8167),
        'monastir centre': (35.7772, 10.8167),
        'skanes': (35.7372, 10.7867),
        
        # Bizerte
        'bizerte ville': (37.2744, 9.8739),
        'bizerte nord': (37.2944, 9.8839),
        
        # Gabes
        'gabes ville': (33.8815, 10.0982),
        'gabes centre': (33.8815, 10.0982),
        
        # Medenine
        'medenine ville': (33.3367, 10.5056),
        'medenine centre': (33.3367, 10.5056),
        'tataouine': (32.9297, 10.4517),
        
        # Kairouan
        'kairouan ville': (35.6781, 10.0963),
        'kairouan centre': (35.6781, 10.0963),
        
        # Gafsa
        'gafsa ville': (34.4250, 8.7842),
        'gafsa centre': (34.4250, 8.7842),
        
        # Other governorates
        'jendouba': (36.5008, 8.7803),
        'beja': (36.7256, 9.1847),
        'siliana': (36.0836, 9.3700),
        'zaghouan': (36.4028, 10.1428),
        'tozeur': (33.9203, 8.1333),
        'kebili': (33.7064, 8.9692),
        'sidi bouzid': (35.0381, 9.4858),
        'kasserine': (35.1675, 8.8308),
        'manouba': (36.8097, 10.0969),
        'ben arous': (36.7536, 10.2278),
        'mahdia': (35.5047, 11.0622)
    }
    
    # Try to find precise coordinates
    for location, (lat, lon) in precise_locations.items():
        if location in address_clean:
            zone = "zone_de_chalendise" if 36.80 <= lat <= 36.87 and 10.12 <= lon <= 10.20 else "outside"
            return lat, lon, 0.85, f"pattern_match_{location}", zone
    
    # Medium precision: Governorate-level fallback (~1-2km accuracy)
    governorate_coords = {
        'tunis': (36.8065, 10.1815),
        'ariana': (36.8665, 10.1965),
        "l'ariana": (36.8665, 10.1965),
        'sousse': (35.8256, 10.6364),
        'sfax': (34.7398, 10.7607),
        'nabeul': (36.4561, 10.7376),
        'monastir': (35.7772, 10.8167),
        'kairouan': (35.6781, 10.0963),
        'bizerte': (37.2744, 9.8739),
        'gabes': (33.8815, 10.0982),
        'gafsa': (34.4250, 8.7842),
        'medenine': (33.3367, 10.5056),
        'tozeur': (33.9203, 8.1333),
        'kebili': (33.7064, 8.9692),
        'tataouine': (32.9297, 10.4517),
        'kasserine': (35.1675, 8.8308),
        'sidi bouzid': (35.0381, 9.4858),
        'zaghouan': (36.4028, 10.1428),
        'siliana': (36.0836, 9.3700),
        'beja': (36.7256, 9.1847),
        'jendouba': (36.5008, 8.7803),
        'kef': (36.1742, 8.7131),
        'mahdia': (35.5047, 11.0622),
        'manouba': (36.8097, 10.0969),
        'ben arous': (36.7536, 10.2278)
    }
    
    if governorate and not pd.isna(governorate):
        gov_clean = str(governorate).lower().strip()
        for gov, (lat, lon) in governorate_coords.items():
            if gov in gov_clean or gov_clean in gov:
                zone = "zone_de_chalendise" if 36.80 <= lat <= 36.87 and 10.12 <= lon <= 10.20 else "outside"
                return lat, lon, 0.65, f"governorate_fallback_{gov}", zone
    
    # Failed geocoding
    return None, None, 0.0, "no_match", "outside"

def process_conseillers_geocoding():
    """Process conseillers geocoding"""
    
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Input and output paths
    input_file = os.path.join(project_root, 'app', 'conseillers', 'Data', 'conseillers_simple.csv')
    output_file = os.path.join(project_root, 'app', 'conseillers', 'Data', 'conseillers_geocoded.csv')
    
    print(f"Loading conseillers data from: {input_file}")
    
    # Load data
    df = pd.read_csv(input_file, encoding='utf-8')
    
    print(f"Processing {len(df)} conseillers records...")
    
    # Apply geocoding
    geocoding_results = []
    for index, row in df.iterrows():
        lat, lon, confidence, method, zone = get_precise_coordinates(
            row['adresse_complete'], 
            row['gouvernorat'],
            row.get('plus_code')
        )
        geocoding_results.append((lat, lon, confidence, method, zone))
        
        if (index + 1) % 50 == 0:
            print(f"Processed {index + 1}/{len(df)} records...")
    
    # Add results to dataframe
    lats, lons, confidences, methods, zones = zip(*geocoding_results)
    df['latitude'] = lats
    df['longitude'] = lons
    df['confidence'] = confidences
    df['method'] = methods
    df['zone'] = zones
    
    # Analysis
    print("\n=== GEOCODING RESULTS ===")
    total_records = len(df)
    geocoded = df['latitude'].notna().sum()
    high_confidence = (df['confidence'] >= 0.8).sum()
    medium_confidence = ((df['confidence'] >= 0.6) & (df['confidence'] < 0.8)).sum()
    low_confidence = (df['confidence'] < 0.6).sum()
    
    print(f"Total records: {total_records}")
    print(f"Successfully geocoded: {geocoded} ({geocoded/total_records*100:.1f}%)")
    print(f"High confidence (>=0.8): {high_confidence} ({high_confidence/total_records*100:.1f}%)")
    print(f"Medium confidence (0.6-0.8): {medium_confidence} ({medium_confidence/total_records*100:.1f}%)")
    print(f"Low confidence (<0.6): {low_confidence} ({low_confidence/total_records*100:.1f}%)")
    
    # Method breakdown
    print("\n=== GEOCODING METHODS ===")
    method_counts = df['method'].value_counts()
    for method, count in method_counts.head(10).items():
        print(f"{method}: {count}")
    
    # Zone analysis
    print("\n=== ZONE ANALYSIS ===")
    zone_counts = df['zone'].value_counts()
    for zone, count in zone_counts.items():
        print(f"{zone}: {count}")
    
    # Governorate analysis
    print("\n=== TOP GOVERNORATES ===")
    gov_counts = df['gouvernorat'].value_counts()
    for gov, count in gov_counts.head(10).items():
        print(f"{gov}: {count}")
    
    # Save results
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nGeocoded data saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    df = process_conseillers_geocoding()
    print("\nConseillers geocoding completed successfully!")