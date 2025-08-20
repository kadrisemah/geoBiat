import os
from os import name, stat
from shapely.geometry import Polygon, LineString, Point
from dash.dependencies import Input, Output, State
import plotly.express as px  
import shapely.speedups
import plotly.io as pio
from itertools import product
import itertools
import plotly.graph_objs as go
import plotly.offline as pyo
import dash
import pandas as pd 
import geopandas as gpd
import seaborn as sns
import json 
import random
from dash import dcc 


df_banks = pd.read_csv(r'app\base_prospection\Data\geo_banks.csv')
df_banks["banque"] = df_banks["banque"].str.upper()
df_banks["agence"] = df_banks["agence"].str.upper()
df_banks["BIAT LA PLUS PROCHE"] = df_banks["BIAT LA PLUS PROCHE"].str.upper()
df_banks["CONCURRENT LE PLUS PROCHE"] = df_banks["CONCURRENT LE PLUS PROCHE"].str.upper()



agence_lib = pd.read_excel(r'app\base_prospection\Data\agence_libelle.xlsx')
agence_lib['AGENCE CTOS'] = agence_lib['AGENCE CTOS'].astype(str)
options = ['A5' ,'51','B5','65'] 
agence_lib = agence_lib[~agence_lib['AGENCE CTOS'].isin(options)] 
df_biat = df_biat = df_banks.loc[df_banks['banque']=="BIAT"]



df_bank_t24 = pd.read_excel(r'app\base_prospection\Data\Nouveau Feuille de calcul Microsoft Excel.xlsx')
df_bank_t24['agence'] = df_bank_t24['agence'].str.upper()
merged = df_biat.merge(df_bank_t24,on='agence',how='right')
df_biat = merged.merge(agence_lib,right_on="AGENCE CTOS",left_on="Code Ag",how="right")




final_scraped_data = pd.read_csv(r'app\base_prospection\Data\final_data_delegationV2.csv')
final_scraped_data.type.replace({"entreprise":"Entreprises"},inplace=True)
final_scraped_data = final_scraped_data[final_scraped_data.type != "Bank"]
final_scraped_data.reset_index(inplace=True,drop=True)



df_banks["agence"].replace({"BIAT BAB BHAR 21": "BIAT BAB BHAR 20"}, inplace=True)

gdf_all_banks = gpd.GeoDataFrame(df_banks, geometry=gpd.points_from_xy(df_banks.long, df_banks.lat))
gdf_delegation = gpd.read_file(os.path.join(os.path.dirname(__file__), 'Data', 'gdf_delegation.geojson'))



def register_callbacks_prospections(prospec):


    # Update Delegations
    @prospec.callback(
        dash.dependencies.Output('slct_delegat', 'options'),
        [dash.dependencies.Input('slct_city', 'value')])
    def set_delegations_options(slct_city):
        if slct_city:
            return [{'label': i, 'value': i} for i in gdf_delegation[gdf_delegation["gouvernorat"].isin(slct_city)]['delegation'].unique()]
        else:
            return ""

    # # Update Zone
    # @prospec.callback(
    #     dash.dependencies.Output('slct_zone', 'options'),
    #     [dash.dependencies.Input('slct_reg', 'value')])
    # def set_reg_options(slct_reg):
    #     if slct_reg:
    #         return [{'label': i, 'value': i} for i in agence_lib[agence_lib["REGION"] == slct_reg]['ZONE'].unique()]
    #     else:
    #         return ""

    # @prospec.callback(
    # #     Output('slct_city', 'options'),
    # #     Input('slct_city', 'value'),
    # #     State('slct_city', 'options')
    # # )
    # # def limit_selection(selected_values, options):
    # #     # Disable the options that have already been selected
    # #     for option in options:
    # #         if option['value'] in selected_values:
    # #             option['disabled'] = True
    # #         else:
    # #             option['disabled'] = False
    # #     # Limit the maximum number of selections to 4
    # #     if len(selected_values) >= 4:
    # #         for option in options:
    # #             if option['value'] not in selected_values:
    # #                 option['disabled'] = True
    # #     return options
    
    # @prospec.callback(
    # Output('slct_city', 'disabled'),
    # Input('slct_reg', 'value')
    # )
    # def update_dropdown(disabled):
    #     print(disabled)
    #     if disabled :
    #         return True
    #     else:
    #         return False
 
    @prospec.callback(
        Output(component_id='second_graph', component_property='figure'),
        Output(component_id='stat_graph', component_property='figure'),
        Output("download-dataframe-csv", "data"),
        Output(component_id='export-data', component_property='n_clicks'),
        [Input(component_id='slct_city', component_property='value'),
        Input(component_id='slct_delegat', component_property='value'),
        Input(component_id='export-data', component_property='n_clicks')
        ]
    )  
    def update_graph(slct_city, slct_delegat, n_clicks):
        # if city & delegation selected
        if (slct_city and slct_delegat):
            fig1 = go.Figure()    
            fig2 = go.Figure()
            bank_data = gdf_all_banks[gdf_all_banks["delegation"].isin(slct_delegat)]
            stat_data = final_scraped_data[(final_scraped_data["gouvernorat"].isin(slct_city)) & \
               (final_scraped_data["delegation"].isin(slct_delegat)) ]
            if stat_data.shape[0] > 0 :
                file_name = ("_").join(list(stat_data['gouvernorat'].unique()))
                file_name += "_" + ("_").join(list(stat_data['delegation'].unique()))
                colors=sns.color_palette("dark:#33eadc",n_colors=len(stat_data["delegation"].unique())).as_hex()
                colordict = {f:colors[i] for i, f in enumerate(stat_data["delegation"].unique())}
                colordict[stat_data["delegation"].unique()[0]] = "#254676"
                
                for i in range(len(stat_data.delegation.unique())):     
                    fig2.add_trace(
                        go.Bar(
                            x=stat_data[stat_data['delegation']==stat_data.delegation.unique()[i]]['type'].value_counts().keys(),
                            y=stat_data[stat_data['delegation']==stat_data.delegation.unique()[i]]['type'].value_counts().values,
                            name=stat_data.delegation.unique()[i],marker_color=colordict[stat_data.delegation.unique()[i]], marker_line_color=colordict[stat_data.delegation.unique()[i]],
                            text=stat_data[stat_data['delegation']==stat_data.delegation.unique()[i]]['type'].value_counts().values, textposition='auto',
                        ))
                fig2.update_traces(marker_line_width=1.5,hoverinfo='skip')
                fig2.update_layout(barmode='group',template="plotly_white",title="Nombre de Prospects par Secteur D’activité - {}".format("_".join(list(stat_data['delegation'].unique()))),xaxis_title="Secteur D’activité",
                    yaxis_title="Nombre de Prospects",title_x=0.5) 

                if bank_data.shape[0]>0 :
                    for i in range(len(bank_data.delegation.unique())):
                        fig1.add_trace(
                            go.Bar(
                                x=bank_data[bank_data['delegation']==bank_data.delegation.unique()[i]]['banque'].value_counts().keys(),
                                y=bank_data[bank_data['delegation']==bank_data.delegation.unique()[i]]['banque'].value_counts().values,
                                name=bank_data.delegation.unique()[i],marker_color=colordict[bank_data.delegation.unique()[i]], marker_line_color=colordict[bank_data.delegation.unique()[i]],
                                text=bank_data[bank_data['delegation']==bank_data.delegation.unique()[i]]['banque'].value_counts().values,
                            ))   
                    fig1.update_traces(marker_line_width=1.5,textposition='auto',hoverinfo='skip',hovertemplate = None)
                    fig1.update_layout(barmode='group',template="plotly_white",title="Nombre de Prospects par Secteur D’activité - {}".format("_".join(list(stat_data['delegation'].unique()))),xaxis_title="Secteur D’activité",
                        yaxis_title="Nombre de Prospects",title_x=0.5)
                    
                     

                    if n_clicks  :
                        return fig1,fig2,dcc.send_data_frame(stat_data.to_excel, "Data_"+file_name+".xlsx"),0
                    return fig1,fig2,"",0

                if bank_data.shape[0]==0 : 
                    fig = px.bar(                      
                        x=[],
                        y=[],
                        title="Aucune donnée à afficher",
                        labels=dict(x="Banque", y="Nombre d'agences"))
                    fig.update_traces(marker_color='#254676', marker_line_color='#254676',
                            marker_line_width=1.5)
                    fig.update_layout(template="plotly_white")

                    if n_clicks  :
                        return fig,fig2,dcc.send_data_frame(stat_data.to_excel, "Data_"+file_name+".xlsx"),0
            else :
                   
                fig2.add_trace(
                        go.Bar(
                            x=[],
                            y=[],
                    ))
                fig2.update_traces(marker_line_width=1.5)
                fig2.update_layout(barmode='group',template="plotly_white",title={'text':"Aucune donnée à afficher","x":0.5},xaxis_title="Secteur D’activité",
                    yaxis_title="Nombre de Prospects",)  
                fig2.update_layout(template="plotly_white",title_x=0.5) 
                if bank_data.shape[0]>0 :                 
                    fig = px.bar(
                        data_frame=bank_data,
                        x=bank_data['banque'].value_counts().keys(),
                        y=bank_data['banque'].value_counts().values,
                        title="Nombre des agences bancaires dans {}".format(
                            "_".join(stat_data["delegation"].unique())),
                        labels=dict(x="Banque", y="Nombre d'agences"))
                    fig.update_traces(marker_color='#254676', marker_line_color='#254676',
                            marker_line_width=1.5)
                    fig.update_layout(template="plotly_white")
                    return fig,fig2,"",0
                else : 
                    fig = px.bar(                      
                        x=[],
                        y=[],
                        title="Aucune donnée à afficher",
                        labels=dict(x="Banque", y="Nombre d'agences"))
                    fig.update_traces(marker_color='#254676', marker_line_color='#254676',
                            marker_line_width=1.5)
                    fig.update_layout(template="plotly_white")   
                    return fig,fig2,"",0
        
        # city selected
        if (slct_city  and not slct_delegat):
            
            fig1 = go.Figure() 
            fig2 = go.Figure()


            bank_data = gdf_all_banks[gdf_all_banks["gouvernorat"].isin(slct_city)]
            stat_data = final_scraped_data[(final_scraped_data["gouvernorat"].isin(slct_city))]
            df_pour = (stat_data.groupby(['gouvernorat'])['Cluster'].value_counts(normalize=True) * 100).to_frame().rename(columns={"Cluster":"Pourcentage"}).reset_index()
            df_pour['Pourcentage'] =( df_pour['Pourcentage'].round()).astype(int)
            colors=sns.color_palette("dark:#33eadc",n_colors=len(stat_data["gouvernorat"].unique())).as_hex()
            colordict = {f:colors[i] for i, f in enumerate(stat_data["gouvernorat"].unique())}
            colordict[stat_data["gouvernorat"].unique()[0]] = "#254676"


            for i in range(len(bank_data.gouvernorat.unique())):
                fig1.add_trace(
                    go.Bar(
                        x=bank_data[bank_data['gouvernorat']==bank_data.gouvernorat.unique()[i]]['banque'].value_counts().keys(),
                        y=bank_data[bank_data['gouvernorat']==bank_data.gouvernorat.unique()[i]]['banque'].value_counts().values,
                        marker_color=colordict[bank_data.gouvernorat.unique()[i]], marker_line_color=colordict[bank_data.gouvernorat.unique()[i]],
                        text=bank_data[bank_data['gouvernorat']==bank_data.gouvernorat.unique()[i]]['banque'].value_counts().values,
                        textposition='auto',
                        name = bank_data["gouvernorat"].unique()[i]
                    ))
                

            for i in range(len(stat_data.gouvernorat.unique())):
                # text_data = df_pour[df_pour['gouvernorat']==stat_data.gouvernorat.unique()[i]]['Pourcentage'].values
                # text_data = [f'{val}%' for val in text_data]

                fig2.add_trace(
                    go.Bar(
                        x=stat_data[stat_data['gouvernorat']==stat_data.gouvernorat.unique()[i]]['Cluster'].value_counts().keys(),
                        y=stat_data[stat_data['gouvernorat']==stat_data.gouvernorat.unique()[i]]['Cluster'].value_counts().values,
                        name = stat_data["gouvernorat"].unique()[i],marker_color=colordict[stat_data.gouvernorat.unique()[i]], marker_line_color=colordict[stat_data.gouvernorat.unique()[i]],
                        text=stat_data[stat_data['gouvernorat']==stat_data.gouvernorat.unique()[i]]['Cluster'].value_counts().values ,\
                             textposition='auto',hovertemplate='%{y}'
                    ))
            fig1.update_traces(marker_line_width=1.5,hoverinfo='skip')
            fig1.update_layout(barmode='group',template="plotly_white",title="Nombre Total des Agences par Banque - {}".format("_".join(slct_city)),xaxis_title="Banque",
                yaxis_title="Nombre d'agences",title_x=0.5)                         
            
            fig2.update_traces(marker_line_width=1.5,hoverinfo="text")
            fig2.update_layout(barmode='group',template="plotly_white",title="Nombre de Prospects par Secteur D’activité - {}".format("_".join(slct_city)),xaxis_title="Secteur D’activité",
                yaxis_title="Nombre de Prospects",title_x=0.5) 
            

            
            file_name = ("_").join(slct_city)

            if n_clicks  :
                return fig1,fig2,dcc.send_data_frame(stat_data.to_excel, "Data_"+file_name+".xlsx"),0
               
            return fig1,fig2,"",0


        else:
            text_data = (final_scraped_data['Cluster'].value_counts(normalize=True) * 100)
            final_scraped_data["Pourcentage"] = final_scraped_data['Cluster'].map(text_data).round().astype(int)
            fig2 = px.bar(
                data_frame=final_scraped_data,
                x=final_scraped_data['Cluster'].value_counts().keys(),
                y=final_scraped_data['Cluster'].value_counts().values,
                text=final_scraped_data['Cluster'].value_counts().values, 
                title="Nombre de Prospects par Secteur D’activité - Ensemble du Territoire Tunisien",
                labels=dict(x="Secteur D’activité", y="Nombre de Prospects"))

        
            fig = px.bar(
                data_frame=gdf_all_banks,
                x=gdf_all_banks['banque'].value_counts().keys(),
                y=gdf_all_banks['banque'].value_counts().values,
                title="Nombre Total des Agences par Banque - Ensemble du Territoire Tunisien",
                labels=dict(x="Banque",y="Nombre d'agences"),
                text=gdf_all_banks['banque'].value_counts().values,
                )
   
            fig.update_traces(marker_color='#254676', marker_line_color='#254676',
                    marker_line_width=1.5,textposition='auto',hoverinfo='skip',hovertemplate = None )
            fig2.update_traces(marker_color='#254676', marker_line_color='#254676',
                    marker_line_width=1.5,hoverinfo='skip',hovertemplate = None )  
            fig.update_layout(template="plotly_white",title_x=0.5)
            fig2.update_layout(template="plotly_white",title_x=0.5)


            if n_clicks  :
                return fig,fig2,dcc.send_data_frame(final_scraped_data.to_excel, "All_GeoData.xlsx"),0
            
           
            return fig,fig2,"",0

     