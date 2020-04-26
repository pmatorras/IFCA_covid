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

def findreg(inreg):
    reg_ini = 'none'
    reg_nm  = 'none'
    for region in regions:
        if inreg in region.lower() or regions[region].lower().find(inreg) is 0 :
            cou_ini  = 'sp'
            reg_ini  = region
    if 'none' in reg_nm: 
        for canton in cantons:
            if inreg in canton.lower() or cantons[canton].lower().find(inreg) is 0:
                cou_ini = 'ch'
                reg_ini = canton
    return cou_ini, reg_ini


def findcountry(inputreg):
    inreg=inputreg.lower()
    reg_sp  = inreg.split('_')
    cou_ini = 'none'
    reg_ini = 'none'
    for country in countries:
        cname=countries[country]
        if inreg in country.lower() or cname.lower().find(inreg) is 0:
            cou_ini = country
            inreg=country
    if('none' in cou_ini or len(reg_sp)>1):
        cou_ini,reg_ini=findreg(reg_sp[len(reg_sp)-1])
    return cou_ini, reg_ini

def handledf(df,cou_in, reg_in,display):
#Depending on the inreg output, open the file accordingly
    if "sp" in cou_in:
        if display is True: shownotes(df)
        df.dropna()
        if 'none' not in reg_in:
            regdf = df.loc[df["CCAA"] == reg_in]
        else:
            df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y').dt.date
            regdf = df.groupby('FECHA', as_index=False).sum()
    elif 'it' in cou_in:
        regdf = df
        df['data']=pd.to_datetime(df['data'], errors='coerce').dt.date
    elif 'fr' in cou_in:
        dffra = df.loc[df["granularite"]=="pays"]
        regdf = dffra.loc[dffra["source_nom"].str.contains('Minis')]

    elif 'uk' in cou_in:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        regdf= df.sort_values(by='Date')
    elif 'ch' in cou_in:
        df['date'] = pd.to_datetime(df['date']).dt.date
        if 'none' not in reg_in:
            regdf=df.loc[df["abbreviation_canton_and_fl"]==reg_in]
        else:
            dfch = df.groupby('date', as_index=False).sum()
            regdf = dfch[dfch['ncumul_conf'].diff()>0]#, regdf['date']
            if len(dfch)>len(regdf): print "MISSING DATA IN", cou_in
    elif 'us' in cou_in:
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d').dt.date
        regdf= df.sort_values(by='date')
    return regdf


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
    parser.add_option('--frommax' , dest='frommax' , help='normalise to max', default=False, action='store_true')
    parser.add_option('--roll' , dest='roll' , help='do roll mean', default=False, action='store_true')
    
    parser.add_option('--n' , dest='ndays' , help='number of days to show', default='100')
    parser.add_option('--new' , dest='new' , help='renew csv', default=False, action='store_true')
    (opt, args) = parser.parse_args()
    regInp  = opt.region
    daily   = opt.daily
    absch   = opt.change
    relch   = opt.rel
    frommax = opt.frommax
    logy    = opt.logy
    disp    = opt.display
    doroll  = opt.roll
    if "none" in opt.region:
        print "choose a region"
        exit()
    datdir = '../data/'
    ndays  = int(opt.ndays)
    regin  = opt.region.lower()

    doCantons   = False
    doRegions   = False
    doCountries = False
    if('canton' in regin or 'all' in regin): doCantons   = True
    if('region' in regin or 'all' in regin): doRegions   = True
    if('countr' in regin or 'all' in regin): doCountries = True

    #exit()
    reg_plots=''
    if(doRegions is True):
        for region in regions:    reg_plots+=region+'_'
    if(doCantons is True):
        for canton in cantons:    reg_plots+=canton+'_'
    if(doCountries is True):
        for country in countries: reg_plots+=country+'_'
    elif True not in [doCantons,doRegions,doCountries]: reg_plots=opt.region
    if(reg_plots[-1]=='_'): reg_plots= reg_plots[:-1]
    
    alldf={}
    for reg in reg_plots.split('_'):
        cou_ini,reg_ini = findcountry(reg)

        path     = paths[cou_ini]
        csv_file = datdir+path.split('/')[-1]
        if(opt.new is True):
            print "downloading files"
            os.system('wget -N '+path+' --directory='+datdir)    
    
        df    = pd.read_csv(csv_file)
        reg_df = handledf(df, cou_ini,reg_ini, opt.display)
        ini   = [cou_ini,reg_ini]
        region_stats(reg_df, ini, daily,absch,relch,frommax,logy, disp, ndays, doroll)
        
        alldfkey=cou_ini
        if 'none' not in reg_ini:alldfkey+='_'+reg_ini
        alldf[alldfkey]=reg_df
    print alldf.keys()
    #compare_curves(alldf, ini, daily,absch,relch, frommax, logy, disp,ndays)
