import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.compat import u
pd.options.mode.chained_assignment = None  # default='warn'

#print out warnings in spanish case
def shownotes(df):
    ccaas=df["CCAA"]
    uccaa=pd.Series(map(u,ccaas[ccaas.str.len()>2]))
    for i in range(0,len(uccaa)):print uccaa[i]

if __name__ == '__main__':
    exec(open("plot_covid.py").read())

    #Define options
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('--reg' , dest='region' , help='# region to plot', default="none")
    parser.add_option('--daily' , dest='daily' , help='check per day cases', default=False, action='store_true')
    parser.add_option('--change' , dest='change' , help='check per day abs changes', default=False, action='store_true')
    parser.add_option('--rel' , dest='rel' , help='check per dayrelative changes', default=False, action='store_true')
    parser.add_option('--logy' , dest='logy' , help='do logy', default=False, action='store_true')
    parser.add_option('--display' , dest='display' , help='display', default=False, action='store_true')
    parser.add_option('--frommax' , dest='frommax' , help='display', default=False, action='store_true')
    parser.add_option('--n' , dest='ndays' , help='number of days to show', default='100')
    parser.add_option('--new' , dest='new' , help='renew csv', default=False, action='store_true')
    (opt, args) = parser.parse_args()

    if "none" in opt.region:
        print "choose a region"
        exit()
    inreg=opt.region.lower()
    datdir='../data/'
    ndays=int(opt.ndays)

    #Check file and open it
    if  ('it' in inreg): path= 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
    elif('fr' in inreg): path= 'https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv'
    elif('uk' in inreg): path= 'https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-totals-uk.csv'
    elif('ch' in inreg): path= 'https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total.csv'
    elif('us' in inreg): path= 'https://covidtracking.com/api/us/daily.csv'
    else:                path= 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'
    if(opt.new is True):
        print "downloading files"
        os.system('wget -N '+path+' --directory='+datdir)    
    csv_file=datdir+path.split('/')[-1]
    
    df = pd.read_csv(csv_file)
    if opt.display is True and 'sp' in inreg:shownotes(df)
    
    if 'sp' in inreg: df = df.dropna() #it used to be df=df[:-2]
    df = df.fillna(0)

    cantons={"GE": "Geneve", "ZH": "Zurich"}
    #Define possible regions
    regions={"Cantabria" : "CB", "Canarias"   : "CN",\
             "Catalunya" : "CT", "Pais Vasco" : "PV",\
             "Madrid"    : "MD", "Andalucia"  : "AN",\
             "Asturias"  : "AS"}
    #Call function given the input
    if "sp" in opt.region.lower():
        df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y').dt.date
        regdf = df.groupby('FECHA', as_index=False).sum()
        regnm = "Spain"
    elif 'it' in inreg:
        regdf = df
        regnm = "Italy"
        df['data']=pd.to_datetime(df['data'], errors='coerce').dt.date
    elif 'fr' in inreg:
        dffra = df.loc[df["granularite"]=="pays"]
        regdf = dffra.loc[dffra["source_nom"].str.contains('Minis')]
        regnm = "France"

    elif 'uk' in inreg:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        regdf= df.sort_values(by='Date')
        regnm= "UK"
        #exit()
    elif 'ch' in inreg:
        regnm= "Switzerland"
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        if len(inreg.split('_'))>1:
            canton=inreg.split('_')[1].upper()
            regdf=df.loc[df["abbreviation_canton_and_fl"]==canton]
            if len(regdf)<1:
                print "unknown canton"
                exit()
            else:
                if canton in cantons:
                    regnm+='_'+cantons[canton]
                else:
                    regnm+='_'+canton
        else:
            dfch = df.groupby('date', as_index=False).sum()
            regdf = dfch[dfch['ncumul_conf'].diff()>0]#, regdf['date']
            if len(dfch)>len(regdf): print "MISSING DATA"
        #exit()
    elif 'us' in inreg:
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d').dt.date
        regdf= df.sort_values(by='date')
        regnm= "USA"
        #exit()
    else:
        for region in regions:
            if opt.region not in region: continue
            regdf = df.loc[df["CCAA"] == regions[region]]
            regnm = region
    plot_region(regdf, regnm, opt.daily,opt.change,opt.rel,opt.frommax,opt.logy, opt.display, ndays)
