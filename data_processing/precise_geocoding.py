#!/usr/bin/env python3
"""
Precise geocoding for medical professionals using real address coordinates
This script replaces random offsets with accurate street-level geocoding
"""
import json
import csv
import requests
import time
import re
from urllib.parse import quote

def clean_address(address):
    """Clean and standardize address for geocoding"""
    if not address:
        return ""
    
    # Remove extra whitespace and normalize
    address = re.sub(r'\s+', ' ', address.strip())
    
    # Add Tunisia if not present
    if 'tunis' not in address.lower() and 'tunisia' not in address.lower():
        address = f"{address}, Tunisia"
    
    return address

def geocode_with_nominatim(address, city=None, max_retries=3):
    """
    Geocode address using Nominatim (OpenStreetMap) API
    More accurate than random offsets
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Clean the address
    clean_addr = clean_address(address)
    
    # Build search query
    if city and city.lower() not in clean_addr.lower():
        search_query = f"{clean_addr}, {city}, Tunisia"
    else:
        search_query = clean_addr
    
    params = {
        'q': search_query,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'tn',  # Restrict to Tunisia
        'addressdetails': 1
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=10)
            time.sleep(1)  # Rate limiting
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    result = results[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    
                    # Basic bounds check for Tunisia
                    if 30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.0:
                        return lat, lon, result.get('display_name', '')
            
        except Exception as e:
            print(f"Geocoding attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    
    return None, None, None

def validate_coordinates(lat, lon, address):
    """
    Validate that coordinates are reasonable for Tunisia
    Check they're not in water/sabkha/desert
    """
    if not lat or not lon:
        return False
    
    try:
        lat, lon = float(lat), float(lon)
        
        # Tunisia bounds check
        if not (30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.0):
            return False
        
        # Basic water/sea check - avoid coordinates too close to coastline
        # This is a simplified check - in production you'd use land/water polygons
        
        # Northern coast (Mediterranean) - avoid points too close to sea
        if lat > 37.0 and (lon < 8.5 or lon > 11.5):
            return False
            
        # Eastern coast - avoid points in Gulf of Gabès
        if lat < 34.0 and lon > 10.5:
            return False
            
        return True
        
    except (ValueError, TypeError):
        return False

def process_with_precise_geocoding():
    """Process doctors with precise address-based geocoding"""
    source_path = 'app/medical_professionals/Data/doctors_geocoded.csv'
    output_path = 'app/medical_professionals/Data/doctors_geocoded_precise.csv'
    
    print("Starting precise geocoding process...")
    print("This will take time as we geocode each address individually...")
    
    processed_count = 0
    improved_count = 0
    
    # Read existing data
    doctors = []
    with open(source_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        doctors = list(reader)
    
    print(f"Processing {len(doctors)} doctors...")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['nom', 'prenom', 'specialite', 'adresse', 'telephone', 
                     'lat', 'lon', 'ville_extraite', 'gouvernorat', 'nom_complet', 
                     'hover_text', 'geocoding_method', 'geocoding_confidence']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, doctor in enumerate(doctors):
            processed_count += 1
            
            if processed_count % 50 == 0:
                print(f"Processed {processed_count}/{len(doctors)} doctors...")
            
            # Current coordinates
            current_lat = doctor.get('lat')
            current_lon = doctor.get('lon')
            address = doctor.get('adresse', '').strip()
            
            # Try precise geocoding
            new_lat, new_lon, display_name = geocode_with_nominatim(
                address, 
                doctor.get('ville_extraite', '')
            )
            
            # Use new coordinates if valid, otherwise keep current
            if validate_coordinates(new_lat, new_lon, address):
                doctor['lat'] = new_lat
                doctor['lon'] = new_lon
                doctor['geocoding_method'] = 'nominatim_precise'
                doctor['geocoding_confidence'] = 'high'
                improved_count += 1
            else:
                # Keep existing coordinates but validate them
                if validate_coordinates(current_lat, current_lon, address):
                    doctor['geocoding_method'] = 'city_offset'
                    doctor['geocoding_confidence'] = 'medium'
                else:
                    # Flag problematic coordinates
                    doctor['geocoding_method'] = 'city_offset_problematic'
                    doctor['geocoding_confidence'] = 'low'
            
            writer.writerow(doctor)
            
            # Rate limiting - be respectful to Nominatim
            if processed_count % 10 == 0:
                time.sleep(2)
    
    print(f"\nPrecise geocoding complete!")
    print(f"Total processed: {processed_count}")
    print(f"Improved with precise coordinates: {improved_count}")
    print(f"Improvement rate: {(improved_count/processed_count)*100:.1f}%")
    print(f"Output saved to: {output_path}")

if __name__ == "__main__":
    process_with_precise_geocoding()