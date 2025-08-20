
from dash import dcc, html
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings("ignore")
import time
# Import the necessaries libraries
import pandas as pd 
import geopandas as gpd 


df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))


accueil_page = html.Div(
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
                                    dcc.Link(dbc.NavLink("Accueil",active=True),href="/",refresh=True),
                                    dcc.Link(dbc.NavLink("Base de Prospection",active=False),href="/prospection",refresh=True),
                                    dcc.Link(dbc.NavLink("Socio-Démographie",active=False),href="/socio_démographie",refresh=True),
                                    dcc.Link(dbc.NavLink("Equipements Financiers",active=False),href="/equip_financ",refresh=True),
                                    dcc.Link(dbc.NavLink("Logement et Patrimoine",active=False),href="/log_patrimoine",refresh=True),
                                    dcc.Link(dbc.NavLink("Assurance",active=False),href="/assurance",refresh=True),
                                    dcc.Link(dbc.NavLink("Dépenses",active=False),href="/depense",refresh=True),


                                ],
                                vertical=True,
                                pills=True,
                                style={"margin-top":"6rem"}
                            ),

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