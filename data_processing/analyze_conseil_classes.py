#!/usr/bin/env python3
"""
Analyze the conseil régional classes in experts comptables data
"""

import pandas as pd
import json
from collections import Counter

def analyze_conseil_classes():
    # Load original data
    with open('../data/data_geo/professionsLibéreales/claasic/experts_comptables_oect.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    df = pd.DataFrame(raw_data)
    
    print('=== CONSEIL RÉGIONAL ANALYSIS ===\n')
    
    print('DISTRIBUTION BY CONSEIL:')
    conseil_dist = df['Conseil_régional'].value_counts()
    for conseil, count in conseil_dist.items():
        percentage = (count/len(df))*100
        print(f'  "{conseil}": {count} experts ({percentage:.1f}%)')
    
    print('\n=== ANALYSIS OF ******* CLASS ===')
    
    # Focus on the ******* entries
    asterisk_experts = df[df['Conseil_régional'] == '*******']
    print(f'Total ******* experts: {len(asterisk_experts)}')
    
    # Analyze membership years
    print('\nMEMBERSHIP YEARS:')
    year_dist = asterisk_experts['Année_adhésion'].value_counts().sort_index()
    for year, count in year_dist.items():
        print(f'  {year}: {count} experts')
    
    # Geographic analysis
    print('\nGEOGRAPHIC DISTRIBUTION:')
    locations = []
    for addr in asterisk_experts['Adresse']:
        addr_upper = str(addr).upper()
        if 'TUNIS' in addr_upper:
            locations.append('Tunis')
        elif 'SFAX' in addr_upper:
            locations.append('Sfax')
        elif 'ARIANA' in addr_upper:
            locations.append('Ariana')
        elif 'SOUSSE' in addr_upper:
            locations.append('Sousse')
        elif 'BEN AROUS' in addr_upper:
            locations.append('Ben Arous')
        else:
            locations.append('Other/Unknown')
    
    loc_counter = Counter(locations)
    for loc, count in loc_counter.items():
        print(f'  {loc}: {count} experts')
    
    # Compare with other councils
    print('\nCOMPARISON WITH OTHER COUNCILS:')
    print('Average membership year by council:')
    for conseil in df['Conseil_régional'].unique():
        conseil_data = df[df['Conseil_régional'] == conseil]
        avg_year = conseil_data['Année_adhésion'].mean()
        min_year = conseil_data['Année_adhésion'].min()
        max_year = conseil_data['Année_adhésion'].max()
        print(f'  {conseil}: avg={avg_year:.1f} (range: {min_year}-{max_year})')
    
    # Contact information analysis
    print('\nCONTACT INFO COMPLETENESS:')
    for conseil in df['Conseil_régional'].unique():
        conseil_data = df[df['Conseil_régional'] == conseil]
        email_count = conseil_data['Email'].notna().sum()
        phone_count = conseil_data['Téléphone'].notna().sum()
        print(f'  {conseil}: {email_count}/{len(conseil_data)} emails, {phone_count}/{len(conseil_data)} phones')
    
    print('\nSAMPLE ******* EXPERTS:')
    sample = asterisk_experts[['Nom', 'Adresse', 'Année_adhésion', 'Email']].head(5)
    for i, (_, row) in enumerate(sample.iterrows(), 1):
        print(f'  {i}. {row["Nom"]} (joined: {row["Année_adhésion"]})')
        print(f'     Email: {row["Email"] if pd.notna(row["Email"]) else "None"}')
        print(f'     Address: {row["Adresse"][:60]}...')
    
    print('\n=== HYPOTHESIS ABOUT ******* ===')
    
    # Check if ******* represents older memberships or special status
    asterisk_avg_year = asterisk_experts['Année_adhésion'].mean()
    overall_avg_year = df['Année_adhésion'].mean()
    
    print(f'******* average year: {asterisk_avg_year:.1f}')
    print(f'Overall average year: {overall_avg_year:.1f}')
    
    if asterisk_avg_year < overall_avg_year:
        print('CONCLUSION: ******* appears to represent OLDER/FOUNDING MEMBERS')
    else:
        print('CONCLUSION: ******* does not correlate with membership age')
    
    # Check geographic concentration
    tunis_asterisk = sum(1 for loc in locations if loc == 'Tunis')
    tunis_percentage = (tunis_asterisk / len(asterisk_experts)) * 100
    print(f'Geographic concentration: {tunis_percentage:.1f}% in Tunis area')
    
    if tunis_percentage > 70:
        print('CONCLUSION: ******* appears to be concentrated in TUNIS region')
    
    print('\nPOSSIBLE MEANINGS:')
    print('1. Founding members or senior experts')
    print('2. Special status members (retired, honorary, etc.)')
    print('3. Members with confidential/private status')
    print('4. Administrative placeholder for unassigned council')
    print('5. Default value for incomplete records')

if __name__ == "__main__":
    analyze_conseil_classes()