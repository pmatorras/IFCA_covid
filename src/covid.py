#see me ha borrado hahaha
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
csv_file='../serie_historica_acumulados.csv'
df=pd.read_csv(csv_file)

print df.columns

Cant= df.loc[df["CCAA Codigo ISO"] == "CN"]

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
plt.title("Cantbria")
plt.legend()
plt.yscale('log')
plt.xticks(days,dates, rotation='vertical')
plt.show()
