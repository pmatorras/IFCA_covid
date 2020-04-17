#get normalised to max values                               
import warnings, os, time, optparse
from datetime import date, datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.compat import u
pd.options.mode.chained_assignment = None  # default='warn' 
def norm_max(var,n):
    varmax=var.max()
    varerr=(np.sqrt(abs(1/var)+(1/varmax))*(var/varmax)).iloc[-n:].fillna(\
0)
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


exec(open("variables.py").read())

#Function to get variable and error                                                                              
def choosevars(reg_df,cou_nm,var_str,daily, absch, relch,frommax, n, cond,fmtvar):
    varnm=regvars[var_str][cou_nm]
    if("act" in var_str.lower()):
        var=reg_df[regvars['cases'][cou_nm]]-reg_df[regvars['recov'][cou_nm]]-reg_df[regvars['death'][cou_nm]]
    else:
        var = reg_df[varnm]
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
        var = 100*var.pct_change().fillna(0)
    if frommax is True:
        var,varerr= norm_max(var,n)

    days=np.linspace(1,len(var),len(var))
    dates = reg_df[regvars['date'][cou_ini]][cond].iloc[-n:]
    labes=''
    if daily is True:labes=labdaily[regs]
    if max(var>0):
        plt.errorbar(days,var,fmt=fmtvar,yerr=varerr, label=varnm+labes)

    return var, varerr



#Choose title for the histograms                                                                                 
def choosetitle(plot_nm,daily,absch,relch,frommax):
    title = "Total cases for "+plot_nm
    ylab  = "Accumulated cases"
    titad = "Accumulated"
    #Add different title depending on the type of plot                                                           
    if(daily is True):
        titad = "Daily"
        title = "Daily new cases for "+plot_nm
        ylab  = "Daily cases"
    if absch is True:
        title = titad+"Changes with respect to the previous day in "+plot_nm
        ylab  = titad+"cases"
    if(relch is True):
        title = titad+" changes respect the previous day in "+plot_nm
        ylab  = titad+" change (%)"
    if frommax is True:
        title   = titad+" Cases normalised to maximum for "+plot_nm
        ylab    = titad+" Cases"
    return title, ylab, titad

#Function to, given the parameters, give a name                                                                  
def nameplot(cou_ini, reg_ini,daily,absch,relch,frommax,dology):
    hname='accumulated'
    if daily   is True: hname='daily'
    if absch   is True: hname+='_abschange'
    if relch   is True: hname+='_relchange'
    if frommax is True: hname+='_frommax'
    if 'none' in reg_ini:     plot_nm = countries[cou_ini]
    else:
        if   'ch' in cou_ini: plot_nm = cantons[reg_ini]
        elif 'sp' in cou_ini: plot_nm = regions[reg_ini]
        else:
            print "country", countries[cou_ini], "has no region", reg_ini
            exit()
    hname+='_'+plot_nm
    if dology is True: hname+='_log'
    hname+='.png'
    hfold='../Plots/'
    os.system("mkdir -p "+hfold)
    hist_nm=hfold+hname
    return hist_nm, plot_nm

def plot_region(reg_df, ini, daily,absch, relch, frommax, dology, display, ninp):
    #Do basic crosschecks to not get meaningless plots                                                            
    cou_ini=ini[0]
    reg_ini=ini[1]
    if relch is True:
        absch=False
        frommax=False
    regs  = cou_ini
    cases = reg_df[regvars['cases'][cou_ini]]
    cond  = cases>10
    if cou_ini in ["Spain","Italy"]: cond=cases>1000
    n=min(ninp,len(cases[cond])-1)

    #Make histograms                                                                                              
    hist_nm, plot_nm   = nameplot(cou_ini,reg_ini,daily,absch,relch,frommax,dology)
    title,ylab,titad = choosetitle(plot_nm,daily,absch,relch,frommax)
    if cou_ini not in 'uk':
        activ, activerr=choosevars(reg_df, cou_ini, 'activ', daily, absch,relch,frommax, n, cond, 'bo-')
    cases, caseserr=choosevars(reg_df, cou_ini, 'cases', daily, absch,relch,frommax, n, cond, 'ko-')
    if True not in [absch,relch] and cou_ini not in ['sp', 'uk']:
        hospi, hospierr=choosevars(reg_df, cou_ini, 'hospi', daily, absch,relch,frommax, n, cond, 'co-')
        serio, serioerr=choosevars(reg_df, cou_ini, 'serio', daily, absch,relch,frommax, n, cond, 'yo-')
    if cou_ini not in 'uk':
        recov, recoverr=choosevars(reg_df, cou_ini, 'recov', daily, absch,relch,frommax, n, cond, 'go-')
    death, deatherr=choosevars(reg_df, cou_ini, 'death', daily, absch,relch,frommax, n, cond, 'ro-')
    days=np.linspace(1,len(cases),len(cases))
    dates = reg_df[regvars['date'][cou_ini]][cond].iloc[-n:]
    if frommax is True:
        plt.axhline(y=1, color='black',linestyle='--')
        plt.axhline(y=0, color='olive',linestyle='--')
        logy=False
        if cou_ini   in 'uk': ymin=-0.1
        elif cou_ini in 'sp': ymin=min(0,min(recov))-0.1
        else :ymin=min(0,min(recov), min(hospi))-0.1
        plt.ylim(ymin,1.1)
    #Set up optional displays                                                                                     
    if(relch is False):
        if daily is False: plt.ylim(5,1.2*np.nanmax(cases))
        if dology is True:
            plt.yscale('log')
            if(cou_ini in 'sp') :plt.ylim(10, 1.2*np.nanmax(cases))

    #Add title and legend                                                                                         
    plt.title(title)
    plt.ylabel(ylab)
    plt.legend()
    plt.grid()
    plt.xticks(days,dates, rotation='vertical')

    
    plt.tight_layout()
    plt.savefig(hist_nm, dpi=200)
    print "plot saved in:\n",hist_nm
    if display is True: os.system('display '+hist_nm)
