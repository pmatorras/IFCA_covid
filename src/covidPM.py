#see me ha borrado hahaha
import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
'''
 Small function to take advantage of the fact of the poisonian unc is the square root, and the unc of the difference is the sqrt of each error squared
'''
def geterrsum(var,n):
    line = pd.Series([0])
    varb = line.append(var, ignore_index=True)
    varsum = varb+var.reset_index(drop=True)
    varsum = varsum[:-1].fillna(0).iloc[-n:]
    varerr = np.sqrt(varsum)
    return varerr

#Function to, given the parameters, give a name
def nameplot(reg_nm,daily,abschange,relative,dology):
    hname='accumulated'
    if daily is True: hname='daily'
    if abschange is True: hname+='_abschange'
    if relative  is True: hname+='_relchange'
    hname+='_'+reg_nm
    if dology is True: hname+='_log'
    hname+='.png'
    hfold='../Plots/'
    os.system("mkdir -p "+hfold)
    histo=hfold+hname
    return histo
def plot_region(reg_df, reg_nm, daily,abschange, relative, dology):
    #Do basic crosschecks to not get meaningless plots
    if(relative is True or abschange is True):
        daily=True
        if relative is True: abschange=False
    cases= reg_df["Casos "]
    cond=cases>10
    if reg_nm is "Spain": cond=cases>1000
    n=min(50,len(cases[cond])-1)
    #Save rows for the general cases
    hospi = reg_df["Hospitalizados"][cond]
    serio = reg_df["UCI"][cond]
    recov = reg_df["Recuperados"][cond]
    death = reg_df["Fallecidos"][cond]
    dates = reg_df["Fecha"][cond]
    cases = cases[cond]
    title = "Total cases for "+reg_nm
    ylab  = "Accumulated cases"
    #Change rows in case daily data is desired
    if(daily is True):
        cases = cases.diff()
        hospi = hospi.diff()
        serio = serio.diff()
        recov = recov.diff()
        death = death.diff()
        title = "Daily new cases for "+reg_nm
        ylab  = "Daily cases"
    #Save errors for both total and daily cases
    caseserr=np.sqrt(cases) 
    hospierr=np.sqrt(hospi) 
    serioerr=np.sqrt(serio) 
    recoverr=np.sqrt(recov) 
    deatherr=np.sqrt(death)
    #Calculate the absolute daily change
    if abschange is True:
        #Get errors
        caseserr = geterrsum(cases,n)
        hospierr = geterrsum(hospi,n)
        serioerr = geterrsum(serio,n)
        recoverr = geterrsum(recov,n)
        deatherr = geterrsum(death,n)

        #Make difference
        cases = cases.diff().iloc[-n:].fillna(0)
        hospi = hospi.diff().iloc[-n:]
        serio = serio.diff().iloc[-n:]
        recov = recov.diff().iloc[-n:]
        death = death.diff().iloc[-n:]
        days  = np.linspace(1,len(cases),len(cases))
        title = "Changes with respect to the previous day in "+reg_nm
        ylab  = "Daily cases"
    #Calculate the relative daily change
    if(relative is True):
        cases = 100*cases.pct_change().iloc[-n:].fillna(0)
        hospi = 100*hospi.pct_change().iloc[-n:].fillna(0)
        serio = 100*serio.pct_change().iloc[-n:].fillna(0)
        recov = 100*recov.pct_change().iloc[-n:].fillna(0)
        death = 100*death.pct_change().iloc[-n:].fillna(0)
        title = "Relative changes respect the previous day in "+reg_nm
        ylab  = "Daily change (%)"
        dology=False
        days=np.linspace(1,len(cases[cond]),len(cases[cond]))
        dates=dates.iloc[-n:]
        plt.plot(days, cases,'bo-')
        plt.plot(days, recov,'go-')
    	plt.plot(days, death,'ro-')
        plt.axhline(y=0, color='black',linestyle='--')
    else:
        #Make histograms
        days=np.linspace(1,len(cases),len(cases))
        plt.errorbar(days,cases,fmt='bo-',yerr=caseserr)
        plt.errorbar(days,recov,fmt='go-',yerr=recoverr)
        plt.errorbar(days,death,fmt='ro-',yerr=deatherr)
        if abschange is False:
            plt.errorbar(days,hospi,fmt='co-',yerr=hospierr)
            plt.errorbar(days,serio,fmt='yo-',yerr=serioerr)

    #Set up optional displays
    if(relative is False):
        if daily is False: plt.ylim(5,1.2*np.nanmax(cases))
        if dology is True:
            plt.yscale('log')
            plt.ylim(10, 1.2*np.nanmax(cases))
    #Add title and legend
    plt.title(title)
    plt.ylabel(ylab)
    plt.legend()
    plt.grid()
    plt.xticks(days,dates, rotation='vertical')
    #plt.show()
    histo=nameplot(reg_nm,daily,abschange,relative,dology)
    plt.savefig(histo)
    print "plot saved in:\n",histo
if __name__ == '__main__':

    #Define options
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('--region' , dest='region' , help='# region to plot', default="ignore")
    parser.add_option('--spain' , dest='spain' , help='run whole country', default=False, action='store_true')
    parser.add_option('--daily' , dest='daily' , help='check per day cases', default=False, action='store_true')
    parser.add_option('--change' , dest='change' , help='check per day abs changes', default=False, action='store_true')
    parser.add_option('--rel' , dest='rel' , help='check per dayrelative changes', default=False, action='store_true')
    parser.add_option('--logy' , dest='logy' , help='do logy', default=False, action='store_true')
    (opt, args) = parser.parse_args()


    #Check file and open it
    os.system('wget -N https://covid19.isciii.es/resources/serie_historica_acumulados.csv  --directory=../data')
    csv_file='../data/serie_historica_acumulados.csv'
    df = pd.read_csv(csv_file)
    df = df[:-2]
    df = df.fillna(0)


    #Define possible regions
    regions={"Cantabria" : "CB", "Canarias"   : "CN",\
             "Catalunya" : "CT", "Pais Vasco" : "PV",\
             "Madrid"    : "MD", "Andalucia"  : "AN",\
             "Asturias"  : "AS"}

    #Call function given the input
    for region in regions:
        if opt.region not in region: continue
        regdf = df.loc[df["CCAA Codigo ISO"] == regions[region]]
        plot_region(regdf, region, opt.daily,opt.change,opt.rel,opt.logy)

    if opt.spain is True:
        df['Fecha'] = pd.to_datetime(df['Fecha'],format='%d/%m/%Y').dt.date
        dfsum = df.groupby('Fecha', as_index=False).sum()
        #plot_region(dfsum,"Spain",opt.daily,opt.change, opt.rel, opt.logy)


