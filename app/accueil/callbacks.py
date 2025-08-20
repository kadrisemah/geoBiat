from dash.dependencies import Input, Output
import plotly.express as px  
import re
import plotly.graph_objs as go

import dash
import pandas as pd 
import geopandas as gpd
import seaborn as sns
import json 

from dash import dcc 


df_banks = pd.read_csv(r'app\accueil\Data\geo_banks.csv')
df_banks["banque"] = df_banks["banque"].str.upper()
df_banks["agence"] = df_banks["agence"].str.upper()
df_banks["BIAT LA PLUS PROCHE"] = df_banks["BIAT LA PLUS PROCHE"].str.upper()
df_banks["CONCURRENT LE PLUS PROCHE"] = df_banks["CONCURRENT LE PLUS PROCHE"].str.upper()

segmentation_client = pd.read_excel(r'app\accueil\Data\Nouvelle segmentation -AGENCE_SEGMENT_03 mars -souad.xlsx',sheet_name='Feuil2')

def transform_value(x):
    if re.match(r'^\d+$', x):
        return int(x)
    else:
        return x

# Apply the transformation function to the ID column
segmentation_client['Étiquettes de lignes'] = segmentation_client['Étiquettes de lignes'].apply(transform_value)


chef_agence = pd.read_excel(r'app\accueil\Data\référentiel DA -20023- avec tel (2).xlsx')
chef_agence['N° de tél '] = chef_agence['N° de tél '].astype(str)
chef_agence.rename(columns={"Prénom & Nom DA ":"Prénom & Nom"},inplace=True)


agence_lib = pd.read_excel(r'app\accueil\Data\agence_libelle.xlsx')
agence_lib = agence_lib.merge(chef_agence,left_on='AGENCE CTOS',right_on='PV',how='left')
agence_lib['AGENCE CTOS'] = agence_lib['AGENCE CTOS'].astype(str)
options = ['A5' ,'51','B5','65'] 
agence_lib = agence_lib[~agence_lib['AGENCE CTOS'].isin(options)] 

df_bank_t24 = pd.read_excel(r'app\accueil\Data\Nouveau Feuille de calcul Microsoft Excel.xlsx')
df_bank_t24['agence'] = df_bank_t24['agence'].str.upper()
df_bank_t24['Code Ag'] = df_bank_t24['Code Ag'].astype(str)

final_scraped_data = pd.read_csv(r'app\accueil\Data\final_data_delegationV2.csv')
final_scraped_data.type.replace({"entreprise":"Entreprise"},inplace=True)
final_scraped_data = final_scraped_data[final_scraped_data.type != "Bank"]
final_scraped_data.reset_index(inplace=True,drop=True)
final_scraped_data = final_scraped_data[final_scraped_data["type"]!="Entreprise"]

df_banks["agence"].replace({"BIAT BAB BHAR 21": "BIAT BAB BHAR 20"}, inplace=True)
df_banks["Distance_Km"] = df_banks["Distance_Km"].astype(str)

colordict = {"BIAT":"#004579","AMEN":"#02892b","ATB":"#a5152a","ATTIJARI":"#fcbd00","BARAKA":"#68696b","BH":"#ff0000","BNA":"#95FF9B","BT":"#2a2053"\
            ,"BTK":"#007dac","BTS":"#FF83DE","QNB":"#C51A93","STB":"#0086d7","TSB":"#35968A","UBCI":"#45b1b3","UIB":"#863756","WIFAK":"#c52f40",\
            "ZITOUNA":"#2DEA19","BFPME":"#FD9A9A","BTE":"#5d85b5","BTL":"#0a545e","ABC":"#07c2ff","BFT":"#6C62FF","CITI_BANK":"#3E4348"}
colordict = dict(sorted(colordict.items())) 
dict_color_bank_df = pd.DataFrame({"banque":colordict.keys(),"color":colordict.values()})
df_banks = dict_color_bank_df.merge(df_banks,on="banque")

df_biat = df_banks[df_banks['banque']=='BIAT'][['agence','delegation','lat','long','banque','Nearest_Biat','Distance_Km','gouvernorat','color','CONCURRENT LE PLUS PROCHE','BIAT LA PLUS PROCHE']]
df_banks_not_biat = df_banks[df_banks['banque']!='BIAT']
merged = df_biat.merge(df_bank_t24,on="agence",how='left')
agence_lib_merged = agence_lib.merge(merged,left_on='AGENCE CTOS',right_on='Code Ag',how='left')

segmentation_client["Étiquettes de lignes"] = segmentation_client["Étiquettes de lignes"].astype(str)
agence_lib_merged = agence_lib_merged.merge(segmentation_client,right_on="Étiquettes de lignes",left_on="AGENCE CTOS",how="left")
agence_lib_merged['Bank_Count_Name'] = agence_lib_merged.groupby('banque')['banque'].transform(lambda x: x + ' (' + str(x.count())+')')


agence_lib_merged = agence_lib_merged[agence_lib_merged['Étiquettes de lignes'].notna()]
agence_lib_merged["NB Clients PP"] = agence_lib_merged["NB Clients PP"].astype(int)
agence_lib_merged["NB Clients TPME"] = agence_lib_merged["NB Clients TPME"].astype(int)
agence_lib_merged["NB Clients PP"] = agence_lib_merged["NB Clients PP"].astype(str)
agence_lib_merged["NB Clients TPME"] = agence_lib_merged["NB Clients TPME"].astype(str)

gdf_not_biat = gpd.GeoDataFrame(df_banks_not_biat, geometry=gpd.points_from_xy(df_banks_not_biat.long, df_banks_not_biat.lat))
gdf_not_biat['Bank_Count_Name'] = gdf_not_biat.groupby('banque')['banque'].transform(lambda x: x + ' (' + str(x.count())+')')
gdf_not_biat['agence'] = gdf_not_biat['agence'].str.upper()
gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))
gdf_delegation = gpd.read_file(r'app\accueil\Data\gdf_delegation.geojson')

def register_callbacks_accueil(accueil):

    # Update Delegations
    @accueil.callback(
        dash.dependencies.Output('slct_delegat', 'options'),
        [dash.dependencies.Input('slct_city', 'value')])
    def set_delegations_options(slct_city):
        if slct_city:
            return [{'label': i, 'value': i} for i in gdf_delegation[gdf_delegation["gouvernorat"].isin(slct_city)]['delegation'].unique()]
        else:
            return ""

    # Linking Graph and inputs
    @accueil.callback(
        Output(component_id='my_bee_map', component_property='figure'),
        [Input(component_id='slct_city', component_property='value'),
        Input(component_id='slct_delegat', component_property='value'),
        ]
    )
    def update_graph(slct_city, slct_delegat):

        # if city is selected only
        if (slct_city and not slct_delegat):
            governorates_gdf = gdf_delegation.dissolve(by='gouvernorat', aggfunc='first').reset_index()
            geojson1 = json.loads(governorates_gdf[governorates_gdf['gouvernorat'].isin(slct_city)].geometry.to_json())
            for i in range(len(list(governorates_gdf[governorates_gdf['gouvernorat'].isin(slct_city)]['gouvernorat']))):
                geojson1['features'][i]['properties']['gouvernorat'] = list(governorates_gdf[governorates_gdf['gouvernorat'].isin(slct_city)]['gouvernorat'])[i]
            dff = gdf_not_biat.copy()
            dff = dff[dff["gouvernorat"].isin(slct_city)]
            dff['Bank_Count_Name'] = dff.groupby('banque')['banque'].transform(lambda x: x + ' (' + str(x.count())+')')
            if len(slct_city) != 1 :
                zoom = 6.7
                center = {"lat":34.9178572,"lon":9.496527}
            else :
                zoom = 8.7
                center = {"lat":dff['geometry'].iloc[0].y,"lon":dff['geometry'].iloc[0].x}
            dff2 = agence_lib_merged.copy() 
            dff2 = dff2[dff2["gouvernorat"].isin(slct_city)]
            dff2['Bank_Count_Name'] = dff2.groupby('banque')['banque'].transform(lambda x: x + ' (' + str(x.count())+')')
            fig = px.choropleth_mapbox(governorates_gdf[governorates_gdf.gouvernorat.isin(slct_city)],
                           geojson=geojson1,
                           locations="gouvernorat", featureidkey="properties.gouvernorat",
                           zoom=zoom,
                           opacity=0.5,
                           center=center,
                           mapbox_style="carto-positron",
                           color="gouvernorat" 
                           )

            try :           
                biat_trace = go.Scattermapbox(
                    lat=dff2["lat"],
                    lon=dff2["long"],
                    text='<b>'+dff2["agence"]+" ("+dff2["AGENCE CTOS"]+")"+'</b>'\
                    
                    "<br>"+dff2["REGION"]+\
                    "<br>"+dff2["ZONE"]+\
                    "<br>NB Clients PP: "+dff2["NB Clients PP"]+\
                    "<br>NB Clients TPME:"+dff2["NB Clients TPME"]+\
                    "<br>"+dff2["Prénom & Nom"]+\
                    "<br>"+dff2["N° de tél "]+"<br>"+\
                    "Conccurent le plus Proche="+dff2["CONCURRENT LE PLUS PROCHE"],
                    marker={"color":colordict["BIAT"],"size":10},
                    mode="markers",
                    hoverinfo="text",
                    visible=True,
                    name=dff2["Bank_Count_Name"].values[0]
                )
                fig.add_trace(biat_trace)
            except : 
                pass
            for ag in dff['agence'].unique():

                bank_trace = go.Scattermapbox(
                    lat=dff[dff["agence"]==ag]["lat"],
                    lon=dff[dff["agence"]==ag]["long"],
                    text='<b>'+dff[dff["agence"]==ag]["agence"].values[0]+'</b>'+"<br>"+"BIAT LA PLUS PROCHE="+dff[dff["agence"]==ag]["BIAT LA PLUS PROCHE"].values,
            #         textfont={"color":"white","size":10, "family":"Courier New"},
                    marker={"color":colordict[ag],"size":10},
                    mode="markers",
                    hoverinfo="text",
                    visible='legendonly',
                    #size="pop_3km"n
                    name=dff[dff["agence"]==ag]["Bank_Count_Name"].values[0],
                )
                fig.add_trace(bank_trace) 
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},legend_title_text="Banques")
            return fig


        # if city & delegation selected
        if (slct_city and slct_delegat):
            geojson1 = json.loads(gdf_delegation[gdf_delegation['delegation'].isin(slct_delegat)].geometry.to_json())
            for i in range(len(list(gdf_delegation[gdf_delegation['delegation'].isin(slct_delegat)]['delegation']))):
                geojson1['features'][i]['properties']['delegation'] = list(gdf_delegation[gdf_delegation['delegation'].isin(slct_delegat)]['delegation'])[i]
            dff = gdf_not_biat.copy()
            dff = dff[dff["gouvernorat"].isin(slct_city)]
            dff = dff[dff["delegation"].isin(slct_delegat)]
            dff['Bank_Count_Name'] = dff.groupby('banque')['banque'].transform(lambda x: x + ' (' + str(x.count())+')')
            if len(slct_city) != 1 and len(slct_city) == 1  :
                zoom = 6.7
                center = {"lat":34.9178572,"lon":9.496527}
            else :
                zoom = 10
                center = {"lat":dff['geometry'].iloc[0].centroid.y,"lon":dff['geometry'].iloc[0].centroid.x}
            dff2 = agence_lib_merged.copy() 
            dff2 = dff2[(dff2["gouvernorat"].isin(slct_city))& (dff2["delegation"].isin(slct_delegat))]
            dff2['Bank_Count_Name'] = dff2.groupby('banque')['banque'].transform(lambda x: x + ' (' + str(x.count())+')')

            fig = px.choropleth_mapbox(gdf_delegation[gdf_delegation.delegation.isin(slct_delegat)],
                           geojson=geojson1,
                           locations="delegation", featureidkey="properties.delegation",
                           zoom=zoom,
                           opacity=0.5,
                           center=center,
                           mapbox_style="carto-positron",
                           color="delegation" 
                           )

            try :           
                biat_trace = go.Scattermapbox(
                    lat=dff2["lat"],
                    lon=dff2["long"],
                    text='<b>'+dff2["agence"]+" ("+dff2["AGENCE CTOS"]+")"+'</b>'\
                    
                    "<br>"+dff2["REGION"]+\
                    "<br>"+dff2["ZONE"]+\
                    "<br>NB Clients PP: "+dff2["NB Clients PP"]+\
                    "<br>NB Clients TPME:"+dff2["NB Clients TPME"]+\
                    "<br>"+dff2["Prénom & Nom"]+\
                    "<br>"+dff2["N° de tél "]+"<br>"+\
                    "Conccurent le plus Proche="+dff2["CONCURRENT LE PLUS PROCHE"],
                    marker={"color":colordict["BIAT"],"size":10},
                    mode="markers",
                    hoverinfo="text",
                    visible=True,
                    name=dff2["Bank_Count_Name"].values[0]
                )
                fig.add_trace(biat_trace)
            except : 
                pass
            for ag in dff['agence'].unique():

                bank_trace = go.Scattermapbox(
                    lat=dff[dff["agence"]==ag]["lat"],
                    lon=dff[dff["agence"]==ag]["long"],
                    text='<b>'+dff[dff["agence"]==ag]["agence"].values[0]+'</b>'+"<br>"+"BIAT LA PLUS PROCHE="+dff[dff["agence"]==ag]["BIAT LA PLUS PROCHE"].values,
            #         textfont={"color":"white","size":10, "family":"Courier New"},
                    marker={"color":colordict[ag],"size":10},
                    mode="markers",
                    hoverinfo="text",
                    visible='legendonly',
                    #size="pop_3km"n
                    name=dff[dff["agence"]==ag]["Bank_Count_Name"].values[0],
                )
                fig.add_trace(bank_trace) 
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},legend_title_text="Banques")
            return fig

        # nothing is selected / initial state                   
        else:
            fig = px.scatter_mapbox(agence_lib_merged, lat="lat", lon="long", color='Bank_Count_Name',color_discrete_sequence=list(agence_lib_merged['color'].values),
                                    zoom=6.7,
                                    hover_data={"long":False,"lat":False,"AGENCE CTOS":True,"REGION":True,"ZONE":True,"NB Clients PP":True,"NB Clients TPME":True,"Prénom & Nom":True,"N° de tél ":True,"banque":False,
                                                    "gouvernorat":False,"delegation":False,"Bank_Count_Name":False,"Nearest_Biat":False, "Distance_Km" :False,"CONCURRENT LE PLUS PROCHE":True,"BIAT LA PLUS PROCHE":False},
                                    center={"lat":34.9178572,
                                            "lon":9.496527
                                                            }
                       )
            fig.update_traces(marker={'size': 10},hovertemplate = '<b>'+agence_lib_merged["agence"]+" ("+agence_lib_merged["AGENCE CTOS"]+")"+'</b>'\
                    "<br>"+agence_lib_merged["REGION"]+\
                    "<br>"+agence_lib_merged["ZONE"]+\
                    "<br>NB Clients PP: "+agence_lib_merged["NB Clients PP"]+\
                    "<br>NB Clients TPME:"+agence_lib_merged["NB Clients TPME"]+\
                    "<br>"+agence_lib_merged["Prénom & Nom"]+\
                    "<br>"+agence_lib_merged["N° de tél "]+"<br>"+\
                    "Conccurent le plus Proche="+agence_lib_merged["CONCURRENT LE PLUS PROCHE"] + '<extra></extra>'),

            fig2 = px.scatter_mapbox(gdf_not_biat, lat="lat", lon="long", color='Bank_Count_Name',color_discrete_sequence=list(gdf_not_biat['color'].unique()),
                                    zoom=6.7,
                                    center={"lat":34.9178572,
                                            "lon":9.496527
                                                            },
                                        hover_data={"long":False,"lat":False,"banque":False,
                                                    "gouvernorat":False,"delegation":False,"Nearest_Biat":False,"Bank_Count_Name":False, "Distance_Km" :False,"CONCURRENT LE PLUS PROCHE":False,"BIAT LA PLUS PROCHE":True},)
            fig2.update_traces(visible='legendonly')
            fig2.update_traces(marker={'size': 10},
                    hovertemplate = '<b>'+gdf_not_biat["agence"]+
                    "<br>" +"BIAT LA PLUS PROCHE : "+gdf_not_biat["BIAT LA PLUS PROCHE"] + '<extra></extra>')
            for i in range(0,len(gdf_not_biat['agence'].unique())):
                fig.add_trace(fig2.data[i]) 
            fig.update_layout(mapbox_style="carto-positron",margin={"r": 0, "t": 0, "l": 0, "b": 0},legend_title_text="Banques")



            return fig


    