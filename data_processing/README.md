# Data Processing Scripts

This folder contains scripts for processing and fixing data issues in the GéoBiat application.

## Scripts

### 1. `fix_doctors_locations.py`
- **Purpose**: Fixes geocoding accuracy for medical professionals
- **Function**: Corrects city/governorate assignments using comprehensive Tunisia location mapping
- **Usage**: `python3 fix_doctors_locations.py`
- **Input**: `app/medical_professionals/Data/doctors_geocoded.csv`
- **Output**: Updated CSV with corrected locations
- **Fixes Applied**: 
  - Hammamet doctors correctly placed in Nabeul (not Ariana/Tunis)
  - All Tunisia cities mapped to correct governorates
  - Improved address parsing and city extraction

### 2. `verify_locations.py`
- **Purpose**: Validates location accuracy of processed data
- **Function**: Checks governorate assignments against official Tunisia governorates
- **Usage**: `python3 verify_locations.py`
- **Output**: Accuracy percentage and detailed report
- **Features**:
  - Shows doctors distribution by governorate
  - Identifies problematic entries
  - Validates against official governorate names

## Results Achieved

### Location Accuracy Improvements
- **Started with**: Random city-level coordinates causing water placement
- **Final Result**: **94.4% realistic accuracy** (1225/1298 doctors properly on land)
- **Fixed Hammamet issue** - all 25 doctors now correctly in Nabeul governorate (not Ariana)
- **Reduced water placement** from 311 to 73 doctors (76% improvement)
- **Comprehensive city mapping** with 100+ Tunisia locations and verified coordinates

### Key Fixes Applied
1. **Governorate accuracy**: 100% correct governorate assignments (1298/1298)
2. **Water avoidance**: Moved doctors from Lac de Tunis, Sebkha Ariana to proper land locations
3. **City-specific coordinates**: Used verified land-based coordinates instead of random offsets
4. **Address parsing**: Improved extraction of cities from medical addresses

## Usage Notes

### Medical Professionals
- Run `fix_doctors_locations.py` whenever new doctor data is added
- Use `verify_locations.py` to check data quality after processing
- Scripts handle Tunisia-specific geographic challenges (Arabic names, regional variations)
- Maintains original data structure while improving accuracy

### Experts Comptables
- Run `process_experts_comptables_simple.py` to convert JSON data to CSV format
- Run `add_precise_coordinates_experts.py` to add high-precision geocoding
- Use `test_experts_data.py` to validate data structure and loading
- Use `show_experts_locations.py` for geographic distribution analysis
- Use `check_coordinate_accuracy.py` to assess coordinate precision for distance calculations

## Future Enhancements

- Add processing scripts for pharmacies and conseillers JSON data
- Implement PDF processing for architects data
- Add batch processing for multiple profession files
- Improve geocoding precision for governorate-level coordinates
- Add distance calculation utilities between professions and BIAT branches

### 3. `process_experts_comptables_simple.py`
- **Purpose**: Initial processing of experts comptables JSON data
- **Function**: Converts JSON to CSV format with basic data cleaning
- **Usage**: `python3 process_experts_comptables_simple.py`
- **Input**: `data/data_geo/professionsLibéreales/claasic/experts_comptables_oect.json`
- **Output**: `app/experts_comptables/Data/experts_comptables_processed.csv`
- **Features**:
  - Address cleaning and standardization
  - Governorate extraction from addresses
  - Profession categorization

### 4. `add_precise_coordinates_experts.py`
- **Purpose**: High-precision geocoding for experts comptables
- **Function**: Applies same precision standards as medical professionals
- **Usage**: `python3 add_precise_coordinates_experts.py`
- **Input**: `app/experts_comptables/Data/experts_comptables_processed.csv`
- **Output**: `app/experts_comptables/Data/experts_comptables_geocoded.csv`
- **Results**: 90.7% geocoding success rate (333/367 experts)
- **Features**:
  - Pattern-based address matching with ~50m precision
  - Governorate-level fallback with ~1-2km precision
  - Zone de Chalendise identification
  - Confidence scoring system

### 5. `test_experts_data.py`
- **Purpose**: Data validation for experts comptables processing
- **Function**: Tests data loading and structure validation
- **Usage**: `python3 test_experts_data.py`
- **Output**: Data structure analysis and validation report

### 6. `show_experts_locations.py`
- **Purpose**: Geographic analysis of experts comptables distribution
- **Function**: Shows location patterns by conseil régional
- **Usage**: `python3 show_experts_locations.py`
- **Output**: Detailed breakdown of expert locations by council and governorate

### 7. `check_coordinate_accuracy.py`
- **Purpose**: Coordinate precision analysis for distance calculations
- **Function**: Evaluates geocoding accuracy and suitability for business intelligence
- **Usage**: `python3 check_coordinate_accuracy.py`
- **Output**: Precision assessment and recommendations for distance calculations

## Results Achieved

### Experts Comptables Processing
- **Total records**: 367 experts comptables
- **Geocoding success**: 90.7% (333/367 experts with coordinates)
- **High precision**: 35.4% (118 experts with street-level accuracy ~50m)
- **Medium precision**: 64.6% (215 experts with district-level accuracy ~1-2km)
- **Zone coverage**: 2 experts in zone de Chalendise
- **Conseil régional distribution**:
  - Tunis Ben Arous: 234 experts (63.7%)
  - Nord: 48 experts (13.1%)
  - Sud: 40 experts (10.9%)
  - ******* (unspecified): 32 experts (8.7%)
  - Centre: 13 experts (3.5%)

### Location Accuracy Improvements