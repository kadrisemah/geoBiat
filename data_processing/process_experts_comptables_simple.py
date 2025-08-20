#!/usr/bin/env python3
"""
Simple processing for Experts Comptables data
Creates basic structure and prepares for manual coordinate addition
"""

import json
import pandas as pd
import numpy as np
import re
import os

def clean_address(address):
    """Clean and standardize address text"""
    if pd.isna(address) or not address:
        return ""
    
    address = str(address).strip()
    address = re.sub(r'\s+', ' ', address)
    address = address.replace('  ', ' ')
    address = address.replace(' ,', ',')
    address = address.replace(', ,', ',')
    
    return address

def extract_governorate(row):
    """Extract governorate from address or conseil régional"""
    
    address = str(row.get('Adresse', '')).lower()
    conseil = str(row.get('Conseil_régional', '')).lower()
    
    # Governorate mappings
    gov_mappings = {
        'tunis': 'Tunis',
        'ben arous': 'Ben Arous', 
        'ariana': 'Ariana',
        'manouba': 'Manouba',
        'sfax': 'Sfax',
        'sousse': 'Sousse',
        'monastir': 'Monastir',
        'mahdia': 'Mahdia',
        'kairouan': 'Kairouan',
        'kasserine': 'Kasserine',
        'sidi bouzid': 'Sidi Bouzid',
        'gafsa': 'Gafsa',
        'tozeur': 'Tozeur',
        'kebili': 'Kebili',
        'gabes': 'Gabès',
        'medenine': 'Médenine',
        'tataouine': 'Tataouine',
        'nabeul': 'Nabeul',
        'zaghouan': 'Zaghouan',
        'bizerte': 'Bizerte',
        'beja': 'Béja',
        'jendouba': 'Jendouba',
        'kef': 'Le Kef',
        'siliana': 'Siliana'
    }
    
    # Check address first
    for key, value in gov_mappings.items():
        if key in address:
            return value
    
    # Check conseil régional  
    if 'tunis' in conseil or 'ben arous' in conseil:
        return 'Tunis'
    elif 'sfax' in conseil or 'sud' in conseil:
        return 'Sfax'
    elif 'sousse' in conseil or 'monastir' in conseil:
        return 'Sousse'
    elif 'nabeul' in conseil:
        return 'Nabeul'
    
    return 'Non déterminé'

def extract_city_from_address(address):
    """Extract city from address"""
    address_lower = address.lower()
    
    cities = [
        'tunis', 'sfax', 'sousse', 'ariana', 'ben arous', 'nabeul', 'monastir', 
        'mahdia', 'kairouan', 'kasserine', 'sidi bouzid', 'gafsa', 'tozeur', 
        'kebili', 'tataouine', 'medenine', 'zaghouan', 'siliana', 'kef', 
        'jendouba', 'beja', 'manouba', 'bizerte', 'gabes'
    ]
    
    for city in cities:
        if city in address_lower:
            return city
    
    # Extract postal codes
    postal_match = re.search(r'\b(\d{4})\b', address)
    if postal_match:
        return f"postal_{postal_match.group(1)}"
    
    return ""

def main():
    """Main processing function"""
    
    # File paths - use relative paths from project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "data", "data_geo", "professionsLibéreales", "claasic", "experts_comptables_oect.json")
    output_dir = os.path.join(base_dir, "app", "experts_comptables", "Data")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading experts comptables data...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} experts comptables records")
    
    # Clean and process data
    df['cleaned_address'] = df['Adresse'].apply(clean_address)
    df['profession'] = 'expert_comptable'
    df['specialite'] = df['Conseil_régional'].fillna('Non spécifié')
    df['gouvernorat'] = df.apply(extract_governorate, axis=1)
    df['ville_detectee'] = df['cleaned_address'].apply(extract_city_from_address)
    
    # Add placeholder coordinates (will be filled by precision geocoding)
    df['latitude'] = None
    df['longitude'] = None
    df['confidence'] = 0.0
    df['method'] = 'pending_geocoding'
    df['zone'] = 'unknown'
    
    # Generate summary
    print(f"\n=== DATA SUMMARY ===")
    print(f"Total records: {len(df)}")
    print(f"Unique governorates: {df['gouvernorat'].nunique()}")
    print(f"Records by governorate:")
    print(df['gouvernorat'].value_counts())
    
    print(f"\nRecords by conseil régional:")
    print(df['Conseil_régional'].value_counts())
    
    # Save processed data
    output_file = f"{output_dir}/experts_comptables_processed.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nProcessed data saved to: {output_file}")
    
    # Create sample for manual verification
    sample_df = df.head(10).copy()
    sample_file = f"{output_dir}/experts_comptables_sample.csv"
    sample_df.to_csv(sample_file, index=False, encoding='utf-8')
    print(f"Sample data saved to: {sample_file}")
    
    return df

if __name__ == "__main__":
    main()