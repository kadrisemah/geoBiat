from dash.dependencies import Input, Output, State
import plotly.express as px  
import plotly.graph_objs as go
import pandas as pd 
import geopandas as gpd
import dash

# Load data (same as medical professionals structure)
try:
    df_experts = pd.read_csv(r'app\experts_comptables\Data\experts_comptables_geocoded.csv', encoding='utf-8')
    df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
    print(f"Loaded {len(df_experts)} experts comptables and {len(df_banks)} banks")
except Exception as e:
    print(f"Error loading data: {e}")
    df_experts = pd.DataFrame()
    df_banks = pd.DataFrame()

# Load geographic boundaries
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

def register_callbacks_experts_comptables(app):
    
    # Callback to populate delegation dropdown based on governorate selection (same as accueil)
    @app.callback(
        dash.dependencies.Output('slct_delegat_experts', 'options'),
        [dash.dependencies.Input('slct_city_experts', 'value')])
    def set_delegations_options_experts(slct_city):
        if slct_city:
            return [{'label': i, 'value': i} for i in gdf_delegation[gdf_delegation["gouvernorat"].isin(slct_city)]['delegation'].unique()]
        else:
            return ""

    # Callback to populate conseil selection dynamically
    @app.callback(
        [Output('conseil_selection', 'options'),
         Output('conseil_selection', 'value')],
        [Input('filter_gouvernorat_experts', 'value'),
         Input('select_all_conseils', 'n_clicks'),
         Input('deselect_all_conseils', 'n_clicks')],
        [State('conseil_selection', 'value')]
    )
    def update_conseil_selection(selected_gouvernorats, select_all_clicks, deselect_all_clicks, current_selection):
        ctx = dash.callback_context
        
        # Filter experts based on gouvernorat selection
        filtered_df = df_experts.copy()
        if selected_gouvernorats:
            filtered_df = filtered_df[filtered_df['gouvernorat'].isin(selected_gouvernorats)]
        
        # Get available conseil options
        available_conseils = sorted(filtered_df['specialite'].dropna().unique())
        options = [{"label": conseil, "value": conseil} for conseil in available_conseils]
        
        # Handle button clicks
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'select_all_conseils':
                return options, available_conseils
            elif button_id == 'deselect_all_conseils':
                return options, []
        
        # Keep current selection if valid
        if current_selection:
            valid_selection = [conseil for conseil in current_selection if conseil in available_conseils]
            return options, valid_selection
        
        return options, available_conseils  # Select all by default

    # Main callback for updating the map (same structure as medical professionals)
    @app.callback(
        Output('experts_bee_map', 'figure'),
        [Input(component_id='slct_city_experts', component_property='value'),
         Input(component_id='slct_delegat_experts', component_property='value'),
         Input(component_id='filter_gouvernorat_experts', component_property='value'),
         Input(component_id='map_layers_experts', component_property='value'),
         Input(component_id='conseil_selection', component_property='value')
        ]
    )
    def update_experts_graph(slct_city, slct_delegat, filter_gouvernorats, map_layers, conseil_selection):
        try:
            # Comprehensive color palette for conseil régional
            color_palette = [
                '#e74c3c', '#3498db', '#27ae60', '#f39c12', '#9b59b6', '#e67e22', '#1abc9c', '#34495e',
                '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7', '#a29bfe',
                '#fd79a8', '#fdcb6e', '#e17055', '#00b894', '#00cec9', '#0984e3', '#ff7675', '#74b9ff'
            ]
            
            # Filter experts based on selections
            filtered_experts = df_experts.copy()
            
            # Apply gouvernorat filter
            if filter_gouvernorats:
                filtered_experts = filtered_experts[filtered_experts['gouvernorat'].isin(filter_gouvernorats)]
            elif slct_city:
                filtered_experts = filtered_experts[filtered_experts['gouvernorat'].isin(slct_city)]
            
            # Apply conseil régional filter
            if conseil_selection:
                filtered_experts = filtered_experts[filtered_experts['specialite'].isin(conseil_selection)]
            
            if slct_city and slct_delegat:
                # Show delegation level map
                fig = px.choropleth_mapbox(gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)],
                               geojson=gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)].geometry,
                               locations=gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)].index,
                               color_discrete_sequence=["rgba(0,0,0,0)"],
                               mapbox_style="carto-positron",
                               zoom=8, opacity=0.5)
                
                # Filter experts by selected delegations
                delegation_to_gouvernorat = gdf_delegation.set_index('delegation')['gouvernorat'].to_dict()
                selected_gouvernorats = []
                for deleg in slct_delegat:
                    if deleg in delegation_to_gouvernorat:
                        selected_gouvernorats.append(delegation_to_gouvernorat[deleg])
                
                if selected_gouvernorats:
                    filtered_experts = filtered_experts[filtered_experts['gouvernorat'].isin(selected_gouvernorats)]

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
            
            # Add experts comptables by conseil régional (if experts layer is selected)
            if 'experts' in (map_layers or []) and len(filtered_experts) > 0:
                # Only show experts with valid coordinates
                valid_experts = filtered_experts[
                    (filtered_experts['latitude'].notna()) & 
                    (filtered_experts['longitude'].notna())
                ]
                
                if len(valid_experts) > 0:
                    all_conseils = sorted(valid_experts['specialite'].dropna().unique())
                    conseil_colors = {}
                    
                    for i, conseil in enumerate(all_conseils):
                        conseil_colors[conseil] = color_palette[i % len(color_palette)]
                    
                    # Add each conseil as separate trace
                    for conseil in valid_experts['specialite'].dropna().unique():
                        conseil_data = valid_experts[valid_experts['specialite'] == conseil]
                        
                        color = conseil_colors.get(conseil, '#95a5a6')
                        
                        # Create hover text
                        hover_text = conseil_data.apply(lambda x: 
                            f"{x['Nom']}<br>Conseil: {x['specialite']}<br>Adresse: {x['cleaned_address'][:50]}...", axis=1)
                        
                        fig.add_trace(go.Scattermapbox(
                            lat=conseil_data['latitude'],
                            lon=conseil_data['longitude'],
                            mode='markers',
                            marker=dict(
                                size=8,
                                color=color,
                                opacity=0.8
                            ),
                            text=hover_text,
                            hovertemplate='<b>%{text}</b><extra></extra>',
                            name=f'{conseil} ({len(conseil_data)})',
                            showlegend=True,
                            legendgroup=conseil,
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
            print(f"Error in experts callback: {e}")
            # Return simple map on error
            fig = go.Figure()
            fig.update_layout(
                mapbox_style="carto-positron",
                mapbox=dict(center=dict(lat=34.0, lon=9.5), zoom=5),
                title=f"Error loading map: {str(e)}"
            )
            return fig