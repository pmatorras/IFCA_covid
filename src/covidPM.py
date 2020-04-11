import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def makenormax(var,n):
    varmax=var.max()
    varerr=(np.sqrt(abs(1/var)+(1/varmax))*(var/varmax)).iloc[-n:].fillna(0)
    var=var.iloc[-n:].fillna(0)/varmax
    return var, varerr
'''
 Small function to take advantage of the fact of the poisonian unc is the square root, and the unc of the difference is the sqrt of each error squared
'''
def geterrsum(var,n, relch):
    line = pd.Series([0])
    varb = line.append(var, ignore_index=True)
    varres = var.reset_index(drop=True)
    varsum = varb+varres
    varsum = varsum[:-1].fillna(0)
    varerr = np.sqrt(varsum)
    if relch is True:
        varrel= abs(1/varerr)+abs(1/varres)
        varerr= abs(varrel*100*varres.pct_change().fillna(0))
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

#Function to get variable and error
def choosevars(reg_df,var_str,daily, absch, relch, n, cond):
    var = reg_df[var_str][cond]
    if daily is True: var=var.diff()
    varerr = np.sqrt(abs(var))
    if n<len(var):
        var    = var.iloc[-n:]
        varerr = varerr.iloc[-n:]
    if absch is True:
        varerr = geterrsum(var,n, relch)
        var    = var.diff().fillna(0)
    if relch is True:
        varerr = geterrsum(var,n,relch)
        #print varerr
        var = 100*var.pct_change().fillna(0)

    return var, varerr


def plot_region(reg_df, reg_nm, daily,abschange, relative, frommax, dology, display, ninp):
    #Do basic crosschecks to not get meaningless plots
    if relative is True: abschange=False
    cases= reg_df["CASOS"]
    cond=cases>10
    if reg_nm is "Spain": cond=cases>1000
    n=min(ninp,len(cases[cond])-1)
    absch=abschange
    relch=relative
    cases, caseserr=choosevars(reg_df,"CASOS"         , daily, absch,relch, n, cond)
    hospi, hospierr=choosevars(reg_df,"Hospitalizados", daily, absch,relch, n, cond)
    serio, serioerr=choosevars(reg_df,"UCI"           , daily, absch,relch, n, cond)
    recov, recoverr=choosevars(reg_df,"Recuperados"   , daily, absch,relch, n, cond)
    death, deatherr=choosevars(reg_df,"Fallecidos"    , daily, absch,relch, n, cond)
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
        activerr = (np.sqrt(abs(np.sqrt(cases+recov)/activ)**2+(1/actmax))*(activ/actmax)).fillna(0)
        
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
        days  = np.linspace(1,len(cases),len(cases))
        title = titad+"Changes with respect to the previous day in "+reg_nm
        ylab  = titad+"cases"
    #Calculate the relative daily change
    if(relative is True):
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

    days=np.linspace(1,len(cases),len(cases))
    plt.errorbar(days,cases,fmt='ko-',yerr=caseserr, label='Casos totales')
    plt.errorbar(days,activecases,fmt='bo-',yerr=activecaseserr, label="Casos activos")
    plt.errorbar(days,recov,fmt='go-',yerr=recoverr)
    plt.errorbar(days,death,fmt='ro-',yerr=deatherr)
    if  True not in [abschange,relative]:
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
    parser.add_option('--n' , dest='ndays' , help='number of days to show', default='100')
    parser.add_option('--new' , dest='new' , help='renew csv', default=False, action='store_true')
    (opt, args) = parser.parse_args()


    #Check file and open it
    if(opt.new is True):os.system('wget -N https://covid19.isciii.es/resources/serie_historica_acumulados.csv  --directory=../data')

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


