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

                        # Filters section
                        html.Div([
                            html.H4("Filtres", style={"margin-top": "2rem", "color": "#2c3e50"}),
                            
                            html.Div([
                                html.Label("Gouvernorat:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                dcc.Dropdown(
                                    id="filter_gouvernorat_conseillers",
                                    options=[{"label": gov, "value": gov} for gov in unique_gouvernorats],
                                    multi=True,
                                    placeholder="Sélectionner gouvernorat(s)",
                                    style={"margin-bottom": "1rem"}
                                )
                            ]),
                            
                            html.Div([
                                html.Label("Affichage:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                dcc.Checklist(
                                    id="map_layers_conseillers",
                                    options=[
                                        {"label": "Conseillers", "value": "conseillers"},
                                        {"label": "Agences BIAT", "value": "biat"},
                                        {"label": "Banques Concurrentes", "value": "competitors"}
                                    ],
                                    value=["conseillers", "biat"],
                                    style={"margin-bottom": "1rem"}
                                )
                            ]),
                            
                            html.Div([
                                html.Label("Précision des Coordonnées:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                html.Div([
                                    dbc.Button("Haute Précision", id="high_precision_conseillers", color="success", size="sm", 
                                              style={"margin-right": "0.5rem", "margin-bottom": "0.5rem"}),
                                    dbc.Button("Précision Moyenne", id="medium_precision_conseillers", color="warning", size="sm",
                                              style={"margin-right": "0.5rem", "margin-bottom": "0.5rem"}),
                                    dbc.Button("Toutes Précisions", id="all_precision_conseillers", color="info", size="sm",
                                              style={"margin-bottom": "0.5rem"})
                                ]),
                                dcc.Checklist(
                                    id="precision_selection_conseillers",
                                    options=[
                                        {"label": "Haute Précision (±30m)", "value": "high"},
                                        {"label": "Précision Moyenne (±1km)", "value": "medium"},
                                        {"label": "Précision Faible", "value": "low"}
                                    ],
                                    value=["high", "medium", "low"],
                                    style={"max-height": "200px", "overflow-y": "scroll", "border": "1px solid #ddd", 
                                          "padding": "0.5rem", "border-radius": "4px", "font-size": "0.85rem"}
                                )
                            ], style={"margin-bottom": "1rem"})
                        ], style={"padding": "1rem", "background-color": "#f8f9fa", "border-radius": "8px"})

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