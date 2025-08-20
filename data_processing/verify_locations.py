#!/usr/bin/env python3
import csv
import sys

def verify_locations():
    """Quick verification of doctor locations"""
    
    # Expected governorates in Tunisia (official names)
    valid_governorates = {
        'Tunis', 'Ariana', 'Ben Arous', 'Nabeul', 'Zaghouan', 'Bizerte',
        'Béja', 'Jendouba', 'Le Kef', 'Siliana', 'Sousse', 'Monastir', 'Mahdia',
        'Kasserine', 'Sidi Bouzid', 'Kairouan', 'Sfax', 'Gafsa', 'Tozeur',
        'Kebili', 'Kébili', 'Gabès', 'Médenine', 'Tataouine', 'Manouba'
    }
    
    print("Verifying medical professionals locations...")
    
    try:
        with open('app/medical_professionals/Data/doctors_geocoded.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            total_count = 0
            valid_gov_count = 0
            governorate_counts = {}
            issues = []
            
            for row in reader:
                total_count += 1
                gouvernorat = row.get('gouvernorat', '').strip()
                ville_extraite = row.get('ville_extraite', '').strip()
                adresse = row.get('adresse', '').strip()
                nom = f"{row.get('nom', '')} {row.get('prenom', '')}"
                
                if gouvernorat in valid_governorates:
                    valid_gov_count += 1
                    governorate_counts[gouvernorat] = governorate_counts.get(gouvernorat, 0) + 1
                else:
                    issues.append({
                        'name': nom,
                        'address': adresse,
                        'extracted_city': ville_extraite,
                        'assigned_gov': gouvernorat
                    })
            
            print(f"\nTotal doctors processed: {total_count}")
            print(f"Valid governorate assignments: {valid_gov_count}")
            print(f"Invalid/missing governorates: {len(issues)}")
            print(f"Accuracy: {(valid_gov_count/total_count)*100:.1f}%")
            
            print("\nDoctors by governorate:")
            for gov, count in sorted(governorate_counts.items()):
                print(f"  {gov}: {count}")
            
            if issues:
                print(f"\nFirst 10 problematic entries:")
                for i, issue in enumerate(issues[:10]):
                    print(f"  {i+1}. {issue['name']}")
                    print(f"     Address: {issue['address']}")
                    print(f"     Extracted: {issue['extracted_city']}")
                    print(f"     Gov: {issue['assigned_gov']}")
                    print()
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    verify_locations()