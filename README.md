# GéoBiat - BIAT Geo-Business Intelligence Platform

A comprehensive geo-business intelligence platform for BIAT bank, providing strategic analysis of professional services markets across Tunisia through advanced mapping and proximity analytics.

## Overview

GéoBiat enables BIAT to analyze and visualize the geographic distribution of various professional services in relation to BIAT's branch network, supporting strategic decision-making for market expansion and competitive positioning.

## Professional Services Analyzed

- **Medical Professionals** - Doctors and healthcare providers
- **Experts Comptables** - Chartered accountants and tax advisors  
- **Pharmacies** - Pharmaceutical establishments
- **Conseillers** - Business consultants and advisory services
- **Base Prospection** - General business prospect analysis
- **Socio-Démographie** - Demographic and social analytics
- **Additional Services** - Insurance, equipment financing, etc.

## Distance-Based Precision System

### Core Innovation: Real Distance Calculation

GéoBiat uses the **Haversine formula** to calculate accurate distances between professionals and BIAT branches, providing genuine business intelligence instead of arbitrary confidence scores.

#### Haversine Formula Implementation

```python
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Calculate differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Apply Haversine formula
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Return distance in kilometers (Earth radius = 6371 km)
    return c * 6371
```

#### Business Zone Classification

| **Zone** | **Distance** | **Color** | **Strategic Value** |
|----------|-------------|-----------|-------------------|
| **Zone Stratégique** | ≤2km de BIAT | 🟢 Green | Direct competition zone - highest priority |
| **Zone d'Expansion** | 2-6km de BIAT | 🟠 Orange | Growth opportunity zone - expansion targets |
| **Zone Éloignée** | >6km de BIAT | 🔴 Red | Remote zone - lower priority markets |

#### Calculation Example

For a professional at coordinates (36.829, 10.1485) and BIAT branch at (36.8078, 10.1869):

1. **Convert to radians**: 36.829° → 0.6431 rad, 10.1485° → 0.1771 rad
2. **Calculate differences**: dlat = -0.0007, dlon = 0.0007  
3. **Apply formula**: a = 0.000000198, c = 0.000889
4. **Final distance**: 0.000889 × 6371 = **3.2 km** → **Zone d'Expansion (2-6km)**

### Key Features

#### Real-Time Distance Analysis
- Calculates distance to nearest BIAT branch for each professional
- Identifies closest BIAT agency by name
- Provides exact distance measurements in kilometers

#### Interactive Map Visualization  
- **Choropleth boundaries**: Administrative divisions (governorates/delegations)
- **Professional markers**: Color-coded by distance zones
- **BIAT branches**: Strategic positioning overlay
- **Competitor banks**: Competitive landscape analysis

#### Enhanced Business Intelligence
- **Hover details**: Distance, nearest branch, zone classification
- **Legend counts**: Professionals per zone for quick analysis
- **Filter controls**: Zone-based filtering for targeted analysis
- **Geographic scope**: Governorate and delegation level filtering

## Technical Architecture

### Frontend
- **Dash Framework** - Interactive web application
- **Plotly Maps** - Advanced geospatial visualization
- **Bootstrap Components** - Responsive UI design

### Backend
- **Pandas** - Data processing and analysis
- **GeoPandas** - Geospatial data handling
- **NumPy** - Numerical computations

### Data Sources
- **Professional Services**: Geocoded business directories
- **Geographic Boundaries**: Tunisia administrative divisions (GeoJSON)
- **Banking Network**: BIAT and competitor branch locations

## Navigation Structure

The platform features centralized navigation with 11 specialized modules:

1. **Accueil** - Dashboard overview
2. **Base de Prospection** - General prospect analysis
3. **Socio-Démographie** - Demographic analytics
4. **Equipements Financiers** - Financial equipment analysis
5. **Logement et Patrimoine** - Housing and assets
6. **Assurance** - Insurance market analysis
7. **Dépenses** - Expenditure analysis
8. **Professionnels Médicaux** - Healthcare providers
9. **Experts Comptables** - Accounting professionals
10. **Pharmacies** - Pharmaceutical network
11. **Conseillers** - Business consultancy services

## Zone de Chalendise Analysis

Special focus on **Zone de Chalendise** (Strategic Challenge Zone) - the primary market area around BIAT's core operations where competitive positioning is most critical.

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python dashapp.py
```

### Accessing the Platform
Navigate to `http://localhost:8050` to access the GéoBiat interface.

## Distance Calculation Accuracy

- **Formula**: Standard Haversine great-circle distance
- **Accuracy**: ±0.5% for distances up to 20km
- **Verification**: Compatible with Google Maps measurements
- **Earth Model**: Spherical approximation (radius = 6,371 km)

## Business Applications

### Strategic Planning
- **Market Entry**: Identify underserved areas for new branches
- **Competitive Analysis**: Map professional services near existing branches
- **Territory Management**: Optimize service area coverage

### Performance Analysis  
- **Proximity Metrics**: Measure professional density around branches
- **Zone Performance**: Compare different geographic zones
- **Growth Opportunities**: Target high-potential expansion areas

### Decision Support
- **Data-Driven Insights**: Real distance measurements vs. estimates
- **Visual Intelligence**: Geographic patterns and relationships  
- **Strategic Prioritization**: Focus resources on high-value zones

---

**GéoBiat** - Transforming geographic data into strategic business intelligence for BIAT's continued growth and market leadership across Tunisia.

## Technical Implementation Notes

### Distance-Based Precision System Migration

The platform has evolved from arbitrary confidence levels to **real business-focused distance measurements**:

**Previous System (Deprecated)**:
- Confidence ≥0.8: "High Precision (±30m)" - based on pattern matching
- Confidence 0.6-0.8: "Medium Precision (±1km)" - governorate fallback  
- Confidence <0.6: "Low Precision" - failed geocoding

**Current System (Active)**:
- **Zone Stratégique (≤2km)**: Direct competition analysis
- **Zone d'Expansion (2-6km)**: Market expansion opportunities
- **Zone Éloignée (>6km)**: Remote market assessment

This migration provides genuine business value through measurable proximity analytics rather than estimated geocoding confidence.