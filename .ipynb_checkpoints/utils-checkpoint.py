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
        df.replace('P.A. Bolzano' , 'Bolzano')
        df.replace('P.A. Trento'  , 'Trento' )
        df.replace('Emilia-Romagna' , 'Emilia Romagna')
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
    
    return pd.Series(dict(zip(popolazione,nu)), name = 'popolazione' )

def create_italy(shapes : pd.DataFrame , popolazione : pd.Series):
    '''merge population and regions shape'''
    italy = shapes.merge(pd.DataFrame(popolazione).reset_index(),left_on = 'denominazione_regione' , right_on = 'index')
    italy.drop('index',axis = 1 , inplace = True)
    return italy

def update_regioni(regioni , today : str):
    '''update up to any month in 2021'''
    
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