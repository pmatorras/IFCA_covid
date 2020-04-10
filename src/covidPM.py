import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#Function to get variable and error
def choosevars(reg_df,var_str,daily, cond):
    var = reg_df[var_str][cond]
    if daily is True: var=var.diff()
    varerr = np.sqrt(abs(var))
    return var, varerr



def makenormax(var,n):
    varmax=var.max()
    varerr=(np.sqrt(abs(1/var)+(1/varmax))*(var/varmax)).iloc[-n:].fillna(0)
    var=var.iloc[-n:].fillna(0)/varmax
    return var, varerr
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

def plot_region(reg_df, reg_nm, daily,abschange, relative, frommax, dology, display, ninp):
    #Do basic crosschecks to not get meaningless plots
    if relative is True: abschange=False
    cases= reg_df["CASOS"]
    cond=cases>10
    if reg_nm is "Spain": cond=cases>1000
    n=min(ninp,len(cases[cond])-1)

    
    cases, caseserr=choosevars(reg_df,"CASOS", daily, cond)
    hospi, hospierr=choosevars(reg_df,"Hospitalizados", daily, cond)
    serio, serioerr=choosevars(reg_df,"UCI", daily, cond)
    recov, recoverr=choosevars(reg_df,"Recuperados", daily, cond)
    death, deatherr=choosevars(reg_df,"Fallecidos", daily, cond)
    dates = reg_df["FECHA"][cond]
    #Save rows for the general cases
    title = "Total cases for "+reg_nm
    ylab  = "Accumulated cases"
    titad = "Accumulated"
    #Change rows in case daily data is desired
    if(daily is True):
        titad = "Daily"
        title = "Daily new cases for "+reg_nm
        ylab  = "Daily cases"
    #Calculate  changes with respect to the maximum
    if frommax is True:
        activ=cases-recov
        actmax=activ.max()
        activerr = (np.sqrt(abs(np.sqrt(cases+recov)/activ)**2+(1/actmax))*(activ/actmax)).iloc[-n:].fillna(0)
        
        activ = activ.iloc[-n:].fillna(0)/actmax

        #activ, activerr=makenormax(activ,n)
        cases, caseserr=makenormax(cases,n)
        hospi, hospierr=makenormax(hospi,n)
        serio, serioerr=makenormax(serio,n)
        recov, recoverr=makenormax(recov,n)
        death, deatherr=makenormax(death,n)
        dates=dates.iloc[-n:]
        
        title   = titad+" Cases normalised to maximum for"+reg_nm
        ylab    = titad+" Cases" 
    #exit()
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
        title = titad+"Changes with respect to the previous day in "+reg_nm
        ylab  = titad+"cases"
    #Calculate the relative daily change
    if(relative is True):
        cases = 100*cases.pct_change().iloc[-n:].fillna(0)
        hospi = 100*hospi.pct_change().iloc[-n:].fillna(0)
        serio = 100*serio.pct_change().iloc[-n:].fillna(0)
        recov = 100*recov.pct_change().iloc[-n:].fillna(0)
        death = 100*death.pct_change().iloc[-n:].fillna(0)
        title = titad+" changes respect the previous day in "+reg_nm
        ylab  = titad+" change (%)"
        dology=False
        days=np.linspace(1,len(cases[cond]),len(cases[cond]))
        dates=dates.iloc[-n:]
    #Make histograms
    if frommax is True:
        activecases=activ
        activecaseserr=activerr
    else:
        activecases=cases-recov
        activecaseserr=np.sqrt(caseserr*caseserr+recoverr*recoverr)

    if relative is True:
        plt.plot(days, cases,'bo-')
        plt.plot(days, recov,'go-')
    	plt.plot(days, death,'ro-')
        plt.axhline(y=0, color='black',linestyle='--')
    else:
        days=np.linspace(1,len(cases),len(cases))
        plt.errorbar(days,cases,fmt='ko-',yerr=caseserr, label='Casos totales')
        plt.errorbar(days,activecases,fmt='bo-',yerr=activecaseserr, label="Casos activos")
        plt.errorbar(days,recov,fmt='go-',yerr=recoverr)
        plt.errorbar(days,death,fmt='ro-',yerr=deatherr)
        if abschange is False:
            plt.errorbar(days,hospi,fmt='co-',yerr=hospierr)
            plt.errorbar(days,serio,fmt='yo-',yerr=serioerr)
        if frommax is True:
            plt.axhline(y=1, color='black',linestyle='--')
            plt.axhline(y=0, color='olive',linestyle='--')
    #Set up optional displays
    if(relative is False):
        if daily is False: plt.ylim(5,1.2*np.nanmax(cases))
        if dology is True:
            plt.yscale('log')
            if(reg_nm in "Spain") :plt.ylim(10, 1.2*np.nanmax(cases))
    #Add title and legend
    plt.title(title)
    plt.ylabel(ylab)
    plt.legend()
    plt.grid()
    plt.xticks(days,dates, rotation='vertical')
    #plt.show()
    histo=nameplot(reg_nm,daily,abschange,relative,dology)
    plt.tight_layout()
    plt.savefig(histo, dpi=200)
    print "plot saved in:\n",histo
    if display is True: os.system('display '+histo)
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
    parser.add_option('--display' , dest='display' , help='display', default=False, action='store_true')
    parser.add_option('--frommax' , dest='frommax' , help='display', default=False, action='store_true')
    parser.add_option('--n' , dest='ndays' , help='display', default='100')
    (opt, args) = parser.parse_args()


    #Check file and open it
    new=False
    if(new is True):os.system('wget -N https://covid19.isciii.es/resources/serie_historica_acumulados.csv  --directory=../data')

    csv_file='../data/serie_historica_acumulados.csv'
    df = pd.read_csv(csv_file)
    df = df.dropna() #to remove the last rows, it used to be df=df[:-2]
    df = df.fillna(0)

    #del df['Unnamed: 7']
    #print df
    #Define possible regions
    regions={"Cantabria" : "CB", "Canarias"   : "CN",\
             "Catalunya" : "CT", "Pais Vasco" : "PV",\
             "Madrid"    : "MD", "Andalucia"  : "AN",\
             "Asturias"  : "AS"}
    #Call function given the input
    for region in regions:
        if opt.region not in region: continue
        regdf = df.loc[df["CCAA"] == regions[region]]
        plot_region(regdf, region, opt.daily,opt.change,opt.rel,opt.frommax,opt.logy, opt.display,  int(opt.ndays))

    if opt.spain is True:
        df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y').dt.date
        dfsum = df.groupby('FECHA', as_index=False).sum()

        x=dfsum["Recuperados"].diff()
        y=dfsum["Fallecidos"].diff()
        #plt.scatter(x,y)
        
        #plt.show()
        plot_region(dfsum,"Spain",opt.daily,opt.change, opt.rel, opt.frommax,opt.logy, opt.display,int(opt.ndays))


