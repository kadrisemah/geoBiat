#!/usr/bin/env python3
"""
Check coordinate accuracy for experts comptables
"""

import pandas as pd
import numpy as np

def analyze_coordinate_accuracy():
    df = pd.read_csv('app/experts_comptables/Data/experts_comptables_geocoded.csv', encoding='utf-8')
    valid_coords = df[(df['latitude'].notna()) & (df['longitude'].notna())]

    print('=== COORDINATE ACCURACY ANALYSIS ===\n')

    print('CONFIDENCE DISTRIBUTION:')
    confidence_dist = valid_coords['confidence'].value_counts().sort_index()
    for conf, count in confidence_dist.items():
        percentage = (count/len(valid_coords))*100
        print(f'  Confidence {conf}: {count} experts ({percentage:.1f}%)')

    print('\nGEOCODING METHOD DISTRIBUTION:')
    method_dist = valid_coords['method'].value_counts()
    for method, count in method_dist.items():
        percentage = (count/len(valid_coords))*100
        print(f'  {method}: {count} experts ({percentage:.1f}%)')

    print('\nHIGH PRECISION ANALYSIS:')
    high_precision = valid_coords[valid_coords['confidence'] >= 0.8]
    medium_precision = valid_coords[(valid_coords['confidence'] >= 0.6) & (valid_coords['confidence'] < 0.8)]
    low_precision = valid_coords[valid_coords['confidence'] < 0.6]

    print(f'  HIGH precision (>=0.8): {len(high_precision)} experts ({len(high_precision)/len(valid_coords)*100:.1f}%)')
    print(f'  MEDIUM precision (0.6-0.8): {len(medium_precision)} experts ({len(medium_precision)/len(valid_coords)*100:.1f}%)')
    print(f'  LOW precision (<0.6): {len(low_precision)} experts ({len(low_precision)/len(valid_coords)*100:.1f}%)')

    print('\nPATTERN MATCH vs FALLBACK:')
    pattern_matches = valid_coords[valid_coords['method'].str.contains('pattern_match', na=False)]
    governorate_fallback = valid_coords[valid_coords['method'].str.contains('governorate_', na=False)]

    print(f'  PRECISE pattern matches: {len(pattern_matches)} experts ({len(pattern_matches)/len(valid_coords)*100:.1f}%)')
    print(f'  Governorate fallback: {len(governorate_fallback)} experts ({len(governorate_fallback)/len(valid_coords)*100:.1f}%)')

    print('\nCOORDINATE PRECISION EXAMPLES:')
    print('\nHIGH precision (pattern matched):')
    if len(pattern_matches) > 0:
        high_sample = pattern_matches[['Nom', 'cleaned_address', 'latitude', 'longitude', 'confidence', 'method']].head(3)
        for _, row in high_sample.iterrows():
            print(f'  • {row["Nom"]} - {row["method"]}')
            print(f'    Address: {row["cleaned_address"][:50]}...')
            print(f'    Coords: ({row["latitude"]:.6f}, {row["longitude"]:.6f}) - Confidence: {row["confidence"]}')

    print('\nMEDIUM precision (governorate level):')
    if len(governorate_fallback) > 0:
        medium_sample = governorate_fallback[['Nom', 'cleaned_address', 'latitude', 'longitude', 'confidence', 'method']].head(3)
        for _, row in medium_sample.iterrows():
            print(f'  • {row["Nom"]} - {row["method"]}')
            print(f'    Address: {row["cleaned_address"][:50]}...')
            print(f'    Coords: ({row["latitude"]:.6f}, {row["longitude"]:.6f}) - Confidence: {row["confidence"]}')

    print('\n=== DISTANCE CALCULATION SUITABILITY ===')
    print(f'Total experts suitable for distance calculations: {len(valid_coords)}/367 ({len(valid_coords)/367*100:.1f}%)')
    
    # Analyze precision levels for distance calculations
    street_level = len(pattern_matches)  # ~50m precision
    district_level = len(governorate_fallback)  # ~1-2km precision
    
    print(f'\nPRECISION LEVELS FOR DISTANCE ANALYSIS:')
    print(f'  STREET-level precision (~50m): {street_level} experts ({street_level/len(valid_coords)*100:.1f}%)')
    print(f'  DISTRICT-level precision (~1-2km): {district_level} experts ({district_level/len(valid_coords)*100:.1f}%)')
    
    print(f'\nRECOMMENDATION:')
    if street_level/len(valid_coords) > 0.3:
        print('  ✓ GOOD: High proportion of precise coordinates')
        print('  ✓ Suitable for accurate distance calculations to BIAT agencies')
        print('  ✓ Can reliably identify nearest experts to each BIAT branch')
    else:
        print('  ⚠ WARNING: Many coordinates are governorate-level only')
        print('  ⚠ Distance calculations will have ~1-2km margin of error')
        print('  ⚠ Consider improving geocoding precision')

if __name__ == "__main__":
    analyze_coordinate_accuracy()