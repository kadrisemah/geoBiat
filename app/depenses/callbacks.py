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

depense = pd.read_excel(r'app\depenses\Data\Proportions budgétaires.xlsx')
depense.columns=depense.iloc[0]
depense.drop(0,axis=0,inplace=True)
depense.rename(columns={np.nan:"Gouvernorat"},inplace=True)
depense = depense.set_index("Gouvernorat")
colors = sns.color_palette("dark:#0E84CE",n_colors=len(depense.columns)).as_hex()
colordict = {f:colors[i] for i, f in enumerate(depense.columns)}
depense_ens_ter = depense.loc[depense.index=="Ens. Territoire"]
depense_ens_ter = depense_ens_ter.T.reset_index().rename(columns={0:"Type","Ens. Territoire":"Pondération"})
depense_ens_ter["Pondération"]= (depense_ens_ter["Pondération"]*100).astype(int).round()
depense_ens_ter["Gouvernorat"] = "Total"



def  register_callbacks_depenses(depenses):

    @depenses.callback(
        Output('slct_gouv', 'options'),
        Input('slct_gouv', 'value'),
        State('slct_gouv', 'options'),
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

    @depenses.callback(
        Output('fig_dep', 'figure'),
        Output("download-dataframe-csv", "data"),
        Output(component_id='export-data', component_property='n_clicks'),
        [Input('slct_gouv', 'value')],
        Input(component_id='export-data', component_property='n_clicks')
        )
    def generate_default_graph(slct_gouv, export_input):

                                    ################# "dépense Figure" #################
        exported_data = ""

        if slct_gouv == None :
            slct_gouv = []
        
        if  len(slct_gouv) != 0  :

            dep_gouv = depense.loc[depense.index.isin(slct_gouv)]
            result = []
            for gouv in dep_gouv.index.unique():
                a= dep_gouv.loc[dep_gouv.index==gouv].T.reset_index()
                a["Gouvernorat"] = gouv
                a.rename(columns={0:"Type",gouv:"Pondération"},inplace=True)
                result.append(a)
            df_resul = pd.concat(result)
            colordict_tot ={'Courses alimentaires': '#000000','Scolarité des enfants': '#454141',"Factures d'électricité, Sonede, Internet": '#645858','Transport': '#807575','Loisirs/ sports': '#AB9E9E',"Produits d'hygiène": '#C0C0C0'}
            dict_df = pd.DataFrame(list(colordict.items()), columns=['Index', 'Color'])
            df_resul = df_resul.merge(dict_df, left_on="Type", right_on='Index')
            dict_df = pd.DataFrame(list(colordict_tot.items()), columns=['Index', 'Color'])
            depense_ens_tot = depense_ens_ter.merge(dict_df, left_on="Type", right_on='Index')
            df_resul["Pondération"]= (df_resul["Pondération"]*100).astype(int).round()
            df_resul = pd.concat([depense_ens_tot,df_resul])
            fig_depense = go.Figure()

            fig_depense.update_layout(
                template="simple_white",
                xaxis=dict(title_text=""),
                yaxis=dict(title_text=""),
                barmode="stack",
            )
            colors = df_resul['Color'].unique()
            for r, c in zip(df_resul['Type'].unique(), colors):
                plot_df = df_resul[df_resul['Type'] == r]
                fig_depense.add_trace(
                    go.Bar(x=plot_df["Gouvernorat"], y=plot_df['Pondération'], name="", marker_color=plot_df['Color'],text=plot_df['Type']),
                )
                
                fig_depense.update_traces(textfont_size=16, textangle=0, textposition="inside",texttemplate='<span style="color:white">%{text}<br>%{y}%</span>')

            fig_depense.update_layout(showlegend=False,xaxis_title="",yaxis_title="",font=dict(),title="Dépenses",title_x=0.5,width=1200, height=800,)
            fig_depense.update_yaxes(visible=False)
            fig_depense.update_xaxes(tickfont=dict(size=14))
            fig_depense.update_xaxes(tickangle=0)
            fig_depense.update_traces(hovertemplate="%{x} - %{text} : %{y} %")



                                        ################# "dépense Figure" #################
        else :

            fig_depense = px.bar(depense_ens_ter,x="Type", y="Pondération",color ="Type",color_discrete_map=colordict,\
            width=480, height=420,template="plotly_white")
            fig_depense.update_layout(showlegend=False,
                                    xaxis_title='',yaxis_title="",width=1200, height=800,
                                    font=dict(),title="Dépenses",title_x=0.5)
            fig_depense.update_traces(textfont_size=18, textangle=0, textposition="inside",texttemplate='%{y}%',hoverinfo="skip",hovertemplate = None)
            fig_depense.update_yaxes(visible=False)
        
        if export_input and not slct_gouv : 

            exported_data = dcc.send_data_frame((depense*100).to_excel, "depense_Ensemble_Territoire.xlsx")
        if export_input and slct_gouv :
            file_name = ("_").join(slct_gouv)
            exported_data = dcc.send_data_frame((depense[depense.index.isin(slct_gouv)]*100).to_excel, "depenses_"+file_name+".xlsx")

        return fig_depense,exported_data,0

 
        


        
