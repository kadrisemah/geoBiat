from dash.dependencies import Input, Output, State 
import plotly.express as px  
import plotly.io as pio
import plotly.graph_objs as go
import dash
import pandas as pd
import numpy as np 
import seaborn as sns
from dash import dcc, html
import random

data = pd.read_excel(r'app\socio_demo\Data\Base EXCEL__BESOIN IA (18-11-22).xlsx')
data.loc[data["B7-Identification chef de famille"] == "Non", 'B7-Identification chef de famille'] = data.loc[data["B7-Identification chef de famille"] == "Non", 'G7-Profession du chef de famille']
data.loc[data["B7-Identification chef de famille"] == "Oui", 'B7-Identification chef de famille'] = data.loc[data["B7-Identification chef de famille"] == "Oui", 'G3-Profession du répondant']
pond = pd.read_excel(r'app\socio_demo\Data\Colonne pondération-Base totale.xlsx')
data = data.merge(pond,on="ID")
data['A7- Urbain/ Rural'].replace({'Une zone urbaine': 'Zone urbaine', 'Une zone rurale': 'Zone rurale'}, inplace=True)


def  register_callbacks_equipe_financ(equi_fiance):

    @equi_fiance.callback(
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

    @equi_fiance.callback(
        Output('fig_taux', 'figure'),
        Output('fig_multi', 'figure'),
        Output('fig_penetration', 'figure'),
        Output('div_penetration', 'style'),
        Output("download-dataframe-csv", "data"),
        Output(component_id='export-data', component_property='n_clicks'),
        [Input('slct_gouv', 'value'),
        Input(component_id='export-data', component_property='n_clicks')])
    def generate_default_graph(slct_gouv, export_input):

        new_data = data.drop(data[data['F1-Taux de bancarisation'] == 'Refuse de répondre'].index)
        new_data.reset_index(inplace=True,drop=True)
        new_data['F2-Pénétration des institutions financières-Autre'] = new_data.apply(lambda row: row['F2-Pénétration des institutions financières-Autre2'] \
            if str(row['F2-Pénétration des institutions financières-Autre1']) == 'nan' \
                    else row['F2-Pénétration des institutions financières-Autre1'], axis=1)

        # new_data = new_data.loc[data["F1-Taux de bancarisation"]=="Oui"].reset_index(drop=True)
        penetration = new_data.filter(regex='^F2|Pondération')
        penetration.drop(["F2-Pénétration des institutions financières-Autre1","F2-Pénétration des institutions financières-Autre2"],axis=1,inplace=True)

        taux_tot = (new_data.groupby(["F1-Taux de bancarisation"])["Pondération"].sum()/new_data["Pondération"].sum()*100).to_frame().reset_index()
        taux_tot['Pondération']= taux_tot['Pondération'].round().astype(int)
        taux_tot["A5-Gouvernorat d'habitation"] = 'Total'

        bancariser_tot = data.loc[data["F1-Taux de bancarisation"]=="Oui"].reset_index(drop=True)
        bancariser_tot = bancariser_tot.filter(regex=('^A5|F2|Pondération'))
        pond = bancariser_tot['Pondération']
        gouv = bancariser_tot["A5-Gouvernorat d'habitation"]
        bancariser_tot = bancariser_tot.iloc[:,1:-1]
        df_tot = bancariser_tot.applymap(lambda x: 0 if x in ['Non',"Nsp",np.nan,"Refus"] else 1)
        df_tot['sum']=df_tot.sum(axis=1)
        df_tot['type_bancarisation'] = df_tot['sum'].apply(lambda x : "Unibancarisé" if x==1 else "Multibancarisé")
        df_tot["A5-Gouvernorat d'habitation"] = gouv
        df_tot["Pondération"] = pond
        bancariser_tot = (df_tot.groupby("type_bancarisation")['Pondération'].sum()/df_tot['Pondération'].sum()*100).to_frame().reset_index()
        bancariser_tot['Pondération'] = bancariser_tot['Pondération'].round().astype(int)
        bancariser_tot["A5-Gouvernorat d'habitation"] = "Total"

        result = {}
        for column in penetration.columns:
            if penetration[column].dtype == 'object': # only for columns with object dtype
                sum_yes = int((penetration.loc[penetration[column] == 'Oui', [column,'Pondération']]['Pondération'].sum()/data.loc[data['F1-Taux de bancarisation'] == 'Oui']['Pondération'].sum()*100).round())
                result[column.split("-")[-1].strip()] = sum_yes
        df_penetration = pd.DataFrame({"Bank":result.keys(),"Pourcentage":result.values()})
        df_penetration.sort_values('Pourcentage',ascending=False,inplace=True)
        bank_11 = ["BIAT", "BNA", "STB", "BH" , "Attijari Bank", "Amen Bank", "UIB", "BT", "ATB", "Banque Zitouna", "UBCI","Poste"]
        # Filter the dataframe
        filtered_df = df_penetration[df_penetration['Bank'].isin(bank_11)]
        # Sum the percentages of the remaining banks
        other_percentage = df_penetration[~df_penetration['Bank'].isin(bank_11)]['Pourcentage'].sum()
        # Create a new row for "Autre" category
        autre_row = pd.DataFrame({'Bank': ['Autre'], 'Pourcentage': [other_percentage]})
        # Concatenate the filtered dataframe with the "Autre" row
        df_penetration = pd.concat([filtered_df, autre_row], ignore_index=True)

        df_penetration["A5-Gouvernorat d'habitation"] = "Total"
        penetration_bancariser = data.loc[data["F1-Taux de bancarisation"]=="Oui"].reset_index(drop=True)
        penetration_bancariser["A5-Gouvernorat d'habitation"] = data.loc[data["F1-Taux de bancarisation"]=="Oui"].reset_index(drop=True)["A5-Gouvernorat d'habitation"]
        exported_data = ""

        if slct_gouv == None :
            slct_gouv = []
        
        if  len(slct_gouv) != 0  :


                                        ################# "taux Figure" #################
            taux_gouv = (data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(['F1-Taux de bancarisation',"A5-Gouvernorat d'habitation"])['ID'].count()/ \
            data[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby(['F1-Taux de bancarisation',"A5-Gouvernorat d'habitation"])['ID'].count().groupby(["A5-Gouvernorat d'habitation"]).sum()*100).to_frame().reset_index()
            taux_gouv['ID']= taux_gouv['ID'].round().astype(int)
            taux_gouv.rename(columns={"ID":"Pondération"},inplace=True)
            taux_gouv_exported = taux_gouv.rename(columns={"F1-Taux de bancarisation":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"})
            taux_gouv_exported["Type"] = "Taux de Bancarisation"

            taux_banc = pd.concat([taux_tot,taux_gouv])
            taux_banc.reset_index(inplace=True,drop=True)
            taux_banc['Color'] = taux_banc.apply(lambda row: "#98918B" if (row["F1-Taux de bancarisation"]=='Non' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                    else ("#4B4845" if (row["F1-Taux de bancarisation"]=='Oui' and row["A5-Gouvernorat d'habitation"] == 'Total') \
                                    else ("#3484b6" if (row["F1-Taux de bancarisation"]=='Oui') \
                        else "#b86a38")),axis=1)

            fig_taux = px.bar(taux_banc, x="A5-Gouvernorat d'habitation", y="Pondération",
                width=480, height=420,template="plotly_white")

            fig_taux.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=taux_banc["Color"],customdata=taux_banc["F1-Taux de bancarisation"])


            fig_taux.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(
                    ),title="Taux de Bancarisation <br> (Banque ou poste)",title_x=0.5,barmode='stack')
            fig_taux.update_yaxes(visible=False)
            fig_taux.update_traces(hovertemplate="%{customdata} : %{y}%")

            
            
            penetration["A5-Gouvernorat d'habitation"] = data["A5-Gouvernorat d'habitation"]

                                        ################## Multi bancarisé #######################
    

            banc_gouv = data.loc[data["A5-Gouvernorat d'habitation"].isin(slct_gouv)]
            bancariser = banc_gouv.loc[banc_gouv["F1-Taux de bancarisation"]=="Oui"].reset_index(drop=True)
            bancariser = bancariser.filter(regex=('^A5|F2|ID'))
            gouv = bancariser["A5-Gouvernorat d'habitation"]
            id_col = bancariser["ID"]
            banc_gouv = bancariser.iloc[:,2:-1]
            df_gouv = banc_gouv.applymap(lambda x: 0 if x in ['Non',"Nsp",np.nan,"Refus"] else 1)
            df_gouv['sum']=df_gouv.sum(axis=1)
            df_gouv['type_bancarisation'] = df_gouv['sum'].apply(lambda x : "Unibancarisé" if x==1 else "Multibancarisé")
            df_gouv["A5-Gouvernorat d'habitation"] = gouv
            df_gouv["ID"] = id_col  
            df_gouv_banc = (df_gouv.groupby(['type_bancarisation',"A5-Gouvernorat d'habitation"])['ID'].count()/ \
            df_gouv.groupby(['type_bancarisation',"A5-Gouvernorat d'habitation"])['ID'].count().groupby(["A5-Gouvernorat d'habitation"]).sum()*100).to_frame().reset_index()
            df_gouv_banc.rename(columns={"ID":"Pondération"},inplace=True)
            df_gouv_banc['Pondération'] = df_gouv_banc['Pondération'].round().astype(int) 
            df_gouv_banc_exported = df_gouv_banc.rename(columns={"type_bancarisation":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"})
            df_gouv_banc_exported["Type"] = "Taux de Multibancarisation"
            df_multi_final = pd.concat([bancariser_tot,df_gouv_banc])     

            df_multi_final.reset_index(inplace=True,drop=True)
            df_multi_final['Color'] = df_multi_final.apply(lambda row: "#98918B" if (row["type_bancarisation"]=='Multibancarisé' and row["A5-Gouvernorat d'habitation"] == 'Total')\
                    else ("#4B4845" if (row["type_bancarisation"]=='Unibancarisé' and row["A5-Gouvernorat d'habitation"] == 'Total') \
                                    else ("#3484b6" if (row["type_bancarisation"]=='Multibancarisé') \
                        else "#b86a38")),axis=1)

            fig_multi_taux = px.bar(df_multi_final, x="A5-Gouvernorat d'habitation", y="Pondération",
                width=480, height=420,template="plotly_white")

            fig_multi_taux.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{customdata}<br>%{y}%</span>',\
                                marker_color=df_multi_final["Color"],customdata=df_multi_final["type_bancarisation"])


            fig_multi_taux.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(
                    ),title="Taux de Multibancarisation <br> (Banque ou poste)",title_x=0.5,barmode='stack')
            fig_multi_taux.update_yaxes(visible=False)
            fig_multi_taux.update_traces(hovertemplate="%{customdata} : %{y}%")

    
            penetration["A5-Gouvernorat d'habitation"] = data["A5-Gouvernorat d'habitation"]
            penetration_gouv= penetration.loc[penetration["A5-Gouvernorat d'habitation"].isin(slct_gouv)]
            result = []
            for column in penetration_gouv.columns:
                if penetration_gouv[column].dtype == 'object' and column.startswith("F"): # only for columns with object dtype
                    gouv_penetration = ((penetration_gouv.loc[penetration_gouv[column] == 'Oui', [column,'Pondération',"A5-Gouvernorat d'habitation"]].groupby("A5-Gouvernorat d'habitation")\
                        ["Pondération"].count()/penetration_bancariser.loc[penetration_bancariser["A5-Gouvernorat d'habitation"].isin(slct_gouv)].groupby("A5-Gouvernorat d'habitation")['Pondération'].count()*100).round()
                        ).to_frame().reset_index().rename(columns={"Pondération":"Pourcentage"})
                    gouv_penetration["Bank"] = column.split("-")[-1].strip()
                    result.append(gouv_penetration)
            concatenated_df = pd.concat(result)
            concatenated_df.sort_values('Pourcentage',ascending=False,inplace=True)
            bank_11 = ["BIAT", "BNA", "STB", "BH" , "Attijari Bank", "Amen Bank", "UIB", "BT", "ATB", "Banque Zitouna", "UBCI","Poste"]
            concatenated_df_filter = concatenated_df[concatenated_df['Bank'].isin(bank_11)]
            other_percentage = concatenated_df[~concatenated_df['Bank'].isin(bank_11)].groupby("A5-Gouvernorat d'habitation")['Pourcentage'].sum()
            other_percentage = other_percentage.to_frame().reset_index()
            other_percentage['Bank'] ="Autre"
            df_penetration_gouv = pd.concat([concatenated_df_filter, other_percentage], ignore_index=True)
            df_penetration_gouv_exported = df_penetration_gouv.rename(columns={"Bank":"Réponse","A5-Gouvernorat d'habitation":"Gouvernorat"})
            df_penetration_gouv_exported["Type"] = "Pénétration des Institutions Financières"
            penetration_tot = pd.concat([df_penetration_gouv,df_penetration])
            penetration_tot.dropna(inplace=True)
            penetration_tot["Pourcentage"] = penetration_tot["Pourcentage"].round().astype(int)             
            penetration_tot['Color'] = penetration_tot.apply(lambda row: "#98918B" if (row["A5-Gouvernorat d'habitation"] == 'Total')\
                                    else ("#3785AF" if (row["A5-Gouvernorat d'habitation"]==penetration_tot["A5-Gouvernorat d'habitation"].unique()[0]) \
                                            else ("#254676" if (row["A5-Gouvernorat d'habitation"]==penetration_tot["A5-Gouvernorat d'habitation"].unique()[-2]) \
                        else "#212949")),axis=1)
            
            # fig_penetration = go.Figure()

            # fig_penetration.update_layout(
            #     template="simple_white",
            #     xaxis=dict(title_text=""),
            #     yaxis=dict(title_text=""),
            # )

            # for r in penetration_tot["Bank"].unique() :
            #     plot_df = penetration_tot[penetration_tot["Bank"] == r]
            #     plot_df.reset_index(inplace=True,drop=True)
            #     total_row = plot_df[plot_df["A5-Gouvernorat d'habitation"] == 'Total']
            #     plot_df = pd.concat([total_row, plot_df.drop(total_row.index)]).reset_index(drop=True)
            #     plot_df["A5-Gouvernorat d'habitation"] = plot_df["A5-Gouvernorat d'habitation"].str.replace(' ', '<br>')
            #     plot_df["Bank"] = plot_df["Bank"].str.replace(' ', '<br>')

            #     fig_penetration.add_trace(
            #         go.Bar(x=plot_df["Bank"], y=plot_df['Pourcentage'], name=r, marker_color=plot_df['Color'],text=plot_df["A5-Gouvernorat d'habitation"]),
            #     )
                
            #     fig_penetration.update_traces(textfont_size=16, textangle=0, textposition="outside",texttemplate='<br>%{y}%')

            # fig_penetration.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Pénétration des Institutions Financières",title_x=0.5,width=1400, height=500,)
            # fig_penetration.update_yaxes(visible=False)
            # fig_penetration.update_xaxes(tickfont=dict(size=10))
            # fig_penetration.update_xaxes(tickangle=0)
            # fig_penetration.update_traces(hovertemplate="%{x} : %{y} %")    
            # penet_style = {}
            category_order = ["Total"]
            if len(penetration_tot["A5-Gouvernorat d'habitation"].unique())==4:
                color_dict = {penetration_tot["A5-Gouvernorat d'habitation"].unique()[0]:"#212949",\
                    penetration_tot["A5-Gouvernorat d'habitation"].unique()[1]:"#81B6D2",\
                        penetration_tot["A5-Gouvernorat d'habitation"].unique()[2]:"#3785AF"}
            elif len(penetration_tot["A5-Gouvernorat d'habitation"].unique())==3:
                color_dict = {penetration_tot["A5-Gouvernorat d'habitation"].unique()[0]:"#212949",\
                    penetration_tot["A5-Gouvernorat d'habitation"].unique()[1]:"#3785AF"}
            else  :
                color_dict = {penetration_tot["A5-Gouvernorat d'habitation"].unique()[0]:"#212949"}
            color_dict["Total"] = "#98918B"
            fig_penetration = px.bar(penetration_tot, x="Bank", y="Pourcentage",
                width=1450, height=500,template="plotly_white",barmode="group",color="A5-Gouvernorat d'habitation",\
                    color_discrete_map=color_dict,category_orders={"A5-Gouvernorat d'habitation": category_order})

            fig_penetration.update_traces(textangle=0, textposition="outside",texttemplate='<span style="color:black">%{y}%</span>',\
                                customdata=penetration_tot["A5-Gouvernorat d'habitation"])


            fig_penetration.update_layout(xaxis_title="",yaxis_title="",font=dict(
                    ),title="Pénétration des Institutions Financières",title_x=0.5,legend_title_text="Gouvernorat")
            fig_penetration.update_yaxes(visible=False)
            fig_penetration.update_traces(hovertemplate="%{customdata} - %{x}<br>%{y} %"+"<extra></extra>")
            penet_style = {}

            exported_gouv = pd.concat([taux_gouv_exported,df_gouv_banc_exported,df_penetration_gouv_exported])


            

    
        else :

                                        ################# "Taux Figure" #################
            category_order  = ['Oui','Non','NSP']
            colors_taux = {"Oui":'#3484b6', "Non":'#b86a38'}
            fig_taux = px.bar(taux_tot, x="F1-Taux de bancarisation", y="Pondération",color = "F1-Taux de bancarisation",color_discrete_map=colors_taux,\
                        width=480, height=420,template="plotly_white",category_orders={'F1-Taux de bancarisation': category_order})
            fig_taux.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Taux de Bancarisation <br> (Banque ou poste)",title_x=0.5)
            fig_taux.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='%{y}%',hoverinfo="skip",hovertemplate = None)
            fig_taux.update_yaxes(visible=False)
            taux_tot = taux_tot.rename(columns={"F1-Taux de bancarisation":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"})
            taux_tot["Type"]="Taux de Bancarisation"
            taux_tot["Gouvernorat"] = taux_tot["Gouvernorat"].replace({"Total":"Ensemble du Territoire Tunisien"})

                                        ################# "Taux Multi Figure" #################

            colors_taux_multi = {"Multibancarisé":'#3484b6', "Unibancarisé":'#b86a38'}
            fig_multi_taux = px.bar(bancariser_tot, x="type_bancarisation", y="Pondération",color = "type_bancarisation",color_discrete_map=colors_taux_multi,\
                        width=480, height=420,template="plotly_white")
            fig_multi_taux.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",
                                    font=dict(),title="Taux de Multibancarisation <br> (Banque ou poste)",title_x=0.5)
            fig_multi_taux.update_traces(textfont_size=14, textangle=0, textposition="inside",texttemplate='%{y}%',hoverinfo="skip",hovertemplate = None)
            fig_multi_taux.update_yaxes(visible=False)
            bancariser_tot = bancariser_tot.rename(columns={"type_bancarisation":"Réponse","Pondération":"Pourcentage","A5-Gouvernorat d'habitation":"Gouvernorat"})
            bancariser_tot["Type"]="Taux de Multiancarisation"
            bancariser_tot["Gouvernorat"] = bancariser_tot["Gouvernorat"].replace({"Total":"Ensemble du Territoire Tunisien"})

            #                             ################## "Pénétration Figure" ####################

            colordict_penetration = {f:"#3785AF" for i, f in enumerate(df_penetration["Bank"].unique())}
            fig_penetration = px.bar(df_penetration,x="Bank",y="Pourcentage",width=1200, height=500,template="plotly_white",\
                                    color='Bank',color_discrete_map=colordict_penetration)
            fig_penetration.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",margin=dict(l=100),
                                    font=dict(),title="Pénétration des Institutions Financières",title_x=0.5)
            fig_penetration.update_traces(textfont_size=14, textangle=0, textposition="outside",texttemplate='%{y}%',hoverinfo="skip",hovertemplate = None)
            fig_penetration.update_yaxes(visible=False)
            penet_style = {"margin-left":"8rem"}
            df_penetration = df_penetration.rename(columns={"Bank":"Réponse","A5-Gouvernorat d'habitation":"Gouvernorat"})
            df_penetration["Type"]="Pénétration des Institutions Financières"
            df_penetration["Gouvernorat"] = df_penetration["Gouvernorat"].replace({"Total":"Ensemble du Territoire Tunisien"})

        if export_input and not slct_gouv : 
            exported = pd.concat([taux_tot,bancariser_tot,df_penetration])
            exported_data = dcc.send_data_frame(exported.to_excel, "equipement_financiers_Ensemble_Territoire.xlsx")
        if export_input and slct_gouv :
            file_name = ("_").join(slct_gouv)
            exported_data = dcc.send_data_frame(exported_gouv.to_excel, "equipement_financiers_"+file_name+".xlsx")

        return fig_taux,fig_multi_taux,fig_penetration, penet_style, exported_data,0


 
        


        
