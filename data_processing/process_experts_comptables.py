#!/usr/bin/env python3
"""
High-precision geocoding for Experts Comptables (Chartered Accountants)
Applies the same precision standards as doctors geocoding
"""

import json
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import re
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")

class ExpertsComptablesGeocoder:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="experts_comptables_biat_precision_v2")
        self.geocode_with_delay = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        
        # High-precision zone boundaries for Chalendise (same as doctors)
        self.chalendise_zones = {
            'core': {'lat_range': (33.8, 34.0), 'lon_range': (9.4, 9.8)},  # Center
            'extended': {'lat_range': (33.7, 34.1), 'lon_range': (9.3, 9.9)},  # Wider area
            'greater_area': {'lat_range': (33.5, 34.3), 'lon_range': (9.0, 10.2)}  # Full region
        }
        
        # Major cities coordinates for validation
        self.city_coordinates = {
            'tunis': (36.8065, 10.1815),
            'sfax': (34.7406, 10.7603),
            'sousse': (35.8256, 10.6369),
            'kairouan': (35.6781, 10.0963),
            'bizerte': (37.2746, 9.8739),
            'gabes': (33.8815, 10.0982),
            'ariana': (36.8625, 10.1956),
            'ben arous': (36.7539, 10.2277),
            'nabeul': (36.4561, 10.7376),
            'monastir': (35.7643, 10.8113),
            'mahdia': (35.5047, 11.0622),
            'kasserine': (35.1674, 8.8363),
            'sidi bouzid': (35.0381, 9.4858),
            'gafsa': (34.4250, 8.7842),
            'tozeur': (33.9197, 8.1339),
            'kebili': (33.7044, 8.9690),
            'tataouine': (32.9297, 10.4517),
            'medenine': (33.3548, 10.5055),
            'zaghouan': (36.4026, 10.1425),
            'siliana': (36.0836, 9.3706),
            'kef': (36.1690, 8.7040),
            'jendouba': (36.5014, 8.7800),
            'beja': (36.7255, 9.1816),
            'manouba': (36.8099, 10.0969)
        }

    def clean_address(self, address: str) -> str:
        """Clean and standardize address text"""
        if pd.isna(address) or not address:
            return ""
        
        # Convert to string and clean
        address = str(address).strip()
        
        # Remove extra spaces and normalize
        address = re.sub(r'\s+', ' ', address)
        
        # Common address cleaning
        address = address.replace('  ', ' ')
        address = address.replace(' ,', ',')
        address = address.replace(', ,', ',')
        
        return address

    def extract_city_from_address(self, address: str) -> str:
        """Extract city/governorate from address"""
        address_lower = address.lower()
        
        # Check for known cities
        for city in self.city_coordinates.keys():
            if city in address_lower:
                return city
                
        # Try to extract from common patterns
        patterns = [
            r'\b(tunis|sfax|sousse|ariana|ben arous|nabeul|monastir|mahdia|kairouan|kasserine|sidi bouzid|gafsa|tozeur|kebili|tataouine|medenine|zaghouan|siliana|kef|jendouba|beja|manouba|bizerte|gabes)\b',
            r'\b(\d{4})\b'  # Postal codes
        ]
        
        for pattern in patterns:
            match = re.search(pattern, address_lower)
            if match:
                return match.group(1)
        
        return ""

    def validate_coordinates(self, lat: float, lon: float, address: str) -> Dict[str, any]:
        """Validate coordinates against known geographic constraints"""
        
        # Tunisia bounds check
        if not (30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.0):
            return {
                'valid': False,
                'issue': 'outside_tunisia',
                'confidence': 0.0,
                'zone': 'invalid'
            }
        
        # Determine zone
        zone = 'outside_region'
        confidence = 0.5
        
        core = self.chalendise_zones['core']
        extended = self.chalendise_zones['extended'] 
        greater = self.chalendise_zones['greater_area']
        
        if (core['lat_range'][0] <= lat <= core['lat_range'][1] and 
            core['lon_range'][0] <= lon <= core['lon_range'][1]):
            zone = 'zone_chalendise_core'
            confidence = 1.0
        elif (extended['lat_range'][0] <= lat <= extended['lat_range'][1] and 
              extended['lon_range'][0] <= lon <= extended['lon_range'][1]):
            zone = 'zone_chalendise_extended'
            confidence = 0.9
        elif (greater['lat_range'][0] <= lat <= greater['lat_range'][1] and 
              greater['lon_range'][0] <= lon <= greater['lon_range'][1]):
            zone = 'zone_chalendise_greater'
            confidence = 0.8
        
        # Check against known city coordinates
        city_from_address = self.extract_city_from_address(address)
        if city_from_address in self.city_coordinates:
            expected_lat, expected_lon = self.city_coordinates[city_from_address]
            distance_km = self.calculate_distance(lat, lon, expected_lat, expected_lon)
            
            if distance_km > 50:  # More than 50km from expected city
                confidence *= 0.7
                
        return {
            'valid': True,
            'zone': zone,
            'confidence': confidence,
            'city_detected': city_from_address
        }

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r

    def geocode_address(self, address: str, name: str = "") -> Dict[str, any]:
        """Geocode a single address with high precision"""
        
        if not address or pd.isna(address):
            return {
                'latitude': None,
                'longitude': None,
                'confidence': 0.0,
                'method': 'no_address',
                'zone': 'unknown'
            }
        
        cleaned_address = self.clean_address(address)
        
        # Try multiple address variations for better accuracy
        address_variations = [
            f"{cleaned_address}, Tunisia",
            f"{cleaned_address}, Tunisie",
            cleaned_address,
        ]
        
        # If name contains city info, add it
        city_from_address = self.extract_city_from_address(cleaned_address)
        if city_from_address:
            address_variations.insert(0, f"{cleaned_address}, {city_from_address}, Tunisia")
        
        best_result = None
        best_confidence = 0.0
        
        for variation in address_variations:
            try:
                location = self.geocode_with_delay(variation)
                if location:
                    validation = self.validate_coordinates(location.latitude, location.longitude, cleaned_address)
                    
                    if validation['valid'] and validation['confidence'] > best_confidence:
                        best_result = {
                            'latitude': location.latitude,
                            'longitude': location.longitude,
                            'confidence': validation['confidence'],
                            'method': 'nominatim_precise',
                            'zone': validation['zone'],
                            'city_detected': validation.get('city_detected', ''),
                            'address_used': variation
                        }
                        best_confidence = validation['confidence']
                        
                        # If we get high confidence, use it
                        if best_confidence >= 0.9:
                            break
                            
            except Exception as e:
                print(f"Geocoding error for {variation}: {e}")
                continue
                
        if best_result:
            return best_result
        
        # Fallback: try to use city coordinates if detected
        city_from_address = self.extract_city_from_address(cleaned_address)
        if city_from_address in self.city_coordinates:
            lat, lon = self.city_coordinates[city_from_address]
            validation = self.validate_coordinates(lat, lon, cleaned_address)
            
            return {
                'latitude': lat,
                'longitude': lon,
                'confidence': 0.6,  # Lower confidence for city-level geocoding
                'method': 'city_fallback',
                'zone': validation['zone'],
                'city_detected': city_from_address
            }
        
        return {
            'latitude': None,
            'longitude': None,
            'confidence': 0.0,
            'method': 'failed',
            'zone': 'unknown'
        }

    def process_experts_comptables(self, json_file_path: str) -> pd.DataFrame:
        """Process the experts comptables JSON file with high-precision geocoding"""
        
        print("Loading experts comptables data...")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} experts comptables records")
        
        # Add geocoding columns
        geocoding_results = []
        
        print("Starting high-precision geocoding...")
        for idx, row in df.iterrows():
            if idx % 50 == 0:
                print(f"Processed {idx}/{len(df)} records...")
            
            # Get address and name
            address = row.get('Adresse', '')
            name = row.get('Nom', '')
            
            # Geocode
            result = self.geocode_address(address, name)
            geocoding_results.append(result)
            
            # Add small delay to respect rate limits
            time.sleep(0.1)
        
        # Add results to dataframe
        for i, result in enumerate(geocoding_results):
            for key, value in result.items():
                df.loc[i, key] = value
        
        # Add standard columns
        df['profession'] = 'expert_comptable'
        df['specialite'] = df['Conseil_régional'].fillna('Non spécifié')
        
        # Extract governorate from address or council region
        df['gouvernorat'] = df.apply(lambda row: self.extract_governorate(row), axis=1)
        
        # Quality metrics
        total_records = len(df)
        geocoded_records = len(df[df['latitude'].notna()])
        high_confidence = len(df[df['confidence'] >= 0.8])
        chalendise_zone = len(df[df['zone'].str.contains('chalendise', na=False)])
        
        print(f"\n=== GEOCODING RESULTS ===")
        print(f"Total records: {total_records}")
        print(f"Successfully geocoded: {geocoded_records} ({geocoded_records/total_records*100:.1f}%)")
        print(f"High confidence (≥0.8): {high_confidence} ({high_confidence/total_records*100:.1f}%)")
        print(f"In Zone de Chalendise: {chalendise_zone} ({chalendise_zone/total_records*100:.1f}%)")
        
        return df

    def extract_governorate(self, row) -> str:
        """Extract governorate from address or other fields"""
        
        # First try from address
        address = str(row.get('Adresse', '')).lower()
        conseil = str(row.get('Conseil_régional', '')).lower()
        
        # Common governorate mappings
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
        
        # Default based on detected city
        city_detected = row.get('city_detected', '')
        if city_detected in gov_mappings:
            return gov_mappings[city_detected]
        
        return 'Non déterminé'


def main():
    """Main processing function"""
    
    # File paths
    input_file = "/mnt/c/Users/Semah Kadri/OneDrive - Value Digital Services/Bureau/GéoBiat/geoBiat/data/data_geo/professionsLibéreales/claasic/experts_comptables_oect.json"
    output_dir = "/mnt/c/Users/Semah Kadri/OneDrive - Value Digital Services/Bureau/GéoBiat/geoBiat/app/experts_comptables/Data"
    
    # Initialize geocoder
    geocoder = ExpertsComptablesGeocoder()
    
    # Process data
    df_processed = geocoder.process_experts_comptables(input_file)
    
    # Save results
    output_file = f"{output_dir}/experts_comptables_geocoded.csv"
    df_processed.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nResults saved to: {output_file}")
    
    # Save only high-confidence records for immediate use
    df_high_confidence = df_processed[df_processed['confidence'] >= 0.7].copy()
    high_conf_file = f"{output_dir}/experts_comptables_high_confidence.csv"
    df_high_confidence.to_csv(high_conf_file, index=False, encoding='utf-8')
    print(f"High confidence records saved to: {high_conf_file}")
    
    # Generate summary report
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Total experts comptables processed: {len(df_processed)}")
    print(f"High confidence geocoded: {len(df_high_confidence)}")
    
    zone_distribution = df_processed['zone'].value_counts()
    print(f"\nZone distribution:")
    for zone, count in zone_distribution.items():
        print(f"  {zone}: {count}")
    
    return df_processed

if __name__ == "__main__":
    main()