#see me ha borrado hahaha
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize


def fit_function(x,a):
    return np.exp(a*x)

def data_region(region):
    return df.loc[df["CCAA Codigo ISO"] == region]

def plot_region(df_region, region_name):
    dailycases = df_region["Casos "].diff()
    dailyhospi = df_region["Hospitalizados"].diff()
    dailyserio = df_region["UCI"].diff()
    dailyrecov = df_region["Recuperados"].diff()
    dailydeath = df_region["Fallecidos"].diff()
    dates = df_region["Fecha"]
    days = np.linspace(1, len(dailycases), len(dailycases))
    dailycases = np.nan_to_num(dailycases, nan = 1)

    ### Print
    plt.errorbar(days, dailycases, fmt='bo-', yerr=np.sqrt(dailycases))
    plt.errorbar(days, dailyhospi, fmt='co-', yerr=np.sqrt(dailyhospi))
    plt.errorbar(days, dailyserio, fmt='yo-', yerr=np.sqrt(dailyserio))
    plt.errorbar(days, dailyrecov, fmt='go-', yerr=np.sqrt(dailyrecov))
    plt.errorbar(days, dailydeath, fmt='ro-', yerr=np.sqrt(dailydeath))
    plt.title("Evolucion COVID19 en " + region_name)
    plt.legend()
    #plt.yscale('log')
    plt.xticks(days,dates, rotation='vertical', fontsize = 5)
    plt.savefig(region_name + ".pdf")
    print("Plot saved as " + region_name + ".pdf")
    plt.clf()

def fit_curve(days, dailycases, save_name):
    params, params_covariance = optimize.curve_fit(fit_function, days, dailycases, p0=[2])
    print(params, params_covariance)
    y_fit = np.exp(days*params[0])
    plt.errorbar(days, dailycases, fmt='purple', yerr=np.sqrt(dailycases), label = r"$\left<NFit\right>$ = {0}".format(np.exp(params[0])))
    plt.plot(days, y_fit)
    #plt.title("COVID19 Cases in " + save_name)
    #plt.savefig(save_name + "_Fit.pdf")
    #print("Figure saved as " + save_name + "_Fit.pdf")


def derivative_t(df, ID, min_case):
    ### Total Number of Cases
    region_cases = df[ID]
    data_len = int(len(region_cases)/19)
    reg_cas_list = np.nan_to_num(region_cases).tolist()
    reshape_cases = np.reshape( reg_cas_list, (data_len,19))
    total_cases = np.sum(reshape_cases, axis = 1)
    ### Dummy days list
    Cant = df.loc[df["CCAA Codigo ISO"] == "MD"]
    dates = Cant["Fecha"]
    days = np.linspace(1, len(total_cases), len(total_cases))
    ### Plot
    cases_above = total_cases > min_case
    plt.errorbar(days[cases_above][:-1], np.diff(total_cases[cases_above]), fmt='bo-', yerr=np.sqrt(np.diff(total_cases[cases_above])), label = "Cases")
    plt.legend()
    plt.yscale('log')
    plt.xticks(days[cases_above][:-1],dates[cases_above][:-1], rotation='vertical', fontsize = 5)
    plt.title("COVID19 Cases in Spain")
    plt.ylabel(r"$\frac{dN(t)}{dt}$")
    plt.savefig("Spain_derivative.pdf")
    print("Figure saved as " + "Spain_derivative.pdf")
    #plt.show()
    plt.clf()



def total_cases(df, ID, min_case):
    ### Total Number of Cases
    region_cases = df[ID]
    data_len = int(len(region_cases)/19)
    reg_cas_list = np.nan_to_num(region_cases).tolist() 
    reshape_cases = np.reshape( reg_cas_list, (data_len,19))
    total_cases = np.sum(reshape_cases, axis = 1)
    ### Dummy days list
    Cant = df.loc[df["CCAA Codigo ISO"] == "MD"]
    dates = Cant["Fecha"]
    days = np.linspace(1, len(total_cases), len(total_cases))
    ### Plot
    cases_above = total_cases > min_case
    plt.errorbar(days[cases_above], total_cases[cases_above], fmt='bo-', yerr=np.sqrt(total_cases[cases_above]), label = "Cases")
    #fit_curve(days[cases_above], total_cases[cases_above], "Spain")
    x = np.linspace(days[cases_above][0], days[cases_above][-1], 1000)
    #plt.plot(x, np.exp(0.3*x), color='b', label = r"$\left<N\right>$ = {0}".format(np.exp(0.3)))
    #plt.plot(x, np.exp(0.35*x), color='g', label = r"$\left<N\right>$ = {0}".format(np.exp(0.35)))
    #plt.plot(x, np.exp(0.4*x), color='r', label = r"$\left<N\right>$ = {0}".format(np.exp(0.4)))
    plt.legend()
    #plt.yscale('log')
    plt.ylabel(r"$N(t)$")
    plt.xticks(days[cases_above],dates[cases_above], rotation='vertical', fontsize = 5)
    plt.title("COVID19 Cases in Spain")
    plt.savefig("Spain_Cases.pdf")
    print("Figure saved as " + "Spain_Cases.pdf")
    #plt.show()
    plt.clf()


def derivative_N(df, ID, min_case):
    ### Total Number of Cases
    region_cases = df[ID]
    data_len = int(len(region_cases)/19)
    reg_cas_list = np.nan_to_num(region_cases).tolist()
    reshape_cases = np.reshape( reg_cas_list, (data_len,19))
    total_cases = np.sum(reshape_cases, axis = 1)
    ### Derivative
    deriv = np.diff(total_cases)
    ### Average
    average_N = total_cases[:-1]/2 + total_cases[1:]/2
    plt.scatter(average_N, deriv)
    plt.title(r"Curve $dN(t)/dt = \mu(t)\cdot N(t)$ COVID19 Spain")
    plt.xlabel(r"$N(t)$")
    plt.ylabel(r"$\frac{dN(t)}{dt}$")
    plt.savefig("Spain_dt_N.pdf")
    #plt.show()
    print("Figure Saved As Spain_dt_N.pdf")
    plt.clf()

def infection_factor(df, ID, min_case):
    ### Total Number of Cases
    region_cases = df[ID]
    data_len = int(len(region_cases)/19)
    reg_cas_list = np.nan_to_num(region_cases).tolist()
    reshape_cases = np.reshape( reg_cas_list, (data_len,19))
    total_cases = np.sum(reshape_cases, axis = 1)
    cases_above = total_cases > min_case
    days = np.linspace(1, len(total_cases), len(total_cases))
    total_cases = total_cases[cases_above]
    ### Derivative
    deriv = np.diff(total_cases)
    ### Average
    average_N = total_cases[:-1]/2 + total_cases[1:]/2
    ### Dummy days list
    Cant = df.loc[df["CCAA Codigo ISO"] == "MD"]
    dates = Cant["Fecha"]
    ### Plot
    plt.scatter(days[cases_above][:-1], np.exp(np.divide(deriv,average_N)))
    ### Fit decrease
    decrease = np.exp(np.divide(deriv,average_N))[-9:-1]
    fit_par = np.polyfit([i for i in range(0,8)], decrease, 1)
    print(fit_par)
    print("Time to reduce IF to 0.5: {0} days".format(int(-fit_par[1]*0.5/fit_par[0])))
    x_fit = np.linspace(0,8, 100)
    y_fit = fit_par[0]*x_fit + fit_par[1]
    plt.plot(np.flip(days[cases_above][-2]-x_fit), y_fit, color = "r")
    plt.title(r"Infection Factor COVID19 Spain")
    plt.xlabel(r"$t [days]$")
    plt.ylabel(r"$\mu(t)$")
    plt.xticks(days[cases_above][:-1],dates[cases_above][:-1], rotation='vertical', fontsize = 5)
    plt.savefig("Spain_InfectionFactor.pdf")
    #plt.show()
    print("Figure Saved As Spain_InfectionFactor.pdf")
    plt.clf()

### Download file
csv_file = "serie_historica_acumulados.csv"
df = pd.read_csv(csv_file)

### Infection Factor
infection_factor(df, "Casos ", 100)
### Derivative Plot
derivative_t(df, "Casos ", 100)

### Total Cases
total_cases(df, "Casos ", 100)

### Regional Cases
Madrid = data_region("MD")
plot_region(Madrid, "Madrid")



