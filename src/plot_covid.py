#get normalised to max values                               
import warnings, os, time, optparse
from datetime import date, datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.compat import u
pd.options.mode.chained_assignment = None  # default='warn' 

def ini_parts(ini):
    cou_ini=ini[0]
    reg_ini=ini[1]
    return cou_ini, reg_ini


def norm_max(var):
    varmax=var.max()
    varerr=(np.sqrt(abs(1/var)+(1/varmax))*(var/varmax)).fillna(0)
    var=var.fillna(0)/varmax
    return var, varerr
'''
Small function to take advantage of the fact of the poisonian unc is the square root, and the unc of the difference is the sqrt of each error squared                       
'''
def geterrsum(var, relch):
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
def choosevars(reg_df,cou_ini,var_str,daily, absch, relch,frommax, n, cond,fmtvar, doroll):
    cou_ini, reg_ini= ini_parts(ini)
    var_nm = regvars[var_str][cou_ini]
    msize = 4
    dashl = '-'
    ali='left'
    if("act" in var_str.lower()):
        ali = 'right'
        var = reg_df[regvars['cases'][cou_ini]]-reg_df[regvars['recov'][cou_ini]]-reg_df[regvars['death'][cou_ini]]
    else:
        var = reg_df[var_nm]
    var  = var[cond]
    
    if daily is True:
        var  =var.diff()
    varmax  = int(max(var.fillna(0)))
    varerr  = np.sqrt(abs(var))
    
    if absch is True:
        varerr = geterrsum(var, relch)
        var    = var.diff().fillna(0)
    if relch is True:
        varerr = 1#geterrsum(var,n,relch)                                  
        var    = 100*var.pct_change().fillna(0)
    if frommax is True:
        var ,varerr  = norm_max(var)
        if varmax<100: varerr=pd.Series(np.zeros(len(var)))
    #print varm, var
    if doroll is True :
        msize = 2
        dashl = ':'
        varm  = var.rolling(7).mean().fillna(0)
    else:
        varm =var
    if n<len(var):
        var    = var.iloc[-n:]
        varerr = varerr.iloc[-n:]
        varm   = varm.iloc[-n:]
    
    varimax = var.reset_index(drop=True).idxmax()

    
    fmtdata = fmtvar+dashl
    days=np.linspace(1,len(var),len(var))
    dates = reg_df[regvars['date'][cou_ini]][cond].iloc[-n:]
    #exit()
    labes=''

    
    if daily is True:labes=labdaily[cou_ini]
    if max(var>0):
        plt.errorbar(days,var,fmt=fmtdata,yerr=varerr,lw=0.4, label=var_nm+labes, markersize=msize)
        plt.plot(days,varm, color=fmtvar[0],linestyle='-',lw=1.25,label='_nolegend_')
        if daily is True: plt.axvline(x=days[varimax],color=fmtvar[0],linestyle='dotted')
        plt.annotate(str(varmax), (days[varimax], 1.05*max(var)), color=fmtvar[0],weight='bold', fontsize=7, horizontalalignment=ali)
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

def getcond(cases,cou_ini,reg_ini, ninp):
    ncas  = 10
    if cou_ini in ['sp','uk','us','fr']: ncas=1000
    if reg_ini in 'CB': ncas=3
    cond=cases>ncas
    n=min(ninp,len(cases[cond])-1)
    return cond, n

def region_stats(reg_df, ini, daily,absch, relch, frommax, dology, display, ninp, doroll):
    #Do basic crosschecks to not get meaningless plots
    cou_ini, reg_ini= ini_parts(ini)
    if relch is True:
        absch=False
        frommax=False
    regs  = cou_ini
    cases = reg_df[regvars['cases'][cou_ini]]
    cond,n= getcond(cases,cou_ini, reg_ini, ninp)
    #Make histograms                                                                                              
    hist_nm, plot_nm   = nameplot(cou_ini,reg_ini,daily,absch,relch,frommax,dology)
    title,ylab,titad = choosetitle(plot_nm,daily,absch,relch,frommax)
    if cou_ini not in 'uk':
        activ, activerr=choosevars(reg_df, cou_ini, 'activ', daily, absch,relch,frommax, n, cond, 'bo',doroll)
    cases, caseserr=choosevars(reg_df, cou_ini, 'cases', daily, absch,relch,frommax, n, cond, 'ko',doroll)
    if True not in [absch,relch] and cou_ini not in ['sp', 'uk']:
        hospi, hospierr=choosevars(reg_df, cou_ini, 'hospi', daily, absch,relch,frommax, n, cond, 'co',doroll)
        serio, serioerr=choosevars(reg_df, cou_ini, 'serio', daily, absch,relch,frommax, n, cond, 'yo',doroll)
    if cou_ini not in 'uk':
        recov, recoverr=choosevars(reg_df, cou_ini, 'recov', daily, absch,relch,frommax, n, cond, 'go',doroll)
    death, deatherr=choosevars(reg_df, cou_ini, 'death', daily, absch,relch,frommax, n, cond, 'ro',doroll)
    days=np.linspace(1,len(cases),len(cases))
    dates = reg_df[regvars['date'][cou_ini]][cond].iloc[-n:]
    if frommax is True:
        plt.axhline(y=1, color='black',linestyle='--')
        plt.axhline(y=0, color='olive',linestyle='--')
        logy=False
        if cou_ini   in 'uk': ymin=-0.1
        elif cou_ini in 'sp': ymin=min(0,min(activ),min(recov))-0.1
        else :ymin=min(0,min(recov), min(hospi))-0.1
        plt.ylim(ymin,1.1)
    #Set up optional displays                                                                                     
    if(relch is False):
        if daily is False: plt.ylim(5,1.2*np.nanmax(cases))
        if dology is True:
            plt.yscale('log')
            ncas=100
            if cou_ini in 'ch' :ncas=10
            plt.ylim(0.5*ncas, 1.2*np.nanmax(cases))

    #Add title and legend                                                                                         
    plt.title(title)
    plt.ylabel(ylab)
    plt.legend()
    plt.grid()
    plt.xticks(days,dates, rotation='vertical')

    
    plt.tight_layout()
    plt.savefig(hist_nm, dpi=200)
    plt.close()
    print "plot saved in:\n",hist_nm
    if display is True: os.system('display '+hist_nm)



def compare_curves(alldf, ini, daily, absch, relch, frommax, logy, disp, ninp):
    print "in"
    cols=['b','g','r','c','m','y','k']
    for i,df in enumerate(alldf):
        reg_df=alldf[df]
        cases = reg_df[regvars['cases'][cou_ini]]
        cond,n= getcond(cases,cou_ini, reg_ini, ninp)

        cases,caseserr=choosevars(reg_df, ini, 'cases', daily, absch,relch,frommax, n, cond, cols[i]+'o-')
        death,deatherr=choosevars(reg_df, ini, 'death', daily, absch,relch,frommax, n, cond, cols[i]+'o:')
        plt.legend()
    plt.show()
    
