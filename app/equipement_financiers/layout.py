
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings("ignore")
import time
# Import the necessaries libraries
import pandas as pd 
import geopandas as gpd 

data = pd.read_excel(r'app\socio_demo\Data\Base EXCEL__BESOIN IA (18-11-22).xlsx')
df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))

equip_financ_page = html.Div(
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
                                    dcc.Link(dbc.NavLink("Equipements Financiers",active=True),href="/equip_financ",refresh=True),
                                    dcc.Link(dbc.NavLink("Logement et Patrimoine",active=False),href="/log_patrimoine",refresh=True),
                                    dcc.Link(dbc.NavLink("Assurance",active=False),href="/assurance",refresh=True),
                                    dcc.Link(dbc.NavLink("Dépenses",active=False),href="/depense",refresh=True),

                                ],
                                vertical=True,
                                pills=True,
                                style={"margin-top":"6rem"}
                            ),
                            html.Div(
                                className="row",
                                children=[
                                    html.Div(
                                        
                                        children=[
                                            # Dropdown to select Bank
                                        dbc.Button("Exporter les données",id="export-data", color="dark", className="me-1 mb-3",n_clicks=0,style={"margin-bottom": "2rem"}),
                                        ],
                                    ),
                                    dcc.Download(id="download-dataframe-csv"),
                                ],
                        style={"margin-top":'4rem'} ),

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
                                        dcc.Dropdown(id="slct_gouv",
                                                    options=[{"label": i, "value": i} for i in data["A5-Gouvernorat d'habitation"].unique()],
                                                    multi=True,
                                                    placeholder="Sélectionnez un ou plusieurs gouvernorat")
                                    ],style={"margin-top":"1rem"}
                                )
                            ,width=4),
                            
                            dbc.Col([
                                dbc.CardGroup(
                                    [
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.Div(html.H5(["Population Tunisienne :",html.Br(),"18 ans+"], className="card-title",style={"font-family": "Open Sans Semi Bold",
                                                                                                                        "letter-spacing": "0px",
                                                                                                                        "font-size": "14px","color":"white"}),)

                                                ]
                                            ),style ={"max-width":"22rem",
                                            "background-color":"#31302f"},
                                            outline=True,color="warning",
                                        ),

                                    ],
                                    className="mt-3 shadow",style={"float":"right","margin-right":"2rem","margin-left":"1rem"}
                                ),     
                                dbc.CardGroup(
                                    [
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H5("Source : Données de l’étude de référence", className="card-title",style={"font-family": "Open Sans Semi Bold",
                                                                                                                        "letter-spacing": "0px",
                                                                                                                        "font-size": "14px","color":"white"}),
                                                ]
                                            ),style ={"max-width":"22rem",
                                            "background-color":"#31302f"},
                                            outline=True,color="warning",
                                        ),

                                    ],
                                    className="mt-3 shadow",style={"float":"right"}
                                )],width=8),


                        ],style={  
                            "margin-left": "1rem",
                            "margin-right": "3rem"})
                    ,
                    html.Div([
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    children=[
                                        dcc.Graph(id="fig_taux")
                                    ],style={"margin-left":"15rem",
                                    "margin-top":"3rem"}
                                )
                            ,width=6),
                            dbc.Col(
                                html.Div(
                                    children=[
                                        dcc.Graph(id="fig_multi") 
                                    ],style={"margin-left":"1rem",
                                    "margin-top":"3rem"}
                                )
                            ,width=6),
                        ],style={  
                            "margin-left": "1rem",
                            "margin-right": "3rem",
                            "margin-top":"1rem",
                            "background-color":"white"})
                    ,
                        dbc.Row([
                            dbc.Col(
                                html.Div(id="div_penetration",
                                    children=[
                                        dcc.Graph(id="fig_penetration")
                                    ],style={"margin-left":"8rem",
                                    "margin-top":"-2rem"}
                                )
                            ),
  
                        ],style={  
                            "background-color":"white",
                            "margin-left": "1rem",
                            "margin-right": "3rem"})
                        ],style={"overflow-y":"scroll"})
                    ,

                    ],
                )

            ],
        )
    ]
)