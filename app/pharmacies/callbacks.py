from dash.dependencies import Input, Output, State
import plotly.express as px  
import plotly.graph_objs as go
import pandas as pd 
import geopandas as gpd
import dash

# Load data (same as medical professionals structure)
try:
    df_pharmacies = pd.read_csv(r'app\pharmacies\Data\pharmacies_geocoded.csv', encoding='utf-8')
    df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
    print(f"Loaded {len(df_pharmacies)} pharmacies and {len(df_banks)} banks")
except Exception as e:
    print(f"Error loading data: {e}")
    df_pharmacies = pd.DataFrame()
    df_banks = pd.DataFrame()

# Load geographic boundaries
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

def register_callbacks_pharmacies(app):
    
    # Callback to populate delegation dropdown based on governorate selection (same as accueil)
    @app.callback(
        dash.dependencies.Output('slct_delegat_pharmacies', 'options'),
        [dash.dependencies.Input('slct_city_pharmacies', 'value')])
    def set_delegations_options_pharmacies(slct_city):
        if slct_city:
            return [{'label': i, 'value': i} for i in gdf_delegation[gdf_delegation["gouvernorat"].isin(slct_city)]['delegation'].unique()]
        else:
            return ""

    # Callback to populate service selection dynamically
    @app.callback(
        [Output('service_selection', 'options'),
         Output('service_selection', 'value')],
        [Input('filter_gouvernorat_pharmacies', 'value'),
         Input('select_all_services', 'n_clicks'),
         Input('deselect_all_services', 'n_clicks')],
        [State('service_selection', 'value')]
    )
    def update_service_selection(selected_gouvernorats, select_all_clicks, deselect_all_clicks, current_selection):
        ctx = dash.callback_context
        
        # Filter pharmacies based on gouvernorat selection
        filtered_df = df_pharmacies.copy()
        if selected_gouvernorats:
            filtered_df = filtered_df[filtered_df['gouvernorat'].isin(selected_gouvernorats)]
        
        # Get available service options
        available_services = sorted(filtered_df['specialite'].dropna().unique())
        options = [{"label": service, "value": service} for service in available_services]
        
        # Handle button clicks
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'select_all_services':
                return options, available_services
            elif button_id == 'deselect_all_services':
                return options, []
        
        # Keep current selection if valid
        if current_selection:
            valid_selection = [service for service in current_selection if service in available_services]
            return options, valid_selection
        
        return options, available_services  # Select all by default

    # Main callback for updating the map (same structure as medical professionals)
    @app.callback(
        Output('pharmacies_bee_map', 'figure'),
        [Input(component_id='slct_city_pharmacies', component_property='value'),
         Input(component_id='slct_delegat_pharmacies', component_property='value'),
         Input(component_id='filter_gouvernorat_pharmacies', component_property='value'),
         Input(component_id='map_layers_pharmacies', component_property='value'),
         Input(component_id='service_selection', component_property='value')
        ]
    )
    def update_pharmacies_graph(slct_city, slct_delegat, filter_gouvernorats, map_layers, service_selection):
        try:
            # Color palette for pharmacy services
            color_palette = [
                '#2ecc71', '#e74c3c', '#3498db', '#f39c12', '#9b59b6', '#e67e22', '#1abc9c', '#34495e',
                '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7', '#a29bfe'
            ]
            
            # Filter pharmacies based on selections
            filtered_pharmacies = df_pharmacies.copy()
            
            # Apply gouvernorat filter
            if filter_gouvernorats:
                filtered_pharmacies = filtered_pharmacies[filtered_pharmacies['gouvernorat'].isin(filter_gouvernorats)]
            elif slct_city:
                filtered_pharmacies = filtered_pharmacies[filtered_pharmacies['gouvernorat'].isin(slct_city)]
            
            # Apply service filter
            if service_selection:
                filtered_pharmacies = filtered_pharmacies[filtered_pharmacies['specialite'].isin(service_selection)]
            
            if slct_city and slct_delegat:
                # Show delegation level map
                fig = px.choropleth_mapbox(gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)],
                               geojson=gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)].geometry,
                               locations=gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)].index,
                               color_discrete_sequence=["rgba(0,0,0,0)"],
                               mapbox_style="carto-positron",
                               zoom=8, opacity=0.5)
                
                # Filter pharmacies by selected delegations
                delegation_to_gouvernorat = gdf_delegation.set_index('delegation')['gouvernorat'].to_dict()
                selected_gouvernorats = []
                for deleg in slct_delegat:
                    if deleg in delegation_to_gouvernorat:
                        selected_gouvernorats.append(delegation_to_gouvernorat[deleg])
                
                if selected_gouvernorats:
                    filtered_pharmacies = filtered_pharmacies[filtered_pharmacies['gouvernorat'].isin(selected_gouvernorats)]

            elif slct_city:
                # Show governorate level map
                governorates_gdf = gdf_delegation.dissolve(by='gouvernorat')
                governorates_gdf = governorates_gdf.reset_index()
                
                fig = px.choropleth_mapbox(governorates_gdf[governorates_gdf.gouvernorat.isin(slct_city)],
                               geojson=governorates_gdf[governorates_gdf.gouvernorat.isin(slct_city)].geometry,
                               locations=governorates_gdf[governorates_gdf.gouvernorat.isin(slct_city)].index,
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
            
            # Add pharmacies by service type (if pharmacies layer is selected)
            if 'pharmacies' in (map_layers or []) and len(filtered_pharmacies) > 0:
                # Only show pharmacies with valid coordinates
                valid_pharmacies = filtered_pharmacies[
                    (filtered_pharmacies['latitude'].notna()) & 
                    (filtered_pharmacies['longitude'].notna())
                ]
                
                if len(valid_pharmacies) > 0:
                    all_services = sorted(valid_pharmacies['specialite'].dropna().unique())
                    service_colors = {}
                    
                    for i, service in enumerate(all_services):
                        service_colors[service] = color_palette[i % len(color_palette)]
                    
                    # Add each service as separate trace
                    for service in valid_pharmacies['specialite'].dropna().unique():
                        service_data = valid_pharmacies[valid_pharmacies['specialite'] == service]
                        
                        color = service_colors.get(service, '#95a5a6')
                        
                        # Create hover text
                        hover_text = service_data.apply(lambda x: 
                            f"{x['Nom']}<br>Type: {x['specialite']}<br>Adresse: {x['cleaned_address'][:50]}...", axis=1)
                        
                        fig.add_trace(go.Scattermapbox(
                            lat=service_data['latitude'],
                            lon=service_data['longitude'],
                            mode='markers',
                            marker=dict(
                                size=6,
                                color=color,
                                opacity=0.7
                            ),
                            text=hover_text,
                            hovertemplate='<b>%{text}</b><extra></extra>',
                            name=f'{service.title()} ({len(service_data)})',
                            showlegend=True,
                            legendgroup=service,
                            visible=True
                        ))
            
            # Add BIAT branches (if biat layer is selected)
            if 'biat' in (map_layers or []):
                biat_data = df_banks[df_banks['banque'].str.upper() == 'BIAT']
                
                if slct_city:
                    biat_data = biat_data[biat_data['gouvernorat'].isin(slct_city)]
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

            # Add competitor banks (if competitors layer is selected)
            if 'competitors' in (map_layers or []):
                competitor_data = df_banks[df_banks['banque'].str.upper() != 'BIAT']
                
                if slct_city:
                    competitor_data = competitor_data[competitor_data['gouvernorat'].isin(slct_city)]
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

            # Update layout (same as medical professionals)
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
            print(f"Error in pharmacies callback: {e}")
            # Return simple map on error
            fig = go.Figure()
            fig.update_layout(
                mapbox_style="carto-positron",
                mapbox=dict(center=dict(lat=34.0, lon=9.5), zoom=5),
                title=f"Error loading map: {str(e)}"
            )
            return fig