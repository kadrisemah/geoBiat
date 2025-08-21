from dash import dcc, html
import dash_bootstrap_components as dbc
from app.components.navigation import create_navigation
import warnings
warnings.filterwarnings("ignore")
import pandas as pd 
import geopandas as gpd 

# Load conseillers data
df_conseillers = pd.read_csv(r'app\conseillers\Data\conseillers_geocoded.csv')
df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))

# Load geographic boundaries (same as accueil)
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

# Get unique categories and governorates
unique_categories = sorted(df_conseillers['categorie'].dropna().unique())
unique_gouvernorats = sorted(df_conseillers['gouvernorat'].dropna().unique())

conseillers_page = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    style={"height": "100vh", "overflow-y": "auto", "padding-right": "10px"},
                    children=[
                        dbc.Row([
                            dbc.Col(                        
                            html.A(
                                html.Img(
                                    className="logo",
                                    src=("assets\\biat.jpg"),       
                                ),
                            href="https://www.biat.com.tn/"),width=3),
                            dbc.Col(
                            html.H2("BIAT - OUTIL DE GEOMARKETING ",style={"padding-top": "8px"}),width=9)]),

                            create_navigation(active_page='conseillers'),

                        # Filters section - Optimized for scrolling
                        html.Div([
                            html.H4("Filtres", style={"margin-top": "1rem", "margin-bottom": "1rem", "color": "#2c3e50"}),
                            
                            # Gouvernorat Filter
                            html.Div([
                                html.Label("Gouvernorat:", style={"font-weight": "bold", "margin-bottom": "0.3rem", "font-size": "0.9rem"}),
                                dcc.Dropdown(
                                    id="filter_gouvernorat_conseillers",
                                    options=[{"label": gov, "value": gov} for gov in unique_gouvernorats],
                                    multi=True,
                                    placeholder="Sélectionner gouvernorat(s)",
                                    style={"margin-bottom": "0.8rem", "font-size": "0.85rem"}
                                )
                            ]),
                            
                            # Map Layers Filter  
                            html.Div([
                                html.Label("Affichage:", style={"font-weight": "bold", "margin-bottom": "0.3rem", "font-size": "0.9rem"}),
                                dcc.Checklist(
                                    id="map_layers_conseillers",
                                    options=[
                                        {"label": "Conseillers", "value": "conseillers"},
                                        {"label": "Agences BIAT", "value": "biat"},
                                        {"label": "Banques Concurrentes", "value": "competitors"}
                                    ],
                                    value=["conseillers", "biat"],
                                    style={"margin-bottom": "0.8rem", "font-size": "0.85rem"}
                                )
                            ]),
                            
                            # Distance-based Precision Filter
                            html.Div([
                                html.Label("Zone de Proximité BIAT:", style={"font-weight": "bold", "margin-bottom": "0.3rem", "font-size": "0.9rem"}),
                                html.P("Basé sur la distance réelle à l'agence BIAT la plus proche", 
                                      style={"font-size": "0.75rem", "color": "#666", "margin-bottom": "0.4rem", "line-height": "1.2"}),
                                
                                # Quick filter buttons - more compact
                                html.Div([
                                    dbc.Button("Stratégique", id="high_precision_conseillers", color="success", size="sm", 
                                              style={"margin-right": "0.3rem", "margin-bottom": "0.4rem", "font-size": "0.75rem", "padding": "0.2rem 0.5rem"}),
                                    dbc.Button("Expansion", id="medium_precision_conseillers", color="warning", size="sm",
                                              style={"margin-right": "0.3rem", "margin-bottom": "0.4rem", "font-size": "0.75rem", "padding": "0.2rem 0.5rem"}),
                                    dbc.Button("Toutes", id="all_precision_conseillers", color="info", size="sm",
                                              style={"margin-bottom": "0.4rem", "font-size": "0.75rem", "padding": "0.2rem 0.5rem"})
                                ]),
                                
                                # Detailed checkboxes - more compact
                                dcc.Checklist(
                                    id="precision_selection_conseillers",
                                    options=[
                                        {"label": "Zone Stratégique (≤2km)", "value": "high"},
                                        {"label": "Zone d'Expansion (2-6km)", "value": "medium"},
                                        {"label": "Zone Éloignée (>6km)", "value": "low"}
                                    ],
                                    value=["high", "medium", "low"],
                                    style={"border": "1px solid #ddd", "padding": "0.4rem", "border-radius": "4px", 
                                          "font-size": "0.8rem", "background-color": "#fff"}
                                )
                            ], style={"margin-bottom": "0.8rem"})
                            
                        ], style={"padding": "0.8rem", "background-color": "#f8f9fa", "border-radius": "8px", "margin-bottom": "1rem"})

                    ],
                ),

                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    children=[
                                        dcc.Dropdown(id="slct_city_conseillers",
                                                    options=[{"label": i, "value": i} for i in gdf_all_banks['gouvernorat'].unique()],
                                                    multi=True,
                                                    placeholder="Sélectionnez un ou plusieurs Gouvernorat")
                                    ],style={"margin-top":"1rem"}
                                )
                            ,width=4),
                            dbc.Col(
                                html.Div(
                                    children=[
                                        dcc.Dropdown(id="slct_delegat_conseillers", 
                                                    multi=True,
                                                    placeholder="Sélectionnez une ou plusieurs Délégation",                                                    
                                                )
                                    ],style={"margin-top":"1rem"}
                                )
                            ,width=4),

                        ],style={  
                            "margin-left": "1rem",
                            "margin-right": "3rem"})
                    ,

        
                        dcc.Graph(id="conseillers_bee_map",style={"height": "93rem",
                                                        "margin-bottom": "1rem",
                                                        "margin-left": "1rem","margin-right": "1rem","margin-top":"1rem"}),
                        

                    ],
                )

            ],
        )
    ]
)