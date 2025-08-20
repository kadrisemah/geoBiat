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

assurance = pd.read_csv(r'app\assurance\Data\assurance.csv')

def  register_callbacks_assurance(assurances):

    @assurances.callback(
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

    @assurances.callback(
        Output('fig_logement', 'figure'),
        Output('fig_voiture', 'figure'),
        Output('fig_sante', 'figure'),
        Output('fig_vie', 'figure'),
        Output("download-dataframe-csv", "data"),
        Output(component_id='export-data', component_property='n_clicks'),
        [Input('slct_gouv', 'value')],
        Input(component_id='export-data', component_property='n_clicks'))
    def generate_default_graph(slct_gouv,export_input):
        assurance_logement = (assurance.groupby('Assurance Logement')['Pondération'].sum()/assurance['Pondération'].sum()*100).to_frame()
        assurance_logement.reset_index(inplace=True)
        assurance_logement['Pondération'] = assurance_logement['Pondération'].round().astype(int) 
        assurance_logement["Gouvernorat"] = "Total"

        assurance['possession voiture'] = assurance['possession voiture'].replace({"Oui, une voiture personelle":"Oui","Oui, une voiture de fonction":"Oui"})
        assurance_voiture =  assurance.drop((assurance[assurance['possession voiture'] == 'Refuse de répondre']).index)
        assurance_voiture = (assurance_voiture.groupby('possession voiture')['Pondération'].sum()/assurance['Pondération'].sum()*100).to_frame()
        assurance_voiture.reset_index(inplace=True)
        assurance_voiture['Pondération'] = assurance_voiture['Pondération'].round().astype(int) 
        assurance_voiture["Gouvernorat"] = "Total"

        

        assurance_sante = (assurance.groupby('Assurance Sante')['Pondération'].sum()/assurance['Pondération'].sum()*100).to_frame()
        assurance_sante.reset_index(inplace=True)
        assurance_sante['Pondération'] = assurance_sante['Pondération'].round().astype(int) 
        assurance_sante["Gouvernorat"] = "Total"

        assurance_vie	 =  assurance.drop(assurance[assurance["Assurance Vie"] == 'Refuse de répondre'].index)
        assurance_vie = (assurance_vie.groupby('Assurance Vie')['Pondération'].sum()/assurance['Pondération'].sum()*100).to_frame()
        assurance_vie.reset_index(inplace=True)
        assurance_vie['Pondération'] = assurance_vie['Pondération'].round().astype(int) 
        assurance_vie["Gouvernorat"] = "Total"

        assurance_logement_exported = assurance_logement.rename(columns={"Assurance Logement":"Réponse","Pondération":"Pourcentage"})
        assurance_logement_exported["Type"] = "Assurance Logement"
        assurance_voiture_exported = assurance_voiture.rename(columns={"possession voiture":"Réponse","Pondération":"Pourcentage"})
        assurance_voiture_exported["Type"] = "Possession Voiture"
        assurance_sante_exported = assurance_sante.rename(columns={"Assurance Sante":"Réponse","Pondération":"Pourcentage"})
        assurance_sante_exported["Type"] = "Assurance Sante"
        assurance_vie_exported = assurance_vie.rename(columns={"Assurance Vie":"Réponse","Pondération":"Pourcentage"})
        assurance_vie_exported["Type"] = "Assurance Vie"
        assurance_total_exported = pd.concat([assurance_logement_exported,assurance_sante_exported,assurance_vie_exported,assurance_voiture_exported])
        assurance_total_exported["Gouvernorat"] = assurance_total_exported["Gouvernorat"].replace({"Total":"Ensemble du Territoire Tunisien"})
        exported_data = ""
        
        if slct_gouv == None :
            slct_gouv = []
        
        if  len(slct_gouv) != 0  :
            
                                        ################# "logement Figure" #################
            
            assurance_logement_gouv = (assurance[assurance["Gouvernorat"].isin(slct_gouv)].groupby(['Assurance Logement',"Gouvernorat"])['ID'].count()/ \
            assurance[assurance["Gouvernorat"].isin(slct_gouv)].groupby(['Assurance Logement',"Gouvernorat"])['ID'].count().groupby(['Gouvernorat']).sum()*100).to_frame().reset_index()
            assurance_logement_gouv['ID']= assurance_logement_gouv['ID'].round().astype(int)
            assurance_logement_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            assurance_logement_gouv_exported = assurance_logement_gouv.rename(columns={"Assurance Logement":"Réponse","Pondération":"Pourcentage"})
            assurance_logement_gouv_exported["Type"] = "Assurance Vie"
            assurance_to_log = pd.concat([assurance_logement,assurance_logement_gouv])
            assurance_to_log.reset_index(inplace=True,drop=True)
            assurance_to_log['Color'] = assurance_to_log.apply(lambda row: "#98918B" if (row["Assurance Logement"]=='Non' and row["Gouvernorat"] == 'Total')\
                    else ("#4B4845" if (row["Assurance Logement"]=='Oui' and row["Gouvernorat"] == 'Total') \
                        else ("#69645F" if (row["Assurance Logement"]=='NSP' and row["Gouvernorat"] == 'Total') \
                                    else ("#3484b6" if (row["Assurance Logement"]=='Oui') \
                                        else ("#4B4845" if (row["Assurance Logement"]=='NSP') \
                        else "#b86a38")))),axis=1)

            fig_ass_logement = px.bar(assurance_to_log, x="Gouvernorat", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_ass_logement.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=assurance_to_log["Color"],customdata=assurance_to_log["Assurance Logement"])


            fig_ass_logement.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(
                    ),title="Assurance Logement",title_x=0.5,barmode='stack')
            fig_ass_logement.update_yaxes(visible=False)
            fig_ass_logement.update_traces(hovertemplate="%{customdata} : %{y} %")

                                        ################# "Voiture Figure" #################

            assurance_voiture_gouv = (assurance[assurance["Gouvernorat"].isin(slct_gouv)].groupby(['possession voiture',"Gouvernorat"])['ID'].count()/ \
            assurance[assurance["Gouvernorat"].isin(slct_gouv)].groupby(['possession voiture',"Gouvernorat"])['ID'].count().groupby(['Gouvernorat']).sum()*100).to_frame().reset_index()
            assurance_voiture_gouv['ID']= assurance_voiture_gouv['ID'].round().astype(int)
            assurance_voiture_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            assurance_voiture_gouv_exported = assurance_voiture_gouv.rename(columns={"possession voiture":"Réponse","Pondération":"Pourcentage"})
            assurance_voiture_gouv_exported["Type"] = "Possession Voiture"

            assurance_tot_voiture = pd.concat([assurance_voiture,assurance_voiture_gouv])
            assurance_tot_voiture.reset_index(inplace=True,drop=True)
            assurance_tot_voiture['Color'] = assurance_tot_voiture.apply(lambda row: "#98918B" if (row["possession voiture"]=='Non' and row["Gouvernorat"] == 'Total')\
                    else ("#4B4845" if (row["possession voiture"]=='Oui' and row["Gouvernorat"] == 'Total') \
                                    else ("#3484b6" if (row["possession voiture"]=='Oui') \
                        else "#b86a38")),axis=1)

            fig_ass_voiture = px.bar(assurance_tot_voiture, x="Gouvernorat", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_ass_voiture.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=assurance_tot_voiture["Color"],customdata=assurance_tot_voiture["possession voiture"])


            fig_ass_voiture.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(
                    ),title="Assurance Voiture",title_x=0.5,barmode='stack')
            fig_ass_voiture.update_yaxes(visible=False)
            fig_ass_voiture.update_traces(hovertemplate="%{customdata} : %{y} %")

            
                                        ################# "Santé Figure" #################
            
            assurance_sante_gouv = (assurance[assurance["Gouvernorat"].isin(slct_gouv)].groupby(['Assurance Sante',"Gouvernorat"])['ID'].count()/ \
            assurance[assurance["Gouvernorat"].isin(slct_gouv)].groupby(['Assurance Sante',"Gouvernorat"])['ID'].count().groupby(['Gouvernorat']).sum()*100).to_frame().reset_index()
            assurance_sante_gouv['ID']= assurance_sante_gouv['ID'].round().astype(int)
            assurance_sante_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            assurance_sante_gouv_exported = assurance_sante_gouv.rename(columns={"Assurance Sante":"Réponse","Pondération":"Pourcentage"})
            assurance_sante_gouv_exported["Type"] = "Assurance Sante"
            assurance_tot_sante = pd.concat([assurance_sante,assurance_sante_gouv])
            assurance_tot_sante.reset_index(inplace=True,drop=True)
            assurance_tot_sante['Color'] = assurance_tot_sante.apply(lambda row: "#98918B" if (row["Assurance Sante"]=='Non' and row["Gouvernorat"] == 'Total')\
                    else ("#4B4845" if (row["Assurance Sante"]=='Oui' and row["Gouvernorat"] == 'Total') \
                        else ("#69645F" if (row["Assurance Sante"]=='NSP' and row["Gouvernorat"] == 'Total') \
                                    else ("#3484b6" if (row["Assurance Sante"]=='Oui') \
                                            else ("#4B4845" if (row["Assurance Sante"]=='NSP') \
                        else "#b86a38")))),axis=1)

            fig_ass_sante = px.bar(assurance_tot_sante, x="Gouvernorat", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_ass_sante.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=assurance_tot_sante["Color"],customdata=assurance_tot_sante["Assurance Sante"])


            fig_ass_sante.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(
                    ),title="Assurance Santé",title_x=0.5,barmode='stack')
            fig_ass_sante.update_yaxes(visible=False)
            fig_ass_sante.update_traces(hovertemplate="%{customdata} : %{y} %")


                                        ################# "Vie Figure" #################
            assurance_vie_gouv	 =  assurance.drop(assurance[assurance["Assurance Vie"] == 'Refuse de répondre'].index)
            assurance_vie_gouv = (assurance_vie_gouv[assurance_vie_gouv["Gouvernorat"].isin(slct_gouv)].groupby(['Assurance Vie',"Gouvernorat"])['ID'].count()/ \
            assurance_vie_gouv[assurance_vie_gouv["Gouvernorat"].isin(slct_gouv)].groupby(['Assurance Vie',"Gouvernorat"])['ID'].count().groupby(['Gouvernorat']).sum()*100).to_frame().reset_index()
            assurance_vie_gouv['ID']= assurance_vie_gouv['ID'].round().astype(int)
            assurance_vie_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            assurance_vie_gouv_exported = assurance_vie_gouv.rename(columns={"Assurance Vie":"Réponse","Pondération":"Pourcentage"})
            assurance_vie_gouv_exported["Type"] = "Assurance Vie"
            assurance_tot_vie = pd.concat([assurance_vie,assurance_vie_gouv])
            assurance_tot_vie.reset_index(inplace=True,drop=True)
            assurance_tot_vie['Color'] = assurance_tot_vie.apply(lambda row: "#98918B" if (row["Assurance Vie"]=='Non' and row["Gouvernorat"] == 'Total')\
                    else ("#4B4845" if (row["Assurance Vie"]=='Oui' and row["Gouvernorat"] == 'Total') \
                                    else ("#3484b6" if (row["Assurance Vie"]=='Oui') \
                        else "#b86a38")),axis=1)

            fig_ass_vie = px.bar(assurance_tot_vie, x="Gouvernorat", y="Pondération",
                width=480, height=450,template="plotly_white")

            fig_ass_vie.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=assurance_tot_vie["Color"],customdata=assurance_tot_vie["Assurance Vie"])


            fig_ass_vie.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(
                    ),title="Assurance Vie",title_x=0.5,barmode='stack')
            fig_ass_vie.update_yaxes(visible=False)
            fig_ass_vie.update_traces(hovertemplate="%{customdata} : %{y} %")
            assurance_gouv_exported = pd.concat([assurance_logement_gouv_exported,assurance_sante_gouv_exported,assurance_vie_gouv_exported,assurance_voiture_gouv_exported])

        else :

                                        ################# "assurance logement Figure" #################
            category_order  = ['Oui','Non','NSP']
            colors_logement = {"Non":'#b86a38', "Oui":'#3484b6',"NSP":"#69645F"}
            fig_ass_logement = px.bar(assurance_logement, x="Assurance Logement", y="Pondération",color = "Assurance Logement",color_discrete_map=colors_logement,\
                        width=480, height=450,template="plotly_white",category_orders={'Assurance Logement': category_order})
            fig_ass_logement.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Assurance Logement",title_x=0.5)
            fig_ass_logement.update_traces(textfont_size=14, textangle=0, textposition="auto",texttemplate='<span style="color:black">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_ass_logement.update_yaxes(visible=False)

                                        ################## "Voiture Figure" ####################

            colors_voiture =  {"Non":'#b86a38', "Oui":'#3484b6'}
            fig_ass_voiture = px.bar(assurance_voiture, x="possession voiture", y="Pondération",color = "possession voiture",color_discrete_map=colors_voiture,\
                        width=480, height=450,template="plotly_white",category_orders={'possession voiture': category_order})
            fig_ass_voiture.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Assurance Voiture",title_x=0.5)
            fig_ass_voiture.update_traces(textfont_size=14, textangle=0, textposition="auto",texttemplate='<span style="color:black">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_ass_voiture.update_yaxes(visible=False)

                                        ################## "Santé Figure" ####################

            colors_sante = {"Non":'#b86a38', "Oui":'#3484b6',"NSP":"#69645F"}
            fig_ass_sante = px.bar(assurance_sante, x="Assurance Sante", y="Pondération",color = "Assurance Sante",color_discrete_map=colors_sante,\
                        width=480, height=450,template="plotly_white",category_orders={'Assurance Sante': category_order})
            fig_ass_sante.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Assurance Sante",title_x=0.5)
            fig_ass_sante.update_traces(textfont_size=14, textangle=0, textposition="auto",texttemplate='<span style="color:black">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_ass_sante.update_yaxes(visible=False)


                                        ################## "Vie Figure" ####################

            colors_sante = {"Non":'#b86a38', "Oui":'#3484b6',}
            fig_ass_vie = px.bar(assurance_vie, x="Assurance Vie", y="Pondération",color = "Assurance Vie",color_discrete_map=colors_sante,\
                        width=480, height=450,template="plotly_white",category_orders={'Assurance Vie': category_order})
            fig_ass_vie.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Assurance Vie",title_x=0.5)
            fig_ass_vie.update_traces(textfont_size=14, textangle=0, textposition="auto",texttemplate='<span style="color:black">%{y}%</span>',hoverinfo="skip",hovertemplate = None )
            fig_ass_vie.update_yaxes(visible=False)
        
        if export_input and not slct_gouv : 
            exported_data = dcc.send_data_frame(assurance_total_exported.to_excel, "assurance_Ensemble_Territoire.xlsx")
        if export_input and slct_gouv :
            file_name = ("_").join(slct_gouv)
            exported_data = dcc.send_data_frame(assurance_gouv_exported.to_excel, "assurance_"+file_name+".xlsx")

        return fig_ass_logement, fig_ass_voiture, fig_ass_sante, fig_ass_vie,exported_data,0


 
        


        
