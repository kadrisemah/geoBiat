#!/usr/bin/env python3
"""
DISTANCE CALCULATION EXAMPLE
Demonstrates precise distance calculations between doctors and banks
"""
import csv
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate precise distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def demonstrate_distance_calculations():
    """Demonstrate precise distance calculations for business analysis"""
    
    print("=== DISTANCE CALCULATION DEMONSTRATION ===")
    
    # Load doctors with precision levels
    doctors = []
    with open('app/medical_professionals/Data/doctors_geocoded.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        doctors = [d for d in reader if d.get('distance_ready') == 'YES']
    
    # Load BIAT banks
    banks = []
    with open('app/base_prospection/Data/geo_banks.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        banks = [b for b in reader if b.get('banque', '').upper() == 'BIAT']
    
    print(f"Loaded {len(doctors)} doctors with HIGH/MEDIUM precision coordinates")
    print(f"Loaded {len(banks)} BIAT branches")
    
    if doctors and banks:
        # Example 1: Find nearest BIAT branch for each high-precision doctor
        print(f"\n=== EXAMPLE 1: NEAREST BIAT BRANCH ANALYSIS ===")
        
        sample_doctors = doctors[:5]  # First 5 doctors for demo
        
        for doctor in sample_doctors:
            doctor_name = f"{doctor['nom']} {doctor['prenom']}"
            doctor_lat = float(doctor['lat'])
            doctor_lon = float(doctor['lon'])
            precision = doctor.get('precision_level', 'UNKNOWN')
            
            # Find nearest BIAT branch
            nearest_bank = None
            min_distance = float('inf')
            
            for bank in banks:
                try:
                    bank_lat = float(bank['lat'])
                    bank_lon = float(bank['long'])  # Note: 'long' in bank data
                    
                    distance = haversine_distance(doctor_lat, doctor_lon, bank_lat, bank_lon)
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_bank = bank
                except:
                    continue
            
            if nearest_bank:
                print(f"\n{doctor_name} ({precision} precision)")
                print(f"  Specialty: {doctor['specialite']}")
                print(f"  Address: {doctor['adresse'][:50]}...")
                print(f"  Nearest BIAT: {nearest_bank['agence']}")
                print(f"  Distance: {min_distance:.2f} km")
                
        # Example 2: Doctors within 2km of a specific BIAT branch
        print(f"\n=== EXAMPLE 2: DOCTORS WITHIN 2KM OF BIAT BRANCH ===")
        
        target_bank = banks[0]  # First BIAT branch
        target_lat = float(target_bank['lat'])
        target_lon = float(target_bank['long'])
        radius_km = 2.0
        
        nearby_doctors = []
        for doctor in doctors:
            try:
                doctor_lat = float(doctor['lat'])
                doctor_lon = float(doctor['lon'])
                
                distance = haversine_distance(target_lat, target_lon, doctor_lat, doctor_lon)
                
                if distance <= radius_km:
                    nearby_doctors.append({
                        'doctor': doctor,
                        'distance': distance
                    })
            except:
                continue
        
        # Sort by distance
        nearby_doctors.sort(key=lambda x: x['distance'])
        
        print(f"BIAT Branch: {target_bank['agence']}")
        print(f"Location: {target_bank.get('gouvernorat', 'Unknown')}")
        print(f"Doctors within {radius_km}km: {len(nearby_doctors)}")
        
        for i, entry in enumerate(nearby_doctors[:5]):  # Show first 5
            doctor = entry['doctor']
            distance = entry['distance']
            print(f"  {i+1}. {doctor['nom']} {doctor['prenom']} - {distance:.2f}km")
            print(f"     {doctor['specialite']} | {doctor.get('precision_level', 'UNKNOWN')} precision")
        
        # Example 3: Business opportunity analysis
        print(f"\n=== EXAMPLE 3: BUSINESS OPPORTUNITY METRICS ===")
        
        # Calculate average distance to nearest BIAT for high-precision doctors
        total_distance = 0
        distance_count = 0
        
        for doctor in doctors:
            try:
                doctor_lat = float(doctor['lat'])
                doctor_lon = float(doctor['lon'])
                
                min_dist = float('inf')
                for bank in banks:
                    bank_lat = float(bank['lat'])
                    bank_lon = float(bank['long'])
                    dist = haversine_distance(doctor_lat, doctor_lon, bank_lat, bank_lon)
                    min_dist = min(min_dist, dist)
                
                if min_dist != float('inf'):
                    total_distance += min_dist
                    distance_count += 1
            except:
                continue
        
        if distance_count > 0:
            avg_distance = total_distance / distance_count
            print(f"Average distance from doctors to nearest BIAT: {avg_distance:.2f} km")
            
            # Count doctors by distance ranges
            ranges = [1, 2, 5, 10]
            for max_dist in ranges:
                count = sum(1 for d in doctors if min_distance_to_biat(d, banks) <= max_dist)
                print(f"Doctors within {max_dist}km of BIAT: {count}")

def min_distance_to_biat(doctor, banks):
    """Calculate minimum distance from doctor to any BIAT branch"""
    try:
        doctor_lat = float(doctor['lat'])
        doctor_lon = float(doctor['lon'])
        
        min_dist = float('inf')
        for bank in banks:
            bank_lat = float(bank['lat'])
            bank_lon = float(bank['long'])
            dist = haversine_distance(doctor_lat, doctor_lon, bank_lat, bank_lon)
            min_dist = min(min_dist, dist)
        
        return min_dist if min_dist != float('inf') else 999
    except:
        return 999

def show_precision_benefits():
    """Show benefits of precision upgrade"""
    print(f"\n=== PRECISION BENEFITS FOR BUSINESS ANALYSIS ===")
    print(f"")
    print(f"HIGH PRECISION COORDINATES (±50m accuracy):")
    print(f"✓ Accurate for catchment area analysis")
    print(f"✓ Precise distance calculations for marketing")
    print(f"✓ Reliable proximity-based segmentation")
    print(f"✓ Accurate competitive positioning analysis")
    print(f"")
    print(f"MEDIUM PRECISION COORDINATES (±100m accuracy):")
    print(f"✓ Good for neighborhood-level analysis")
    print(f"✓ Suitable for branch planning decisions")
    print(f"✓ Reliable for radius-based customer identification")
    print(f"")
    print(f"BUSINESS USE CASES:")
    print(f"• Target doctors within 1km of new BIAT branches")
    print(f"• Identify underserved medical areas for expansion")
    print(f"• Calculate market penetration by specialty and location")
    print(f"• Optimize ATM placement near medical centers")
    print(f"• Design territory-based sales strategies")

if __name__ == "__main__":
    demonstrate_distance_calculations()
    show_precision_benefits()