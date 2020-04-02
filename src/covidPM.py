#see me ha borrado hahaha
import warnings, os, time, optparse
from datetime import date, datetime
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.system('wget -nc https://covid19.isciii.es/resources/serie_historica_acumulados.csv  --directory=../data')

csv_file='../data/serie_historica_acumulados.csv'


df=pd.read_csv(csv_file)

print df.columns
def plot_region(reg_ISO, reg_nm):
    Cant= df.loc[df["CCAA Codigo ISO"] == reg_ISO]

    dailycases= Cant["Casos "].diff()
    dailyhospi= Cant["Hospitalizados"].diff()
    dailyserio= Cant["UCI"].diff()
    dailyrecov= Cant["Recuperados"].diff()
    dailydeath= Cant["Fallecidos"].diff()
    dates=Cant["Fecha"]
    days=np.linspace(1,len(dailycases),len(dailycases))


    plt.errorbar(days,dailycases,fmt='bo-',yerr=np.sqrt(dailycases))
    plt.errorbar(days,dailyhospi,fmt='co-',yerr=np.sqrt(dailyhospi))
    plt.errorbar(days,dailyserio,fmt='yo-',yerr=np.sqrt(dailyserio))
    plt.errorbar(days,dailyrecov,fmt='go-',yerr=np.sqrt(dailyrecov))
    plt.errorbar(days,dailydeath,fmt='ro-',yerr=np.sqrt(dailydeath))
    plt.title(reg_nm)
    plt.legend()
    plt.yscale('log')
    plt.xticks(days,dates, rotation='vertical')
    plt.show()

if __name__ == '__main__':

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--region' , dest='region' , help='# region to plot', default="Cantabria")

    (opt, args) = parser.parse_args()
    
    regions={"Cantabria" : "CB", "Canarias" : "CN",\
             "Catalunya":"CT", "Pais Vasco" : "PV",\
             "Madrid": "MD"}
    for region in regions:
        if region not in opt.region: continue
        plot_region(regions[region], region)
