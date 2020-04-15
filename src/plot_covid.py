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
def choosevars(reg_df,reg_nm,var_str,daily, absch, relch,frommax, n, cond,fmtvar):
    regs=getregs(reg_nm)
    varnm=regvars[var_str][regs]
    if("act" in var_str.lower()):
        var=reg_df[regvars['cases'][regs]]-reg_df[regvars['recov'][regs]]-reg_df[regvars['death'][regs]]
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
    dates = reg_df[regvars['date'][regs]][cond].iloc[-n:]
    labes=''
    if daily is True:labes=labdaily[regs]
    if max(var>0):
        plt.errorbar(days,var,fmt=fmtvar,yerr=varerr, label=varnm+labes)

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
        title   = titad+" Cases normalised to maximum for "+reg_nm
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

def plot_region(reg_df, reg_nm, daily,absch, relch, frommax, dology, display, ninp):
    #Do basic crosschecks to not get meaningless plots                                                            
    if relch is True:
        absch=False
        frommax=False
    regs  = getregs(reg_nm)
    cases = reg_df[regvars['cases'][regs]]
    cond  = cases>10
    if reg_nm in ["Spain","Italy"]: cond=cases>1000
    n=min(ninp,len(cases[cond])-1)

    #Make histograms                                                                                              
    title,ylab,titad= choosetitle(reg_nm,daily,absch,relch,frommax)
    if regs not in 'uk':
        activ, activerr=choosevars(reg_df, reg_nm, 'activ', daily, absch,relch,frommax, n, cond, 'bo-')
    cases, caseserr=choosevars(reg_df, reg_nm, 'cases', daily, absch,relch,frommax, n, cond, 'ko-')
    if True not in [absch,relch] and regs not in ['sp', 'uk']:
        hospi, hospierr=choosevars(reg_df, reg_nm, 'hospi', daily, absch,relch,frommax, n, cond, 'co-')
        serio, serioerr=choosevars(reg_df, reg_nm, 'serio', daily, absch,relch,frommax, n, cond, 'yo-')
    if regs not in 'uk':
        recov, recoverr=choosevars(reg_df, reg_nm, 'recov', daily, absch,relch,frommax, n, cond, 'go-')
    death, deatherr=choosevars(reg_df, reg_nm, 'death', daily, absch,relch,frommax, n, cond, 'ro-')
    days=np.linspace(1,len(cases),len(cases))
    dates = reg_df[regvars['date'][regs]][cond].iloc[-n:]
    if frommax is True:
        plt.axhline(y=1, color='black',linestyle='--')
        plt.axhline(y=0, color='olive',linestyle='--')
        logy=False
        if regs   in 'uk': ymin=-0.1
        elif regs in 'sp': ymin=min(0,min(recov))-0.1
        else :ymin=min(0,min(recov), min(hospi))-0.1
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
