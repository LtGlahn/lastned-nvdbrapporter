"""
Sammenligner innholdet i V2, V3 og V4-rapporter fra 
[NVDB rapporter / driftskontrakter](https://www.vegdata.no/produkter-og-tjenester/nvdb-rapporter/driftskontrakt-rapporter/)

Koden nedenfor regner ut antall, lengde og areal fra V4-rapporten og sammenligner med data fra V2 og V3-rapportene
"""


import fnmatch
import os
import re
import json
import requests 
from copy import deepcopy
import pdb
from datetime import datetime 

import pandas as pd 
import numpy as np

"""
De egenskapene som kan finnes i reglene: 

'withCount', 
'withCountFrom', 
'withFilter', 
'withLengthFromRoadnet', 
'withLengthPreferingFromAttribute', 
'withCustomPresetsNumberInRange', 
'withFeatureLabel', 
'withAreaFromAttribute', 
'withAreaFromAttributeOrCrossSection', 
'withAreaFromCrossSection',
'withAverage', 
'YearlyGrassCuttingAreaPreset'

"""


def finnrapportfil( mappenavn, sokestreng  ): 
    """
    Rappet fra https://gist.github.com/techtonik/5694830 
    """
    rule = re.compile(fnmatch.translate(sokestreng), re.IGNORECASE)
    rapp =  [name for name in os.listdir(mappenavn) if rule.match(name)]

    # Fjerner helvetes bedritne excel-backupfiler 
    rapp = [ x for x in rapp if '~$' not in x]
    
    if len( rapp ) == 1: 
        rapp = rapp[0]
    else: 
        raise FileNotFoundError( 'Fant ' + str( len(rapp ) ) + ' rapporter med søket: ' + mappenavn + sokestreng  )

    rapp = mappenavn + rapp
    return rapp 

def finnrapportfilnavn( mappenavn ): 

    filnavn = {    
        'v1rapp' : finnrapportfil( mappenavn, '*V1*.XLSX' ), 
        'v2rapp' : finnrapportfil( mappenavn, '*V2*.XLSX' ), 
        'v3rapp' : finnrapportfil( mappenavn, '*V3*.xlsx' ), 
        'v4rapp' : finnrapportfil( mappenavn, '*V4*.XLSX' ),
    }

    try: 
        filnavn['funkra'] = finnrapportfil( mappenavn, '*StandardVedleggsfil*.xlsx') 
    except FileNotFoundError: 
        pass 
    return filnavn 

def aggregertmengdesummering( mindf ): 
    """
    Summerer alle "antall", "lengde" og "areal"-kolonnenne per rad i regnearket

    Totalantall per objekttype er summen av alle radene som baserer seg på denne objekttypen
    Dette kan være spinn gale hvis det er overlapp i utvalget for disse objekttypene. 


    ARGUMENTS:
        Dataframe hentet fra V2 eller V3 - rapport 

    KEYWORDS: 
        None 
    
    Returns
        dictionary 

    """

    antallkolonner = [ navn for navn in list( mindf.columns) if 'Antall' in navn]
    lengdekolonner = [ navn for navn in list( mindf.columns) if 'Lengde' in navn]
    arealkolonner = [ navn for navn in list( mindf.columns) if 'Areal' in navn]

    
    data = { }
    rader = list( set( list( mindf['Beskrivelse']  )))
    for rad in rader: 

        data[rad] = {       'totalAntall' : int( np.nansum( mindf[ mindf['Beskrivelse'] == rad][antallkolonner].to_numpy() )   ), 
                            'totalLengde' :      np.nansum( mindf[ mindf['Beskrivelse'] == rad][lengdekolonner].to_numpy() ), 
                            'totalAreal'  :      np.nansum( mindf[ mindf['Beskrivelse'] == rad][arealkolonner].to_numpy()  ) } 

    return data 


def lesV3( filnavn ): 
    """
    Leser V3-rapport. Må iterere over variabelt antall faner med vegnummer 
    """ 

    v3 = pd.read_excel( filnavn,  header=5)

    tb = [ navn for navn in list( v3.columns) if 'tabeller' in navn ][0]
    fanenavn = list( v3[tb] ) 
    
    v3data = pd.read_excel( filnavn, sheet_name=fanenavn[0], header=5 )
    col = list( v3data.columns )[0:7] 
    v3data = v3data[col].copy()
    allefaner = [v3data ]

    for fane in fanenavn[1:]: 
        temp = pd.read_excel( filnavn, sheet_name=fane, header=5 )
        allefaner.append( temp[col].copy())

    altsammen = pd.concat( allefaner )

    return altsammen 

def kjenteproblem(skrivutalt=False, skrivutproblem=False ):


    vinterfeil  =  'Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier'
    arealfeil1  =  '' # Spesialregel areal = Lengde x Bredde feiler'
    dakatfeil1  =  '' #  'FIKSA Regeldefinisjon er utdatert ihht datakatalog, må justeres'
    vekgryss    =  '' #  'Telling av vegkryss og avledede verdier (primærveg, sekundærveg) feiler'
    vegdekkefeil = '' # 'Utdaterte regler, vi må justere ihht ny datakatalog FIKSA men ' + arealfeil1

    problem = { 'ATK-punkt'									                : '', 
                'Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)'	: '', 
                'Alle NVDB-data for Vegoppmerking, langsgående'				: '', 
                'Avfallsbeholdere'											: '', 
                'Belysningsstrekning'										: '', 
                'Bomstasjon'												: '', 
                'Busslomme'													: arealfeil1, 
                'Trafikklomme u/busslomme'									: arealfeil1, 
                'Bygninger'													: '', 
                'Dekke, Betong'												: vegdekkefeil, 
                'Dekke, Grus'												: vegdekkefeil, 
                'Dekke, Stein'												: vegdekkefeil, 
                'Fanggjerde'												: arealfeil1, 
                'Ferist'													: '', 
                'Ferjekai registrert som bru i NVDB'						: '', 
                'Fjellsikringsutstyr'										: '', 
                'Fortau'													: arealfeil1, 
                'Gjerde'													: arealfeil1, 
                'Grøft, terrenggrøft'										: '', 
                'Grøft. untatt terrenggrøft'								: '', 
                'Grøntanlegg Beplantninger'									: '', 
                'Grøntanlegg Busker'										: '', 
                'Grøntanlegg Grasdekker'									: '', 
                'Grøntanlegg Trær'											: '', 
                'Informasjonstavle'											: '', 
                'Kaier'														: '', 
                'Kanalisering primærveg'									: vekgryss, 
                'Kanalisering sekundærveg'									: vekgryss, 
                'Kantklippareal'											: arealfeil1, 
                'Kantklippareal, årlig anbefalt areal'						: 'Må sjekke spesialregel for "Anbefalt årlig"', 
                'Kantstein'													: '', 
                'Kantstolper'												: '', 
                'Kollektivtrafikkterminaler'								: '', 
                'Kontroll- og veieplasser'									: '', 
                'Kum, Alle NVDB-data'										: '', 
                'Kum, Hjelpesluk'											: '', 
                'Kum, ikke tilknyttet lukket dren.'							: '', 
                'Kum, tilknyttet lukket drenering'							: '', 
                'Leskur'													: '', 
                'Lukka drenering'											: '', 
                'Mur'														: arealfeil1, 
                'Oppsamlingsbasseng'										: '', 
                'Parkeringsområde'											: '', 
                'Pumpestasjon'												: '', 
                'Rasteplass'												: '', 
                'Rekkverk'													: '', 
                'Rekkverksende, Ettergivende'								: '', 
                'Skilt, innvendig belysning'								: '', 
                'Skilt, uten belysning'										: '', 
                'Skilt, utvendig belysning'									: '', 
                'Skilt, variable'											: '', 
                'Skiltplate, Alle NVDB-data unntatt tunnelmarkering'		: '', 
                'Skiltportaler'												: '', 
                'Skiltportaler (Skiltpkt)'									: '', 
                'Skjerm'													: arealfeil1, 
                'Skredoverbygg'												: '', 
                'Snø- og isrydding'											: '', 
                'Stikkrenne'												: '', 
                'Strøsandkasse'												: '', 
                'Støtpute'													: '', 
                'Taktile Indikatorer'										: arealfeil1, 
                'Tellepunkt'												: '', 
                'Tellesløyfer'												: '', 
                'Toalettskåler'												: '', 
                'Trafikkdelere'												: '', 
                'Trafikkspeil'												: '', 
                'Trafikkøyer'												: '', 
                'Trapper'													: '', 
                'Tunneler'													: '', 
                'Tunnelmarkering'											: '', 
                'Utemøbler'													: '', 
                'Vegbanereflektorer'										: '', 
                'Vegbom'													: '', 
                'Vegbredde'													: dakatfeil1, 
                'Vegkryss'													: vekgryss, 
                'Vegoppmerking, forsterket'									: '', 
                'Vegoppmerking, tverrgående'								: '', 
                'Vegskulder/vegkant'										: '', 
                'Viltrekk'													: '', 
                'Vinterdriftsklasse A'      								: vinterfeil, 
                'Vinterdriftsklasse B,  Høy'								: vinterfeil, 
                'Vinterdriftsklasse B,  Middels'							: vinterfeil, 
                'Vinterdriftsklasse B, Lav'									: vinterfeil, 
                'Vinterdriftsklasse C'										: vinterfeil, 
                'Vinterdriftsklasse D'										: vinterfeil, 
                'Vinterdriftsklasse GsA'									: vinterfeil, 
                'Vinterdriftsklasse GsB'									: vinterfeil, 
                'Vinterdriftsklasse Sideanlegg'								: vinterfeil, 
                'Voll'														: '', 
                'Værstasjon'												: '', 
                'Værutsatt veg'												: '',
                'ÅDT (1), 0 - 500'										    : vinterfeil, 
                'ÅDT (2), 500 - 1500'										: vinterfeil, 
                'ÅDT (3), 1500 - 3000'										: vinterfeil, 
                'ÅDT (4), 3000 - 5000'										: vinterfeil, 
                'ÅDT (5), 5000 - 6000'										: vinterfeil, 
                'ÅDT (6), 6000 - 10000' 									: vinterfeil, 
                'ÅDT (7), 10000 - 20000'									: vinterfeil
            }

    if skrivutalt: 
        print( json.dumps( problem, indent=4 ))
    elif skrivutproblem: 
        p2 = { x for x in problem if problem[x] != ''}
        print( json.dumps( p2, indent=4 ))
    else: 
        return problem 

def oversettfunkranavn(skrivutalt=False, sjekkulike=False, sjekkugyldige=False, skrivutgyldige=False ):
    oversett = { 'ATK-punkt'									            : 'ATK-punkt', 
                'Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)'	: 'Bruer', 
                'Alle NVDB-data for Vegoppmerking, langsgående'				: False, 
                'Avfallsbeholdere'											: 'Avfallsbeholdere', 
                'Belysningsstrekning'										: False, 
                'Bomstasjon'												: 'Bomstasjon', 
                'Busslomme'													: 'Busslomme', 
                'Bygninger'													: 'Bygninger', 
                'Fanggjerde'												: 'Fanggjerde', 
                'Ferist'													: 'Ferist', 
                'Ferjekai registrert som bru i NVDB'						: False, 
                'Fjellsikringsutstyr'										: 'Bergsikringsutstyr', 
                'Fortau'													: 'Fortau', 
                'Gjerde'													: 'Gjerde (unntatt fanggjerde)', 
                'Grøft, terrenggrøft'										: False, 
                'Grøft. untatt terrenggrøft'								: False, 
                'Grøntanlegg Beplantninger'									: 'Grøntanlegg Beplantninger', 
                'Grøntanlegg Busker'										: 'Grøntanlegg Busker', 
                'Grøntanlegg Grasdekker'									: 'Grøntanlegg Grasdekker', 
                'Grøntanlegg Trær'											: 'Grøntanlegg Trær', 
                'Informasjonstavle'											: 'Informasjonstavler', 
                'Kaier'														: 'Kaier', 
                'Kanalisering primærveg'									: False, 
                'Kanalisering sekundærveg'									: False, 
                'Kantklippareal'											: False, 
                'Kantklippareal, årlig anbefalt areal'						: False, 
                'Kantstein'													: 'Kantstein', 
                'Kantstolper'												: 'Kantstolper', 
                'Kollektivtrafikkterminaler'								: False, 
                'Kontroll- og veieplasser'									: 'Kontroll- og veieplasser', 
                'Kum, Alle NVDB-data'										: False, 
                'Kum, Hjelpesluk'											: False, 
                'Kum, ikke tilknyttet lukket dren.'							: 'Kum ikke tilknyttet lukket dren.', 
                'Kum, tilknyttet lukket drenering'							: 'Kum tilknyttet lukket drenering', 
                'Leskur'													: 'Leskur', 
                'Lukka drenering'											: False, 
                'Mur'														: 'Mur', 
                'Oppsamlingsbasseng'										: 'Oppsamlingsbasseng', 
                'Parkeringsområde'											: 'Parkeringsplass', 
                'Pumpestasjon'												: 'Pumpestasjon', 
                'Rasteplass'												: 'Rasteplass', 
                'Rekkverk'													: 'Rekkverk', 
                'Rekkverksende, Ettergivende'								: False, 
                'Skilt, innvendig belysning'								: False, 
                'Skilt, uten belysning'										: False, 
                'Skilt, utvendig belysning'									: False, 
                'Skilt, variable'											: 'Skilt, variable', 
                'Skiltplate, Alle NVDB-data unntatt tunnelmarkering'		: 'Skilt', 
                'Skiltportaler'												: 'Skiltportaler', 
                'Skiltportaler (Skiltpkt)'									: 'Skiltportaler (Skiltpkt)', 
                'Skjerm'													: 'Skjerm (unntatt snøskjerm)', 
                'Skredoverbygg'												: 'Skredoverbygg', 
                'Snø- og isrydding'											: 'Snø og isrydding', 
                'Stikkrenne'												: 'Stikkrenne', 
                'Strøsandkasse'												: 'Strøsandkasse', 
                'Støtpute'													: 'Støtpute', 
                'Taktile Indikatorer'										: False, 
                'Tellepunkt'												: 'Tellepunkt', 
                'Tellesløyfer'												: False, 
                'Toalettskåler'												: 'Toalettskåler', 
                'Trafikkdelere'												: 'Trafikkdelere', 
                'Trafikklomme u/busslomme'									: 'Trafikklomme (u/busslomme)', 
                'Trafikkspeil'												: 'Trafikkspeil', 
                'Trafikkøyer'												: 'Trafikkøy', 
                'Trapper'													: False, 
                'Tunneler'													: 'Tunnel', 
                'Tunnelmarkering'											: 'Tunnelmarkering', 
                'Utemøbler'													: 'Utemøbler', 
                'Vegbanereflektorer'										: 'Vegbanereflektorer', 
                'Vegbom'													: 'Bommer', 
                'Vegbredde'													: False, 
                'Vegkryss'													: 'Vegkryss', 
                'Vegoppmerking, forsterket'									: False, 
                'Vegoppmerking, tverrgående'								: False, 
                'Vegskulder/vegkant'										: 'Vegskulder/vegkant', 
                'Viltrekk'													: 'Vilttrekk', 
                'Vinterdriftsklasse B,  Høy'								: 'Vinterdriftsklasse B, Høy', 
                'Vinterdriftsklasse B,  Middels'							: 'Vinterdriftsklasse B, Middels', 
                'Vinterdriftsklasse B, Lav'									: 'Vinterdriftsklasse B, Lav', 
                'Vinterdriftsklasse C'										: 'Vinterdriftsklasse C', 
                'Vinterdriftsklasse D'										: 'Vinterdriftsklasse D', 
                'Vinterdriftsklasse GsB'									: False, 
                'Vinterdriftsklasse Sideanlegg'								: 'Vinterdriftsklasse Sideanlegg', 
                'Voll'														: 'Voll', 
                'Værstasjon'												: 'Værstasjon', 
                'Værutsatt veg'												: False
            }
    
    if sjekkulike: 
        sub = { x : oversett[x] for x in oversett if oversett[x] and x != oversett[x] }
        for x in sub: 
            print( f"{x} => {sub[x]} ")

    elif sjekkugyldige: 
        sub = { x : oversett[x] for x in oversett if not oversett[x] }
        for x in sub: 
            print( f"{x} ")

    elif skrivutalt: 
        for x in oversett: 
            print( f"{x} => {oversett[x]} ")

    elif skrivutgyldige:
        sub = { x : oversett[x] for x in oversett if oversett[x] } 
        for x in sub: 
            print( f"{x} => {oversett[x]} ")

    else: 
        return oversett

def lesfunkraV3( filnavn, giMegV3=False ):
    """
    Leser såkalt "standard vedleggsfil" og henter V2-fanen 
    """
    funkraV3 = pd.read_excel( filnavn, sheet_name='V3 Sum pr veg', header=6)

    funkraV3.dropna( subset=['Veg'], inplace=True )

    funkraV3 = funkraV3[ funkraV3['Veg'] != 'Veg' ]
    funkraV3 = funkraV3[ funkraV3['Beskrivelse'] != 'Total veglengde (inkl. armer og ramper)' ]
    if not giMegV3: # Returnerer den orginale V3-fila 
        funkraV3 = funkraV3.groupby('Beskrivelse').agg( { 'Antall' : sum, 'Lengde (km)' : sum, 'm2' : sum } ).reset_index()

    return funkraV3 

def oppfriskdakat( filnavn='rapportdefinisjon.json'): 

    with open( filnavn) as f:
        regler = json.load( f )

    url = 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper.json'
    dakat = requests.get( url, params={'inkluder' : 'egenskapstyper'} ).json()

    dakatdict = {}
    for objtype in dakat: 

        dakatdict[objtype['id']] = {  'objTypeId'   : objtype['id'], 
                                      'objTypeNavn' : objtype['navn'], 
                                      'egenskaper'  : { }  
                                    }
        for eg in objtype['egenskapstyper']: 

            dakatdict[objtype['id']]['egenskaper'][eg['id']] = { 'navn'  : eg['navn'], 'id' : eg['id']}
            if 'tillatte_verdier' in eg:
                dakatdict[objtype['id']]['egenskaper'][eg['id']]['tillatte_verdier'] = { }
                for enumdata in eg['tillatte_verdier']: 
                    dakatdict[objtype['id']]['egenskaper'][eg['id']]['tillatte_verdier'][enumdata['id']] = enumdata['verdi']
                    

    regler['dakat'] = dakatdict
    with open( filnavn, 'w') as f: 
        json.dump( regler, f, ensure_ascii=False, indent=4 )

    
def v4tellv2( v4DataFrame): 
    """
    Teller V4-dataframe etter V2-regler. Returnerer liste med objektID som skal telles; hvis samme
    objekt skal telles flere ganger så forekommer det så mange ganger som det skal telles. 
    """

    v4 = deepcopy( v4DataFrame  )
    ## Omgår feil fordi samme objekt finnes på V2 og V3
    # v4['v2vegkat'] = v4['Vegkategori'].apply( lambda x: 'Riksveg' if x in ['E','R'] else x )
    # v4['v2sort'] = v4['v2vegkat'] + v4['Trafikantgruppe']
    v4['v2sort'] = v4['Vegkategori'] + v4['Trafikantgruppe']
    telleliste = []

    # Teller hvilke objekter som inngår i de ulike V2-sorteringene 
    for kolonne in list( v4['v2sort'].unique() ): 
        dump =  list( v4[ v4['v2sort'] == kolonne ]['Objekt Id'].unique()   )  
        telleliste.extend( dump )

    return telleliste

def v4tellv3( v4DataFrame): 
    """
    Teller V4-dataframe etter V3-regler. Returnerer liste med objektID som skal telles; hvis samme
    objekt skal telles flere ganger så forekommer det så mange ganger som det skal telles. 
    """

    v4 = deepcopy( v4DataFrame  )
    v4['v3sort'] = v4['Vegkategori'] + v4['Fase'] + v4['vegnummer'].astype(str)
    telleliste = []

    # Teller hvilke objekter som inngår i de ulike V2-sorteringene 
    for ark in list( v4['v3sort'].unique() ): 
        telleliste.extend( list( v4[ v4['v3sort'] == ark ]['Objekt Id'].unique()   )  )

    return telleliste



def lesregler( filename='rapportdefinisjon.json'):
    """
    Leser regelsett for alle radene i V2/V3 - rapportene

    Regelsett er oversatt fra koden https://github.com/nvdb-vegdata/nvdb-rapport-api/blob/master/src/main/java/no/svv/veirapporter/engine/utils/ContractUtils.java 

    ARGUMENTS: 
        None 

    KEYWORDS: 
        filename string filnavn med json-data

    RETURNS: 
        Liste med dictionary 
    """

    with open( "rapportdefinisjon.json") as f:
        rdef = json.load( f)

    regelListe =  [  { 'Beskrivelse' : x, **rdef['mengdeaggregering'][x] }    for x in rdef['mengdeaggregering']  ] 

    return (regelListe, rdef['dakat'])

def tellWithCountFrom( v4, telleListe, egNavn ): 

    count = 0
    unik = v4[ v4['Filteringshjelp'] == 1].copy()
    unik.loc[ unik[egNavn].isnull(), 'Antall' ] = 1 
    for id in telleListe: 
        count += unik[ unik['Objekt Id'] == id ].iloc[0][egNavn]

    return count 

def tellv4antall( v4, regl, dakat  ): 

    v4_antallObjekt = { 'kommentar' : '' }
    if 'withCount' in regl: 
        v4_antallObjekt['v4'] = v4['Filteringshjelp'].sum() 
        v4_antallObjekt['v2'] = len( v4tellv2( v4 ) ) 
        v4_antallObjekt['v3'] = len( v4tellv3( v4 ) ) 

    elif 'withCountFrom' in regl: 
        v4_antallObjekt['v4'] = v4['Filteringshjelp'].sum() 
        egenskapNavn = dakat['egenskaper'][str( regl['withCountFrom'] )]['navn']
        telleIdV2 = v4tellv2( v4 )
        v4_antallObjekt['v2'] = tellWithCountFrom( v4, telleIdV2, egenskapNavn) 
        telleIdV3 = v4tellv3( v4 )
        v4_antallObjekt['v3'] = tellWithCountFrom( v4, telleIdV3, egenskapNavn)

    if 'v4' in v4_antallObjekt and 'v3' in v4_antallObjekt and 'v2' in v4_antallObjekt: 

        if v4_antallObjekt['v4'] != v4_antallObjekt['v2'] or v4_antallObjekt['v4'] != v4_antallObjekt['v3']:
            v4_antallObjekt['kommentar'] = 'OBS: Samme objekt inngår i flere tellinger i'
        
            if v4_antallObjekt['v4'] != v4_antallObjekt['v2']: 
                v4_antallObjekt['kommentar'] += ' V2 '
            
            if v4_antallObjekt['v4'] != v4_antallObjekt['v3']: 
                v4_antallObjekt['kommentar'] += ' V3 '
            
            v4_antallObjekt['kommentar'] += 'rapport'


    return v4_antallObjekt  


def lesv4( filnavn, sheet_name ): 
    return pd.read_excel( filnavn, sheet_name=sheet_name, header=5)

def egenskapfilter(v4, regl, dakat): 
    """
    Filterer V4-dataframe på egenskapverdi hvis reglene tilsier det

    ARGUMENTS:
        v4 - dataframe 

        regl - Regler 

        dakat = datakatalogdefinisjon for denne objekttypen, tilpasset vår logikk

    KEYWORDS: 
        None 

    RETURNS:
        Et subsett av den opprinnelige dataframen (evt hele)
    """

    if len( v4 ) >  0: 
        debugdata = v4.copy( )

        regel = parserfilteregler( regl, dakat) 
        if regel:
            data = [] 
            if 'inverse' in regel: 
                for verdi in regel['verdier']:
                    v4 = v4[ v4[regel['egenskapsNavn']]  != verdi]
            else: 
                for verdi in regel['verdier']: 
                    data.append( v4[ v4[regel['egenskapsNavn']]  == verdi ]  )

                v4 = pd.concat( data )

        elif 'withCustomPresetsNumberInRange' in regl and isinstance( regl['withCustomPresetsNumberInRange'], list ) and \
            len( regl['withCustomPresetsNumberInRange']) == 3: 

            if regl['withCustomPresetsNumberInRange'][0] != 4623: 
                raise ValueError( f"Må lage mer robust håndtering av regel 'withCustomPresetsNumberInRange' {regl} "  )

            terskler = regl['withCustomPresetsNumberInRange']
            v4 = v4[ (v4['ÅDT, total'] >= terskler[1]) & (v4['ÅDT, total'] < terskler[2]) ].copy()

    return v4    

def parserfilteregler( regl, dakat ): 
    """
    parser regler egenskapfilter, returnere dictionary med det som trengs for å filtrere på dataframe
    """ 

    regel = None 
    if 'withFilter' in regl: 
        regel = {}
        if '!' in regl['withFilter']:
            regel['inverse'] = True 
        tall = ''.join( [ x for x in regl['withFilter'] if x.isnumeric() or x == ' '   ] ).strip().split()
        regel['egenskapId'] = tall[0]
        regel['egenskapsNavn'] = dakat['egenskaper'][tall[0]]['navn']
        regel['verdier'] = [ ]
        for tt in tall[1:]:
            regel['verdier'].append( dakat['egenskaper'][tall[0]]['tillatte_verdier'][tt] )

    elif 'withCustomPresetsNumberInRange' in regl: 
        pass 
        # Har hardkodet løsning 
        # "ÅDT (4), 3000 - 5000": {
        #     "objtype": 540,
        #     "withFeatureLabel": true,
        #     "withCustomPresetsNumberInRange": [
        #         4623,
        #         3000,
        #         5000
        #     ]
        # }


    return regel 

def applyYearlyGrassCuttingAreaPreset( anbefalt_intervall ):
    """
    Regner ut "klippefaktor" [0.25, 0.5, 1, 2] som arealet skal justeres med. 
    """
    faktor = 1

    if   anbefalt_intervall == '2 g. pr år': 
        faktor = 2
    elif anbefalt_intervall == '1 g. pr år': 
        faktor = 1
    elif anbefalt_intervall == '2.hvert år': 
        faktor = 0.5
    elif anbefalt_intervall == '3-5. hvert år': 
        faktor = 0.25
    elif anbefalt_intervall and isinstance(anbefalt_intervall, str) and len( anbefalt_intervall ) > 1: 
        print( f'RAR DATAVERDI: Kantklippareal, anbefalt areal klarer ikke tolke egenskapverdi {anbefalt_intervall}')

    return faktor 

def kantklippspesial( v4, regl, dakat  ):
    """
    For kantklippareal har vi regelen YearlyGrassCuttingAreaPreset
    """
    v4 = deepcopy(v4)

    if not 'YearlyGrassCuttingAreaPreset' in regl: 
        print( f'Kantklippspesial: Mangler YearlyGrassCuttingAreaPreset i regel {regl}'   )        
        return v4 

    if not 'withAreaFromAttributeOrCrossSection' in regl: 
        print( f'Kantklippspesial: Mangler withAreaFromAttributeOrCrossSection i regel {regl} '   )        
        return v4

    arealvariabel = dakat['egenskaper'][str(regl['withAreaFromAttributeOrCrossSection'][0])]['navn']
    v4['kantklippfaktor'] = v4['Kantklipp, anbefalt intervall'].apply( lambda x : applyYearlyGrassCuttingAreaPreset( x )  )
    v4[arealvariabel] = v4[arealvariabel] * v4['kantklippfaktor']

    return v4 

def arealtelling( v4, regl, dakat): 

    lengdevariabel = None
    arealvariabel  = None 
    svar = None 

    if 'withLengthPreferingFromAttribute' in regl: 
        lengdevariabel = dakat['egenskaper'][str( regl['withLengthPreferingFromAttribute'] ) ]['navn']

    v4kopi = laglengder( v4, lengdevariabel=lengdevariabel) # har føyd til kolonne syntetiskLengde 

    # Spesialregel for årlig beregning av kantklipp 
    if 'YearlyGrassCuttingAreaPreset' in regl: 
        v4kopi = kantklippspesial( v4, regl, dakat )


    # 'withAreaFromAttribute' Bruker areal-egenskap (hvis den finnes), ingen backup
    # egenskapID for areal
    if 'withAreaFromAttribute' in regl: 
        arealvariabel = dakat['egenskaper'][str(regl['withAreaFromAttribute'])]['navn']
        svar = np.nansum( v4kopi[arealvariabel]  )

     #'withAreaFromCrossSection'  Bruker bredde-egenskap og lengden   
     # egenskapID for bredde
    if 'withAreaFromCrossSection' in regl: 
        breddevariabel = dakat['egenskaper'][str(regl['withAreaFromCrossSection'])]['navn']
        v4kopi['areal'] = v4kopi['syntetiskLengde'] * v4kopi[breddevariabel]
        svar = np.nansum( v4kopi['areal'] )
    
    # 'withAreaFromAttributeOrCrossSection' Bruker areal-egenskap hvis den finnes, alternativt bredde * lengde 
    # Liste med egenskapID: [ Areal, Bredde   ]
    # Lager to dataframes (dem som har areal-egenskap, og resten), som så summeres 
    if 'withAreaFromAttributeOrCrossSection' in regl: 
        my2dTuple = regl['withAreaFromAttributeOrCrossSection'] # Areal, bredde
        arealvariabel  = dakat['egenskaper'][str( my2dTuple[0] )]['navn']
        breddevariabel = dakat['egenskaper'][str( my2dTuple[1] )]['navn']

        A = v4kopi[ ~v4kopi[arealvariabel].isnull() ] 
        B = v4kopi[ v4kopi[arealvariabel].isnull() ].copy()
        B['areal'] = B['syntetiskLengde'] * B[breddevariabel]
        
        svar =  np.nansum( A[arealvariabel]  ) + np.nansum(  B['areal']  )

    return svar 

def lengdetelling( v4, regl, dakat): 
    """
    Teller lengder.
    """
    lengdevariabel = None

    if 'withLengthPreferingFromAttribute' in regl: 
        lengdevariabel = dakat['egenskaper'][str( regl['withLengthPreferingFromAttribute'] ) ]['navn']

    v4kopi = laglengder( v4, lengdevariabel=lengdevariabel)

    return v4kopi['syntetiskLengde'].sum()

def laglengder( v4, lengdevariabel=None ):
    """
    Beregner lengde og føyer den til kolonnen 'syntetiskLengde', til bruk i lengde- og arealberegning
    """

    v4['syntetiskLengde'] = v4['Lengde vegnett']

    # Deler datasettet i to. 
    if lengdevariabel: 
        dfVeglengde = v4[ v4[lengdevariabel].isnull() ] 
        dfEgenskap  = v4[ ~v4[lengdevariabel].isnull() ]
        dfEgenskap  = dfEgenskap[ dfEgenskap['Filteringshjelp'] == 1 ]
        dfEgenskap['syntetiskLengde'] = dfEgenskap[lengdevariabel]
        v4 = pd.concat( [dfVeglengde, dfEgenskap] )

    return v4 

def sjekkrapportdefinisjon( velgregel=None, skrivalt=True, objektTyper=None ): 

    (regelListe, fulldakat) = lesregler()

    if objektTyper: 
        if isinstance( objektTyper, int): 
            objektTyper = [ objektTyper ]
        regelListe = [ x for x in regelListe if x['objtype'] in objektTyper  ]

    if velgregel: 
        regelListe = [ x for x in regelListe if velgregel in x  ]


    variabelListe = [ 'withCount', 'withCountFrom', 'withFilter', 'withLengthFromRoadnet', 
                        'withLengthPreferingFromAttribute', 'withCustomPresetsNumberInRange', 
                        'withFeatureLabel', 'withAreaFromAttribute', 
                        'withAreaFromAttributeOrCrossSection', 'withAreaFromCrossSection',
                        'withAverage', 'YearlyGrassCuttingAreaPreset' ]

    for regl in regelListe: 

        objtype = regl['objtype']
        dakat = fulldakat[str(objtype)]
        if skrivalt:
            print( f"\"{regl['Beskrivelse']}\" ==== {objtype} {dakat['objTypeNavn']} "  )
        for var in variabelListe: 
            if var in regl: 
                if var in ['withCount',  'withLengthFromRoadnet', 'withFeatureLabel', 'YearlyGrassCuttingAreaPreset', 'withAverage']:
                    if skrivalt: 
                        print(f"\t{var} {regl[var]}  "  )
                else: 

                    tall = None 
                    if isinstance( regl[var], str): 
                        tall = ''.join( [ x for x in regl[var] if x.isnumeric() or x == ' '   ] ).strip().split()
                    elif isinstance( regl[var], int): 
                        tall = [ str( regl[var] )]
                    elif isinstance( regl[var], list):
                        tall = regl[var] 

                    if tall: 
                        if var in  ['attributeMatches', 'withCustomPresetsNumberInRange', 'withFilter']:
                            tall = [ tall[0] ]
                        for tull in tall: 
                            try: 
                                mystring = f"\t{var} {regl[var]} Egenskap: {tull}  {dakat['egenskaper'][str(tull)]['navn']} "
                                if skrivalt:
                                    print( mystring  )
                            except KeyError: 
                                print( f"\tUGYLDIG EGENSKAPID {tull} for \"{regl['Beskrivelse']}\" {objtype} {dakat['objTypeNavn']}: {var}={regl[var]}" ) 
                    else: 
                        print( f"\tKlarte ikke oversette til datakatalog-egenskaper: {var} {regl[var]} ")

def feilprint( overskrift, v2sum, v3sum, v4sum, prosentavvik, regl, funkratall='', kommentar=''  ): 
    """
    Lager markdown-sammendrag av avvik
    """

    if funkratall:
        funkratall=f"\n\nFrå Funkra={funkratall} "

    errstr = f"""

# Avvik {overskrift} {prosentavvik} => {regl['objtype']} {regl['Beskrivelse']}

```
V2={int(v2sum):>12}
V3={int(v3sum):>12}
V4={int(v4sum):>12} {funkratall}
```
{kommentar}
Regler: {regl}

"""
    return errstr

def lagProsentTekst( svarA, svarB, fasit, avrunding=2, uendeligtekst='Inf' ):
    prosentavvik = max([ 100*abs(svarA-fasit )/fasit, 100*abs(svarB-fasit)/fasit ]) 
    prosent_tekst = uendeligtekst
    if fasit == 0:
        if svarA == 0 and svarB == 0: 
            prosent_tekst = "0"
            prosentavvik = 0
        else: 
            prosentavvik = 10000

    else: 
        prosent_tekst = f"{round(prosentavvik, avrunding)}"   

    return (prosentavvik, prosent_tekst)

def funkrasjekk( funkraV3, v2sum, v3sum, v4sum, regl,  antall=False, lengde=False, areal=False, prosentterskel=1 ): 
    """
    Skriver ut resultatet av sammenligning med gml Funkra (hvis det finnes data) 
    Hvis avvik > prosent returnerer tekststreng 
    OBS! Kun en av parametrene antall, lende eller areal av gangen
    """
    svar = ''

    if antall: 
        kolonnenavn = 'Antall'
        beskrivelse = 'antall'
        benevning = 'stk'
    elif lengde: 
        kolonnenavn = 'Lengde (km)'
        beskrivelse = 'lengde'
        benevning = 'm'
    elif areal:
        kolonnenavn = 'm2'
        beskrivelse = 'areal'
        benevning = 'm^2'
    else: 
        return svar

    babel = oversettfunkranavn()

    if regl['Beskrivelse'] in babel: 
        funkraNavn = babel[regl['Beskrivelse']]
        if funkraNavn: 
            funkratall = float( funkraV3[ funkraV3['Beskrivelse'] == funkraNavn ][kolonnenavn] ) 
            if lengde: 
                funkratall = funkratall * 1000

            if funkratall != 0: # Antar det ikke finnes noe data her når tallet == 0

                svar =  _intern_funkrasjekk( funkratall, 'v2', beskrivelse, v2sum, regl, benevning, v2sum, v3sum, v4sum, antall=antall)
                svar += _intern_funkrasjekk( funkratall, 'v3', beskrivelse, v3sum, regl, benevning, v2sum, v3sum, v4sum, antall=antall)
                svar += _intern_funkrasjekk( funkratall, 'v4', beskrivelse, v4sum, regl, benevning, v2sum, v3sum, v4sum, antall=antall)

    return svar 

def _intern_funkrasjekk(  funkratall, rapporttype, beskrivelse, tall, regl, benevning, v2sum, v3sum, v4sum, antall=False ):
    svar = ''
    prosentterskel = 1
    prosenttegn = '%'
    if antall: 
        prosentavvik = abs( funkratall - tall )
        prosent_tekst = f"{prosentavvik} " 
        prosentterskel = 0.5
        prosenttegn = 'stk'
    else: 
        (prosentavvik, prosent_tekst) = lagProsentTekst(funkratall, funkratall, tall )
    if prosentavvik  < prosentterskel: 
        print( f"Funkrasjekk for {rapporttype} suksess {regl['objtype']} {regl['Beskrivelse']} {beskrivelse}={int(tall)}{benevning} "  )
    else: 
        print( f"FUNKRASJEKK for {rapporttype} FEILER {beskrivelse} {regl['objtype']} {regl['Beskrivelse']}", 
                f"Ny {rapporttype}={int(tall)}{benevning}, Funkra={int(funkratall)}{benevning} "  )
        # print(f"\t{regl} " )
        svar = feilprint( f'FUNKRASJEKK for {rapporttype} FEILER {beskrivelse}', v2sum, v3sum, v4sum, f'{prosent_tekst}{prosenttegn}', 
                            regl, funkratall=f"{round(funkratall)}" )    
    return svar 

def sjekkmengder( mappenavn, objekttyper ): 

    feilmeldinger = f"\n# Oppsummering av avvik\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S') }" 
    feilmelding_nulldata = ""

    filnavn = finnrapportfilnavn( mappenavn )

    # Leser regler for de ulike radene
    (regelListe, dakat) = lesregler()

    # Leser V2-data 
    v2 = pd.read_excel( filnavn['v2rapp'], sheet_name='V2', header=5)  
    v2sum = aggregertmengdesummering( v2 )

    # Leser V3-data 
    v3 = lesV3( filnavn['v3rapp'])
    v3sum = aggregertmengdesummering( v3 )

    # Leser V4-data
    v4oversikt = pd.read_excel( filnavn['v4rapp'] )
    v4indeks = list( v4oversikt['Unnamed: 0'])[5:]
    v4indeks =  {  int( n.split('-')[0] )  : n  for n in v4indeks }

    # Leser Funkraliste hvis den finnes 
    if 'funkra' in filnavn: 
        funkraV3 = lesfunkraV3( filnavn['funkra'])
    else: 
        funkraV3 = None 

    if isinstance( objekttyper, int):
        objekttyper = [ objekttyper ]

    for objekttype in objekttyper: 
        v4data = lesv4( filnavn['v4rapp'], sheet_name=v4indeks[objekttype])

        regler = [ x for x in regelListe if x['objtype'] == objekttype ]
        if len( regler ) == 0: 
            print( 'Fant ingen regler for objekttype', objekttype)

        for regl in regler: 

            if regl['Beskrivelse'] not in v2sum: 

                errstr =  f"--- Null data for {objekttype} {regl['Beskrivelse']} i V2-rapporten for dette kontraktsområdet "
                feilmelding_nulldata += '\n' + errstr  
                print( errstr )

            else: 

                kommentar = ''
                v4 = deepcopy( v4data ) 
                # Filtrerer på egenskapverdi 
                v4 = egenskapfilter(v4, regl, dakat[str(objekttype)])

                ######################################################################################################
                # Sjekker antall ----- 
                if 'withCount' in regl or 'withCountFrom' in regl: 
                    v4_antallObjekt = tellv4antall( v4, regl, dakat[str(objekttype)]  )
                    kommentar = v4_antallObjekt['kommentar']


                    if 'v4' in  v4_antallObjekt and 'v3' in v4_antallObjekt and 'v2' in v4_antallObjekt:
                        
                        v2svar = v2sum[regl['Beskrivelse']]['totalAntall']
                        v3svar = v3sum[regl['Beskrivelse']]['totalAntall']
                        if v4_antallObjekt['v2'] == v2svar and v4_antallObjekt['v3'] == v3svar: 
                            print( f"Antallsukses \t {objekttype}  {regl['Beskrivelse']} {v4_antallObjekt['v4']} stk {v4_antallObjekt['kommentar'] } ")
                        else: 
                            print( f"FEIL ANTALL! {objekttype} {regl['Beskrivelse']} V2={v2svar}, V3={v3svar} V4={v4_antallObjekt['v4']} {v4_antallObjekt['kommentar']}" )
                            # print( f"\t{regl}")
                        if isinstance( funkraV3, pd.core.frame.DataFrame):
                            feilmeldinger += funkrasjekk( funkraV3, v2svar, v3svar, v4_antallObjekt['v4'], regl,  antall=v4_antallObjekt['v4']  )

                    else: 
                        print( f"---- TELLING FEILER {objekttype} {regl} ")
                        feilmeldinger += feilprint( 'antall', v2svar, v3svar, v4_antallObjekt['v4'], '', regl )


                ######################################################################################################
                # Sjekker lengde -----------
                if 'withLengthFromRoadnet' in regl or 'withLengthPreferingFromAttribute' in regl or 'withFeatureLabel' in regl: 
                    v4lengde = lengdetelling( v4, regl, dakat[str(objekttype)])

                    v2svar = v2sum[regl['Beskrivelse']]['totalLengde'] 
                    v3svar = v3sum[regl['Beskrivelse']]['totalLengde'] 
                    (prosentavvik, prosent_tekst) = lagProsentTekst(v2svar, v3svar, v4lengde )

                    if prosentavvik < 1:
                        print(f"Lengdesuksess \t {objekttype} {regl['Beskrivelse']} {v4lengde} avvik= {prosent_tekst}% " )
                    else: 
                        print( f"FEIL LENGDE avvik={prosent_tekst}% ! {objekttype} {regl['Beskrivelse']} V2={v2svar}, V3={v3svar}, V4={v4lengde} {kommentar}" )
                        # print( f"\t{regl}")
                        feilmeldinger += feilprint( 'lengde', v2svar, v3svar, v4lengde, f"{prosent_tekst}%", regl )

                    if isinstance( funkraV3, pd.core.frame.DataFrame):
                        feilmeldinger += funkrasjekk( funkraV3, v2svar, v3svar, v4lengde, regl,  lengde=v4lengde  )


                ######################################################################################################
                # Sjekker Areal ----------- 
                if 'withAreaFromAttribute' in regl or 'withAreaFromAttributeOrCrossSection' in regl or 'withAreaFromCrossSection' in regl:
                    v4areal = arealtelling( v4, regl, dakat[str(objekttype)])
                    v2svar = v2sum[regl['Beskrivelse']]['totalAreal']
                    v3svar = v3sum[regl['Beskrivelse']]['totalAreal']
                    (prosentavvik, prosent_tekst) = lagProsentTekst(v2svar, v3svar, v4areal )
                    if prosentavvik < 1:                   
                        print(f"Arealsuksess \t {objekttype} {regl['Beskrivelse']} {v4areal}m^2 avvik= {prosent_tekst}% " )
                    else: 
                        print( f"FEIL AREAL avvik={prosent_tekst}% ! {objekttype} {regl['Beskrivelse']}", 
                                f" V2={round(v2svar)}, V3={round(v3svar)}, V4={round(v4areal)} {kommentar}" )
                        # print( f"\t{regl}")
                        feilmeldinger += feilprint( 'areal', v2svar, v3svar, v4areal, f"{prosent_tekst}%", regl )

                    if isinstance( funkraV3, pd.core.frame.DataFrame):
                        feilmeldinger += funkrasjekk( funkraV3, v2svar, v3svar, v4areal, regl,  areal=v4areal )


    print( '\n\n', feilmeldinger)
    print( '\n\n# Manglende data i dette kontraktsområdet\n\n', "```\n", feilmelding_nulldata, "```" )

if __name__ == "__main__":

    mappenavn = './testmagnus2/'

    filnavn = finnrapportfilnavn( mappenavn ) 
    v4oversikt = pd.read_excel( filnavn['v4rapp'] )  
    v4indeks = list( v4oversikt['Unnamed: 0'])[5:] 
    objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  
    sjekkmengder( mappenavn, objektliste )  