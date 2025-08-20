"""
Fix medical professionals location accuracy
This script corrects the geocoding errors by improving city/location detection
"""
import json
import csv
import random

# Comprehensive Tunisia cities and towns with correct governorate assignments
TUNISIA_LOCATIONS = {
    # Tunis Governorate
    'tunis': {'lat': 36.8065, 'lon': 10.1815, 'gouvernorat': 'Tunis'},
    'carthage': {'lat': 36.8529, 'lon': 10.3312, 'gouvernorat': 'Tunis'},
    'sidi_bou_said': {'lat': 36.8703, 'lon': 10.3499, 'gouvernorat': 'Tunis'},
    'la_marsa': {'lat': 36.8786, 'lon': 10.3247, 'gouvernorat': 'Tunis'},
    'bab_el_bhar': {'lat': 36.8019, 'lon': 10.1797, 'gouvernorat': 'Tunis'},
    
    # Ariana Governorate
    'ariana': {'lat': 36.8622, 'lon': 10.1647, 'gouvernorat': 'Ariana'},
    'raoued': {'lat': 36.8947, 'lon': 10.1884, 'gouvernorat': 'Ariana'},
    'soukra': {'lat': 36.8833, 'lon': 10.2167, 'gouvernorat': 'Ariana'},
    'ettadhamen': {'lat': 36.8139, 'lon': 10.0639, 'gouvernorat': 'Ariana'},
    
    # Ben Arous Governorate
    'ben_arous': {'lat': 36.7539, 'lon': 10.2192, 'gouvernorat': 'Ben Arous'},
    'rades': {'lat': 36.7628, 'lon': 10.2736, 'gouvernorat': 'Ben Arous'},
    'ezzahra': {'lat': 36.7544, 'lon': 10.3031, 'gouvernorat': 'Ben Arous'},
    'hammam_lif': {'lat': 36.7292, 'lon': 10.3408, 'gouvernorat': 'Ben Arous'},
    'mohamedia': {'lat': 36.6786, 'lon': 10.2847, 'gouvernorat': 'Ben Arous'},
    
    # Manouba Governorate
    'manouba': {'lat': 36.8103, 'lon': 10.0964, 'gouvernorat': 'Manouba'},
    'denden': {'lat': 36.8069, 'lon': 10.0333, 'gouvernorat': 'Manouba'},
    'oued_ellil': {'lat': 36.8139, 'lon': 10.0542, 'gouvernorat': 'Manouba'},
    
    # Nabeul Governorate (IMPORTANT: Hammamet belongs here!)
    'nabeul': {'lat': 36.4561, 'lon': 10.7376, 'gouvernorat': 'Nabeul'},
    'hammamet': {'lat': 36.4000, 'lon': 10.6167, 'gouvernorat': 'Nabeul'},  # CORRECTED!
    'kelibia': {'lat': 36.8478, 'lon': 11.0936, 'gouvernorat': 'Nabeul'},
    'korba': {'lat': 36.5744, 'lon': 10.8592, 'gouvernorat': 'Nabeul'},
    'menzel_temime': {'lat': 36.7831, 'lon': 10.9906, 'gouvernorat': 'Nabeul'},
    'grombalia': {'lat': 36.6072, 'lon': 10.4947, 'gouvernorat': 'Nabeul'},
    'soliman': {'lat': 36.7058, 'lon': 10.4947, 'gouvernorat': 'Nabeul'},
    
    # Zaghouan Governorate
    'zaghouan': {'lat': 36.4028, 'lon': 10.1425, 'gouvernorat': 'Zaghouan'},
    'fahs': {'lat': 36.3833, 'lon': 10.0833, 'gouvernorat': 'Zaghouan'},
    'zriba': {'lat': 36.3903, 'lon': 10.1364, 'gouvernorat': 'Zaghouan'},
    
    # Bizerte Governorate
    'bizerte': {'lat': 37.2744, 'lon': 9.8739, 'gouvernorat': 'Bizerte'},
    'menzel_bourguiba': {'lat': 37.1544, 'lon': 9.7856, 'gouvernorat': 'Bizerte'},
    'mateur': {'lat': 37.0406, 'lon': 9.6656, 'gouvernorat': 'Bizerte'},
    'ras_jebel': {'lat': 37.1739, 'lon': 9.8717, 'gouvernorat': 'Bizerte'},
    'menzel_jemil': {'lat': 37.2336, 'lon': 9.9164, 'gouvernorat': 'Bizerte'},
    
    # Beja Governorate
    'beja': {'lat': 36.7256, 'lon': 9.1817, 'gouvernorat': 'Béja'},
    'medjez_el_bab': {'lat': 36.6481, 'lon': 9.6103, 'gouvernorat': 'Béja'},
    'testour': {'lat': 36.5544, 'lon': 9.4439, 'gouvernorat': 'Béja'},
    'nefza': {'lat': 37.0425, 'lon': 9.2842, 'gouvernorat': 'Béja'},
    
    # Jendouba Governorate
    'jendouba': {'lat': 36.5014, 'lon': 8.7803, 'gouvernorat': 'Jendouba'},
    'tabarka': {'lat': 36.9544, 'lon': 8.7572, 'gouvernorat': 'Jendouba'},
    'ain_draham': {'lat': 36.7789, 'lon': 8.6867, 'gouvernorat': 'Jendouba'},
    'fernana': {'lat': 36.6719, 'lon': 8.9697, 'gouvernorat': 'Jendouba'},
    
    # Le Kef Governorate
    'kef': {'lat': 36.1742, 'lon': 8.7051, 'gouvernorat': 'Le Kef'},
    'dahmani': {'lat': 36.1042, 'lon': 8.5264, 'gouvernorat': 'Le Kef'},
    'sers': {'lat': 36.0881, 'lon': 8.9714, 'gouvernorat': 'Le Kef'},
    'tajerouine': {'lat': 36.0453, 'lon': 8.5583, 'gouvernorat': 'Le Kef'},
    
    # Siliana Governorate
    'siliana': {'lat': 36.0872, 'lon': 9.3706, 'gouvernorat': 'Siliana'},
    'makthar': {'lat': 35.8597, 'lon': 9.2000, 'gouvernorat': 'Siliana'},
    'bou_arada': {'lat': 36.3547, 'lon': 9.6222, 'gouvernorat': 'Siliana'},
    'rouhia': {'lat': 36.0631, 'lon': 9.7339, 'gouvernorat': 'Siliana'},
    
    # Sousse Governorate
    'sousse': {'lat': 35.8256, 'lon': 10.6411, 'gouvernorat': 'Sousse'},
    'msaken': {'lat': 35.7267, 'lon': 10.5814, 'gouvernorat': 'Sousse'},
    'kalaa_kebira': {'lat': 35.8889, 'lon': 10.5306, 'gouvernorat': 'Sousse'},
    'enfida': {'lat': 36.1333, 'lon': 10.3833, 'gouvernorat': 'Sousse'},
    'hergla': {'lat': 36.0328, 'lon': 10.5278, 'gouvernorat': 'Sousse'},
    
    # Monastir Governorate
    'monastir': {'lat': 35.7643, 'lon': 10.8113, 'gouvernorat': 'Monastir'},
    'ksar_hellal': {'lat': 35.6447, 'lon': 10.8892, 'gouvernorat': 'Monastir'},
    'moknine': {'lat': 35.6167, 'lon': 10.9000, 'gouvernorat': 'Monastir'},
    'sahline': {'lat': 35.7767, 'lon': 10.8347, 'gouvernorat': 'Monastir'},
    'bekalta': {'lat': 35.6167, 'lon': 10.9833, 'gouvernorat': 'Monastir'},
    'jemmal': {'lat': 35.6228, 'lon': 10.7575, 'gouvernorat': 'Monastir'},
    'ksibet_thrayet': {'lat': 35.6472, 'lon': 10.7639, 'gouvernorat': 'Monastir'},
    
    # Mahdia Governorate
    'mahdia': {'lat': 35.5047, 'lon': 11.0622, 'gouvernorat': 'Mahdia'},
    'ksour_essef': {'lat': 35.4192, 'lon': 10.9958, 'gouvernorat': 'Mahdia'},
    'chorbane': {'lat': 35.2989, 'lon': 10.8111, 'gouvernorat': 'Mahdia'},
    'el_jem': {'lat': 35.3000, 'lon': 10.7167, 'gouvernorat': 'Mahdia'},
    'bou_merdes': {'lat': 35.5731, 'lon': 11.0286, 'gouvernorat': 'Mahdia'},
    
    # Sfax Governorate
    'sfax': {'lat': 34.7406, 'lon': 10.7603, 'gouvernorat': 'Sfax'},
    'sakiet_ezzit': {'lat': 34.8139, 'lon': 10.7392, 'gouvernorat': 'Sfax'},
    'sakiet_eddaier': {'lat': 34.6703, 'lon': 10.6842, 'gouvernorat': 'Sfax'},
    'jebeniana': {'lat': 34.5167, 'lon': 10.9000, 'gouvernorat': 'Sfax'},
    'bir_ali_ben_khalifa': {'lat': 34.2406, 'lon': 10.0953, 'gouvernorat': 'Sfax'},
    'el_hencha': {'lat': 34.6308, 'lon': 10.7272, 'gouvernorat': 'Sfax'},
    
    # Kairouan Governorate
    'kairouan': {'lat': 35.6781, 'lon': 10.0963, 'gouvernorat': 'Kairouan'},
    'haffouz': {'lat': 35.6431, 'lon': 9.6775, 'gouvernorat': 'Kairouan'},
    'sbikha': {'lat': 35.9342, 'lon': 9.9125, 'gouvernorat': 'Kairouan'},
    'el_alaa': {'lat': 35.9903, 'lon': 9.5381, 'gouvernorat': 'Kairouan'},
    'bou_hajla': {'lat': 35.5656, 'lon': 9.7872, 'gouvernorat': 'Kairouan'},
    
    # Kasserine Governorate
    'kasserine': {'lat': 35.1676, 'lon': 8.8362, 'gouvernorat': 'Kasserine'},
    'sbeitla': {'lat': 35.2361, 'lon': 9.1161, 'gouvernorat': 'Kasserine'},
    'feriana': {'lat': 34.9508, 'lon': 8.5631, 'gouvernorat': 'Kasserine'},
    'foussana': {'lat': 35.1342, 'lon': 8.9669, 'gouvernorat': 'Kasserine'},
    'thala': {'lat': 35.5744, 'lon': 8.6678, 'gouvernorat': 'Kasserine'},
    
    # Sidi Bouzid Governorate
    'sidi_bouzid': {'lat': 35.0378, 'lon': 9.4844, 'gouvernorat': 'Sidi Bouzid'},
    'regueb': {'lat': 34.8389, 'lon': 9.7611, 'gouvernorat': 'Sidi Bouzid'},
    'jelma': {'lat': 34.9269, 'lon': 9.5756, 'gouvernorat': 'Sidi Bouzid'},
    'mezzouna': {'lat': 35.3669, 'lon': 9.6531, 'gouvernorat': 'Sidi Bouzid'},
    'menzel_bouzaiane': {'lat': 35.0867, 'lon': 9.5892, 'gouvernorat': 'Sidi Bouzid'},
    
    # Gafsa Governorate
    'gafsa': {'lat': 34.425, 'lon': 8.7842, 'gouvernorat': 'Gafsa'},
    'metlaoui': {'lat': 34.3211, 'lon': 8.4008, 'gouvernorat': 'Gafsa'},
    'redeyef': {'lat': 34.3831, 'lon': 8.1558, 'gouvernorat': 'Gafsa'},
    'moulares': {'lat': 34.5169, 'lon': 8.4028, 'gouvernorat': 'Gafsa'},
    'sened': {'lat': 34.4106, 'lon': 8.6714, 'gouvernorat': 'Gafsa'},
    
    # Tozeur Governorate
    'tozeur': {'lat': 33.9197, 'lon': 8.1335, 'gouvernorat': 'Tozeur'},
    'nefta': {'lat': 33.8781, 'lon': 7.8775, 'gouvernorat': 'Tozeur'},
    'degache': {'lat': 33.9831, 'lon': 8.2103, 'gouvernorat': 'Tozeur'},
    'hamet_jerid': {'lat': 33.8831, 'lon': 8.1503, 'gouvernorat': 'Tozeur'},
    
    # Kebili Governorate
    'kebili': {'lat': 33.7047, 'lon': 8.9692, 'gouvernorat': 'Kébili'},
    'douz': {'lat': 33.4678, 'lon': 9.0203, 'gouvernorat': 'Kébili'},
    'souk_lahad': {'lat': 33.9281, 'lon': 8.8956, 'gouvernorat': 'Kébili'},
    'faouar': {'lat': 33.5456, 'lon': 9.1328, 'gouvernorat': 'Kébili'},
    
    # Gabès Governorate
    'gabes': {'lat': 33.8815, 'lon': 10.0982, 'gouvernorat': 'Gabès'},
    'mareth': {'lat': 33.6394, 'lon': 10.2742, 'gouvernorat': 'Gabès'},
    'el_hamma': {'lat': 33.8903, 'lon': 9.7981, 'gouvernorat': 'Gabès'},
    'matmata': {'lat': 33.5456, 'lon': 9.9664, 'gouvernorat': 'Gabès'},
    'nouvelle_matmata': {'lat': 33.5664, 'lon': 9.9681, 'gouvernorat': 'Gabès'},
    'menzel_el_habib': {'lat': 33.8669, 'lon': 10.0814, 'gouvernorat': 'Gabès'},
    
    # Médenine Governorate
    'medenine': {'lat': 33.3545, 'lon': 10.5055, 'gouvernorat': 'Médenine'},
    'ben_gardane': {'lat': 33.1372, 'lon': 11.2194, 'gouvernorat': 'Médenine'},
    'zarzis': {'lat': 33.5039, 'lon': 11.1122, 'gouvernorat': 'Médenine'},
    'houmt_souk': {'lat': 33.8758, 'lon': 10.8575, 'gouvernorat': 'Médenine'},
    'midoun': {'lat': 33.8081, 'lon': 10.9925, 'gouvernorat': 'Médenine'},
    'jerba': {'lat': 33.8075, 'lon': 10.8531, 'gouvernorat': 'Médenine'},
    'djerba': {'lat': 33.8075, 'lon': 10.8531, 'gouvernorat': 'Médenine'},
    
    # Tataouine Governorate
    'tataouine': {'lat': 32.9297, 'lon': 10.4518, 'gouvernorat': 'Tataouine'},
    'remada': {'lat': 32.3053, 'lon': 10.3958, 'gouvernorat': 'Tataouine'},
    'ghomrassen': {'lat': 33.0619, 'lon': 10.3411, 'gouvernorat': 'Tataouine'},
    'smار': {'lat': 32.7356, 'lon': 10.2231, 'gouvernorat': 'Tataouine'}
}

def extract_city_from_address(address):
    """Enhanced city extraction with comprehensive location matching"""
    if not address or address == "N/A":
        return None
        
    address_lower = address.lower()
    
    # Priority matching - exact city names first
    for city in TUNISIA_LOCATIONS.keys():
        city_clean = city.replace('_', ' ')
        if city_clean in address_lower or city in address_lower:
            return city
    
    # Special cases and common variations
    variations = {
        'hammamet': ['hammamet', 'yasmine hammamet'],
        'tunis': ['tunis', 'tunisia', 'tunis1001', 'tunisia1001', 'centre ville tunis'],
        'ariana': ['ariana', "l'ariana"],
        'sfax': ['sfax'],
        'sousse': ['sousse', 'susah'],
        'bizerte': ['bizerte'],
        'gabes': ['gabes', 'gabès'],
        'nabeul': ['nabeul'],
        'mahdia': ['mahdia'],
        'monastir': ['monastir'],
        'kairouan': ['kairouan', 'kairwan'],
        'kasserine': ['kasserine'],
        'gafsa': ['gafsa'],
        'medenine': ['medenine', 'médenine'],
        'ben_arous': ['ben arous', 'benarous', 'ben-arous'],
        'sidi_bouzid': ['sidi bouzid', 'sidi bou zid'],
        'kef': ['le kef', 'kef'],
        'djerba': ['djerba', 'jerba', 'houmt souk', 'houmt_souk'],
        'la_marsa': ['la marsa', 'marsa'],
        'carthage': ['carthage'],
        'rades': ['rades', 'radès'],
        'hammam_lif': ['hammam lif', 'hammam-lif'],
        'menzel_bourguiba': ['menzel bourguiba', 'menzel-bourguiba'],
        'enfida': ['enfida'],
        'el_jem': ['el jem', 'el-jem'],
        'tabarka': ['tabarka'],
        'ain_draham': ['ain draham', 'ain-draham']
    }
    
    for standard_name, alts in variations.items():
        for alt in alts:
            if alt in address_lower:
                return standard_name
                
    return None

def add_offset(lat, lon):
    """Add random offset to spread markers"""
    offset = 0.02  # Reduced offset for better accuracy
    lat_offset = random.uniform(-offset, offset)
    lon_offset = random.uniform(-offset, offset)
    return lat + lat_offset, lon + lon_offset

def process_doctors_data():
    """Process doctors data with improved location accuracy"""
    source_path = 'data/data_geo/professionsLibéreales/claasic/docteurs_tunisie.json'
    output_path = 'app/medical_professionals/Data/doctors_geocoded.csv'
    
    print("Loading doctors data...")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        doctors_data = json.load(f)
    
    print(f"Processing {len(doctors_data)} doctors with improved location accuracy...")
    
    geocoded_count = 0
    corrections_made = 0
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['nom', 'prenom', 'specialite', 'adresse', 'telephone', 'lat', 'lon', 'ville_extraite', 'gouvernorat', 'nom_complet', 'hover_text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for doctor in doctors_data:
            city = extract_city_from_address(doctor['adresse'])
            
            if city and city in TUNISIA_LOCATIONS:
                location_info = TUNISIA_LOCATIONS[city]
                lat, lon = add_offset(location_info['lat'], location_info['lon'])
                
                # Track if this is a correction (Hammamet should be in Nabeul, not Tunis)
                if 'hammamet' in doctor['adresse'].lower() and location_info['gouvernorat'] == 'Nabeul':
                    corrections_made += 1
                
                nom_complet = f"{doctor['prenom']} {doctor['nom']}"
                hover_text = f"{doctor['specialite']}<br>{nom_complet}<br>{doctor['adresse']}"
                
                writer.writerow({
                    'nom': doctor['nom'],
                    'prenom': doctor['prenom'],
                    'specialite': doctor['specialite'],
                    'adresse': doctor['adresse'],
                    'telephone': doctor['telephone'],
                    'lat': lat,
                    'lon': lon,
                    'ville_extraite': city,
                    'gouvernorat': location_info['gouvernorat'],
                    'nom_complet': nom_complet,
                    'hover_text': hover_text
                })
                geocoded_count += 1
    
    print(f"Successfully processed {geocoded_count} doctors")
    print(f"Location corrections made: {corrections_made}")
    print(f"Data saved to: {output_path}")

if __name__ == "__main__":
    process_doctors_data()