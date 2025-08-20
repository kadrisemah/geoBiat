from dash.dependencies import Input, Output, State
import plotly.express as px  
import plotly.graph_objs as go
import pandas as pd 
import geopandas as gpd
import dash

# Load data (same as accueil structure)
df_doctors = pd.read_csv(r'app\medical_professionals\Data\doctors_geocoded.csv')
df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')

# Load geographic boundaries
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

def register_callbacks_medical_professionals(app):
    
    # Callback to populate delegation dropdown based on governorate selection (same as accueil)
    @app.callback(
        dash.dependencies.Output('slct_delegat', 'options'),
        [dash.dependencies.Input('slct_city', 'value')])
    def set_delegations_options(slct_city):
        if slct_city:
            return [{'label': i, 'value': i} for i in gdf_delegation[gdf_delegation["gouvernorat"].isin(slct_city)]['delegation'].unique()]
        else:
            return ""

    # Main callback for updating the map (same structure as accueil)
    @app.callback(
        Output('my_bee_map', 'figure'),
        [Input(component_id='slct_city', component_property='value'),
        Input(component_id='slct_delegat', component_property='value'),
        ]
    )
    def update_graph(slct_city, slct_delegat):

        # Comprehensive color palette for medical specialties
        color_palette = [
            '#e74c3c', '#3498db', '#27ae60', '#f39c12', '#9b59b6', '#e67e22', '#1abc9c', '#34495e',
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7', '#a29bfe',
            '#fd79a8', '#fdcb6e', '#e17055', '#00b894', '#00cec9', '#0984e3', '#ff7675', '#74b9ff',
            '#55a3ff', '#ff4757', '#3742fa', '#2f3542', '#ff3838', '#ff9ff3', '#54a0ff', '#5f27cd', 
            '#00d2d3', '#ff9f43', '#feca57', '#48dbfb', '#0abde3', '#006ba6', '#0582ca', '#00a8cc', 
            '#00c896', '#f8b500', '#ff6348', '#ff4444', '#ffbb33', '#00C851', '#33b5e5', '#AA66CC', 
            '#FF8800', '#0099CC', '#669900', '#FF4444', '#CC0000', '#9933CC', '#dc143c', '#ff1493',
            '#ff69b4', '#ffa07a', '#fa8072', '#e9967a', '#f4a460', '#daa520', '#ffd700', '#adff2f',
            '#7fff00', '#32cd32', '#98fb98', '#90ee90', '#00fa9a', '#00ff7f', '#40e0d0', '#48d1cc',
            '#20b2aa', '#5f9ea0', '#4682b4', '#6495ed', '#87ceeb', '#87cefa', '#00bfff', '#1e90ff',
            '#6a5acd', '#7b68ee', '#9370db', '#8a2be2', '#9400d3', '#9932cc', '#ba55d3', '#da70d6',
            '#ee82ee', '#dda0dd', '#c71585', '#db7093', '#ff6347', '#ffa500', '#ff7f50', '#ff4500'
        ]
        
        # Filter doctors based on selections
        filtered_doctors = df_doctors.copy()
        
        if slct_city and slct_delegat:
            # Show delegation level map
            fig = px.choropleth_mapbox(gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)],
                           geojson=gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)].geometry,
                           locations=gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)].index,
                           color_discrete_sequence=["rgba(0,0,0,0)"],
                           mapbox_style="carto-positron",
                           zoom=8, opacity=0.5)
            
            # Filter doctors by selected delegations
            # Map delegation to gouvernorat for doctors
            delegation_to_gouvernorat = gdf_delegation.set_index('delegation')['gouvernorat'].to_dict()
            selected_gouvernorats = []
            for deleg in slct_delegat:
                if deleg in delegation_to_gouvernorat:
                    selected_gouvernorats.append(delegation_to_gouvernorat[deleg])
            
            if selected_gouvernorats:
                filtered_doctors = filtered_doctors[filtered_doctors['gouvernorat'].isin(selected_gouvernorats)]

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
            
            # Filter doctors by selected governorats
            filtered_doctors = filtered_doctors[filtered_doctors['gouvernorat'].isin(slct_city)]

        else:
            # Show all Tunisia with all doctors
            fig = px.scatter_mapbox(df_doctors, lat="lat", lon="lon", 
                                  mapbox_style="carto-positron", zoom=5)
            fig.data = []  # Clear default trace
        
        # Add medical professionals by specialty (similar to banks by type in accueil)
        if len(filtered_doctors) > 0:
            all_specialties = sorted(filtered_doctors['specialite'].unique())
            specialty_colors = {}
            
            for i, specialty in enumerate(all_specialties):
                specialty_colors[specialty] = color_palette[i % len(color_palette)]
            
            # Add each specialty as separate trace
            for specialty in filtered_doctors['specialite'].unique():
                specialty_data = filtered_doctors[filtered_doctors['specialite'] == specialty]
                
                color = specialty_colors.get(specialty, '#95a5a6')
                
                fig.add_trace(go.Scattermapbox(
                    lat=specialty_data['lat'],
                    lon=specialty_data['lon'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=color,
                        opacity=0.8
                    ),
                    text=specialty_data['hover_text'],
                    hovertemplate='<b>%{text}</b><extra></extra>',
                    name=f'{specialty} ({len(specialty_data)})',
                    showlegend=True,
                    legendgroup=specialty,
                    visible=True
                ))
        
        # Add BIAT branches (same as accueil)
        biat_data = df_banks[df_banks['banque'].str.upper() == 'BIAT']
        
        if slct_city:
            biat_data = biat_data[biat_data['gouvernorat'].isin(slct_city)]
        
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

        # Add competitor banks
        competitor_data = df_banks[df_banks['banque'].str.upper() != 'BIAT']
        
        if slct_city:
            competitor_data = competitor_data[competitor_data['gouvernorat'].isin(slct_city)]
        
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

        # Update layout (same as accueil)
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