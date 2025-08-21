from dash import Input, Output, callback
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

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
    """Update the conseillers map based on all filters"""
    
    # Create the figure
    fig = go.Figure()
    
    # Add delegation boundaries
    if selected_gouvernorats:
        filtered_gdf = gdf_delegation[gdf_delegation['gouvernorat'].isin(selected_gouvernorats)]
    else:
        filtered_gdf = gdf_delegation.copy()
    
    if selected_delegations:
        filtered_gdf = filtered_gdf[filtered_gdf['delegation'].isin(selected_delegations)]
    
    # Add delegation boundaries
    for idx, row in filtered_gdf.iterrows():
        if row.geometry.geom_type == 'Polygon':
            x, y = row.geometry.exterior.coords.xy
            fig.add_trace(go.Scattermapbox(
                lat=list(y), lon=list(x),
                mode='lines', fill='toself',
                fillcolor='rgba(135,206,235,0.1)',
                line=dict(color='rgba(135,206,235,0.8)', width=1),
                hoverinfo='text',
                hovertext=f"Délégation: {row['delegation']}<br>Gouvernorat: {row['gouvernorat']}",
                showlegend=False
            ))
        elif row.geometry.geom_type == 'MultiPolygon':
            for geom in row.geometry.geoms:
                x, y = geom.exterior.coords.xy
                fig.add_trace(go.Scattermapbox(
                    lat=list(y), lon=list(x),
                    mode='lines', fill='toself',
                    fillcolor='rgba(135,206,235,0.1)',
                    line=dict(color='rgba(135,206,235,0.8)', width=1),
                    hoverinfo='text',
                    hovertext=f"Délégation: {row['delegation']}<br>Gouvernorat: {row['gouvernorat']}",
                    showlegend=False
                ))
    
    # Filter conseillers data
    df_filtered = df_conseillers.copy()
    
    # Apply governorate filter
    if filter_gouvernorats:
        df_filtered = df_filtered[df_filtered['gouvernorat'].isin(filter_gouvernorats)]
    
    # Apply location filter
    if selected_gouvernorats:
        df_filtered = df_filtered[df_filtered['gouvernorat'].isin(selected_gouvernorats)]
    
    # Apply precision filter
    if precision_levels:
        precision_filter = False
        if "high" in precision_levels:
            precision_filter |= (df_filtered['confidence'] >= 0.8)
        if "medium" in precision_levels:
            precision_filter |= ((df_filtered['confidence'] >= 0.6) & (df_filtered['confidence'] < 0.8))
        if "low" in precision_levels:
            precision_filter |= (df_filtered['confidence'] < 0.6)
        
        df_filtered = df_filtered[precision_filter]
    
    # Remove records without coordinates
    df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])
    
    # Add conseillers points
    if map_layers and "conseillers" in map_layers and not df_filtered.empty:
        # Color by precision level
        df_filtered['precision_level'] = df_filtered['confidence'].apply(
            lambda x: 'Haute Précision (±30m)' if x >= 0.8 
                     else 'Précision Moyenne (±1km)' if x >= 0.6 
                     else 'Précision Faible'
        )
        
        colors = {'Haute Précision (±30m)': '#2E8B57',
                  'Précision Moyenne (±1km)': '#FF8C00', 
                  'Précision Faible': '#DC143C'}
        
        for precision_level in df_filtered['precision_level'].unique():
            df_precision = df_filtered[df_filtered['precision_level'] == precision_level]
            
            fig.add_trace(go.Scattermapbox(
                lat=df_precision['latitude'],
                lon=df_precision['longitude'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=colors[precision_level],
                    opacity=0.7
                ),
                text=[f"<b>{row['nom']}</b><br>" +
                      f"Adresse: {row['adresse_complete']}<br>" +
                      f"Téléphone: {row['telephone']}<br>" +
                      f"Gouvernorat: {row['gouvernorat']}<br>" +
                      f"Précision: {precision_level}<br>" +
                      f"Méthode: {row['method']}" 
                      for idx, row in df_precision.iterrows()],
                hoverinfo='text',
                name=f'Conseillers - {precision_level} ({len(df_precision)})',
                showlegend=True
            ))
    
    # Add BIAT branches
    if map_layers and "biat" in map_layers:
        df_biat = df_banks[df_banks['bank_name'] == 'BIAT'].copy()
        if selected_gouvernorats:
            df_biat = df_biat[df_biat['gouvernorat'].isin(selected_gouvernorats)]
        
        if not df_biat.empty:
            fig.add_trace(go.Scattermapbox(
                lat=df_biat['lat'],
                lon=df_biat['long'],
                mode='markers',
                marker=dict(size=12, color='#1f77b4', symbol='bank'),
                text=[f"<b>BIAT - {row['agency_name']}</b><br>" +
                      f"Adresse: {row['address']}<br>" +
                      f"Gouvernorat: {row['gouvernorat']}"
                      for idx, row in df_biat.iterrows()],
                hoverinfo='text',
                name=f'Agences BIAT ({len(df_biat)})',
                showlegend=True
            ))
    
    # Add competitor banks
    if map_layers and "competitors" in map_layers:
        df_competitors = df_banks[df_banks['bank_name'] != 'BIAT'].copy()
        if selected_gouvernorats:
            df_competitors = df_competitors[df_competitors['gouvernorat'].isin(selected_gouvernorats)]
        
        if not df_competitors.empty:
            fig.add_trace(go.Scattermapbox(
                lat=df_competitors['lat'],
                lon=df_competitors['long'],
                mode='markers',
                marker=dict(size=10, color='#ff7f0e', symbol='bank'),
                text=[f"<b>{row['bank_name']} - {row['agency_name']}</b><br>" +
                      f"Adresse: {row['address']}<br>" +
                      f"Gouvernorat: {row['gouvernorat']}"
                      for idx, row in df_competitors.iterrows()],
                hoverinfo='text',
                name=f'Banques Concurrentes ({len(df_competitors)})',
                showlegend=True
            ))
    
    # Determine map center
    if not df_filtered.empty:
        center_lat = df_filtered['latitude'].mean()
        center_lon = df_filtered['longitude'].mean()
        zoom = 10
    elif selected_gouvernorats and not filtered_gdf.empty:
        bounds = filtered_gdf.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        zoom = 9
    else:
        center_lat, center_lon = 36.8065, 10.1815  # Tunisia center
        zoom = 7
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig