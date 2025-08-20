
import pandas as pd
import numpy as np 
import warnings
warnings.filterwarnings('ignore')
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns



############################################### DATA PREPROCESSING ###############################################

def filter_data(df,NDT,Code):
    columns_needed = ["A5-Gouvernorat d'habitation","A6-Délégation d'habitation","A4- Tanche d'âge","A3- Genre du répondant","Pondération"]
    filtred_data_origin = df[[col for col in df.columns if col.startswith(Code) or col in columns_needed]]
    filtred_data_origin = filtred_data_origin.astype(str)
    for c in NDT[NDT["N°"].str.startswith(Code)]["Base de répondants de la question"]:
        if len(c.split("="))>1:
            for col in list(df[[col for col in df.columns if col.startswith(c.split("=")[0].strip())]].columns):
                if col not in filtred_data_origin.columns.values :
                    filtred_data_origin = pd.concat([filtred_data_origin,df[[col for col in df.columns if col.startswith(c.split("=")[0].strip())]]],axis=1)
    filtred_data_origin = filtred_data_origin.astype({"Pondération": float}, errors='raise') 
    return filtred_data_origin



def handleAutreColumns(data):
    ################ Remove Empty Autre Column ###################
    outputdata = data.copy()
    list_list_columns = []
    list_df = []
    for d in data.columns:
        if "autre" in d.lower() and len(data[d].unique())==1 and data[d].unique()[0]=="nan":
            outputdata = data.drop(d,axis=1)
    ################ Group Autre Column ###################
    for d in outputdata.columns:
        code = d.split("-")[0]
        if "autre" in d.lower():
            dff = outputdata[[col for col in outputdata.columns if col.startswith(code)]]
            if list(dff.columns) not in list_list_columns:
                list_df.append(outputdata[[col for col in outputdata.columns if col.startswith(code)]])
                list_list_columns.append(list(dff.columns))
    ################ Keep Only necessary column #############
    for l in list_df:
        if l.shape[1] == 2 :
            if (l.iloc[:,0].value_counts(normalize=True) * 100).to_frame().loc["Autre"].values[0] > 10.0:
                l.iloc[:,0] = np.where(l.iloc[:,0] == "Autre", l.iloc[:,1], l.iloc[:,0])
                outputdata[l.columns[0]] = l.iloc[:,0]
                outputdata.drop(l.columns[[1]],axis=1,inplace=True)
            else :
                outputdata.drop(l.columns[[1]],axis=1,inplace=True)
        if l.shape[1] > 2 : 
            dff = l[[col for col in l.columns if "autre" in col.lower()]]
            if (dff.iloc[:,0].value_counts(normalize=True) * 100).to_frame().loc["Oui"].values[0] > 10.0:
                dff.iloc[:,0] = np.where(dff.iloc[:,0]== "Oui", dff.iloc[:,1], dff.iloc[:,0])
                outputdata[dff.columns[0]] = dff.iloc[:,0]
                outputdata.drop(dff.columns[[1]],axis=1,inplace=True)
            else : 
                outputdata.drop(dff.columns[[1]],axis=1,inplace=True)

    return outputdata

def extract_base_data(NDT,data,code):
    dicti = {}
    for c in data.columns:
        if c.startswith(code):
            N = c.split("-")[0].replace(" ","")
            base = NDT[NDT['N°']==N]["Base de répondants de la question"].iloc[0].split("\n")
            if len(base)>1:
                for x in NDT[NDT['N°']==base[1].split("=")[0].strip()]["Détails réponses"].iloc[0].split("\n"):
                    if x.startswith(base[1].split("=")[1].strip()):
                        a = base[1].split("=")[0].strip() + ":" + x.split("-")[1].strip()
                dicti[N] = a
            else:
                if len (base[0].split("="))>1:
                    for x in NDT[NDT['N°']==base[0].split("=")[0].strip()]["Détails réponses"].iloc[0].split("\n"):
                        if x.startswith(base[0].split("=")[1].strip()):
                            a = base[0].split("=")[0].strip() + ":" + x.split("-")[1].strip()
                    dicti[N] = a
                else : 
                    dicti[N] = base[0]
    return dicti

def process_column_name(data_frame):
    new_columns=[]
    for d in data_frame.columns:
        if len(d.split("-"))>1 :
            new_columns.append(d.split("-",1)[1].strip().replace("-"," -"))
        else :
            new_columns.append(d.split("-",1)[0].strip().replace("-"," -"))
    data_frame.columns = new_columns
    return data_frame

############################################### ****END DATA PREPROCESSING**** ###########################################


###############################################  ****DATA PLOTTING****  ##################################################
def hex_to_rgb(hex):
  hex = hex.replace("#","")
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(str(decimal))
  
  return "rgba"+'('+",".join(rgb)+",1"+")"

def process_legends_plots(data,column_name):
    empty_list = []
    dict_values = {}
    for d in data[column_name].unique():
        text = d.strip().replace(" ","")
        try : 
            dict_values[d] = tuple(int(item) for item in re.findall(r'^\D*(\d+)*\D*(\d+)*', text)[0])
        except:
            tup = re.findall(r'^\D*(\d+)*\D*(\d+)*', text)[0]
            try:
                tup =(int(tup[0]),0)
                dict_values[d] = tup
            except:
                empty_list.append(d)
    dict_ordred = {k: v for k, v in sorted(dict_values.items(), key=lambda item: item[1])}
    list_categories_labels = list(dict_ordred.keys())
    list_categories_labels = list_categories_labels + empty_list
    return list_categories_labels


def plot_tous_all_tunis(data,column_name):
    
    data[column_name] = data[column_name].replace(np.nan, 'Refuse de répondre')
    data[column_name] = data[column_name].replace(["nan"], 'Refuse de répondre')

    df_plot = data.groupby(["A5-Gouvernorat d'habitation",column_name])['Pondération'].sum().to_frame().reset_index()
    list_pond = []
    list_base = []
    list_pond2 = []
    for g in df_plot["A5-Gouvernorat d'habitation"].unique():
        for p in df_plot[df_plot["A5-Gouvernorat d'habitation"] ==g]["Pondération"]:
            list_pond.append(p/df_plot[df_plot["A5-Gouvernorat d'habitation"] ==g]["Pondération"].sum()*100)
    for gg in range(df_plot.shape[0]):
        list_base.append(data[data["A5-Gouvernorat d\'habitation"]==df_plot["A5-Gouvernorat d\'habitation"].iloc[gg]].shape[0])
    df_plot["Pondération en %"] =  list_pond
    df_plot["Pondération en %"] = (df_plot["Pondération en %"].apply(lambda x: "{:.1f}".format(x))).astype(float)
    df_plot["Base"] = list_base
    
    df_plot2 = data.groupby([column_name])["Pondération"].sum().to_frame().reset_index()
    for pp in df_plot2["Pondération"]:
        list_pond2.append(pp/df_plot2["Pondération"].sum()*100)
    df_plot2["Pondération en %"] = list_pond2
    df_plot2["Pondération en %"] = (df_plot2["Pondération en %"].apply(lambda x: "{:.1f}".format(x))).astype(float)
    df_plot2["Gouvernorat d'habitation"] = "Total"
    df_plot2["Base"] = data.shape[0]

    df_plot = process_column_name(df_plot)
    df_plot2 = process_column_name(df_plot2)
    df_plot.sort_values(["Gouvernorat d'habitation"],inplace=True)
    df_plot = pd.concat([df_plot,df_plot2])
    df_plot.reset_index(inplace=True,drop=True)
    column_name = column_name.split("-",1)[1].strip().replace("-"," -")
    lables_sorted = process_legends_plots(df_plot,column_name)
    colors1 = {"Oui":'#259E21', "Non":'rgb(252, 75, 51)', "Refuse de répondre":'#424242',"NSP":"#A4A4A4"}
    colors=sns.color_palette("tab10",n_colors=len(df_plot[column_name].unique())).as_hex()
    colordict = {f:colors[i] for i, f in enumerate(df_plot[column_name].unique())}
    colordict.update(colors1)
    fig = px.bar(df_plot, x="Gouvernorat d'habitation", y="Pondération en %",hover_data = {"Pondération en %":True,"Gouvernorat d'habitation":False,"Base":True,column_name:True},\
        color = column_name,color_discrete_map=colordict,text_auto=True,category_orders={column_name:lables_sorted})
    fig.update_layout(title="Pondération Par Gouvernorat et "+column_name+" Base ("+str(data.shape[0])+")",barmode='stack',font=dict(
        family="Courier New, monospace",
        size=13
    ),)
    fig.update_layout(title_x=0.5,xaxis={'categoryorder':'array', 'categoryarray':df_plot["Gouvernorat d'habitation"]})
    fig.update_traces(textfont_color="white",textposition='inside',textfont={"size": 14})

    return fig

def plot_tous_per_gouv(data,column_name,gouv):
    list_pond = []
    list_base = []
    data[column_name] = data[column_name].replace(np.nan, 'Refuse de répondre')
    data[column_name] = data[column_name].replace(["nan"], 'Refuse de répondre')
    gouv_data = data[data["A5-Gouvernorat d\'habitation"]==gouv]
    df_plot = gouv_data.groupby(["A5-Gouvernorat d'habitation",column_name])['Pondération'].sum().to_frame().reset_index()
    for p in df_plot["Pondération"]:
        list_pond.append(p/df_plot["Pondération"].sum()*100)
    for gg in range(df_plot.shape[0]):
        list_base.append(data[data["A5-Gouvernorat d\'habitation"]==df_plot["A5-Gouvernorat d\'habitation"].iloc[gg]].shape[0])
    df_plot["Pondération en %"] =  list_pond
    df_plot["Pondération en %"] = (df_plot["Pondération en %"].apply(lambda x: "{:.1f}".format(x))).astype(float)
    df_plot["Base"] = list_base
    df_plot = process_column_name(df_plot)
    column_name = column_name.split("-",1)[1].strip().replace("-"," -")
    lables_sorted = process_legends_plots(df_plot,column_name)
    colors1 = {"Oui":'#259E21', "Non":'rgb(252, 75, 51)', "Refuse de répondre":'#424242',"NSP":"#A4A4A4"}
    colors=sns.color_palette("tab10",n_colors=len(df_plot[column_name].unique())).as_hex()
    colordict = {f:colors[i] for i, f in enumerate(df_plot[column_name].unique())}
    colordict.update(colors1)
    fig = px.bar(df_plot, x="Pondération en %", y=column_name, color = column_name,color_discrete_map=colordict,hover_data = {"Pondération en %":True,"Gouvernorat d'habitation":False,"Base":True,column_name:False}\
        ,text_auto=True,orientation='h',category_orders={column_name:lables_sorted})
    fig.update_layout(title="Pondération"+" Par "+column_name+" à "+gouv+" Base ("+str(df_plot.iloc[0]['Base'])+")",barmode='stack', yaxis={'categoryorder': 'total ascending'},font=dict(
        family="Courier New, monospace",
        size=13,
    ),)
    fig.update_layout(title_x=0.5)
    fig.update_layout(legend_traceorder="reversed")
    fig.update_traces(textfont_color="white",textposition='inside',textfont={"size": 14})
    return fig

def plot_tous_per_gouv_and_filter(data,column_name,gouv,filter_column):
    list_pond = []
    list_base = []
    data[column_name] = data[column_name].replace(np.nan, 'Refuse de répondre')
    data[column_name] = data[column_name].replace(["nan"], 'Refuse de répondre')
    gouv_data = data[data["A5-Gouvernorat d\'habitation"]==gouv]
    df_plot = gouv_data.groupby(["A5-Gouvernorat d'habitation",column_name,filter_column])['Pondération'].sum().to_frame().reset_index()
    for p in range(df_plot.shape[0]):
        list_pond.append((df_plot.iloc[p]["Pondération"]/gouv_data[gouv_data[column_name]==df_plot.iloc[p][column_name]]["Pondération"].sum())*100)
    for gg in range(df_plot.shape[0]):
        list_base.append(data[data["A5-Gouvernorat d\'habitation"]==df_plot["A5-Gouvernorat d\'habitation"].iloc[gg]].shape[0])
    df_plot["Pondération en %"] =  list_pond
    df_plot["Pondération en %"] = (df_plot["Pondération en %"].apply(lambda x: "{:.1f}".format(x))).astype(float)
    df_plot["Base"] = list_base
    
    df_plot = process_column_name(df_plot)
    column_name = column_name.split("-",1)[1].strip().replace("-"," -")
    filter_column = filter_column.split("-",1)[1].strip().replace("-"," -")
    df_plot.sort_values(by=[filter_column,"Pondération en %"],inplace=True)
    lables_sorted = process_legends_plots(df_plot,column_name)
    
    colors1 = {"Oui":'#259E21', "Non":'rgb(252, 75, 51)', "Refuse de répondre":'#424242',"NSP":"#A4A4A4"}
    colors=sns.color_palette("tab10",n_colors=len(df_plot[column_name].unique())).as_hex()
    colordict = {f:colors[i] for i, f in enumerate(df_plot[column_name].unique())}
    colordict.update(colors1)
    
    fig = px.bar(df_plot, x="Pondération en %", y=column_name, hover_data = {"Pondération en %":True,"Gouvernorat d'habitation":False,"Base":True,column_name:False},\
        color = filter_column,color_discrete_map=colordict,text_auto=True,orientation='h',category_orders={column_name:lables_sorted})
    
    fig.update_layout(title="Pondération"+" Par "+filter_column+" et Par "+column_name+" à "+gouv+" Base ("+str(df_plot.iloc[0]['Base'])+")",\
        barmode='stack', yaxis={'autorange': 'reversed'},font=dict(
        family="Courier New, monospace",
        size=13,
    ),)
    fig.update_layout(title_x=0.5)
    fig.update_traces(textfont_color="white",textposition='inside',textfont={"size": 15})
    return fig

def plot_pie_all_tunisie(data,column_name,filter):
    colors_init = {"Oui":'rgba(37, 158, 33, 1)', "Non":'rgba(252, 75, 51, 1)', "Refuse de répondre":'rgba(66, 66, 66, 1)',"NSP":"rgba(164, 164, 164, 1)"}
    base = data.shape[0]
    data[column_name] = data[column_name].replace(np.nan, 'Refuse de répondre')
    data[column_name] = data[column_name].replace(["nan"], 'Refuse de répondre')
    df_pie = data.groupby([column_name,])['Pondération'].sum().to_frame().reset_index()
    Base = data[column_name].value_counts().to_frame().reset_index()
    Base.rename(columns={column_name:"Base"},inplace=True)
    list_purc_pond = []
    for p in df_pie["Pondération"]:
        list_purc_pond.append(p/df_pie["Pondération"].sum()*100)
    df_pie['Pondération en %'] = list_purc_pond
    df_pie["Pondération en %"] = (df_pie["Pondération en %"].apply(lambda x: "{:.1f}".format(x))).astype(float)
    colors=sns.color_palette("tab10",n_colors=len(df_pie[column_name].unique())).as_hex()
    colordict = {f:colors[i] for i, f in enumerate(df_pie[column_name].unique())}
    colordict.update(colors_init)
    df_pie["color"] = df_pie[column_name].apply(lambda x: colordict.get(x))
    df_pie["color"] = df_pie["color"].apply(lambda x : hex_to_rgb(x) if x.startswith('#') else x)
    df_pie.loc[df_pie[column_name]!=filter,'color'] = df_pie.loc[df_pie[column_name]!=filter,'color'].str.replace("1\)",'0.485\)')
    df_pie = process_column_name(df_pie)
    column_name = column_name.split("-")[1].strip()
    df_pie = df_pie.merge(Base,left_on=column_name,right_on="index")
    df_pie.drop("index",axis=1,inplace=True)
    value_unique = df_pie[column_name].unique()
    pulls = [0.25 if x == filter else 0 for x in value_unique]
    fig = go.Figure(data = go.Pie(values = df_pie["Pondération en %"], 
                                labels = df_pie[column_name],
                                pull = pulls,
                                marker_colors = df_pie["color"],text=df_pie["Base"],hovertemplate = "<b><extra></extra>%{label}</b>: <br>"+"Pondération"+": %{percent} </br>"+'Base: %{text}'))
    fig.update_layout(title=column_name +" en Tunisie "+" (Base:"+str(base)+")",font=dict(
        family="Courier New, monospace",
        size=13
    ),)
    fig.update_layout(title_x=0.5)
    fig.update_traces(textfont_color="white",textfont={"size": 15},textposition='inside')
    return fig

def plot_pie_per_gouv(data,column_name,filter,gouv):
    colors_init = {"Oui":'rgba(37, 158, 33, 1)', "Non":'rgba(252, 75, 51, 1)', "Refuse de répondre":'rgba(66, 66, 66, 1)',"NSP":"rgba(164, 164, 164, 1)"}
    gouv_data = data[data["A5-Gouvernorat d\'habitation"]==gouv]
    base = gouv_data.shape[0]
    gouv_data[column_name] = gouv_data[column_name].replace(np.nan, 'Refuse de répondre')
    gouv_data[column_name] = gouv_data[column_name].replace(["nan"], 'Refuse de répondre')
    df_pie = gouv_data.groupby([column_name,])['Pondération'].sum().to_frame().reset_index()
    Base = gouv_data[column_name].value_counts().to_frame().reset_index()
    Base.rename(columns={column_name:"Base"},inplace=True)
    list_purc_pond = []
    for p in df_pie["Pondération"]:
        list_purc_pond.append(p/df_pie["Pondération"].sum()*100)
    df_pie['Pondération en %'] = list_purc_pond
    df_pie["Pondération en %"] = (df_pie["Pondération en %"].apply(lambda x: "{:.1f}".format(x))).astype(float)
    colors=sns.color_palette("tab10",n_colors=len(df_pie[column_name].unique())).as_hex()
    colordict = {f:colors[i] for i, f in enumerate(df_pie[column_name].unique())}
    colordict.update(colors_init)
    df_pie["color"] = df_pie[column_name].apply(lambda x: colordict.get(x))
    df_pie["color"] = df_pie["color"].apply(lambda x : hex_to_rgb(x) if x.startswith('#') else x)
    df_pie.loc[df_pie[column_name]!=filter,'color'] = df_pie.loc[df_pie[column_name]!=filter,'color'].str.replace("1\)",'0.485\)')
    df_pie = process_column_name(df_pie)
    column_name = column_name.split("-")[1].strip()
    df_pie = df_pie.merge(Base,left_on=column_name,right_on="index")
    value_unique = df_pie[column_name].unique()
    pulls = [0.25 if x == filter else 0 for x in value_unique]
    fig = go.Figure(data = go.Pie(values = df_pie["Pondération en %"], 
                                labels = df_pie[column_name],
                                pull = pulls,
                                marker_colors = df_pie["color"],text=df_pie["Base"],hovertemplate = "<b><extra></extra>%{label}</b>: <br>"+"Pondération"+": %{percent} </br>"+'Base: %{text}'))
    fig.update_layout(title=column_name +" "+gouv+" (Base:"+str(base)+")",font=dict(
        family="Courier New, monospace",
        size=13
    ),)
    fig.update_layout(title_x=0.5)
    fig.update_traces(textfont_color="white",textfont={"size": 15},textposition='inside')
    return fig

def generate_sub_plot(pie_fig,bar_fig):
    fig = make_subplots(rows=2, cols=1, specs=[[{"type":'pie'},],
            [{"type":'bar'}]],row_heights=[0.45, 0.55])
    fig.add_trace(
        go.Pie(pie_fig.data[0],showlegend=False,textposition="inside",textfont_color="white"),
        row=1,col=1
    )
    for i in range(len(bar_fig.data)):
        fig.add_trace(
            bar_fig.data[i],
            row=2, col=1
        )
        fig.update_layout(barmode="stack")
        
    fig.update_layout(title = bar_fig.layout.title,font=dict(
        family="Courier New, monospace",
        size=13,
    ))
    fig.update_layout(
        autosize=False,
        width=1466,
        height=850,)
    fig.update_traces(textfont_color="white",textfont={"size": 14},textposition='inside')

    fig.update_layout(title_x=0.5,xaxis={'categoryorder':'array', 'categoryarray':bar_fig.layout['xaxis']['categoryarray'],
    'title':bar_fig.layout.xaxis.title.text},yaxis={'title':bar_fig.layout.yaxis.title.text})
       
    return fig 

def sub_plot_all_tunisie(data,dict_code_plots,code_column):
    list_figure = []
    code_list = []
    for d in data.columns:
        df_filter = data.copy()
        if d.startswith(code_column):
            code = d.split("-")[0].strip()
            if dict_code_plots[code] != "A tous":
                test_code = " "
                while test_code != "A tous":
                    
                    test_code = dict_code_plots[code].split(":")[0]
                    value_code = dict_code_plots[code].split(":")[1]
                    column_name = [x for x in df_filter.columns if x.startswith(test_code)][0]
                    code = test_code
                    test_code = dict_code_plots[code].split(":")[0]
                    code_list.append(column_name)
                if len(code_list)==1:
                    df_filter = df_filter[df_filter[column_name]==value_code]
                    df_filter.reset_index(inplace=True,drop=True)
                    fig2 = plot_tous_all_tunis(df_filter,d)
                    fig = plot_pie_all_tunisie(data,code_list[-1],value_code)
                else : 
                    df_filter = df_filter[df_filter[code_list[-1]]==value_code]
                    df_filter.reset_index(inplace=True,drop=True)
                    fig = plot_pie_all_tunisie(df_filter,code_list[0],value_code)
                    last_filter = dict_code_plots[d.split("-")[0].strip()].split(":")[1]
                    df_filter = df_filter[df_filter[code_list[0]]==last_filter]
                    df_filter.reset_index(inplace=True,drop=True)
                    fig2 = plot_tous_all_tunis(df_filter,d)
                list_figure.append(generate_sub_plot(fig,fig2))
                code_list = []
            else: 
                list_figure.append(plot_tous_all_tunis(data,d))
        
    return list_figure



def sub_plot_gouv(data,dict_code_plots,code_column,gouv):
    list_figure = []
    code_list = []
    for d in data.columns:
        df_filter = data.copy()
        if d.startswith(code_column):
            code = d.split("-")[0].strip()
            if dict_code_plots[code] != "A tous":
                test_code = " "
                while test_code != "A tous":
                    
                    test_code = dict_code_plots[code].split(":")[0]
                    value_code = dict_code_plots[code].split(":")[1]
                    column_name = [x for x in df_filter.columns if x.startswith(test_code)][0]
                    code = test_code
                    test_code = dict_code_plots[code].split(":")[0]
                    code_list.append(column_name)
                if len(code_list)==1:
                    df_filter = df_filter[df_filter[column_name]==value_code]
                    df_filter.reset_index(inplace=True,drop=True)
                    fig2 = plot_tous_per_gouv(df_filter,d,gouv)
                    fig = plot_pie_per_gouv(data,code_list[-1],value_code,gouv)
                else : 
                    df_filter = df_filter[df_filter[code_list[-1]]==value_code]
                    df_filter.reset_index(inplace=True,drop=True)
                    fig = plot_pie_per_gouv(df_filter,code_list[0],value_code,gouv)
                    last_filter = dict_code_plots[d.split("-")[0].strip()].split(":")[1]
                    df_filter = df_filter[df_filter[code_list[0]]==last_filter]
                    df_filter.reset_index(inplace=True,drop=True)
                    fig2 = plot_tous_per_gouv(df_filter,d,gouv)
                list_figure.append(generate_sub_plot(fig,fig2))
                for dd in ["A3- Genre du répondant","A4- Tanche d'âge"] :
                    list_figure.append(plot_tous_per_gouv_and_filter(df_filter,d,gouv,dd))
                code_list = []
            else: 
                list_figure.append(plot_tous_per_gouv(data,d,gouv))
                for dd in ["A3- Genre du répondant","A4- Tanche d'âge"] :
                    list_figure.append(plot_tous_per_gouv_and_filter(df_filter,d,gouv,dd))
        
    return list_figure

###############################################  ****END DATA PLOTTING****  ##################################################