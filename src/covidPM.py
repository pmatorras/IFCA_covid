import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.compat import u
pd.options.mode.chained_assignment = None  # default='warn'
def shownotes(df):
    ccaas=df["CCAA"]
    uccaa=pd.Series(map(u,ccaas[ccaas.str.len()>2]))
    for i in range(0,len(uccaa)):print uccaa[i]
    

def norm_max(var,n):
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


#Function to get variable and error
def choosevars(reg_df,reg_nm,var_str,daily, absch, relch,frommax, n, cond):
    if("act" in var_str.lower()):
        if('France' in reg_nm) :
            var = reg_df["cas_confirmes"]- reg_df["gueris"]
        elif('US' in reg_nm):
            var = reg_df["positive"]-reg_df["recovered"]
        else:
            var = reg_df["CASOS"]- reg_df["Recuperados"]

    else:
        var = reg_df[var_str]
    var=var[cond]
    if daily is True: var=var.diff()
    varerr = np.sqrt(abs(var))
    if n<len(var):
        var    = var.iloc[-n:]
        varerr = varerr.iloc[-n:]
    if absch is True:
        varerr = geterrsum(var,n, relch)
        var    = var.diff().fillna(0)
    if relch is True:
        varerr = 1#geterrsum(var,n,relch)
        #print varerr
        var = 100*var.pct_change().fillna(0)
    if frommax is True:
        var,varerr= norm_max(var,n)
    return var, varerr

#Choose title for the histograms
def choosetitle(reg_nm,daily,absch,relch,frommax):
    title = "Total cases for "+reg_nm
    ylab  = "Accumulated cases"
    titad = "Accumulated"
    #Add different title depending on the type of plot
    if(daily is True):
        titad = "Daily"
        title = "Daily new cases for "+reg_nm
        ylab  = "Daily cases"
    if absch is True:
        title = titad+"Changes with respect to the previous day in "+reg_nm
        ylab  = titad+"cases"
    if(relch is True):
        title = titad+" changes respect the previous day in "+reg_nm
        ylab  = titad+" change (%)"
    if frommax is True:
        title   = titad+" Cases normalised to maximum for"+reg_nm
        ylab    = titad+" Cases" 
    return title, ylab, titad

#Function to, given the parameters, give a name
def nameplot(reg_nm,daily,absch,relch,frommax,dology):
    hname='accumulated'
    if daily is True: hname='daily'
    if absch is True: hname+='_abschange'
    if relch is True: hname+='_relchange'
    if frommax is True: hname+='_frommax'
    hname+='_'+reg_nm
    if dology is True: hname+='_log'
    hname+='.png'
    hfold='../Plots/'
    os.system("mkdir -p "+hfold)
    histo=hfold+hname
    return histo

regvars={'cases':{'sp':'CASOS'         , 'it':'totale_casi',\
                  'fr':'cas_confirmes' , 'us':'positive'},\
         'activ':{'sp':'Casos Activos' , 'it':'totale_positivi',\
                  'fr':'cas_actifs'    , 'us':'activeCases'},\
         'hospi':{'sp':'Hospitalizados', 'it':'totale_ospedalizzati',\
                  'fr':'hospitalises'  , 'us':'hospitalizedCurrently'},\
         'serio':{'sp':'UCI'           , 'it':'terapia_intensiva',\
                  'fr':'hospitalises'  , 'us':'inIcuCurrently'},\
         'recov':{'sp':'Recuperados'   , 'it':'ricoverati_con_sintomi',\
                  'fr':'gueris'        , 'us':'recovered'},\
         'death':{'sp':'Fallecidos'    , 'it':'deceduti',\
                  'fr':'deces'         , 'us':'death'},\
         'date' :{'sp':'FECHA'         , 'it':'data', 'fr':'date', 'us': 'date'}
}
labdaily={'sp':' diarios', 'it':' giornaliero', 'fr':' par jour', 'us': ' per day'}

def plot_region(reg_df, reg_nm, daily,absch, relch, frommax, dology, display, ninp):
    #Do basic crosschecks to not get meaningless plots
    if relch is True:
        absch=False
        frommax=False
    regs='sp'
    if 'it' in reg_nm.lower(): regs='it'
    if 'fr' in reg_nm.lower(): regs='fr'
    if 'us' in reg_nm.lower(): regs='us'
    cases= reg_df[regvars['cases'][regs]]
    cond=cases>10
    if reg_nm in ["Spain","Italy"]: cond=cases>1000
    n=min(ninp,len(cases[cond])-1)

    if regs is 'fr':
        deathhos=reg_df[regvars['death'][regs]]
        deathout= reg_df['deces_ehpad']
        death = deathhos+deathout
        reg_df[regvars['death'][regs]]=death
        #reg_df=reg_df.deces+reg_df.deces_ehpad# type(death)

    activ, activerr=choosevars(reg_df, reg_nm, regvars['activ'][regs], daily, absch,relch,frommax, n, cond)
    cases, caseserr=choosevars(reg_df, reg_nm, regvars['cases'][regs], daily, absch,relch,frommax, n, cond)
    hospi, hospierr=choosevars(reg_df, reg_nm, regvars['hospi'][regs], daily, absch,relch,frommax, n, cond)
    serio, serioerr=choosevars(reg_df, reg_nm, regvars['serio'][regs], daily, absch,relch,frommax, n, cond)
    recov, recoverr=choosevars(reg_df, reg_nm, regvars['recov'][regs], daily, absch,relch,frommax, n, cond)
    death, deatherr=choosevars(reg_df, reg_nm, regvars['death'][regs], daily, absch,relch,frommax, n, cond)
    days=np.linspace(1,len(cases),len(cases))
    dates = reg_df[regvars['date'][regs]][cond].iloc[-n:]
    #print dates, type(dates)

    #Make histograms
    title,ylab,titad= choosetitle(reg_nm,daily,absch,relch,frommax)
    labes=''
    if daily is True:labes=labdaily[regs]
    plt.errorbar(days,activ,fmt='bo-',yerr=activerr, label=regvars['activ'][regs]+labes)
    plt.errorbar(days,cases,fmt='ko-',yerr=caseserr, label=regvars['cases'][regs]+labes)
    plt.errorbar(days,recov,fmt='go-',yerr=recoverr, label=regvars['recov'][regs]+labes)
    plt.errorbar(days,death,fmt='ro-',yerr=deatherr, label=regvars['death'][regs]+labes)
    if  True not in [absch,relch]:# and "Sp" not in reg_nm:
        plt.errorbar(days,hospi,fmt='co-',yerr=hospierr)
        plt.errorbar(days,serio,fmt='yo-',yerr=serioerr)
    if frommax is True:
        plt.axhline(y=1, color='black',linestyle='--')
        plt.axhline(y=0, color='olive',linestyle='--')
        logy=False
        ymin=min(0,min(recov), min(serio), min(hospi))-0.1
        plt.ylim(ymin,1.1)
    #Set up optional displays
    if(relch is False):
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

    histo=nameplot(reg_nm,daily,absch,relch,frommax,dology)
    plt.tight_layout()
    plt.savefig(histo, dpi=200)
    print "plot saved in:\n",histo
    if display is True: os.system('display '+histo)

if __name__ == '__main__':

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
    print "plot"
   
    plot_region(regdf, regnm, opt.daily,opt.change,opt.rel,opt.frommax,opt.logy, opt.display, ndays)
