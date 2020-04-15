
#Dictionary with variables for each dataframe
regvars={'cases':{'sp':'CASOS'         , 'it':'totale_casi',\
                  'fr':'cas_confirmes' , 'us':'positive' ,\
                  'uk':'ConfirmedCases', 'ch':'ncumul_conf'},\
         'activ':{'sp':'Casos Activos' , 'it':'totale_positivi',\
                  'fr':'cas_actifs'    , 'us':'activeCases',\
                  'uk':'n/A'           , 'ch':'ncumul_axt'},\
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
#add daily to legend if necessary
labdaily={'sp':' diarios', 'it':' giornaliero', 'fr':' par jour', 'us': \
' per day', 'uk': ' per day', 'ch': ' per day'}

#Function to get the abbreviated name of the df            
def getregs(reg_nm):
    regs='sp'
    if 'it' in reg_nm.lower(): regs='it'
    if 'fr' in reg_nm.lower(): regs='fr'
    if 'uk' in reg_nm.lower(): regs='uk'
    if 'us' in reg_nm.lower(): regs='us'
    if 'sw' in reg_nm.lower(): regs='ch'
    return regs
