#!/usr/bin/env python3
"""
Check coordinate accuracy for all professional categories
Verify exact locations for distance calculations
"""

import pandas as pd
import numpy as np
import os

def analyze_profession_accuracy(file_path, profession_name):
    """Analyze coordinate accuracy for a single profession"""
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Basic stats
        total_records = len(df)
        with_coords = len(df[(df['latitude'].notna()) & (df['longitude'].notna())])
        geocoding_rate = (with_coords / total_records) * 100
        
        # Confidence analysis
        if 'confidence' in df.columns:
            high_confidence = len(df[df['confidence'] >= 0.8])
            medium_confidence = len(df[(df['confidence'] >= 0.6) & (df['confidence'] < 0.8)])
            low_confidence = len(df[df['confidence'] < 0.6])
            
            high_pct = (high_confidence / total_records) * 100
            medium_pct = (medium_confidence / total_records) * 100
            low_pct = (low_confidence / total_records) * 100
        else:
            high_confidence = medium_confidence = low_confidence = 0
            high_pct = medium_pct = low_pct = 0
        
        # Method analysis
        method_dist = {}
        if 'method' in df.columns:
            method_counts = df['method'].value_counts()
            
            # Categorize methods
            pattern_matches = 0
            governorate_fallbacks = 0
            failed_geocoding = 0
            
            for method, count in method_counts.items():
                method_str = str(method).lower()
                if 'pattern_match' in method_str:
                    pattern_matches += count
                elif 'governorate' in method_str:
                    governorate_fallbacks += count
                elif 'no_match' in method_str or 'failed' in method_str:
                    failed_geocoding += count
            
            pattern_pct = (pattern_matches / total_records) * 100
            governorate_pct = (governorate_fallbacks / total_records) * 100
            failed_pct = (failed_geocoding / total_records) * 100
        else:
            pattern_matches = governorate_fallbacks = failed_geocoding = 0
            pattern_pct = governorate_pct = failed_pct = 0
        
        # Zone analysis
        zone_dist = {}
        chalendise_count = 0
        if 'zone' in df.columns:
            zone_counts = df['zone'].value_counts()
            for zone, count in zone_counts.items():
                zone_dist[zone] = count
                if 'chalendise' in str(zone).lower():
                    chalendise_count += count
        
        chalendise_pct = (chalendise_count / total_records) * 100
        
        return {
            'profession': profession_name,
            'total_records': total_records,
            'geocoded_records': with_coords,
            'geocoding_rate': geocoding_rate,
            'high_confidence': high_confidence,
            'high_confidence_pct': high_pct,
            'medium_confidence': medium_confidence,
            'medium_confidence_pct': medium_pct,
            'low_confidence': low_confidence,
            'low_confidence_pct': low_pct,
            'pattern_matches': pattern_matches,
            'pattern_matches_pct': pattern_pct,
            'governorate_fallbacks': governorate_fallbacks,
            'governorate_fallbacks_pct': governorate_pct,
            'failed_geocoding': failed_geocoding,
            'failed_geocoding_pct': failed_pct,
            'chalendise_count': chalendise_count,
            'chalendise_pct': chalendise_pct,
            'zone_distribution': zone_dist
        }
        
    except Exception as e:
        print(f"Error analyzing {profession_name}: {e}")
        return None

def main():
    """Main analysis function"""
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # File paths for all professions
    professions = [
        {
            'name': 'Medical Professionals',
            'file': os.path.join(base_dir, 'app', 'medical_professionals', 'Data', 'doctors_geocoded.csv')
        },
        {
            'name': 'Experts Comptables', 
            'file': os.path.join(base_dir, 'app', 'experts_comptables', 'Data', 'experts_comptables_geocoded.csv')
        },
        {
            'name': 'Pharmacies',
            'file': os.path.join(base_dir, 'app', 'pharmacies', 'Data', 'pharmacies_geocoded.csv')
        }
    ]
    
    print("=== COORDINATE ACCURACY ANALYSIS FOR ALL PROFESSIONS ===\n")
    
    results = []
    
    for prof in professions:
        print(f"Analyzing {prof['name']}...")
        result = analyze_profession_accuracy(prof['file'], prof['name'])
        if result:
            results.append(result)
    
    print("\n" + "="*80)
    print("COMPREHENSIVE COORDINATE ACCURACY REPORT")
    print("="*80)
    
    # Summary table
    print(f"\n{'PROFESSION':<20} {'TOTAL':<8} {'GEOCODED':<10} {'SUCCESS':<8} {'HIGH PREC':<10} {'STREET LVL':<10}")
    print("-" * 80)
    
    total_records = 0
    total_geocoded = 0
    total_high_conf = 0
    total_pattern_matches = 0
    
    for result in results:
        total_records += result['total_records']
        total_geocoded += result['geocoded_records']
        total_high_conf += result['high_confidence']
        total_pattern_matches += result['pattern_matches']
        
        print(f"{result['profession']:<20} "
              f"{result['total_records']:<8} "
              f"{result['geocoded_records']:<10} "
              f"{result['geocoding_rate']:<7.1f}% "
              f"{result['high_confidence']:<10} "
              f"{result['pattern_matches']:<10}")
    
    print("-" * 80)
    print(f"{'TOTAL':<20} "
          f"{total_records:<8} "
          f"{total_geocoded:<10} "
          f"{(total_geocoded/total_records)*100:<7.1f}% "
          f"{total_high_conf:<10} "
          f"{total_pattern_matches:<10}")
    
    print(f"\n=== PRECISION BREAKDOWN ===")
    
    for result in results:
        print(f"\n** {result['profession']} **")
        print(f"  Total Records: {result['total_records']:,}")
        print(f"  Successfully Geocoded: {result['geocoded_records']:,} ({result['geocoding_rate']:.1f}%)")
        print(f"")
        print(f"  PRECISION LEVELS:")
        print(f"    High Precision (≥0.8): {result['high_confidence']:,} ({result['high_confidence_pct']:.1f}%)")
        print(f"    Medium Precision (0.6-0.8): {result['medium_confidence']:,} ({result['medium_confidence_pct']:.1f}%)")
        print(f"    Low Precision (<0.6): {result['low_confidence']:,} ({result['low_confidence_pct']:.1f}%)")
        print(f"")
        print(f"  GEOCODING METHODS:")
        print(f"    Street-Level Pattern Matching (~30-50m): {result['pattern_matches']:,} ({result['pattern_matches_pct']:.1f}%)")
        print(f"    Governorate-Level Fallback (~1-2km): {result['governorate_fallbacks']:,} ({result['governorate_fallbacks_pct']:.1f}%)")
        print(f"    Failed Geocoding: {result['failed_geocoding']:,} ({result['failed_geocoding_pct']:.1f}%)")
        print(f"")
        print(f"  ZONE DE CHALENDISE: {result['chalendise_count']:,} ({result['chalendise_pct']:.1f}%)")
    
    print(f"\n=== DISTANCE CALCULATION SUITABILITY ===")
    
    excellent_count = 0
    good_count = 0 
    acceptable_count = 0
    poor_count = 0
    
    for result in results:
        if result['geocoding_rate'] >= 95 and result['high_confidence_pct'] >= 70:
            category = "EXCELLENT"
            excellent_count += 1
        elif result['geocoding_rate'] >= 90 and result['high_confidence_pct'] >= 50:
            category = "GOOD"
            good_count += 1
        elif result['geocoding_rate'] >= 80 and result['high_confidence_pct'] >= 30:
            category = "ACCEPTABLE"
            acceptable_count += 1
        else:
            category = "NEEDS IMPROVEMENT"
            poor_count += 1
            
        print(f"  {result['profession']}: {category}")
        print(f"    - Suitable for precise distance calculations: {'YES' if category in ['EXCELLENT', 'GOOD'] else 'PARTIALLY' if category == 'ACCEPTABLE' else 'NO'}")
        print(f"    - Recommended for BIAT branch analysis: {'HIGH PRIORITY' if category == 'EXCELLENT' else 'MEDIUM PRIORITY' if category in ['GOOD', 'ACCEPTABLE'] else 'LOW PRIORITY'}")
    
    print(f"\n=== OVERALL ASSESSMENT ===")
    overall_geocoding = (total_geocoded / total_records) * 100
    overall_high_precision = (total_high_conf / total_records) * 100
    overall_street_level = (total_pattern_matches / total_records) * 100
    
    print(f"Total Professional Records: {total_records:,}")
    print(f"Overall Geocoding Success: {overall_geocoding:.1f}%")
    print(f"Overall High Precision: {overall_high_precision:.1f}%")
    print(f"Overall Street-Level Accuracy: {overall_street_level:.1f}%")
    
    if excellent_count >= 2:
        assessment = "EXCELLENT - Ready for precise distance analysis"
    elif good_count + excellent_count >= 2:
        assessment = "GOOD - Suitable for business intelligence"
    elif acceptable_count + good_count + excellent_count >= 2:
        assessment = "ACCEPTABLE - Usable with margin of error"
    else:
        assessment = "NEEDS IMPROVEMENT - Consider precision upgrades"
    
    print(f"\nFINAL RECOMMENDATION: {assessment}")
    
    if assessment.startswith("EXCELLENT") or assessment.startswith("GOOD"):
        print(f"✓ PROCEED with distance calculations between professionals and BIAT branches")
        print(f"✓ DATA QUALITY is sufficient for strategic business decisions")
        print(f"✓ COORDINATE PRECISION supports market analysis and expansion planning")
    else:
        print(f"⚠ CONSIDER improving geocoding precision before critical business decisions")
        print(f"⚠ CURRENT DATA suitable for general analysis but not precise distance calculations")

if __name__ == "__main__":
    main()