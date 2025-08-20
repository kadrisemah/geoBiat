from dash.dependencies import Input, Output, State 
import plotly.express as px  
import plotly.io as pio
import plotly.graph_objs as go
import dash
import pandas as pd 
import seaborn as sns
from dash import dcc 
from .functions import *
from dash import html
import random
import time

data = pd.read_excel(r'app\socio_demo\Data\Base EXCEL__BESOIN IA (18-11-22).xlsx')
data.loc[data["B7-Identification chef de famille"] == "Non", 'B7-Identification chef de famille'] = data.loc[data["B7-Identification chef de famille"] == "Non", 'G7-Profession du chef de famille']
data.loc[data["B7-Identification chef de famille"] == "Oui", 'B7-Identification chef de famille'] = data.loc[data["B7-Identification chef de famille"] == "Oui", 'G3-Profession du répondant']
pond = pd.read_excel(r'app\socio_demo\Data\Colonne pondération-Base totale.xlsx')
data = data.merge(pond,on="ID")
data['A7- Urbain/ Rural'].replace({'Une zone urbaine': 'Zone urbaine', 'Une zone rurale': 'Zone rurale'}, inplace=True)




def  register_callbacks_socio_demo(socio_demo):

    @socio_demo.callback(
        Output('slct_gouv', 'options'),
        Input('slct_gouv', 'value'),
        State('slct_gouv', 'options')
    )
    def limit_selection(selected_values, options):
        # Disable the options that have already been selected
        for option in options:
            if option['value'] in selected_values:
                option['disabled'] = True
            else:
                option['disabled'] = False
        # Limit the maximum number of selections to 4
        if len(selected_values) >= 3:
            for option in options:
                if option['value'] not in selected_values:
                    option['disabled'] = True
        return options

    @socio_demo.callback(
        Output('fig_genre', 'figure'),
        Output('fig_age', 'figure'),
        Output('fig_region', 'figure'),
        Output('fig_gouv', 'figure'),
        Output("download-dataframe-csv", "data"),
        Output(component_id='export-data', component_property='n_clicks'),
        [Input('slct_gouv', 'value'),
        Input(component_id='export-data', component_property='n_clicks')])
    def generate_default_graph(slct_gouv, export_input):
        exported_data = ""
        if slct_gouv == None :
            slct_gouv = []
        
        if  len(slct_gouv) != 0  :
                                        ################# "Gender Figure" #################
            data_gouv = data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)]
            genre_gouv = (data_gouv.groupby(["A3- Genre du répondant","A5-Gouvernorat d'habitation"])["ID"].count()/data_gouv.groupby(["A5-Gouvernorat d'habitation"])["ID"].count()*100).to_frame().reset_index()
            genre_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            genre_gouv['Pondération']= genre_gouv['Pondération'].round()
            genre_total = (data.groupby(["A3- Genre du répondant"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            genre_total['Pondération']= genre_total['Pondération'].round()
            genre_total["A5-Gouvernorat d'habitation"] = 'Total'
            genre_gouv = pd.concat([genre_total,genre_gouv])
            genre_gouv.reset_index(inplace=True,drop=True)
            genre_gouv['Color'] = genre_gouv.apply(lambda row: "#69645F" if (row['A3- Genre du répondant']=='Femme' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#4B4845" if (row['A3- Genre du répondant']=='Homme' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                    else ("#3484b6" if (row['A3- Genre du répondant']=='Homme') \
                        else "#b86a38")),axis=1)
            fig_genre = px.bar(genre_gouv, x="A5-Gouvernorat d'habitation", y="Pondération",
             width=500, height=468,template="plotly_white")
            fig_genre.update_layout(xaxis_title='',font=dict(),title="Genre",title_x=0.5,barmode='stack')
            fig_genre.update_yaxes(visible=False)
            fig_genre.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                    marker_color=genre_gouv["Color"],customdata=genre_gouv["A3- Genre du répondant"])
            fig_genre.update_traces(hovertemplate="%{customdata} : %{y} %")
            genre_gouv["type"] = "Genre du répondant"
            genre_gouv["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            genre_gouv.rename(columns={"A3- Genre du répondant":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)

                                        ################## "Age Figure" ####################
            age_gouv_data = (data_gouv.groupby(["A4- Tanche d'âge","A5-Gouvernorat d'habitation"])["ID"].count()/data_gouv.groupby(["A5-Gouvernorat d'habitation"])["ID"].count()*100).to_frame().reset_index()
            age_gouv_data.rename(columns={"ID":"Pondération"},inplace=True) 
            age_gouv_data['Pondération']= age_gouv_data['Pondération'].round()
            age_total = (data.groupby(["A4- Tanche d'âge"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            age_total['Pondération']= age_total['Pondération'].round()
            age_total["A5-Gouvernorat d'habitation"] = 'Total'
            age_gouv_data = pd.concat([age_total,age_gouv_data])
            age_gouv_data.reset_index(inplace=True,drop=True)
            age_gouv_data['Color'] = age_gouv_data.apply(lambda row: "#98918B" if (row["A4- Tanche d'âge"]=='18 à 29 ans' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#69645F" if (row["A4- Tanche d'âge"]=='30 à 39 ans' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                    else ("#4B4845" if (row["A4- Tanche d'âge"]=='40 à 49 ans' and row["A5-Gouvernorat d'habitation"] == 'Total') \
                        else ("#161514" if (row["A4- Tanche d'âge"]=='50 ans et plus' and row["A5-Gouvernorat d'habitation"] == 'Total')
                            else ("#79BDD6" if (row["A4- Tanche d'âge"]=='18 à 29 ans') \
                                else ("#3785AF" if (row["A4- Tanche d'âge"]=='30 à 39 ans') \
                                    else ("#254676" if (row["A4- Tanche d'âge"]=='40 à 49 ans') \
                        else "#212949")))))),axis=1)
            fig_age = px.bar(age_gouv_data, x="A5-Gouvernorat d'habitation", y="Pondération",
             width=600, height=468,template="plotly_white")
            fig_age.update_layout(xaxis_title='',font=dict(),title="Age",title_x=0.5,barmode='stack')
            fig_age.update_yaxes(visible=False)
            fig_age.update_traces(textfont_size=16, textangle=0, textposition="auto",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                    marker_color=age_gouv_data["Color"],customdata=age_gouv_data["A4- Tanche d'âge"])
            fig_age.update_traces(hovertemplate="%{customdata} : %{y} %")
            age_gouv_data["type"] = "Tanche d'âge"
            age_gouv_data["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            age_gouv_data.rename(columns={"A4- Tanche d'âge":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)

                                        ################## "Region Figure" ####################

            region_gouv = (data_gouv.groupby(["A7- Urbain/ Rural","A5-Gouvernorat d'habitation"])["ID"].count()/data_gouv.groupby(["A5-Gouvernorat d'habitation"])["ID"].count()*100).to_frame().reset_index()
            region_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            region_gouv['Pondération']= region_gouv['Pondération'].round()
            region_total = (data.groupby(["A7- Urbain/ Rural"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            region_total['Pondération']= region_total['Pondération'].round()
            region_total["A5-Gouvernorat d'habitation"] = 'Total'
            region_gouv = pd.concat([region_total,region_gouv])
            region_gouv.reset_index(inplace=True,drop=True)
            region_gouv['Color'] = region_gouv.apply(lambda row: "#4B4845" if (row['A7- Urbain/ Rural']=='Zone urbaine' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#69645F" if (row['A7- Urbain/ Rural']=='Zone rurale' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                    else ("#212949" if (row['A7- Urbain/ Rural']=='Zone urbaine') \
                        else "#3785AF")),axis=1)
            fig_region = px.bar(region_gouv, x="A5-Gouvernorat d'habitation", y="Pondération",
             width=580, height=468,template="plotly_white")
            fig_region.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Type de Région",title_x=0.5,barmode='stack')
            fig_region.update_traces(textfont_size=16, textangle=0, textposition="auto",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                    marker_color=region_gouv["Color"],customdata=region_gouv["A7- Urbain/ Rural"])
            fig_region.update_yaxes(visible=False)
            fig_region.update_traces(hovertemplate="%{customdata} : %{y} %")
            region_gouv["type"] = "Type de Région"
            region_gouv["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            region_gouv.rename(columns={"A7- Urbain/ Rural":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)


                                        ################## "Gouvernorat Figure" ####################
            gouv = (data.groupby(["A5-Gouvernorat d'habitation"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            gouv['Pondération']= gouv['Pondération'].round()
            gouv = gouv.sort_values(by='Pondération', ascending=False)
            colordict_gouv = {f:"#3785AF" if f not in slct_gouv else "#4B4845" for i, f in enumerate(gouv["A5-Gouvernorat d'habitation"].unique())}
            fig_gouv = px.bar(gouv, x="A5-Gouvernorat d'habitation", y="Pondération",color = "A5-Gouvernorat d'habitation",\
                        width=850, height=480,template="plotly_white",color_discrete_map=colordict_gouv)
            fig_gouv.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),xaxis={'categoryorder':'array'},title="Gouvernorat",title_x=0.5)
            fig_gouv.update_traces(textfont_size=14, textangle=0, textposition="outside",texttemplate='<span style="color:black">%{y:f}%</span>',hoverinfo='skip',hovertemplate = None )
            fig_gouv.update_yaxes(visible=False)
            fig_gouv.update_xaxes(tickangle=45)
            
            exported_data_socio_gouv = pd.concat([genre_gouv,age_gouv_data,region_gouv])
            exported_data_socio_gouv.reset_index(inplace=True,drop=True)
            exported_data_socio_gouv.drop("Color",axis=1,inplace=True)


    
        else :
            category_gender_order = ["Homme","Femme"]
            category_zone_order = ["Zone urbaine","Zone rurale"]



                                        ################# "Gender Figure" #################
            genre = (data.groupby(["A3- Genre du répondant"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            genre['Pondération']= genre['Pondération'].round()
            colors_genre = {"Femme":'#b86a38', "Homme":'#3484b6'}
            fig_genre = px.bar(genre, x="A3- Genre du répondant", y="Pondération",color = "A3- Genre du répondant",color_discrete_map=colors_genre,\
                        width=480, height=450,template="plotly_white",category_orders={"A3- Genre du répondant": category_gender_order})
            fig_genre.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Genre",title_x=0.5)
            fig_genre.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{y}%</span>',hoverinfo='skip',hovertemplate = None )
            fig_genre.update_yaxes(visible=False)

                                        ################## "Age Figure" ####################
            age = (data.groupby(["A4- Tanche d'âge"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            age['Pondération']= age['Pondération'].round()
            colordict_age = {'18 à 29 ans': '#79BDD6','30 à 39 ans': '#3785AF','40 à 49 ans': '#254676','50 ans et plus': '#212949'}
            fig_age = px.bar(age, x="A4- Tanche d'âge", y="Pondération",color = "A4- Tanche d'âge",color_discrete_map=colordict_age,\
                        width=480, height=450,template="plotly_white")
            fig_age.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Age",title_x=0.5)
            fig_age.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_age.update_yaxes(visible=False)


                                        ################## "Region Figure" ####################
            region = (data.groupby(["A7- Urbain/ Rural"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            region['Pondération']= region['Pondération'].round()
            colordict_region = {'Zone urbaine': '#212949','Zone rurale': '#3785AF'}
            fig_region = px.bar(region, x="A7- Urbain/ Rural", y="Pondération",color = "A7- Urbain/ Rural",color_discrete_map=colordict_region,\
                        width=480, height=450,template="plotly_white",category_orders={"A7- Urbain/ Rural": category_zone_order})
            fig_region.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Type de Région",title_x=0.5)
            fig_region.update_traces(textfont_size=14, textposition="inside",texttemplate='<span style="color:white">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_region.update_yaxes(visible=False)

                                        ################## "Gouvernorat Figure" ####################
            gouv = (data.groupby(["A5-Gouvernorat d'habitation"])["Pondération"].sum()/data["Pondération"].sum()*100).to_frame().reset_index()
            gouv['Pondération']= gouv['Pondération'].round()
            gouv = gouv.sort_values(by='Pondération', ascending=False)
            colordict_gouv = {f:"#3785AF" for i, f in enumerate(gouv["A5-Gouvernorat d'habitation"].unique())}
            fig_gouv = px.bar(gouv, x="A5-Gouvernorat d'habitation", y="Pondération",color = "A5-Gouvernorat d'habitation",\
                        width=850, height=450,template="plotly_white",color_discrete_map=colordict_gouv)
            fig_gouv.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),xaxis={'categoryorder':'array'},title="Gouvernorat",title_x=0.5)
            fig_gouv.update_traces(textfont_size=14, textposition="outside",texttemplate='<span style="color:black">%{y:f}%</span>',hoverinfo='skip',hovertemplate = None )
            fig_gouv.update_yaxes(visible=False)
            fig_gouv.update_xaxes(tickangle=45)


            genre['type'] = "Tanche d'âge"
            age['type'] = "Tanche d'âge"
            region['type'] = "Type de Région"
            genre["Gouvernorat"] = "Ensemble du Territoire Tunisien"
            age["Gouvernorat"] = "Ensemble du Territoire Tunisien"
            region["Gouvernorat"] = "Ensemble du Territoire Tunisien"
            region.rename(columns={"A7- Urbain/ Rural":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            age.rename(columns={"A4- Tanche d'âge":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            genre.rename(columns={"A3- Genre du répondant":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            exported_data_socio_total = pd.concat([genre,age,region])
            exported_data_socio_total.reset_index(inplace=True,drop=True)
        if export_input and not slct_gouv : 
            exported_data = dcc.send_data_frame(exported_data_socio_total.to_excel, "Socio_demo_Ensemble_Territoire.xlsx")
        if export_input and slct_gouv :
            file_name = ("_").join(slct_gouv)
            exported_data = dcc.send_data_frame(exported_data_socio_gouv.to_excel, "Socio_demo_"+file_name+".xlsx")
        return fig_genre,fig_age,fig_region,fig_gouv,exported_data, 0


    

    # # Update Delegations
    # @socio_demo.callback(
    #     Output('container', 'children'),
    #     [Input('slct_gouv', 'value'),
    #     Input('slct_domain', 'value'),])
    # def generate_graphs(slct_gouv,slct_domain):
    #     graphs = []
    #     list_del_col = []
    #     if(not slct_gouv and slct_domain):
    #         df = filter_data(data,NDT,slct_domain)
    #         ds = handleAutreColumns(df)
    #         for c in ds.columns:
    #             if 'autre' in c.lower() or 'refuse' in c.lower() :
    #                 list_del_col.append(c)
    #         ds.drop(list_del_col,axis=1,inplace=True) 
    #         dict_code_plots = extract_base_data(NDT,ds,slct_domain)
    #         list_figure = sub_plot_all_tunisie(ds,dict_code_plots,slct_domain)
    #         for fig in range(len(list_figure)) :
    #             graphs.extend([dcc.Graph(
    #                 id='graph-{}'.format(fig),
    #                 figure=list_figure[fig]
    #             ),html.Hr(style={"margin-top": "0.03rem",
    #                               "margin-bottom" : "0.03rem",
    #                                "border-width": "0",
    #                                 "border-top-width": "0px",
    #                                 "border-top": "0.5px solid #c6bebe"})])
    #         return html.Div(graphs)
    #     graphs = []
    #     if(slct_gouv and slct_domain):
    #         df = filter_data(data,NDT,slct_domain)
    #         ds = handleAutreColumns(df)
    #         dict_code_plots = extract_base_data(NDT,ds,slct_domain)
    #         list_figure = sub_plot_gouv(ds,dict_code_plots,slct_domain,slct_gouv)
    #         for fig in range(len(list_figure)) :
    #             graphs.extend([dcc.Graph(
    #                 id='graph-{}'.format(fig),
    #                 figure=list_figure[fig]
    #             ),html.Hr(style={"margin-top": "0.03rem",
    #                               "margin-bottom" : "0.03rem",
    #                                "border-width": "0",
    #                                 "border-top-width": "0px",
    #                                 "border-top": "0.5px solid #c6bebe"})])
    #         return html.Div(graphs)
        
    #     if ((slct_gouv or not slct_gouv) and not slct_domain):
    #         graphs.append(dcc.Graph(
    #                             id='graph-init',
    #                             figure={
    #                                 'data': [],
    #                                 'layout': {
    #                                     'title': '<b>No Data to Display, Please select a Domain</b>',
    #                                     "title_x":"0.5",
    #                                     "template":"plotly_white"
    #                                 }
    #                             }
    #                         ))
    #         return html.Div(graphs)

 
        


        
