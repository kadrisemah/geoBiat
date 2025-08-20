from dash import dcc, html
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings("ignore")
import pandas as pd 
import geopandas as gpd 

# Load doctors data
df_doctors = pd.read_csv(r'app\medical_professionals\Data\doctors_geocoded.csv')
df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))

# Load geographic boundaries (same as accueil)
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

# Get unique specialties and governorates
unique_specialties = sorted(df_doctors['specialite'].unique())
unique_gouvernorats = sorted(df_doctors['gouvernorat'].unique())

medical_professionals_page = html.Div(
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

                            dbc.Nav(
                                [
                                    dcc.Link(dbc.NavLink("Accueil",active=False),href="/",refresh=True),
                                    dcc.Link(dbc.NavLink("Base de Prospection",active=False),href="/prospection",refresh=True),
                                    dcc.Link(dbc.NavLink("Socio-Démographie",active=False),href="/socio_démographie",refresh=True),
                                    dcc.Link(dbc.NavLink("Equipements Financiers",active=False),href="/equip_financ",refresh=True),
                                    dcc.Link(dbc.NavLink("Logement et Patrimoine",active=False),href="/log_patrimoine",refresh=True),
                                    dcc.Link(dbc.NavLink("Assurance",active=False),href="/assurance",refresh=True),
                                    dcc.Link(dbc.NavLink("Dépenses",active=False),href="/depense",refresh=True),
                                    dcc.Link(dbc.NavLink("Professionnels Médicaux",active=True),href="/medical_professionals",refresh=True),
                                    dcc.Link(dbc.NavLink("Experts Comptables",active=False),href="/experts_comptables",refresh=True),
                                    dcc.Link(dbc.NavLink("Pharmacies",active=False),href="/pharmacies",refresh=True),

                                ],
                                vertical=True,
                                pills=True,
                                style={"margin-top":"6rem"}
                            ),

                        # Filters section
                        html.Div([
                            html.H4("Filtres", style={"margin-top": "2rem", "color": "#2c3e50"}),
                            
                            html.Div([
                                html.Label("Gouvernorat:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                dcc.Dropdown(
                                    id="filter_gouvernorat",
                                    options=[{"label": gov, "value": gov} for gov in unique_gouvernorats],
                                    multi=True,
                                    placeholder="Sélectionner gouvernorat(s)",
                                    style={"margin-bottom": "1rem"}
                                )
                            ]),
                            
                            html.Div([
                                html.Label("Spécialité Médicale:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                dcc.Dropdown(
                                    id="filter_speciality",
                                    options=[{"label": spec, "value": spec} for spec in unique_specialties],
                                    multi=True,
                                    placeholder="Sélectionner spécialité(s)",
                                    style={"margin-bottom": "1rem"}
                                )
                            ]),
                            
                            html.Div([
                                html.Label("Affichage:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                dcc.Checklist(
                                    id="map_layers",
                                    options=[
                                        {"label": "Professionnels Médicaux", "value": "doctors"},
                                        {"label": "Agences BIAT", "value": "biat"},
                                        {"label": "Banques Concurrentes", "value": "competitors"}
                                    ],
                                    value=["doctors", "biat"],
                                    style={"margin-bottom": "1rem"}
                                )
                            ]),
                            
                            html.Div([
                                html.Label("Spécialités à Afficher:", style={"font-weight": "bold", "margin-bottom": "0.5rem"}),
                                html.Div([
                                    dbc.Button("Tout Sélectionner", id="select_all_specialties", color="primary", size="sm", 
                                              style={"margin-right": "0.5rem", "margin-bottom": "0.5rem"}),
                                    dbc.Button("Tout Désélectionner", id="deselect_all_specialties", color="secondary", size="sm",
                                              style={"margin-bottom": "0.5rem"})
                                ]),
                                dcc.Checklist(
                                    id="specialty_selection",
                                    options=[],  # Will be populated dynamically
                                    value=[],    # Will be populated dynamically
                                    style={"max-height": "300px", "overflow-y": "scroll", "border": "1px solid #ddd", 
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
                                        dcc.Dropdown(id="slct_city",
                                                    options=[{"label": i, "value": i} for i in gdf_all_banks['gouvernorat'].unique()],
                                                    multi=True,
                                                    placeholder="Sélectionnez un ou plusieurs Gouvernorat")
                                    ],style={"margin-top":"1rem"}
                                )
                            ,width=4),
                            dbc.Col(
                                html.Div(
                                    children=[
                                        dcc.Dropdown(id="slct_delegat", 
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


        
                        dcc.Graph(id="my_bee_map",style={"height": "93rem",
                                                        "margin-bottom": "1rem",
                                                        "margin-left": "1rem","margin-right": "1rem","margin-top":"1rem"}),
                        

                    ],
                )

            ],
        )
    ]
)