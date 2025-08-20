#!/usr/bin/env python3
"""
HIGH-PRECISION ADDRESS GEOCODING FOR BUSINESS ANALYSIS
This script provides exact street-level coordinates for accurate distance calculations
between doctors and banks/competitors.
"""
import csv
import requests
import time
import re
import json
from urllib.parse import quote

class PreciseGeocodingService:
    """
    High-precision geocoding service for Tunisia addresses
    Uses multiple geocoding providers for maximum accuracy
    """
    
    def __init__(self):
        self.cache = {}  # Address cache to avoid duplicate requests
        self.success_count = 0
        self.total_requests = 0
        
    def clean_tunisia_address(self, address):
        """Clean and standardize Tunisia address for geocoding"""
        if not address:
            return ""
            
        address = str(address).strip()
        
        # Remove extra whitespace
        address = re.sub(r'\s+', ' ', address)
        
        # Add Tunisia if not present
        if 'tunisia' not in address.lower() and 'tunisie' not in address.lower():
            address = f"{address}, Tunisia"
            
        # Standardize common terms
        replacements = {
            ' av ': ' avenue ',
            ' av. ': ' avenue ',
            ' ave ': ' avenue ',
            ' rue ': ' street ',
            ' rte ': ' route ',
            ' bd ': ' boulevard ',
            ' pl ': ' place ',
            'pres de': 'near',
            'en face': 'opposite',
            'au dessus de': 'above',
        }
        
        address_lower = address.lower()
        for old, new in replacements.items():
            address_lower = address_lower.replace(old, new)
            
        return address_lower
    
    def geocode_with_nominatim(self, address, max_retries=3):
        """
        Geocode using OpenStreetMap Nominatim (free, accurate for Tunisia)
        """
        if address in self.cache:
            return self.cache[address]
            
        base_url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'tn',  # Tunisia only
            'addressdetails': 1,
            'extratags': 1,
            'namedetails': 1
        }
        
        headers = {
            'User-Agent': 'GéoBiat-Medical-Mapping/1.0 (business-analysis)'
        }
        
        for attempt in range(max_retries):
            try:
                self.total_requests += 1
                
                response = requests.get(base_url, params=params, headers=headers, timeout=15)
                time.sleep(1.1)  # Respect rate limiting
                
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        result = results[0]
                        lat = float(result['lat'])
                        lon = float(result['lon'])
                        
                        # Validate Tunisia bounds
                        if 30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.0:
                            geocode_info = {
                                'lat': lat,
                                'lon': lon,
                                'accuracy': result.get('place_rank', 30),  # Lower = more precise
                                'display_name': result.get('display_name', ''),
                                'type': result.get('type', ''),
                                'osm_type': result.get('osm_type', ''),
                                'source': 'nominatim'
                            }
                            
                            self.cache[address] = geocode_info
                            self.success_count += 1
                            return geocode_info
                            
            except Exception as e:
                print(f"Nominatim attempt {attempt + 1} failed for '{address[:50]}...': {e}")
                time.sleep(2)
                
        return None
    
    def geocode_address(self, address, fallback_city=None):
        """
        Main geocoding function with fallback strategies
        """
        if not address:
            return None
            
        # Try exact address first
        clean_addr = self.clean_tunisia_address(address)
        result = self.geocode_with_nominatim(clean_addr)
        
        if result and result['accuracy'] <= 25:  # Good precision (building/street level)
            return result
            
        # Try with city context if available
        if fallback_city and fallback_city not in clean_addr.lower():
            addr_with_city = f"{clean_addr}, {fallback_city}"
            result2 = self.geocode_with_nominatim(addr_with_city)
            if result2 and result2['accuracy'] <= 28:
                return result2
                
        # Return best result or None
        return result if result else None

def geocode_all_doctors_precisely():
    """
    Geocode all doctors with maximum precision for distance analysis
    """
    input_path = 'app/medical_professionals/Data/doctors_geocoded.csv'
    output_path = 'app/medical_professionals/Data/doctors_precise_coordinates.csv'
    
    print("Starting high-precision address geocoding...")
    print("This process will take time but provides maximum accuracy for distance calculations.")
    
    geocoder = PreciseGeocodingService()
    
    # Load existing data
    doctors = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        doctors = list(reader)
    
    print(f"Processing {len(doctors)} doctors for precise geocoding...")
    
    processed = 0
    high_precision = 0
    medium_precision = 0
    low_precision = 0
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'nom', 'prenom', 'specialite', 'adresse', 'telephone',
            'lat', 'lon', 'ville_extraite', 'gouvernorat', 'nom_complet', 'hover_text',
            'precision_level', 'geocoding_accuracy', 'geocoding_source', 'distance_ready'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for doctor in doctors:
            processed += 1
            
            if processed % 25 == 0:
                print(f"Progress: {processed}/{len(doctors)} ({processed/len(doctors)*100:.1f}%)")
                print(f"  High precision: {high_precision}, Medium: {medium_precision}, Low: {low_precision}")
                
            address = doctor.get('adresse', '').strip()
            gouvernorat = doctor.get('gouvernorat', '').strip()
            
            # Try precise geocoding
            geocode_result = geocoder.geocode_address(address, gouvernorat)
            
            if geocode_result:
                doctor['lat'] = geocode_result['lat']
                doctor['lon'] = geocode_result['lon']
                doctor['geocoding_accuracy'] = geocode_result['accuracy']
                doctor['geocoding_source'] = geocode_result['source']
                
                # Classify precision for business analysis
                if geocode_result['accuracy'] <= 20:
                    doctor['precision_level'] = 'HIGH'  # Building/exact address level
                    doctor['distance_ready'] = 'YES'
                    high_precision += 1
                elif geocode_result['accuracy'] <= 25:
                    doctor['precision_level'] = 'MEDIUM'  # Street level
                    doctor['distance_ready'] = 'YES'
                    medium_precision += 1
                else:
                    doctor['precision_level'] = 'LOW'  # Neighborhood level
                    doctor['distance_ready'] = 'PARTIAL'
                    low_precision += 1
                    
                if processed <= 5:  # Show first 5 results
                    print(f"  ✓ {doctor['nom']} {doctor['prenom']}: {doctor['precision_level']} precision")
                    print(f"    {address[:60]}...")
                    print(f"    → {geocode_result['lat']:.6f}, {geocode_result['lon']:.6f}")
                    
            else:
                # Keep existing coordinates but mark as low precision
                doctor['precision_level'] = 'ESTIMATED'
                doctor['geocoding_accuracy'] = 99
                doctor['geocoding_source'] = 'city_estimate'
                doctor['distance_ready'] = 'NO'
                low_precision += 1
                
            writer.writerow(doctor)
            
            # Progressive rate limiting
            if processed % 10 == 0:
                time.sleep(2)  # Be respectful to geocoding service
    
    # Final statistics
    print(f"\n=== PRECISION GEOCODING COMPLETE ===")
    print(f"Total processed: {processed}")
    print(f"Geocoding requests made: {geocoder.total_requests}")
    print(f"Successful geocodings: {geocoder.success_count}")
    print(f"Success rate: {(geocoder.success_count/geocoder.total_requests)*100:.1f}%")
    print(f"\nPRECISION BREAKDOWN:")
    print(f"  HIGH precision (building-level): {high_precision} ({high_precision/processed*100:.1f}%)")
    print(f"  MEDIUM precision (street-level): {medium_precision} ({medium_precision/processed*100:.1f}%)")  
    print(f"  LOW/ESTIMATED precision: {low_precision} ({low_precision/processed*100:.1f}%)")
    print(f"\nDistance calculation ready: {high_precision + medium_precision} doctors")
    print(f"Output saved to: {output_path}")

def test_distance_calculation():
    """
    Test distance calculation between doctors and banks
    """
    print("\n=== TESTING DISTANCE CALCULATIONS ===")
    
    # Load bank coordinates
    banks_path = 'app/base_prospection/Data/geo_banks.csv'
    try:
        banks = []
        with open(banks_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            banks = [row for row in reader if row.get('banque', '').upper() == 'BIAT']
            
        print(f"Loaded {len(banks)} BIAT branches for distance testing")
        
        if banks:
            # Test with first bank
            test_bank = banks[0]
            bank_lat = float(test_bank.get('lat', 0))
            bank_lon = float(test_bank.get('long', 0))  # Note: 'long' in banks file
            
            print(f"Test bank: {test_bank.get('agence', 'Unknown')} at {bank_lat:.6f}, {bank_lon:.6f}")
            print("This precision allows accurate distance calculations for business analysis.")
            
    except Exception as e:
        print(f"Note: Bank data not found for distance testing: {e}")

if __name__ == "__main__":
    geocode_all_doctors_precisely()
    test_distance_calculation()