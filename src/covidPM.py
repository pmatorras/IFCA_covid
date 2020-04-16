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




def findreg(region):
    inreg=region.lower()
    ccaa='none'
    regnm='none'
    for country in countries:
        cname=countries[country]
        if inreg in country.lower():
            regnm=cname
            inreg=country
    if('none' in regnm):
        for region in regions:
            if inreg in region.lower() :
                inreg = 'sp'
                regnm = region
                ccaa  = regions[region]
                print "region is", region
        if len(inreg.split('_'))>1: regnm='Switzerland'#print "this is a canton"
        elif(inreg  is not 'sp' and len(inreg.split('_'))<2):
            print "Country or region",inreg,"not found"
            exit()
    return regnm,inreg,ccaa

def handledf(df,inreg,display):
#Depending on the inreg output, open the file accordingly
    if "sp" in inreg:
        if display is True: shownotes(df)
        df.dropna()
        if 'none' not in ccaa:
            regdf = df.loc[df["CCAA"] == ccaa]
        else:
            df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y').dt.date
            regdf = df.groupby('FECHA', as_index=False).sum()
    elif 'it' in inreg:
        regdf = df
        df['data']=pd.to_datetime(df['data'], errors='coerce').dt.date
    elif 'fr' in inreg:
        dffra = df.loc[df["granularite"]=="pays"]
        regdf = dffra.loc[dffra["source_nom"].str.contains('Minis')]

    elif 'uk' in inreg:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        regdf= df.sort_values(by='Date')
    elif 'ch' in inreg:
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
    parser.add_option('--frommax' , dest='frommax' , help='display', default=False, action='store_true')
    parser.add_option('--n' , dest='ndays' , help='number of days to show', default='100')
    parser.add_option('--new' , dest='new' , help='renew csv', default=False, action='store_true')
    (opt, args) = parser.parse_args()

    if "none" in opt.region:
        print "choose a region"
        exit()
    datdir='../data/'
    ndays=int(opt.ndays)

    regs=''
    if 'all' in opt.region.lower():
        for country in countries:
            regs+=country+'_'

            #regs=opt.region
    for reg in regs.split('_'):
        print reg
    #exit()
    regnm, inreg, ccaa =findreg(opt.region)
    path=paths[inreg.split('_')[0]]

    if(opt.new is True):
        print "downloading files"
        os.system('wget -N '+path+' --directory='+datdir)    
    csv_file=datdir+path.split('/')[-1]
    
    df = pd.read_csv(csv_file)

    regdf=handledf(df, inreg, opt.display)
    print regdf, regnm
    plot_region(regdf, regnm, opt.daily,opt.change,opt.rel,opt.frommax,opt.logy, opt.display, ndays)
