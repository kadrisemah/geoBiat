#!/usr/bin/env python3
"""
Test script to verify experts comptables data loading
"""

import pandas as pd
import numpy as np

def test_data_loading():
    try:
        # Test loading the geocoded experts data
        df_experts = pd.read_csv(r'app\experts_comptables\Data\experts_comptables_geocoded.csv')
        print(f"Successfully loaded {len(df_experts)} experts comptables records")
        
        print(f"\nColumns: {list(df_experts.columns)}")
        print(f"\nData types:")
        print(df_experts.dtypes)
        
        print(f"\nFirst few records:")
        print(df_experts[['Nom', 'latitude', 'longitude', 'confidence', 'zone']].head())
        
        # Check for valid coordinates
        valid_coords = df_experts[
            (df_experts['latitude'].notna()) & 
            (df_experts['longitude'].notna())
        ]
        print(f"\nRecords with valid coordinates: {len(valid_coords)}")
        
        # Check specialites
        print(f"\nSpecialites (conseil régional):")
        print(df_experts['specialite'].value_counts())
        
        # Check gouvernorats
        print(f"\nGouvernorats:")
        print(df_experts['gouvernorat'].value_counts())
        
        return True
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

if __name__ == "__main__":
    test_data_loading()