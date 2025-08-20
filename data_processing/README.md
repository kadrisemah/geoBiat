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

- Run `fix_doctors_locations.py` whenever new doctor data is added
- Use `verify_locations.py` to check data quality after processing
- Scripts handle Tunisia-specific geographic challenges (Arabic names, regional variations)
- Maintains original data structure while improving accuracy

## Future Enhancements

- Add processing scripts for other data types (banks, demographics, etc.)
- Implement batch processing for multiple CSV files
- Add data validation for new datasets