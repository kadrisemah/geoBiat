#!/usr/bin/env python3
"""
Simple processing for Pharmacies data
Converts nested JSON structure to flat CSV with basic data cleaning
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

def extract_governorate_from_nested_structure(gov_key):
    """Extract and standardize governorate name"""
    
    # Governorate mappings for standardization
    gov_mappings = {
        'ariana': 'Ariana',
        'beja': 'Béja',
        'ben arous': 'Ben Arous', 
        'bizerte': 'Bizerte',
        'gabes': 'Gabès',
        'gafsa': 'Gafsa',
        'jendouba': 'Jendouba',
        'kairouan': 'Kairouan',
        'kasserine': 'Kasserine',
        'kebili': 'Kebili',
        'kef': 'Le Kef',
        'mahdia': 'Mahdia',
        'manouba': 'Manouba',
        'medenine': 'Médenine',
        'monastir': 'Monastir',
        'nabeul': 'Nabeul',
        'sfax': 'Sfax',
        'sidi bouzid': 'Sidi Bouzid',
        'siliana': 'Siliana',
        'sousse': 'Sousse',
        'tataouine': 'Tataouine',
        'tozeur': 'Tozeur',
        'tunis': 'Tunis',
        'zaghouan': 'Zaghouan'
    }
    
    gov_lower = str(gov_key).lower().strip()
    return gov_mappings.get(gov_lower, gov_key)

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
    
    # File paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "data", "data_geo", "professionsLibéreales", "claasic", "pharmacies_tunisie_complet.json")
    output_dir = os.path.join(base_dir, "app", "pharmacies", "Data")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading pharmacies data...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Flattening nested structure...")
    
    # Flatten the nested structure
    pharmacies_list = []
    
    for gouvernorat, delegations in data.items():
        if not isinstance(delegations, dict):
            continue
            
        for delegation, categories in delegations.items():
            if not isinstance(categories, dict):
                continue
                
            for category, pharmacies in categories.items():
                if not isinstance(pharmacies, list):
                    continue
                    
                for pharmacy in pharmacies:
                    if isinstance(pharmacy, dict):
                        # Create flattened record
                        flat_record = {
                            'Nom': pharmacy.get('Nom', ''),
                            'Adresse': pharmacy.get('Adresse', ''),
                            'Téléphone': pharmacy.get('Téléphone', ''),
                            'gouvernorat_source': gouvernorat,
                            'delegation_source': delegation,
                            'category': category  # jour/nuit
                        }
                        pharmacies_list.append(flat_record)
    
    df = pd.DataFrame(pharmacies_list)
    print(f"Flattened {len(df)} pharmacy records")
    
    # Clean and process data
    df['cleaned_address'] = df['Adresse'].apply(clean_address)
    df['profession'] = 'pharmacie'
    df['specialite'] = df['category']  # jour/nuit service
    df['gouvernorat'] = df['gouvernorat_source'].apply(extract_governorate_from_nested_structure)
    df['delegation'] = df['delegation_source'].str.title()
    df['ville_detectee'] = df['cleaned_address'].apply(extract_city_from_address)
    
    # Add placeholder coordinates (will be filled by precision geocoding)
    df['latitude'] = None
    df['longitude'] = None
    df['confidence'] = 0.0
    df['method'] = 'pending_geocoding'
    df['zone'] = 'unknown'
    
    # Generate summary
    print(f"\n=== PHARMACY DATA SUMMARY ===")
    print(f"Total records: {len(df)}")
    print(f"Unique governorates: {df['gouvernorat'].nunique()}")
    print(f"Records by governorate:")
    print(df['gouvernorat'].value_counts())
    
    print(f"\nRecords by category (jour/nuit):")
    print(df['specialite'].value_counts())
    
    print(f"\nTop delegations:")
    print(df['delegation'].value_counts().head(10))
    
    # Save processed data
    output_file = f"{output_dir}/pharmacies_processed.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nProcessed data saved to: {output_file}")
    
    # Create sample for manual verification
    sample_df = df.head(10).copy()
    sample_file = f"{output_dir}/pharmacies_sample.csv"
    sample_df.to_csv(sample_file, index=False, encoding='utf-8')
    print(f"Sample data saved to: {sample_file}")
    
    return df

if __name__ == "__main__":
    main()