#!/usr/bin/env python3
"""
Show experts comptables locations by conseil régional
"""

import pandas as pd
import numpy as np

def show_experts_locations():
    # Load data
    df = pd.read_csv('app/experts_comptables/Data/experts_comptables_geocoded.csv', encoding='utf-8')
    
    # Filter only records with valid coordinates
    valid_coords = df[(df['latitude'].notna()) & (df['longitude'].notna())]
    
    print("=== EXPERTS COMPTABLES BY CONSEIL RÉGIONAL ===\n")
    
    for conseil in sorted(valid_coords['specialite'].unique()):
        conseil_data = valid_coords[valid_coords['specialite'] == conseil]
        print(f"** {conseil} ** ({len(conseil_data)} experts)")
        
        # Show gouvernorat distribution
        gov_dist = conseil_data['gouvernorat'].value_counts()
        for gov, count in gov_dist.items():
            print(f"   - {gov}: {count} experts")
        
        # Show coordinate ranges
        lat_range = (conseil_data['latitude'].min(), conseil_data['latitude'].max())
        lon_range = (conseil_data['longitude'].min(), conseil_data['longitude'].max())
        print(f"   Latitude range: {lat_range[0]:.4f} to {lat_range[1]:.4f}")
        print(f"   Longitude range: {lon_range[0]:.4f} to {lon_range[1]:.4f}")
        
        # Show some example locations
        sample_experts = conseil_data[['Nom', 'cleaned_address', 'gouvernorat', 'latitude', 'longitude']].head(3)
        print("   Sample locations:")
        for _, expert in sample_experts.iterrows():
            print(f"      {expert['Nom']} - {expert['gouvernorat']} ({expert['latitude']:.4f}, {expert['longitude']:.4f})")
        
        print()
    
    print("=== SUMMARY ===")
    print(f"Total experts with coordinates: {len(valid_coords)}")
    print(f"Geographic spread:")
    print(f"  Latitude: {valid_coords['latitude'].min():.4f} to {valid_coords['latitude'].max():.4f}")
    print(f"  Longitude: {valid_coords['longitude'].min():.4f} to {valid_coords['longitude'].max():.4f}")
    
    # Zone analysis
    zone_dist = valid_coords['zone'].value_counts()
    print(f"\nZone distribution:")
    for zone, count in zone_dist.items():
        print(f"  {zone}: {count}")

if __name__ == "__main__":
    show_experts_locations()