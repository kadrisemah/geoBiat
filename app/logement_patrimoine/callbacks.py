from dash.dependencies import Input, Output, State 
import plotly.express as px  
import plotly.io as pio
import plotly.graph_objs as go
import dash
import pandas as pd 
import seaborn as sns
from dash import dcc 
from dash import html
import random

data = pd.read_excel(r'app\socio_demo\Data\Base EXCEL__BESOIN IA (18-11-22).xlsx')
data.loc[data["B7-Identification chef de famille"] == "Non", 'B7-Identification chef de famille'] = data.loc[data["B7-Identification chef de famille"] == "Non", 'G7-Profession du chef de famille']
data.loc[data["B7-Identification chef de famille"] == "Oui", 'B7-Identification chef de famille'] = data.loc[data["B7-Identification chef de famille"] == "Oui", 'G3-Profession du répondant']

pond = pd.read_excel(r'app\socio_demo\Data\Colonne pondération-Base totale.xlsx')

data = data.merge(pond,on="ID")
data['A7- Urbain/ Rural'].replace({'Une zone urbaine': 'Zone urbaine', 'Une zone rurale': 'Zone rurale'}, inplace=True)




def  register_callbacks_logement_patrimoine(log_patri):

    @log_patri.callback(
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

    @log_patri.callback(
        Output('fig_logement', 'figure'),
        Output('fig_voiture', 'figure'),
        Output('fig_internet', 'figure'),
        Output('fig_mobile', 'figure'),
        Output('fig_mobile',"style"),
        Output("download-dataframe-csv", "data"),
        Output(component_id='export-data', component_property='n_clicks'),
        [Input('slct_gouv', 'value'),
        Input(component_id='export-data', component_property='n_clicks')])
    def generate_default_graph(slct_gouv, export_input):

        style_mob = {}

        logement = data.drop(data[data['C3- Type de logement'] == 'Refuse de répondre'].index)
        voiture = data.drop(data[data["C9-Possession d'une voiture"] == 'Refuse de répondre'].index)
        internet = data.drop(data[(data['D2-Accès à Internet à domicile'] == 'Refuse de répondre') | (data['D2-Accès à Internet à domicile'] == 'Nsp') ].index)
    
        logement = (logement.groupby('C3- Type de logement')['Pondération'].sum()/logement['Pondération'].sum()*100).to_frame().reset_index()
        logement['Pondération'] = logement['Pondération'].round().astype(int)
        logement['C3- Type de logement'].replace({"Propriétaire de votre logement":"Propriétaire","Logé gratuitement (par exemple maison de fonction…)":"Logé gratuitement"},inplace=True)
        logement["A5-Gouvernorat d'habitation"] = "Total"

        mobile_tot = data.filter(regex=('^D5|Pond|A5'))
        mobile_ordinaire_tot = mobile_tot[["D5-Possession téléphone mobile- Téléphone mobile ordinaire ","Pondération","A5-Gouvernorat d'habitation"]]
        smartphone_tot = mobile_tot[["D5-Possession téléphone mobile- Un Smartphone","Pondération","A5-Gouvernorat d'habitation"]]
        mobile_ordinaire_pour_tot = (mobile_ordinaire_tot.groupby(["D5-Possession téléphone mobile- Téléphone mobile ordinaire "])['Pondération'].sum()/data['Pondération'].sum()*100).reset_index()
        smartphone_pour_tot = (smartphone_tot.groupby(["D5-Possession téléphone mobile- Un Smartphone"])['Pondération'].sum()/data['Pondération'].sum()*100).reset_index()
        mobile_ordinaire_pour_tot['type'] = 'Mobile ordinaire'
        smartphone_pour_tot['type'] = 'Smartphone'
        smartphone_pour_tot["A5-Gouvernorat d'habitation"] = 'Total'
        mobile_ordinaire_pour_tot["A5-Gouvernorat d'habitation"] = 'Total'
        smartphone_pour_tot.rename(columns={"D5-Possession téléphone mobile- Un Smartphone":"Réponse"},inplace=True)
        mobile_ordinaire_pour_tot.rename(columns={"D5-Possession téléphone mobile- Téléphone mobile ordinaire ":"Réponse"},inplace=True)
        mobile_tot = pd.concat([mobile_ordinaire_pour_tot,smartphone_pour_tot])
        mobile_tot['Pondération'] = mobile_tot['Pondération'].round().astype(int)

        voiture = (voiture.groupby("C9-Possession d'une voiture")['Pondération'].sum()/voiture['Pondération'].sum()*100).to_frame().reset_index()
        voiture['Pondération'] = voiture['Pondération'].round().astype(int) 
        voiture["C9-Possession d'une voiture"].replace({"Oui, une voiture de fonction":"Voiture de fonction","Oui, une voiture personelle":"Voiture personelle"},inplace=True)
        voiture["A5-Gouvernorat d'habitation"] = "Total"

        internet = (internet.groupby('D2-Accès à Internet à domicile')['Pondération'].sum()/internet['Pondération'].sum()*100).to_frame().reset_index()
        internet["Pondération"] = internet["Pondération"].round().astype(int)
        internet["A5-Gouvernorat d'habitation"] = "Total"


        
        exported_data = ""

        if slct_gouv == None :
            slct_gouv = []
        
        if  len(slct_gouv) != 0  :
            
                                        ################# "logement Figure" #################
            logement_gouv = (data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(['C3- Type de logement',"A5-Gouvernorat d'habitation"])['ID'].count()/ \
            data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(['C3- Type de logement',"A5-Gouvernorat d'habitation"])['ID'].count().groupby("A5-Gouvernorat d'habitation").sum()*100).to_frame().reset_index()
            logement_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            logement_gouv['Pondération']= logement_gouv['Pondération'].round().astype(int)
            logement_gouv['C3- Type de logement'].replace({"Propriétaire de votre logement":"Propriétaire","Logé gratuitement (par exemple maison de fonction…)":"Logé gratuitement"},inplace=True)

            logement_gouv = pd.concat([logement,logement_gouv])
            logement_gouv.reset_index(inplace=True,drop=True)


            logement_gouv['Color'] = logement_gouv.apply(lambda row: "#98918B" if (row["C3- Type de logement"]=='Locataire' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#69645F" if (row["C3- Type de logement"]=='Logé gratuitement' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                    else ("#4B4845" if (row["C3- Type de logement"]=='Propriétaire' and row["A5-Gouvernorat d'habitation"] == 'Total') \
                                else ("#79BDD6" if (row["C3- Type de logement"]=='Locataire') \
                                    else ("#254676" if (row["C3- Type de logement"]=='Propriétaire') \
                        else "#212949")))),axis=1)

            fig_logement = px.bar(logement_gouv, x="A5-Gouvernorat d'habitation", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_logement.update_traces(textfont_size=16, textangle=0, textposition="auto",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=logement_gouv["Color"],customdata=logement_gouv["C3- Type de logement"])


            fig_logement.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Condition de Logement",title_x=0.5,barmode='stack')
            fig_logement.update_yaxes(visible=False)
            fig_logement.update_traces(hovertemplate="%{customdata} : %{y} %")
            logement_gouv['type'] = "Type de logement"
            logement_gouv["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            logement_gouv.rename(columns={"C3- Type de logement":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            

                                        ################## "Voiture Figure" ####################
            voiture_gouv = (data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(["C9-Possession d'une voiture","A5-Gouvernorat d'habitation"])['ID'].count()/ \
            data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(["C9-Possession d'une voiture","A5-Gouvernorat d'habitation"])['ID'].count().groupby("A5-Gouvernorat d'habitation").sum()*100).to_frame().reset_index()
            voiture_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            voiture_gouv['Pondération']= voiture_gouv['Pondération'].round().astype(int)
            voiture_gouv = pd.concat([voiture,voiture_gouv])
            voiture_gouv.reset_index(inplace=True,drop=True)
            voiture_gouv["C9-Possession d'une voiture"].replace({"Oui, une voiture de fonction":"Voiture de fonction","Oui, une voiture personelle":"Voiture personelle"},inplace=True)


            voiture_gouv['Color'] = voiture_gouv.apply(lambda row: "#98918B" if (row["C9-Possession d'une voiture"]=='Non' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#69645F" if (row["C9-Possession d'une voiture"]=='Voiture de fonction' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                    else ("#4B4845" if (row["C9-Possession d'une voiture"]=='Voiture personelle' and row["A5-Gouvernorat d'habitation"] == 'Total') \
                                else ("#161514" if (row["C9-Possession d'une voiture"]=='Voiture de fonction') \
                                    else ("#79BDD6" if (row["C9-Possession d'une voiture"]=='Voiture personelle') \
                        else "#b86a38")))),axis=1)

            fig_voiture = px.bar(voiture_gouv, x="A5-Gouvernorat d'habitation", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_voiture.update_traces(textfont_size=16, textangle=0, textposition="auto",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=voiture_gouv["Color"],customdata=voiture_gouv["C9-Possession d'une voiture"])


            fig_voiture.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Possession Voiture",title_x=0.5,barmode='stack')
            fig_voiture.update_yaxes(visible=False)
            fig_voiture.update_traces(hovertemplate="%{customdata} : %{y} %")
            voiture_gouv['type'] = "Possession d'une voiture"
            voiture_gouv["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            voiture_gouv.rename(columns={"C9-Possession d'une voiture":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)


                                        ################## "Internet Figure" ####################
            Internet_gouv =(data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(["D2-Accès à Internet à domicile","A5-Gouvernorat d'habitation"])['ID'].count()/ \
            data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(["D2-Accès à Internet à domicile","A5-Gouvernorat d'habitation"])['ID'].count().groupby("A5-Gouvernorat d'habitation").sum()*100).to_frame().reset_index()
            Internet_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            Internet_gouv['Pondération']= Internet_gouv['Pondération'].round()
            Internet_gouv['Pondération'] = Internet_gouv['Pondération'].astype(int)
            Internet_gouv = pd.concat([internet,Internet_gouv])
            Internet_gouv.reset_index(inplace=True,drop=True)
            Internet_gouv['Color'] = Internet_gouv.apply(lambda row: "#98918B" if (row["D2-Accès à Internet à domicile"]=='Non' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#69645F" if (row["D2-Accès à Internet à domicile"]=='Oui' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                                else ("#3484b6" if (row["D2-Accès à Internet à domicile"]=='Oui') \
                        else "#b86a38")),axis=1)

            fig_internet = px.bar(Internet_gouv, x="A5-Gouvernorat d'habitation", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_internet.update_traces(textfont_size=16, textangle=0, textposition="auto",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=Internet_gouv["Color"],customdata=Internet_gouv["D2-Accès à Internet à domicile"])


            fig_internet.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Accès Internet à Domicile",title_x=0.5,barmode='stack')
            fig_internet.update_yaxes(visible=False)
            fig_internet.update_traces(hovertemplate="%{customdata} : %{y} %")
            Internet_gouv['type'] = "Accès à Internet à domicile"
            Internet_gouv["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            Internet_gouv.rename(columns={"D2-Accès à Internet à domicile":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)



                                        ################## "Mobile Figure" ####################
            style_mob = {"margin-left": "-9rem",
                        "margin-top": "-3rem"}
            df_mobile = data.filter(regex=('^D5|Pond|A5'))
            df_mobile = df_mobile[df_mobile["A5-Gouvernorat d'habitation"].isin(slct_gouv)]
            mobile_ordinaire = df_mobile[["D5-Possession téléphone mobile- Téléphone mobile ordinaire ","Pondération","A5-Gouvernorat d'habitation"]]
            smartphone = df_mobile[["D5-Possession téléphone mobile- Un Smartphone","Pondération","A5-Gouvernorat d'habitation"]]
            mobile_ordinaire_pour = (mobile_ordinaire.groupby(["D5-Possession téléphone mobile- Téléphone mobile ordinaire ","A5-Gouvernorat d'habitation"]).count()/mobile_ordinaire.groupby(["D5-Possession téléphone mobile- Téléphone mobile ordinaire ","A5-Gouvernorat d'habitation"]).count().groupby("A5-Gouvernorat d'habitation").sum()*100).reset_index()
            smartphone_pour = (smartphone.groupby(["D5-Possession téléphone mobile- Un Smartphone","A5-Gouvernorat d'habitation"]).count()/smartphone.groupby(["D5-Possession téléphone mobile- Un Smartphone","A5-Gouvernorat d'habitation"]).count().groupby("A5-Gouvernorat d'habitation").sum()*100).reset_index()
            mobile_ordinaire_pour['type'] = 'Mobile ordinaire'
            smartphone_pour['type'] = 'Smartphone'
            smartphone_pour.rename(columns={"D5-Possession téléphone mobile- Un Smartphone":"Réponse"},inplace=True)
            mobile_ordinaire_pour.rename(columns={"D5-Possession téléphone mobile- Téléphone mobile ordinaire ":"Réponse"},inplace=True)
            mobile = pd.concat([mobile_ordinaire_pour,smartphone_pour])

            df_plot_mobile = pd.concat([mobile_tot,mobile])
            df_plot_mobile['Pondération']=df_plot_mobile['Pondération'].round().astype(int)
            df_plot_mobile['Color'] = df_plot_mobile.apply(lambda row: "#69645F" if (row["Réponse"]=='Non' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                else ("#98918B" if (row["Réponse"]=='Oui' and row["A5-Gouvernorat d'habitation"] == 'Total')  \
                                else ("#3484b6" if (row["Réponse"]=='Oui' and row["A5-Gouvernorat d'habitation"] != 'Total') \
                        else "#b86a38")),axis=1)
            df_plot_mobile['type'] = df_plot_mobile['type'].str.replace('Mobile ordinaire', 'Mobile<br>Ordinaire')

            fig_mobile = go.Figure()

            fig_mobile.update_layout(
                template="simple_white",
                xaxis=dict(title_text=""),
                yaxis=dict(title_text=""),
                barmode="stack",
            )
            colors = df_plot_mobile['Color'].unique()
            for r, c in zip(df_plot_mobile["Réponse"].unique(), colors):
                plot_df = df_plot_mobile[df_plot_mobile["Réponse"] == r]
                fig_mobile.add_trace(
                    go.Bar(x=[plot_df["A5-Gouvernorat d'habitation"], plot_df["type"]], y=plot_df['Pondération'], name="", marker_color=plot_df['Color'],text=plot_df['Réponse']),
                )
                
                fig_mobile.update_traces(textfont_size=16, textangle=0, textposition="auto",texttemplate='<span style="color:white">%{text}<br>%{y}%</span>')

            fig_mobile.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Possession Mobile",title_x=0.5,width=700, height=500,)
            fig_mobile.update_yaxes(visible=False)
            fig_mobile.update_xaxes(tickfont=dict(size=12))
            fig_mobile.update_xaxes(tickangle=0)
            fig_mobile.update_traces(hovertemplate="%{x} - %{text} : %{y} %")
            df_plot_mobile["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            df_plot_mobile.rename(columns={"Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)

            exported_data_logement_gouv = pd.concat([logement_gouv,Internet_gouv,voiture_gouv,df_plot_mobile])
            exported_data_logement_gouv.reset_index(inplace=True,drop=True)
            exported_data_logement_gouv.drop("Color",axis=1,inplace=True)




        else :
            category_internet_order = ["Oui","Non"]
                                        ################# "logement Figure" #################
            colors_logement = {"Locataire":'#79BDD6', "Propriétaire":'#254676',"Logé gratuitement":"#212949"}
            fig_logement = px.bar(logement, x="C3- Type de logement", y="Pondération",color = "C3- Type de logement",color_discrete_map=colors_logement,\
                        width=480, height=450,template="plotly_white")
            fig_logement.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Condition de Logement",title_x=0.5)
            fig_logement.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_logement.update_yaxes(visible=False)

                                        ################## "Voiture Figure" ####################
            colors_voiture = {"Non":'#b86a38', "Voiture de fonction":'#161514',"Voiture personelle":"#79BDD6"}
            fig_voiture = px.bar(voiture, x="C9-Possession d'une voiture", y="Pondération",color = "C9-Possession d'une voiture",color_discrete_map=colors_voiture,\
                        width=480, height=450,template="plotly_white")
            fig_voiture.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Possession Voiture",title_x=0.5)
            fig_voiture.update_traces(textfont_size=14, textangle=0, textposition="auto",texttemplate='<span style="color:black">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_voiture.update_yaxes(visible=False)

                                        ################## "Internet Figure" ####################
            colors_internet = {"Non":'#b86a38', "Oui":'#3484b6'}
            fig_internet = px.bar(internet, x="D2-Accès à Internet à domicile", y="Pondération",color = "D2-Accès à Internet à domicile",color_discrete_map=colors_internet,\
                        width=480, height=450,template="plotly_white",category_orders={'D2-Accès à Internet à domicile': category_internet_order})
            fig_internet.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Accès Internet à Domicile",title_x=0.5)
            fig_internet.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_internet.update_yaxes(visible=False)

                                        ################## "Mobile Figure" ####################
            colors_mobile = {"Non":'#b86a38', "Oui":'#3484b6'}
            fig_mobile = px.bar(mobile_tot, x="type", y="Pondération",color = "Réponse",text="Réponse",color_discrete_map=colors_mobile,\
                        width=480, height=450,template="plotly_white")
            fig_mobile.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Possession Mobile",title_x=0.5)
            fig_mobile.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{text}<br>%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_mobile.update_yaxes(visible=False)
            internet['type'] = "Accès à Internet à domicile"
            voiture['type'] = "Possession d'une voiture"
            logement['type'] = "Type de logement"
            mobile_tot["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            internet["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            voiture["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            logement["A5-Gouvernorat d'habitation"].replace({'Total': "Ensemble du Territoire Tunisien"}, inplace=True)
            logement.rename(columns={"C3- Type de logement":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            voiture.rename(columns={"C9-Possession d'une voiture":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            internet.rename(columns={"D2-Accès à Internet à domicile":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            mobile_tot.rename(columns={"Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"},inplace=True)
            exported_data_logement_total = pd.concat([logement,internet,voiture,mobile_tot])
            exported_data_logement_total.reset_index(inplace=True,drop=True)


        if export_input and not slct_gouv : 
            exported_data = dcc.send_data_frame(exported_data_logement_total.to_excel, "logement_et_patrimoine_Ensemble_Territoire.xlsx")
        if export_input and slct_gouv :
            file_name = ("_").join(slct_gouv)
            exported_data = dcc.send_data_frame(exported_data_logement_gouv.to_excel, "logement_et_patrimoine_"+file_name+".xlsx")

        return fig_logement, fig_voiture, fig_internet, fig_mobile , style_mob, exported_data, 0


 
        


        
