
#Dictionary with variables for each dataframe
regvars={'cases':{'sp':'CASOS'         , 'it':'totale_casi',\
                  'fr':'cas_confirmes' , 'us':'positive' ,\
                  'uk':'ConfirmedCases', 'ch':'ncumul_conf'},\
         'activ':{'sp':'Casos Activos' , 'it':'totale_positivi',\
                  'fr':'cas_actifs'    , 'us':'activeCases',\
                  'uk':'n/A'           , 'ch':'ncumul_act'},\
         'hospi':{'sp':'Hospitalizados', 'it':'totale_ospedalizzati',\
                  'fr':'hospitalises'  , 'us':'hospitalizedCurrently',\
                  'uk':'n/A'           , 'ch':'ncumul_hosp'},\
         'serio':{'sp':'UCI'           , 'it':'terapia_intensiva',\
                  'fr':'hospitalises'  , 'us':'inIcuCurrently',\
                  'uk':'n/A'           , 'ch':'ncumul_ICU'},\
         'recov':{'sp':'Recuperados'   , 'it':'ricoverati_con_sintomi',\
                  'fr':'gueris'        , 'us':'recovered',\
                  'uk':'n/A'           , 'ch':'ncumul_released'},\
         'death':{'sp':'Fallecidos'    , 'it':'deceduti',\
                  'fr':'deces'         , 'us':'death',\
                  'uk':'Deaths'        , 'ch':'ncumul_deceased'},\
         'date' :{'sp':'FECHA'         , 'it':'data', 'fr':'date', 'us':\
 'date', 'uk':'Date', 'ch':'date'}
}

paths={'it':'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv',
       'fr': 'https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv',
       'uk': 'https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-totals-uk.csv',
       'ch': 'https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total.csv',
       'us': 'https://covidtracking.com/api/us/daily.csv',
       'sp': 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'}
#'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'}

#add daily to legend if necessary
labdaily={'sp':' diarios', 'it':' giornaliero', 'fr':' par jour', 'us': \
' per day', 'uk': ' per day', 'ch': ' per day'}

#Define possible regions
cantons={"GE": "Geneve", "ZH": "Zurich"}
regions ={ "CB": "Cantabria", "CN": "Canarias" , "CT": "Catalunya",\
        "MD": "Madrid"   , "AN": "Andalucia", "AS": "Asturias"}

countries={'sp':'Spain','it':'Italy','fr':'France','uk': 'UK','us':'USA','ch':'Switzerland'}
