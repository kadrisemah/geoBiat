#!/usr/bin/env python3
"""
Simple processing of Conseillers data
Convert JSON to flat CSV structure
"""

import json
import pandas as pd
import re
import os

def extract_governorate(adresse):
    """Extract governorate from detailed address string"""
    if not adresse or pd.isna(adresse):
        return None
    
    # Common pattern: "Gouvernorat de [Name]" or "Gouvernorat de l'[Name]"
    gov_patterns = [
        r'Gouvernorat de l\'([^,\s]+)',
        r'Gouvernorat de ([^,\s]+)',
        r'Gouvernorat\s+([^,\s]+)'
    ]
    
    for pattern in gov_patterns:
        match = re.search(pattern, adresse, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Extract city/region names from common patterns
    location_patterns = [
        r'([A-Za-z\s]+)\s+-\s+Tunisie',
        r'([A-Za-z\s]+)\s+Gouvernorat',
        r'([A-Za-z\s]+)\s+-\s+\d+'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, adresse, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Common governorates
            if any(gov in location.lower() for gov in ['tunis', 'ariana', 'sousse', 'sfax', 'nabeul', 'monastir', 'kairouan', 'bizerte', 'gabes', 'gafsa', 'medenine', 'tozeur', 'kebili', 'tataouine', 'kasserine', 'sidi bouzid', 'zaghouan', 'siliana', 'beja', 'jendouba', 'kef', 'mahdia', 'manouba']):
                return location
    
    return None

def process_conseillers_data():
    """Process conseillers JSON data and create simple CSV"""
    
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Input and output paths
    input_file = os.path.join(project_root, 'data', 'data_geo', 'professionsLibéreales', 'claasic', 'conseillers_goafrica.json')
    output_file = os.path.join(project_root, 'app', 'conseillers', 'Data', 'conseillers_simple.csv')
    
    print(f"Processing conseillers data from: {input_file}")
    
    # Load JSON data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} conseillers records")
    
    # Process each record
    processed_records = []
    
    for record in data:
        # Extract fields
        nom = record.get('Nom', '').strip()
        adresse = record.get('Adresse', '').strip()
        telephone = record.get('Telephone', '').strip()
        categorie = record.get('Categorie', '').strip()
        lien = record.get('Lien', '').strip()
        
        # Extract governorate
        gouvernorat = extract_governorate(adresse)
        
        # Extract Google Plus Code if present
        plus_code = None
        plus_code_match = re.search(r'([A-Z0-9]{4}\+[A-Z0-9]{2,})', adresse)
        if plus_code_match:
            plus_code = plus_code_match.group(1)
        
        # Create processed record
        processed_record = {
            'nom': nom,
            'adresse_complete': adresse,
            'plus_code': plus_code,
            'telephone': telephone,
            'categorie': categorie,
            'gouvernorat': gouvernorat,
            'lien': lien,
            'profession': 'Conseillers'
        }
        
        processed_records.append(processed_record)
    
    # Create DataFrame
    df = pd.DataFrame(processed_records)
    
    # Data quality analysis
    print("\n=== DATA QUALITY ANALYSIS ===")
    print(f"Total records: {len(df)}")
    print(f"Records with names: {df['nom'].notna().sum()}")
    print(f"Records with addresses: {df['adresse_complete'].notna().sum()}")
    print(f"Records with Google Plus Codes: {df['plus_code'].notna().sum()}")
    print(f"Records with phone numbers: {df['telephone'].notna().sum()}")
    print(f"Records with governorates: {df['gouvernorat'].notna().sum()}")
    
    # Governorate distribution
    print("\n=== GOVERNORATE DISTRIBUTION ===")
    gov_counts = df['gouvernorat'].value_counts()
    for gov, count in gov_counts.items():
        print(f"{gov}: {count}")
    
    print(f"\nMissing governorate: {df['gouvernorat'].isna().sum()}")
    
    # Category analysis
    print("\n=== CATEGORY ANALYSIS ===")
    cat_counts = df['categorie'].value_counts()
    for cat, count in cat_counts.items():
        print(f"{cat}: {count}")
    
    # Save processed data
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nProcessed data saved to: {output_file}")
    
    return df

if __name__ == "__main__":
    df = process_conseillers_data()
    print("\nConseillers data processing completed successfully!")