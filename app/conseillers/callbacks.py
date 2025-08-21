from dash import Input, Output, callback
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import warnings
from math import radians, cos, sin, asin, sqrt
import numpy as np
warnings.filterwarnings("ignore")

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return float('inf')
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return c * 6371  # Earth radius in km

def calculate_distance_based_precision(conseiller_lat, conseiller_lon, biat_branches):
    """Calculate precision based on distance to nearest BIAT branch"""
    if pd.isna(conseiller_lat) or pd.isna(conseiller_lon):
        return "no_coords", "Pas de Coordonnées", 0.0, None, float('inf')
    
    # Find nearest BIAT branch
    min_distance = float('inf')
    nearest_branch = None
    
    for _, branch in biat_branches.iterrows():
        if pd.notna(branch['lat']) and pd.notna(branch['long']):
            distance = haversine_distance(conseiller_lat, conseiller_lon, branch['lat'], branch['long'])
            if distance < min_distance:
                min_distance = distance
                nearest_branch = branch['agence']
    
    # Assign precision based on distance - REDUCED THRESHOLDS FOR BETTER DISTRIBUTION
    if min_distance <= 2.0:
        return "high", f"Zone Stratégique (≤2km de BIAT)", 0.9, nearest_branch, min_distance
    elif min_distance <= 6.0:
        return "medium", f"Zone d'Expansion (2-6km de BIAT)", 0.7, nearest_branch, min_distance
    else:
        return "low", f"Zone Éloignée (>6km de BIAT)", 0.3, nearest_branch, min_distance

def register_callbacks_conseillers(app):
    """Register all conseillers callbacks"""
    
    # Import here to avoid circular imports
    from dash import Input, Output, callback_context
    
    @app.callback(
        Output('slct_delegat_conseillers', 'options'),
        [Input('slct_city_conseillers', 'value')]
    )
    def update_delegation_options_conseillers(selected_gouvernorats):
        return _update_delegation_options_conseillers(selected_gouvernorats)
    
    @app.callback(
        [Output('precision_selection_conseillers', 'value')],
        [Input('high_precision_conseillers', 'n_clicks'),
         Input('medium_precision_conseillers', 'n_clicks'), 
         Input('all_precision_conseillers', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_precision_selection_conseillers(high_clicks, medium_clicks, all_clicks):
        return _update_precision_selection_conseillers(high_clicks, medium_clicks, all_clicks)
    
    @app.callback(
        Output('conseillers_bee_map', 'figure'),
        [Input('slct_city_conseillers', 'value'),
         Input('slct_delegat_conseillers', 'value'),
         Input('filter_gouvernorat_conseillers', 'value'),
         Input('map_layers_conseillers', 'value'),
         Input('precision_selection_conseillers', 'value')]
    )
    def update_conseillers_map(selected_gouvernorats, selected_delegations, filter_gouvernorats, 
                              map_layers, precision_levels):
        return _update_conseillers_map(selected_gouvernorats, selected_delegations, filter_gouvernorats, 
                                      map_layers, precision_levels)

# Load conseillers data
df_conseillers = pd.read_csv(r'app\conseillers\Data\conseillers_geocoded.csv')
df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))

# Data loaded successfully

# Load geographic boundaries
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

def _update_delegation_options_conseillers(selected_gouvernorats):
    """Update delegation options based on selected gouvernorats"""
    if not selected_gouvernorats:
        # Return all delegations if no governorate is selected
        delegations = sorted(gdf_delegation['delegation'].unique())
        return [{'label': i, 'value': i} for i in delegations]
    
    # Filter delegations based on selected governorates
    filtered_gdf = gdf_delegation[gdf_delegation['gouvernorat'].isin(selected_gouvernorats)]
    delegations = sorted(filtered_gdf['delegation'].unique())
    return [{'label': i, 'value': i} for i in delegations]

def _update_precision_selection_conseillers(high_clicks, medium_clicks, all_clicks):
    """Update precision selection based on button clicks"""
    from dash import callback_context
    
    if not callback_context.triggered:
        return [["high", "medium", "low"]]
    
    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'high_precision_conseillers':
        return [["high"]]
    elif button_id == 'medium_precision_conseillers':
        return [["medium"]]
    elif button_id == 'all_precision_conseillers':
        return [["high", "medium", "low"]]
    
    return [["high", "medium", "low"]]

def _update_conseillers_map(selected_gouvernorats, selected_delegations, filter_gouvernorats, 
                          map_layers, precision_levels):
    """Update the conseillers map with DISTANCE-BASED PRECISION SYSTEM"""
    
    try:
        # Filter conseillers based on selections
        filtered_conseillers = df_conseillers.copy()
        
        # Apply gouvernorat filter (matching experts_comptables EXACT pattern)
        if filter_gouvernorats:
            filtered_conseillers = filtered_conseillers[filtered_conseillers['gouvernorat'].isin(filter_gouvernorats)]
        elif selected_gouvernorats:
            filtered_conseillers = filtered_conseillers[filtered_conseillers['gouvernorat'].isin(selected_gouvernorats)]
        
        # Get BIAT branches for distance calculation
        biat_branches = df_banks[df_banks['banque'].str.upper() == 'BIAT'].copy()
        
        # Calculate distance-based precision for all conseillers
        precision_data = []
        valid_coords_count = 0
        for _, conseiller in filtered_conseillers.iterrows():
            precision_level, precision_label, confidence, nearest_branch, distance = calculate_distance_based_precision(
                conseiller['latitude'], conseiller['longitude'], biat_branches
            )
            
            if precision_level != 'no_coords':
                valid_coords_count += 1
                
            precision_data.append({
                'distance_precision_level': precision_level,
                'distance_precision_label': precision_label,
                'distance_confidence': confidence,
                'nearest_biat': nearest_branch,
                'distance_km': distance if distance != float('inf') else None
            })
        
        # Add precision data to dataframe
        precision_df = pd.DataFrame(precision_data)
        filtered_conseillers = pd.concat([filtered_conseillers.reset_index(drop=True), precision_df], axis=1)
        
        # Apply precision filter based on NEW distance-based system
        if precision_levels:
            # Create boolean mask for filtering
            mask = pd.Series([False] * len(filtered_conseillers))
            
            if "high" in precision_levels:
                mask = mask | (filtered_conseillers['distance_precision_level'] == 'high')
            if "medium" in precision_levels:
                mask = mask | (filtered_conseillers['distance_precision_level'] == 'medium')
            if "low" in precision_levels:
                mask = mask | (filtered_conseillers['distance_precision_level'] == 'low')
            
            # Apply the filter
            filtered_conseillers = filtered_conseillers[mask]
        
        # Create map structure EXACTLY like experts_comptables
        if selected_gouvernorats and selected_delegations:
            # Show delegation level map
            fig = px.choropleth_mapbox(gdf_delegation[gdf_delegation.delegation.isin(selected_delegations)],
                           geojson=gdf_delegation[gdf_delegation.delegation.isin(selected_delegations)].geometry,
                           locations=gdf_delegation[gdf_delegation.delegation.isin(selected_delegations)].index,
                           color_discrete_sequence=["rgba(0,0,0,0)"],
                           mapbox_style="carto-positron",
                           zoom=8, opacity=0.5)
            
            # Filter conseillers by selected delegations
            delegation_to_gouvernorat = gdf_delegation.set_index('delegation')['gouvernorat'].to_dict()
            selected_gouvernorats_from_deleg = []
            for deleg in selected_delegations:
                if deleg in delegation_to_gouvernorat:
                    selected_gouvernorats_from_deleg.append(delegation_to_gouvernorat[deleg])
            
            if selected_gouvernorats_from_deleg:
                filtered_conseillers = filtered_conseillers[filtered_conseillers['gouvernorat'].isin(selected_gouvernorats_from_deleg)]

        elif selected_gouvernorats:
            # Show governorate level map
            governorates_gdf = gdf_delegation.dissolve(by='gouvernorat')
            governorates_gdf = governorates_gdf.reset_index()
            
            fig = px.choropleth_mapbox(governorates_gdf[governorates_gdf.gouvernorat.isin(selected_gouvernorats)],
                           geojson=governorates_gdf[governorates_gdf.gouvernorat.isin(selected_gouvernorats)].geometry,
                           locations=governorates_gdf[governorates_gdf.gouvernorat.isin(selected_gouvernorats)].index,
                           color_discrete_sequence=["rgba(0,0,0,0)"],
                           mapbox_style="carto-positron",
                           zoom=6, opacity=0.5)

        else:
            # Show all Tunisia - create empty map
            fig = go.Figure()
            fig.update_layout(
                mapbox_style="carto-positron",
                mapbox=dict(center=dict(lat=34.0, lon=9.5), zoom=5)
            )
        
        # Add conseillers by DISTANCE-BASED precision level
        if 'conseillers' in (map_layers or []) and len(filtered_conseillers) > 0:
            # Only show conseillers with valid coordinates
            valid_conseillers = filtered_conseillers[
                (filtered_conseillers['latitude'].notna()) & 
                (filtered_conseillers['longitude'].notna()) &
                (filtered_conseillers['distance_precision_level'].notna())
            ]
            
            if len(valid_conseillers) > 0:
                # Distance-based precision colors
                precision_colors = {
                    'high': '#2E8B57',      # Green for ≤5km (strategic zone)
                    'medium': '#FF8C00',    # Orange for 5-15km (expansion zone)
                    'low': '#DC143C'        # Red for >15km (remote zone)
                }
                
                # Add each precision level as separate trace
                for precision_level in valid_conseillers['distance_precision_level'].unique():
                    if precision_level == 'no_coords':
                        continue
                        
                    precision_data = valid_conseillers[valid_conseillers['distance_precision_level'] == precision_level]
                    color = precision_colors.get(precision_level, '#95a5a6')
                    
                    # Enhanced hover text with distance info
                    hover_text = precision_data.apply(lambda x: 
                        f"{x['nom']}<br>"
                        f"Distance BIAT: {x['distance_km']:.1f}km<br>"
                        f"Agence BIAT proche: {x['nearest_biat']}<br>"
                        f"Zone: {x['distance_precision_label']}<br>"
                        f"Adresse: {str(x['adresse_complete'])[:40]}...", axis=1)
                    
                    # Label for legend
                    if precision_level == 'high':
                        legend_label = f'≤2km de BIAT ({len(precision_data)})'
                    elif precision_level == 'medium':
                        legend_label = f'2-6km de BIAT ({len(precision_data)})'
                    else:
                        legend_label = f'>6km de BIAT ({len(precision_data)})'
                    
                    fig.add_trace(go.Scattermapbox(
                        lat=precision_data['latitude'],
                        lon=precision_data['longitude'],
                        mode='markers',
                        marker=dict(
                            size=10 if precision_level == 'high' else 8 if precision_level == 'medium' else 6,
                            color=color,
                            opacity=0.8
                        ),
                        text=hover_text,
                        hovertemplate='<b>%{text}</b><extra></extra>',
                        name=legend_label,
                        showlegend=True,
                        legendgroup=precision_level,
                        visible=True
                    ))
        
        # Add BIAT branches (EXACT COPY of experts_comptables pattern)
        if 'biat' in (map_layers or []):
            biat_data = df_banks[df_banks['banque'].str.upper() == 'BIAT']
            
            if selected_gouvernorats:
                biat_data = biat_data[biat_data['gouvernorat'].isin(selected_gouvernorats)]
            elif filter_gouvernorats:
                biat_data = biat_data[biat_data['gouvernorat'].isin(filter_gouvernorats)]
            
            if len(biat_data) > 0:
                fig.add_trace(go.Scattermapbox(
                    lat=biat_data['lat'],
                    lon=biat_data['long'],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='#004579',  # BIAT color
                        opacity=0.9,
                        symbol='circle'
                    ),
                    text=biat_data['agence'],
                    hovertemplate='<b>BIAT - %{text}</b><extra></extra>',
                    name=f'Agences BIAT ({len(biat_data)})',
                    showlegend=True
                ))

        # Add competitor banks (EXACT COPY of experts_comptables pattern)
        if 'competitors' in (map_layers or []):
            competitor_data = df_banks[df_banks['banque'].str.upper() != 'BIAT']
            
            if selected_gouvernorats:
                competitor_data = competitor_data[competitor_data['gouvernorat'].isin(selected_gouvernorats)]
            elif filter_gouvernorats:
                competitor_data = competitor_data[competitor_data['gouvernorat'].isin(filter_gouvernorats)]
            
            if len(competitor_data) > 0:
                fig.add_trace(go.Scattermapbox(
                    lat=competitor_data['lat'],
                    lon=competitor_data['long'],
                    mode='markers',
                    marker=dict(
                        size=6,
                        color='orange',
                        opacity=0.6,
                        symbol='square'
                    ),
                    text=competitor_data['agence'] + ' (' + competitor_data['banque'].str.upper() + ')',
                    hovertemplate='<b>%{text}</b><extra></extra>',
                    name=f'Concurrents ({len(competitor_data)})',
                    showlegend=True
                ))

        # Update layout (EXACT COPY of experts_comptables)
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left", 
                x=0.01,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
                font=dict(size=10),
                itemsizing="constant",
                itemclick="toggle",
                itemdoubleclick="toggleothers"
            )
        )
        
        return fig

    except Exception as e:
        print(f"Error in conseillers map callback: {e}")
        # Return empty map on error
        fig = go.Figure()
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox=dict(center=dict(lat=34.0, lon=9.5), zoom=5),
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        return fig