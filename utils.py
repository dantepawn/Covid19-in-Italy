import numpy as np
import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
import seaborn as sns

import datetime 

regioni_url = 'https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson'


def create_df_regioni(days):
    '''scrape github , download data return a dataframe'''
    
    df = pd.DataFrame()
    for i in days:
        url =  f'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-{i}.csv'
  #df.append(pd.read_csv(url, encoding= 'Latin'))dpc-covid19-ita-regioni
        df = pd.concat([df,pd.read_csv(url, encoding="Latin")])
        df.data = pd.to_datetime(df.data , yearfirst=True)
        df = df[df['codice_regione'].map(lambda x :len(str(x)) < 3)] # notes are excluded
    #rename regions
        df.replace('P.A. Bolzano' , 'Bolzano' , inplace = True)
        df.replace('P.A. Trento'  , 'Trento' , inplace = True )
        df.replace('Emilia-Romagna' , 'Emilia Romagna' , inplace = True)
        #df['denominazione_regione'] = df['denominazione_regione'].mask(df['denominazione_regione']=='P.A. Bolzano', 'Bolzano')
        #df['denominazione_regione'] = df['denominazione_regione'].mask(df['denominazione_regione']=='P.A. Trento', 'Trento')
    return df


def create_regioni_shape():
    'with trento e bolzano'
    regioni_url = 'https://gist.githubusercontent.com/datajournalism-it/f1abb68e718b54f6a0fe/raw/23636ff76534439b52b87a67e766b11fa7373aa9/regioni-con-trento-bolzano.geojson'
    regioni = gpd.read_file(regioni_url)
    regioni.rename(columns={'Regione':'denominazione_regione'},inplace=True)
    return regioni


def create_popolazione():
    '''create a Series of regional populations'''

    popolazione = "Lombardia,Lazio,Campania,Sicilia,Veneto,Emilia Romagna,Piemonte,Puglia,Toscana,Calabria,Sardegna,Liguria,Marche,Abruzzo,Friuli Venezia Giulia,Umbria,Basilicata,Molise,Valle d'Aosta,Bolzano,Trento".split(',')
    nu = [10060574,5879082,5801692,4999891,4905854,4459477,4356406,4029053,3729641,1947131,1639591,1550640,1525271,1311580,1215220 ,882015,562869,305617,125666,533349,545497]

    
    return pd.Series(data  = dict(zip(popolazione,nu))  , name = 'popolazione')

def create_italy(shapes : pd.DataFrame , popolazione : pd.Series):
    '''merge population and region s shape'''
    italy = shapes.merge(pd.DataFrame(popolazione).reset_index(),left_on = 'denominazione_regione' , right_on = 'index')
    italy.drop('index',axis = 1 , inplace = True)
    return italy

def update_regioni(regioni , today : str):
    '''updates from the last point in the local dataframe '''
    
    #get the last day of the dataset
    daterange = pd.date_range(start = regioni.data.iloc[-1],end = today)
    days = []
    
    for x in daterange:
        dd = '0'+str(x.day)
        mm = '0'+str(x.month)
        yyyy = str(x.year)
        days.append(yyyy+mm[-2:]+dd[-2:])
    
    df = pd.DataFrame()
    for i in days[1:]: # exclude the first day it is already in the dataset
        
        url =  'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-{i}.csv'.format(i)
    #df.append(pd.read_csv(url, encoding= 'Latin'))dpc-covid19-ita-regioni
        df = pd.concat([df,pd.read_csv(url, encoding="Latin")])
        df.data = pd.to_datetime(df.data , yearfirst=True)
        df = df[df['codice_regione'].map(lambda x :len(str(x)) < 3)]
    #rename regions
        df['denominazione_regione'] = df['denominazione_regione'].mask(df['denominazione_regione']=='P.A. Bolzano', 'Trentino-Alto Adige')
        df['denominazione_regione'] = df['denominazione_regione'].mask(df['denominazione_regione']=='P.A. Trento', 'Trentino-Alto Adige')
    regioni = pd.concat([regioni,df],axis = 0)    
    return regioni


#taday is automatically set to yesteday
#gdf[str(today)]

def region_plot_old(df , italy , day = '2020-11-10' ,save = True):
    
    df.data = pd.to_datetime(df.data)
    df = df.set_index('data')
    df = df[day]
    df = df.groupby('denominazione_regione')['nuovi_positivi'].sum()
    df = italy.merge(df, on ='denominazione_regione')
    #gdf = gpd.GeoDataFrame(df ) #, geometry = df.geometry)
    df['totale_casi per 1m abitanti'] = 1e6*df['nuovi_positivi'] // df['popolazione']
    
    fig, ax = plt.subplots(figsize= (12,8))
    plt.xticks([])
    plt.yticks([])
    plt.title(f'Nuovi positivi per 1m abitanti \n {day}')
    
    gdf.plot(column = 'totale_casi per 1m abitanti',
                               cmap = 'inferno',
                               vmax = 1000,
                               vmin = 0,
                               legend =True,
                               ax = ax)
    if save:
        plt.savefig(fname = f'./images/it_cv{day}.png' ,format = 'png')

def plot_region(regioni_df , df , day , field = 'nuovi_positivi' , save = False):
    df.data = pd.to_datetime(df.data)
    df = df.set_index('data')
    df = df[day]
    df = df.groupby('denominazione_regione')[field].sum()
    
    
    regioni_df = regioni_df.join(df , on = 'denominazione_regione' )
    
    regioni_df['totale_casi per 1m abitanti'] = 1e5*regioni_df['nuovi_positivi'] // regioni_df['popolazione']

    fig, ax = plt.subplots(figsize= (12,8))
    plt.xticks([])
    plt.yticks([])
    plt.title(f'Nuovi positivi per 100k abitanti \n {day}')

    regioni_df.plot(column = 'totale_casi per 1m abitanti',
                               cmap = 'inferno',
                               vmax = 200,
                               vmin = 0,
                               legend =True,
                                   ax = ax)
    if save:
        plt.savefig(fname = f'./images/it_cv{day}.png' ,format = 'png')        
        
        

def barchart(df  , title = 'nuovi_positivi' , color_map = 'viridis'):
    data = df.groupby('data')[title].sum() 
    
    clr = sns.color_palette(color_map , n_colors =1+ data.values.max())
    colors = [clr[x] for x in data.values]
    
    labels = [str(x)[8:10]+str(x)[4:7] for x in data.index[[30*i for i in range(1+(data.shape[0]//30))]]]
    
    fg , ax = plt.subplots(figsize = (16,5))
    #plt.xticks(ticks= [31*x for x in range(0,1+ospedalizzati.shape[0]//31)],rotation = 45)
    plt.grid(color = 'grey')
    plt.xticks([30*i for i in range(1+(data.shape[0]//30))] , labels=labels)
    plt.bar(data.index , data.values, width = 1.0 , color = colors)
    
    plt.title(label= title.replace('_',' ') , fontdict ={'fontsize':'xx-large'})   
    
    
def barchartv1(df, field = 'nuovi_positivi' , color_map = 'viridis'):
    df_grouped = df.groupby('data')[field].sum()
    
    clr = sns.color_palette(color_map , n_colors =1+ df_grouped.values.max())
    colors = [clr[x] for x in df_grouped.values]
    fg , ax = plt.subplots(figsize = (16,4))
    plt.bar(df_grouped.index , df_grouped.values, width = 1.0 , color = colors)
    plt.title(label= field.replace('_',' ') , fontdict ={'fontsize':'xx-large'})    
    
def plot_incidenza(regioni_shape , df , end_date , save = False):
    daterange = pd.date_range( end = end_date , periods = 7 , freq='d')
    df = df.loc[daterange[0]:daterange[-1],:].groupby('denominazione_regione')['nuovi_positivi'].sum()
    regioni_df = regioni_shape.join(df , on = 'denominazione_regione' )
    regioni_df.loc[:,'incidenza'] = 1e5*regioni_df['nuovi_positivi']/regioni_df['popolazione']
    
    fig, ax = plt.subplots(figsize= (12,8))
    plt.xticks([])
    plt.yticks([])
    plt.title(f'Incidenza Settimanale \n {end_date}')

    regioni_df.plot(column = 'incidenza',
                               cmap = 'inferno',
                               vmax = 500,
                               vmin = 0,
                               legend =True,
                                   ax = ax)
    if save:
        plt.savefig(fname = f'./images/it_cv{end_date}.png' ,format = 'png')  
        