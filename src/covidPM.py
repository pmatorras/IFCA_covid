#see me ha borrado hahaha
import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_region(reg_df, reg_nm, daily):
    title="Total cases for "+reg_nm
    cases= reg_df["Casos "]
    hospi= reg_df["Hospitalizados"]
    serio= reg_df["UCI"]
    recov= reg_df["Recuperados"]
    death= reg_df["Fallecidos"]
    
    if(daily==True):
        cases= cases.diff()
        hospi= hospi.diff()
        serio= serio.diff()
        recov= recov.diff()
        death= death.diff()
        title="Total cases for "+reg_nm
        
        
    dates=reg_df["Fecha"]
    days=np.linspace(1,len(cases),len(cases))

    plt.errorbar(days,cases,fmt='bo-',yerr=np.sqrt(cases))
    plt.errorbar(days,hospi,fmt='co-',yerr=np.sqrt(hospi))
    plt.errorbar(days,serio,fmt='yo-',yerr=np.sqrt(serio))
    plt.errorbar(days,recov,fmt='go-',yerr=np.sqrt(recov))
    plt.errorbar(days,death,fmt='ro-',yerr=np.sqrt(death))
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.yscale('log')
    if daily is False: plt.ylim(5,1.2*np.nanmax(cases))
    plt.xticks(days,dates, rotation='vertical')
    plt.show()

if __name__ == '__main__':

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--region' , dest='region' , help='# region to plot', default="Cantabria")

    (opt, args) = parser.parse_args()



    os.system('wget -nc https://covid19.isciii.es/resources/serie_historica_acumulados.csv  --directory=../data')

    csv_file='../data/serie_historica_acumulados.csv'
    

    df=pd.read_csv(csv_file)
    df = df[:-1]
    df= df.fillna(0)
    print df.columns

    regions={"Cantabria" : "CB", "Canarias" : "CN",\
             "Catalunya":"CT", "Pais Vasco" : "PV",\
             "Madrid": "MD"}
    for region in regions:
        if region not in opt.region: continue
        regdf= df.loc[df["CCAA Codigo ISO"] == regions[region]]
        #plot_region(regdf, region, False)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        dfsum= df.groupby('Fecha', as_index=False).sum()
        #DATE COLUMN NOT BEING READ PROPERLY, CHECK THAT OUT
        
        #allregs=dfsum.sort_values(by='Fecha')
        #allregs.Fecha=pd.to_datetime(allregs.Fecha)
        #print type(allregs.Fecha)

