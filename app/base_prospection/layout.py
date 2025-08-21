
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from app.components.navigation import create_navigation
import warnings
warnings.filterwarnings("ignore")
import time
# Import the necessaries libraries
import pandas as pd 
import geopandas as gpd 


df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
agence_lib = pd.read_excel(r'app\base_prospection\Data\agence_libelle.xlsx')
agence_lib['AGENCE CTOS'] = agence_lib['AGENCE CTOS'].astype(str)
options = ['A5' ,'51','B5','65'] 
agence_lib = agence_lib[~agence_lib['AGENCE CTOS'].isin(options)] 

gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": "20px",
    "margin": "auto",
}

prospection_page = html.Div(
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

                            create_navigation(active_page='prospection'),
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
                            html.Div(className="div-for-dropdown",
                                children=[
                                    dcc.Dropdown(id="slct_city",
                                                options=[{"label": i, "value": i} for i in gdf_all_banks['gouvernorat'].unique()],
                                                multi=True,
                                                placeholder="Sélectionnez un ou plusieurs gouvernorat"
                                                ,style={"margin-top":"1rem"})
                                                
                                ]
                            )
                        ,width=3),
                        dbc.Col(
                            html.Div(className="div-for-dropdown",
                                children=[
                                    dcc.Dropdown(id="slct_delegat", 
                                                multi=True,
                                                placeholder="Sélectionnez une ou plusieurs Délegation",
                                                style={"margin-top":"1rem"}
                                            )
                                ]
                            )
                        ,width=3),

                        dbc.Col(
                        dbc.CardGroup(
                            [
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H5("Source : Données scrapées", className="card-title",style={"font-family": "Open Sans Semi Bold",
                                                                                                                "letter-spacing": "0px",
                                                                                                                "font-size": "14px","color":"white"}),
                                        ]
                                    ),style ={"max-width":"22rem",
                                    "background-color":"#31302f"},
                                    outline=True,color="warning",
                                ),

                            ],
                            className="mt-3 shadow",style={"float":"right"}
                        ),width=6)
                    ],style={  
                        "margin-left": "1rem",
                        "margin-right": "3rem"})
                    ,

                        html.Div([
                            dcc.Graph(id="stat_graph",style={"margin-top":"1rem","margin-left":"1rem",'width': '99%', 'height': '600px'}),
                            dcc.Graph(id="second_graph",style={"margin-left":"1rem",'width': '99%', 'height': '600px','margin-bottom':'1rem'}),]
                            ,style={"overflow-y":"scroll"})



                    ],
                )

            ],
        )
    ]
)





