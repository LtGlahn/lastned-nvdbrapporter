"""
Ny og forhåpentligvis bedre rutiner for å kvalitetssikre driftskontrakt-rapporter

Bruker de gode funksjonene fra driftskontraktsjekk.py for å 
laste inn og - i noen grad - manipulere data. Men den overordnede logikken er 
skrevet på ny, forhåpentligvis enklere og bedre. 

Her returnerer vi to dataframes: En med alle tallene som er henta, og en med differanser  

"""

import pdb 
from datetime import datetime
from copy import deepcopy 

import pandas as pd
import pickle
import numpy as np

import STARTHER
import nvdbapiv3

from driftkontraktsjekk import finnrapportfil, finnrapportfilnavn
from driftkontraktsjekk import lesV3, lesfunkraV3, oversettfunkranavn
from driftkontraktsjekk import lesv4, egenskapfilter, parserfilteregler
from driftkontraktsjekk import lesregler, egenskapfilter, kjenteproblem
from driftkontraktsjekk import kantklippspesial



def oppsummerDiff_htmlfarge( mintekst ): 

    # manglerFarge = 'style="background-color:#c0f0d4"'
    # manglerFarge = 'style="text-align:center;'
    # okFarge = 'style="text-align:center;background-color:#03ff5f"'
    # noeFarge = 'style="text-align:center;background-color:#fff566"'
    # myeFarge = 'style="text-align:center;background-color:#ff9999"'

    manglerFarge    = 'class="neutral"'
    okFarge         = 'class="OK"'
    noeFarge        = 'class="noeavvik"' 
    myeFarge        = 'class="myeavvik"'



    if mintekst.upper() == 'BLANK' or mintekst == '-': 
        svar = manglerFarge 
    elif mintekst.upper() == 'OK': 
        svar = okFarge
    elif mintekst.upper() in  ['NOE', 'NOE AVVIK']: 
        svar = noeFarge
    elif mintekst.upper() in ['MYE', 'MYE AVVIK', 'STORE AVVIK']: 
        svar = myeFarge
    else: 
        pass 
        # svar = 'style="text-align:center;'

    return svar 

def oppsummerDiff_skrivhtmlrad( mindict ): 
    """
    Tar resultatet fra oppsummerDiff og lager en rad til HTML-tabell, med fargekoder 

    For noen spesifikke tekstverdiene i  "antall", "lengde" og "areal" vil vi endre bakgrunnsfarge på cellen
    """

    # antallfarge = oppsummerDiff_htmlfarge( mindict['antall'] )
    # lengdeFarge = oppsummerDiff_htmlfarge( mindict['lengde'] )
    # arealFarge = oppsummerDiff_htmlfarge( mindict['areal'] )
    
    tableRow = (    f"<tr>"
                    f"<td> {mindict['objtype'] } </td>" 
                    f"<td> {mindict['Beskrivelse']} </td>" 
                    f"<td  {mindict['antallFarge']}> {mindict['antall']} </td> "
                    f"<td  {mindict['lengdeFarge']}> {mindict['lengde']} </td>"
                    f"<td  {mindict['arealFarge']}>  {mindict['areal']} </td>"
                    f"<td> {mindict['Kjent problem']} </td>"
                    f"</tr>\n" )

    return tableRow

def oppsummerDiff( diff ): 
    """
    Oppsummerer en dataframe laget av "differanser" fra mengdesjekk 
    """

    antall           =  diff['antall'].max()
    lengde           =  diff['lengde'].max()
    areal            =  diff['areal'].max()
    antallprosent    =  diff['antallprosent'].max()
    lengdeprosent    =  diff['lengdeprosent'].max()
    arealprosent     =  diff['arealprosent'].max()

    antallFarge = ''
    if np.isnan( antall ): 
        antall = '-'
        antallFarge = oppsummerDiff_htmlfarge( antall )
    elif antall == 0 and np.isnan( antallprosent ): 
        antall = 'OK'
        antallFarge = oppsummerDiff_htmlfarge( antall )
    elif antall == 0 and antallprosent == 0: 
        antall = 'OK'
        antallFarge = oppsummerDiff_htmlfarge( antall )
    elif antall == 1: 
        antallFarge = oppsummerDiff_htmlfarge( 'Noe avvik' )
        antall = '1 stk'
    elif antallprosent < 2: 
        antallFarge = oppsummerDiff_htmlfarge( 'Noe avvik' )
        antall = f'{antallprosent:.2f}%'
    elif antallprosent > 2: 
        antallFarge = oppsummerDiff_htmlfarge( 'Mye avvik' )
        antall = f'{antallprosent:.2f}%'
    else: 
        antall = 'FEIL i QA'
    
    lengdeFarge = ''
    if np.isnan( lengde ): 
        lengde = '-'
    elif lengde == 0 and np.isnan( lengdeprosent ): 
        lengde = 'OK'
        lengdeFarge = oppsummerDiff_htmlfarge( lengde )
    elif ~np.isnan( lengdeprosent) and lengdeprosent < 0.5: 
        lengde = f'{lengdeprosent:.2f}%'
        lengdeFarge = oppsummerDiff_htmlfarge( 'OK' )
    elif ~np.isnan( lengdeprosent) and lengdeprosent < 2: 
        lengde = f'{lengdeprosent:.2f}%'
        lengdeFarge = oppsummerDiff_htmlfarge( 'Noe avvik' )        
    elif ~np.isnan( lengdeprosent) and lengdeprosent > 2: 
        lengde = f'{lengdeprosent:.2f}%'
        lengdeFarge = oppsummerDiff_htmlfarge( 'Store avvik' )        
    else: 
        lengde = 'FEIL i QA'

    arealFarge = ''
    if np.isnan( areal ): 
        areal = '-'
    elif areal == 0 and np.isnan( arealprosent ): 
        areal = 'OK'
        arealFarge = oppsummerDiff_htmlfarge( areal )
    elif ~np.isnan( arealprosent) and arealprosent < 0.5: 
        arealFarge = oppsummerDiff_htmlfarge( 'OK' )
        areal = f'{arealprosent:.2f}%'
    elif ~np.isnan( arealprosent) and arealprosent < 2: 
        arealFarge = oppsummerDiff_htmlfarge( 'Noe avvik' )
        areal = f'{arealprosent:.2f}%'
    elif ~np.isnan( arealprosent) and arealprosent > 2: 
        arealFarge = oppsummerDiff_htmlfarge( 'Store avvik' )
        areal = f'{arealprosent:.2f}%'
    else: 
        areal = 'FEIL i QA'

    objtype = list( set( list( diff['objtype'].unique()) ))
    if len( objtype) == 1: 
        objtype = objtype[0]
    else: 
        objtype = ','.join( [ str(x) for x in objtype ] )


    oppsum = { 
            'type'             :  ', '.join( list( diff['type'].unique()) ),
            'datakilde'        : ', '.join( list( diff['datakilde'].unique()) ), 
            'telletype'        : ', '.join( list( diff['type'].unique()) ), 
            'Beskrivelse'      : ', '.join( list( diff['Beskrivelse'].unique()) ), 
            'objtype'          : objtype,  
            'antall'           : antall,
            'antallFarge'      : antallFarge,
            'lengde'           : lengde,
            'lengdeFarge'      : lengdeFarge,
            'areal'            : areal,
            'arealFarge'       : arealFarge,
            'avvik'            : ', '.join( list( diff['avvik'].unique()) ),  
            'Kjent problem'    : ', '.join( list( diff['Kjent problem'].unique()) )  
    }

    return oppsum

def lagHtmlOppsummering( diff, omraade='' ): 

    if omraade != '': 
        omraade = f"\n\n<p>Rapporten er laget for kontraktsområde: {omraade}.</p>\n\n"

    tid = datetime.now().isoformat()[0:16]
    tid = tid.replace( 'T', '  ')

    svar = (    f'<!DOCTYPE html>\n'
                f'<html>\n'
                f'<head>\n'
                f'<style>\n'
                f'.neutral {{ background-color: white; text-align: center; }}\n' 
                f'.OK  {{ background-color:#03ff5f; text-align: center; }} \n'
                f'.noeavvik {{ background-color:#fff566;  text-align: center;}} \n'
                f'.myeavvik {{ background-color:#fc9996; text-align: center; }} \n'
                f'td {{ padding:15px }} \n'
                f'</style>\n\n'
                f"<h1> Oppsummering</h1>\n\n" 
                f'<p>Denne tabellen er laget ved å bruke data fra V4-tabellen og egenprodusert kode som "etterligner" beregning av V2- og V3-tabellene, for antall, lengde og areal per vegstrekning.</p>'
                f'{omraade}\n\n' 
                f'Rapport generert: {tid}\n\n'
                f'<h3>Kjente svakheter</h3>\n\n'
                f'\n\n' 
                f'<p>Kolonnen <em>"Kjente feil"</em> lister opp feil vi kjenner til i produksjonssystemet vårt. Feilsøking og feilretting pågår.</p>\n'
                f'\n'
                f"<table><thead><tr><td>TypeID</td><td>Beskrivelse</td><td>Antall</td><td>Lengde</td><td>Areal</td><td>Kjente feil</td></tr></thead>\n" )

    for beskr in list( diff['Beskrivelse'].unique() ): 
        oppsum = oppsummerDiff( diff[ diff['Beskrivelse'] == beskr ] )
        htmlrad = oppsummerDiff_skrivhtmlrad( oppsum )
        svar += htmlrad 
    
    svar += '</table>\n</body>\n</html>'
    return svar 


def loggTelling( telling ):

    if not isinstance( telling, list): 
        telling = [ telling ]

    for tell in telling:

        antall = tell['antall']
        lengde = tell['lengde']
        areal = tell['areal']
        avvik = ''
        if 'avvik' in tell and tell['avvik'] != '': 
            avvik = 'AVVIK: ' + tell['avvik']

        kjent = ''
        if 'Kjent problem' in tell: 
            kjent = tell['Kjent problem']

        if np.isnan( antall): 
            antall = '-'
        else: 
            antall = round( antall )
        if np.isnan( lengde): 
            lengde = '-'
        else: 
            lengde = round( lengde )
        if np.isnan( areal ): 
            areal = '-'
        else: 
            areal = round( areal )


        print( f"{tell['type']:<12} {tell['datakilde']:<10} {tell['objtype']} {tell['Beskrivelse']:<60} {tell['telletype']}", 
                f"\t {antall:>7} stk {lengde:>10} m {areal:>10} m2 {avvik}"   )
                # f"\t {antall:>7} stk {lengde:>10} m {areal:>10} m2 {avvik} {kjent}"   )


def tellV4somV3( v3, v4, funkraV3, regl, dakat, v4datakilde='V4', debug=False): 

    tellinger = []
    differ =  []
    kjent = ''
    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]

    v4temp = v4.copy()
    v4temp['Veg'] = v4temp['Vegkategori'] + 'V' + v4temp['vegnummer'].astype('str')
    for Veg in v4temp['Veg'].unique():

        debug = None 
        # if 'FV5400' in Veg: 
        #     debug = True 

        tellV4 = v4mengdetelling( v4temp[ v4temp['Veg'] == Veg ], v4datakilde, 'langs-'+Veg, regl, dakat, debug=debug  )

        debugSkrivMeter( v4temp[ v4temp['Veg'] == Veg ], 'langs-'+Veg, regl, debug=debug)
        loggTelling( tellV4 )
        tellinger.append( tellV4 )

        if Veg in v3.keys() and regl['Beskrivelse'] in list( v3[Veg]['Beskrivelse']):
            row = v3[Veg][ v3[Veg]['Beskrivelse'] == regl['Beskrivelse']].iloc[0]


            tellV3 = {  'type'          : 'telling',
                         'datakilde'     : 'V3',  
                        'telletype'     : 'langs-'+Veg, 
                        'Beskrivelse'   : regl['Beskrivelse'], 
                        'objtype'       : regl['objtype'], 
                        'antall'        : row['Antall'],
                        'lengde'        : row['Lengde (m)'], 
                        'areal'         : row['Areal (m2)'], 
                        'Kjent problem' : kjent, 
                        'regl'          : regl  }
            loggTelling (tellV3 )
            tellinger.append( tellV3 )

            diff  = finnDifferanser( tellV3, tellV4, regl)
            loggTelling( diff )
            differ.append( diff )
        else: 
            print( 'Ingen data i V3-rapporten samsvarer med', regl['objtype'], regl['Beskrivelse'])

    return (tellinger, differ) 


def tellV4somV2( v2, v4, funkraV3, regl, dakat, v4datakilde='V4', debug=False ): 

    tellinger = []
    differ =  []
    kjent = ''
    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]

    v4temp = v4.copy()
    # v4temp['E+R'] = v4temp['Vegkategori'] + 'V' + v4temp['vegnummer'].astype('str')

    # Aktuelle kolonner i V2-rapporten 
    v2kol =  [ x for x in  list( v2.columns)[3:] if not 'Unnamed' in x  ]
    vegtyper = [ x.split('-')[0].strip() for x in v2kol ]
    vegtyper = set( vegtyper )

    for Veg in vegtyper:

        v4uttrekk = None 
        if Veg == 'E+R': 
            v4uttrekk = v4temp[ (v4temp['Vegkategori'] == 'E') | (v4temp['Vegkategori'] == 'R' ) ]
            v4uttrekk = v4uttrekk[ v4uttrekk['trafikantgruppe'] == 'K' ]
        elif Veg == 'g/s': 
            v4uttrekk = v4temp[ v4temp['trafikantgruppe'] == 'G' ]
        elif Veg == 'F' or Veg == 'K' or Veg == 'P' or Veg == 'S': 
            v4uttrekk = v4temp[ v4temp['Vegkategori'] == Veg ]
            v4uttrekk = v4uttrekk[ v4uttrekk['trafikantgruppe'] == 'K' ]
        else: 
            print( 'IKKE IMPLEMENTERT: Kolonne', Veg, 'i V2-rapporten. FIKS OPP!')
            # pdb.set_trace()

        if isinstance( v4uttrekk, pd.core.frame.DataFrame): 

            tellV4 = v4mengdetelling( v4uttrekk, v4datakilde, 'langs-'+Veg, regl, dakat  )
            debugSkrivMeter( v4uttrekk, 'langs-'+Veg, regl, debug=debug)

            loggTelling( tellV4 )
            tellinger.append( tellV4 )

            antallKolonne =  [ x for x in v2kol if Veg in x and 'Antall' in x][0]
            lengdeKolonne =  [ x for x in v2kol if Veg in x and 'Lengde' in x][0]
            arealKolonne  =  [ x for x in v2kol if Veg in x and 'Areal'  in x][0]

            if regl['Beskrivelse'] in list( v2['Beskrivelse']): 
                v2row = v2[ v2['Beskrivelse'] == regl['Beskrivelse']].iloc[0]

                tellV2 = {  'type'          : 'telling',
                            'datakilde'     : 'V2',  
                            'telletype'     : 'langs-'+Veg, 
                            'Beskrivelse'   : regl['Beskrivelse'], 
                            'objtype'       : regl['objtype'], 
                            'antall'        : v2row[antallKolonne],
                            'lengde'        : v2row[lengdeKolonne], 
                            'areal'         : v2row[arealKolonne], 
                            'Kjent problem' : kjent, 
                            'regl'          : regl  }
                loggTelling (tellV2 )
                tellinger.append( tellV2 )

                diff  = finnDifferanser( tellV2, tellV4, regl)
                loggTelling( diff )
                
                differ.append( diff )
            else: 
                print( 'Ingen data i V2-rapporten samsvarer med', regl['objtype'], regl['Beskrivelse'])

    return (tellinger, differ) 


def finnDifferanser( tellA, tellB, regl): 

    antall        = lengde       = areal        = np.nan
    antallprosent = lengdeprosent = arealprosent = np.nan
    karrakter = mellomrom = kjent = ''

    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]

    antall = abs( tellA['antall'] - tellB['antall'] ) 
    lengde = abs( tellA['lengde'] - tellB['lengde'] ) 
    areal  = abs( tellA['areal']  - tellB['areal']  ) 

    if ~np.isnan( antall ) and antall > 0: 
        antallprosent = 100 * antall / max( tellA['antall'], tellB['antall'])
        if antall == 1: 
            karrakter += 'mangler 1stk'
        elif antall > 1: 
            karrakter += 'MANGLER FLERE'

    if karrakter != '':
        mellomrom = 'og'

    if ~np.isnan( lengde ) and lengde > 0: 
        lengdeprosent = 100 * lengde / max( tellA['lengde'], tellB['lengde'])
        if lengdeprosent < 0.5: 
            pass
        elif lengdeprosent < 2: 
            karrakter = ' '.join( [ karrakter, mellomrom, 'små lengdeavvik' ] )
        elif lengdeprosent < 5: 
            karrakter = ' '.join( [ karrakter, mellomrom, 'noe lengdeavvik' ] )
        else: 
            karrakter = ' '.join( [ karrakter, mellomrom, 'STORE lengdeavvik' ] )

    if karrakter != '':
        mellomrom = 'og'


    if ~np.isnan( areal ) and areal > 0: 
        arealprosent = 100 * areal / max( tellA['areal'], tellB['areal'])

        if arealprosent < 0.5: 
            pass
        elif arealprosent < 2: 
            karrakter = ' '.join( [ karrakter, mellomrom, 'små arealavvik' ] )
        elif arealprosent < 5: 
            karrakter = ' '.join( [ karrakter, mellomrom, 'noe arealavvik' ] )
        else: 
            karrakter = ' '.join( [ karrakter, mellomrom, 'STORE arealavvik' ] )

    # if regl['Beskrivelse'] == 'Kantklippareal, årlig anbefalt areal':
    #     pdb.set_trace()


    diff   = {  'type'          : 'differanse',
                'datakilde'     : tellA['datakilde'] + ' og ' + tellB['datakilde'], 
                'telletype'     : tellA['telletype'], 
                'Beskrivelse'   : regl['Beskrivelse'], 
                'objtype'       : regl['objtype'], 
                'antall'        : antall,
                'lengde'        : lengde, 
                'areal'         : areal, 
                'antallprosent' : antallprosent,
                'lengdeprosent' : lengdeprosent,
                'arealprosent'  : arealprosent, 
                'avvik'         : karrakter, 
                'Kjent problem' : kjent,
                'regl'          : regl, 
                }


    return diff 

def debugSkrivMeter( v4, vegstrekning, regl, debug=False): 
    """
    Skriver detaljert meter-stedfesting for objektene som inngår i en telling
    """

    if debug: 

        print( f"\nDetaljert meterangivelse for {regl['Beskrivelse']} {vegstrekning} " )


        for junk, row in v4.iterrows(): 

            konnekteringKorreksjon = ''
            if 'orginalLengde' in v4.columns and row['orginalLengde'] != row['Lengde vegnett']: 
                konnekteringKorreksjon = 'KORRIGERT, orginal lengde=' + str( row['orginalLengde'] )

            if np.isnan( row['KryssSystem/SideAnlegg Nummer'] ): 
                print( ( f"\t\t{vegstrekning}\t {row['Objekt Id']}\t {row['Vegkategori']}{row['Fase']}{row['vegnummer']}"
                        f" s{row['Strekningsnummer']}d{row['Delstrekningsnummer']}"
                        f" m{row['Frameter']}-{row['Tilmeter']}"
                        f" LENGDE={row['Lengde vegnett']} {konnekteringKorreksjon}" ))

            else: 
                print( ( f"\t\t{vegstrekning}\t {row['Objekt Id']}\t {row['Vegkategori']}{row['Fase']}{row['vegnummer']}"
                        f" s{row['Strekningsnummer']}d{row['Delstrekningsnummer']}"
                        f" m{row['Frameter']} " 
                        f"{row['KD/SD']}{row['Delnummer']} m{row['Frameter ']}-{row['Tilmeter ']}"
                        f" LENGDE={row['Lengde vegnett']} {konnekteringKorreksjon}" 
                        ))

        # pdb.set_trace()
    

def v4mengdetelling( v4, datakilde, telletype, regl, dakat, debug=None):
    """
    Regner ut antall, lengde og areal for en V4-dataframe. 

    Hvis du skal ha V2- eller V3-oppsummering så må du filtrere det på forhånd 

    RETURNS: 
        tell - dictionary med metadata og antall, lengde, areal
    """
    
    col_id = 'Objekt Id'
    antall = lengde = areal = np.nan 
    colAntall = colLengde = colAreal = colTverrsnitt = None 
    v4raadata = v4.copy()

    if len( v4 ) > 0: 

        if 'Lengde vegnett' in v4.columns: 
            colVeglengde = 'Lengde vegnett'
        elif 'lengde' in v4.columns:  # vegnnettsdata fra NVDB api / nvdbapiv3.py ? 
            colVeglengde = 'lengde'
        elif 'strekningslengde' in v4.columns:  # Litt usikker på denne, har den med for sikkerhets skyld? 
            colVeglengde = 'strekningslengde'
        elif 'segmentlengde' in v4.columns:  # fagdata fra NVDB api / nvdbapiv3.py 
            colVeglengde = 'segmentlengde'
        else: 
            print( 'ADVARSEL - mangler kolonne for "Lengde vegnett" i dataframe', datakilde, telletype, v4.columns)

        # Teller antall  
        if 'withCount' in regl: 
            antall = len( v4[col_id].unique() )
        elif 'withCountFrom' in regl: 
            colAntall = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withCountFrom'] )]['navn']

            if not colAntall in v4.columns: 
                v4[colAntall] = np.nan 

            # Finner dem med antall-egenskap, og den inverse
            harAntall  = v4[ ~v4[colAntall].isnull() ].drop_duplicates( subset=col_id)
            ikkeAntall = v4[  v4[colAntall].isnull() ].drop_duplicates( subset=col_id)
            antall     = harAntall[colAntall].sum() + len( ikkeAntall[col_id].unique() )

        # Lengde-regler og variabler 
        # 'withLengthFromRoadnet', 
        # 'withLengthPreferingFromAttribute',  
        if 'withLengthPreferingFromAttribute' in regl: 
            colLengde = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withLengthPreferingFromAttribute'] )]['navn']
        
            if not colLengde in v4.columns: 
                v4[colLengde] = np.nan 

        # Areal-regler og variabler
        # 'withAreaFromAttribute', 
        # 'withAreaFromAttributeOrCrossSection', 
        # 'withAreaFromCrossSection',
        # 'YearlyGrassCuttingAreaPreset'
        if 'withAreaFromAttribute' in regl: 
            colAreal = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromAttribute'] )]['navn']

            if not colAreal in v4.columns: 
                v4[colAreal] = np.nan 

        elif 'withAreaFromCrossSection' in regl: 
            colTverrsnitt = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromCrossSection'] )]['navn'] 
            if not colTverrsnitt in v4.columns: 
                v4[colTverrsnitt] = np.nan 

        elif 'withAreaFromAttributeOrCrossSection' in regl: 
            colAreal      = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromAttributeOrCrossSection'][0] )]['navn']
            colTverrsnitt = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromAttributeOrCrossSection'][1] )]['navn']
            if not colTverrsnitt in v4.columns:
                v4[colTverrsnitt] = np.nan 
            if not colAreal in v4.columns: 
                v4[colAreal] = np.nan 

        # Lager en v4-kopi spesielt for arealberegning 
        v4areal = v4.copy()

        arealsum_harAreal = arealsum_TxL = 0 


        if colAreal: 
        
            # Finner først dem som har  - og ikke har - Areal-egenskap
            harAreal  = v4areal[ ~v4areal[colAreal].isnull() ].drop_duplicates(subset=col_id)
            arealsum_harAreal = harAreal[colAreal].sum()
            v4areal   = v4areal[ v4areal[colAreal].isnull() ].copy() # Har ikke areal

        # Finne dem tversnitt (bredde eller høyde)
        if colTverrsnitt: 

            tverr    = v4areal[ ~v4areal[colTverrsnitt].isnull() ].copy()

            # Av dem igjen, finne dem som har Lengde-egenskap og multiplisere bredden/høyden med lengden
            if colLengde: 
                tverr_len           = tverr[ ~tverr[colLengde].isnull()].drop_duplicates( subset=col_id ).copy()
                tverr_veg           = tverr[  tverr[colLengde].isnull()].copy()        
                tverr_len[colAreal] = tverr_len[colTverrsnitt] * tverr_len[colLengde] 
                tverr_veg[colAreal] = tverr_veg[colTverrsnitt] * tverr_veg[colVeglengde]
                arealsum_TxL        = tverr_len[colAreal].sum() + tverr_veg[colAreal].sum()
            else: 
                tverr[colAreal]     = tverr[colTverrsnitt] * tverr[colVeglengde]
                arealsum_TxL        = tverr[colAreal].sum()

        if debug: 
            pass 
            # pdb.set_trace( )

        areal = arealsum_harAreal + arealsum_TxL

        # Variabler for lengde 
        # 'withLengthFromRoadnet', 
        # 'withLengthPreferingFromAttribute', 
        if colLengde: 

            harLengde = v4[ ~v4[colLengde].isnull() ].drop_duplicates( subset=col_id )
            lengde = harLengde[colLengde].sum() + v4[ v4[colLengde].isnull() ][colVeglengde].sum()

        elif 'withLengthFromRoadnet' in regl or 'withFeatureLabel' in regl: 
            lengde = v4[colVeglengde].sum()

    kjent = ''
    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]

    # Spesialregler for årlig klipp av kantareal, modifiserer V4 
    # med et areal som er multiplisert med faktor 0.25-2
    if 'YearlyGrassCuttingAreaPreset' in regl: 
        v4areal = kantklippspesial( v4raadata, regl, dakat[str( regl['objtype'] )], strekning=telletype, debug=debug)
        areal = v4areal['Areal'].sum()
        lengde = np.nan

    tell = {    'type'          : 'telling',
                'datakilde'     : datakilde,  
                'telletype'     : telletype, 
                'Beskrivelse'   : regl['Beskrivelse'], 
                'objtype'       : regl['objtype'], 
                'antall' : antall, 'lengde' : lengde, 'areal' : areal, 
                'Kjent problem' : kjent,
                'regl' : regl  }

    # loggTelling( tell )
    return tell 

def hentdata( mappenavn, lespickle=False, hentFunkraV3=False  ): 

    filnavn = None 

    filnavn = finnrapportfilnavn( mappenavn )
    v1    = pd.read_excel( filnavn['v1rapp'], sheet_name='Samlet, alt vegnett', header=5) 
    v2    = pd.read_excel( filnavn['v2rapp'], sheet_name='V2', header=5) 
    v3alt = pd.read_excel( filnavn['v3rapp'], sheet_name=None, header=5 )
    v4alt = pd.read_excel( filnavn['v4rapp'], sheet_name=None, header=5 )
   
    # Leser Funkraliste hvis den finnes 
    funkraV3 = None
    if hentFunkraV3:         
        if not filnavn: 
            filnavn = finnrapportfilnavn( mappenavn )
        if 'funkra' in filnavn: 
            funkraV3 = lesfunkraV3( filnavn['funkra'], giMegV3=True )

    return (v1, v2, v3alt, v4alt, funkraV3)

def feilObjektDefinisjon(regl): 
    data = []
    kjent = ''

    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]


    spesial = { 241 : 'Ingen data for 241', 
                810 : 'Summering vinterdriftsklasse feiler'}

    # if regl['objtype'] in [241, 810 ]: 
    if regl['objtype'] in [ -9, -10 ]: 
        antall = lengde = areal = np.nan 
        tell = { 'type'          : 'FEIL',
                'datakilde'     : 'V2,V3,V4',  
                'telletype'     : 'FEIL', 
                'Beskrivelse'   : regl['Beskrivelse'], 
                'objtype'       : regl['objtype'], 
                'antall'        : antall, 
                'lengde'        : lengde, 
                'areal'         : areal, 
                'avvik'         : spesial[regl['objtype']], 
                'Kjent problem'  : kjent,
                'regl'          : regl }
        data.append( tell )
        loggTelling( tell )
    return data


def hentNvdbdata( objType, nvdbFilter ): 

    sok = nvdbapiv3.nvdbFagdata( objType )
    sok.filter( nvdbFilter )
    data = pd.DataFrame( sok.to_records( ))

    if len( data ) == 0: 

        data = pd.DataFrame( columns = ['objekttype', 'nvdbId', 'versjon', 'startdato', 'veglenkesekvensid', 'detaljnivå',
                                        'typeVeg', 'kommune', 'fylke', 'vref', 'vegkategori', 'fase', 'nummer',
                                        'startposisjon', 'sluttposisjon', 'segmentlengde', 'adskilte_lop',
                                        'trafikantgruppe', 'geometri'] )

    data.rename( columns= { 'vegkategori' : 'Vegkategori', 'nvdbId' : 'Objekt Id', 'nummer' : 'vegnummer'}, inplace=True)

    # Lengde for punktdata, ellers tryner det
    if not 'segmentlengde' in data: 
        data['segmentlengde'] = np.nan

    return data 


def sammenlignV4( nvdbData, v4regneark, komradeNavn, objtype ): 

    antall          = np.nan 
    lengde          = np.nan 
    antallprosent   = np.nan 
    lengdeprosent   = np.nan 
    feilstring      = ''
    nvdbAntall      = np.nan # len( nvdbId)
    v4Antall        = np.nan # len( v4Id )
    lengdeNvdb      = np.nan 
    lengdeV4        = np.nan 

    if len( nvdbData) > 0: 
        nvdbAntall = len( list( nvdbData['Objekt Id'].unique() ))
        lengdeNvdb =  nvdbData['segmentlengde'].sum()

    if len( v4regneark ) > 0: 
        v4Antall   = len( list( v4regneark['Objekt Id'].unique()  ) )
        lengdeV4   =  v4regneark['Lengde vegnett'].sum()


    if len( nvdbData ) > 0 and len( v4regneark ) > 0: 
        nvdbId = set( list(   nvdbData['Objekt Id']  ))
        v4Id   = set( list( v4regneark['Objekt Id']  ))

        diffA = list( nvdbId - v4Id ) 
        diffB = list( v4Id - nvdbId )

        max_ID = 6
        feilstring = '' 
        if len( diffA ) > 0: 
            idString = ','.join( [ str(x) for x in diffA[:max_ID] ]  ) 
            if len( diffA ) > max_ID+1:
                idString += f".... (totalt {len(diffA)} objekter"

            feilstring += f"QA V4  {len(diffA)} objekt av type {objtype} mangler i V4-rapport, men finnes i {komradeNavn} : {idString} " 
            print( feilstring)

        if len( diffB ) > 0: 
            idString = ','.join( [ str(x) for x in diffB[:max_ID] ]  ) 
            if len( diffB ) > max_ID+1:
                idString += f".... (totalt {len(diffB)} objekter"

            feilstring += f"QA V4  {len(diffB)} objekt av type {objtype} FINNES i V4-rapport, men ikke i nedlasting fra {komradeNavn} : {idString} " 
            print( f"QA V4  {len(diffB)} objekt av type {objtype} FINNES i V4-rapport, men ikke i nedlasting fra {komradeNavn} : {idString} " )

        antall = len( diffA ) + len( diffB )
        maks_antall = max( [ len( nvdbId  ), len( v4Id) ] )
        if ~np.isnan( antall ) and ~np.isnan( maks_antall) and maks_antall > 0: 
            antallprosent = 100 * antall / maks_antall 

        lengde = abs( lengdeNvdb - lengdeV4 ) 
        maks_lengde = max( [ lengdeNvdb, lengdeV4  ] )

        if ~np.isnan( lengde ) and ~np.isnan( maks_lengde) and maks_lengde > 0: 
            lengdeprosent = 100 * lengde / maks_lengde 


    beskrivelse = f"Tellekontroll {objtype} innafor {komradeNavn} "
    diff   = {  'type'          : 'differanse',
                'datakilde'     : 'nvdb og V4', 
                'telletype'     : 'tellALT', 
                'Beskrivelse'   : beskrivelse, 
                'objtype'       : objtype, 
                'antall'        : antall,
                'lengde'        : lengde, 
                'areal'         : np.nan, 
                'antallprosent' : antallprosent,
                'lengdeprosent' : lengdeprosent,
                'arealprosent'  : np.nan, 
                'avvik'         : feilstring, 
                'Kjent problem' : '',
                'regl'          : { 'objtype' : objtype, 'Beskrivelse' : beskrivelse} 
                }

    nvdbBeskrivelse = f"Tellekontroll {objtype} innafor {komradeNavn} "
    tellNvdb = {    'type'          : 'telling',
                    'datakilde'     : 'nvdb',  
                    'telletype'     : 'tellALT', 
                    'Beskrivelse'   : nvdbBeskrivelse, 
                    'objtype'       : objtype, 
                    'antall' : nvdbAntall, 'lengde' : lengdeNvdb, 'areal' : np.nan, 
                    'Kjent problem' : '',
                    'regl'          : { 'objtype' : objtype, 'Beskrivelse' : nvdbBeskrivelse }   
                    }


    v4Beskrivelse = f"Tellekontroll {objtype} innafor {komradeNavn} "
    tellV4   = {    'type'          : 'telling',
                    'datakilde'     : 'v4',  
                    'telletype'     : 'tellALT', 
                    'Beskrivelse'   : v4Beskrivelse, 
                    'objtype'       : objtype, 
                    'antall' : v4Antall, 'lengde' : lengdeV4, 'areal' : np.nan, 
                    'Kjent problem' : '',
                    'regl'          : { 'objtype' : objtype, 'Beskrivelse' : nvdbBeskrivelse }   
                    }

    loggTelling( tellV4)
    loggTelling( tellNvdb)
    loggTelling( diff )

    return diff, [tellNvdb, tellV4 ]


def v4filterEnvegMot( v4data, v1): 
    """
    Filtrerer vekk "adskilte løp" basert på vegnettsrapport V1

    Forutsetter at fagdata blir segmentert på start- og slutt adskilte løp. Ser slik ut... 

    Vær obs på forskjellen mellom 'Frameter', 'Tilmeter' og 'Frameter ', 'Tilmeter ' i kolonnenavnene
    Frameter, Tilmneter inklusive mellomrom bakerst = meterverdier på sideanlegg og kryssdeler 
    Uten mellomrom bakerst = meterverdier på vanlig veg. 
    """

    mot_vanlig = v1[  (v1['Adskilte Løp'] == 'MOT') & (  v1['KryssSystem/SideAnlegg Nummer'].isnull() ) ]
    mot_side   = v1[  (v1['Adskilte Løp'] == 'MOT') & ( ~v1['KryssSystem/SideAnlegg Nummer'].isnull() ) ]

    v4_vanlig = v4data[  v4data['KryssSystem/SideAnlegg Nummer'].isnull()   ]
    v4_side   = v4data[ ~v4data['KryssSystem/SideAnlegg Nummer'].isnull()   ]

    motgaaende = [ ]
    if len( mot_vanlig  ) > 0 and len( v4_vanlig ) > 0: 
        for junk, row in mot_vanlig.iterrows(): 
            temp = v4_vanlig[   (v4_vanlig['Vegkategori']           == row['Vegkategori']) & 
                                (v4_vanlig['Fase']                  == row['Fase']) & 
                                (v4_vanlig['vegnummer']             == row['vegnummer']) & 
                                (v4_vanlig['Strekningsnummer']      == row['Strekningsnummer']) & 
                                (v4_vanlig['Delstrekningsnummer']   == row['Delstrekningsnummer']) & 
                                (v4_vanlig['Frameter']              <  row['Tilmeter']) & 
                                (v4_vanlig['Tilmeter']              >  row['Frameter']) 
                            ].copy()   

            if len( temp ) > 0: 
                motgaaende.append( temp )

    if len( mot_side  ) > 0 and len( v4_side ) > 0: 
        for junk, row in mot_side.iterrows(): 
            temp = v4_side[     (v4_side['Vegkategori']                     == row['Vegkategori']) & 
                                (v4_side['Fase']                            == row['Fase']) & 
                                (v4_side['vegnummer']                       == row['vegnummer']) & 
                                (v4_side['Strekningsnummer']                == row['Strekningsnummer']) & 
                                (v4_side['Delstrekningsnummer']             == row['Delstrekningsnummer']) & 
                                (v4_side['Frameter']                        == row['Frameter']) & 
                                (v4_side['KS/SA']                           == row['KS/SA']) & 
                                (v4_side['KryssSystem/SideAnlegg Nummer']   == row['KryssSystem/SideAnlegg Nummer']) &
                                (v4_side['Delnummer']                       ==  row['Delnummer']) &
                                (v4_side['Frameter ']                        <  row['Tilmeter ']) & 
                                (v4_side['Tilmeter ']                        >  row['Frameter ']) 
                            ].copy()

            if len( temp ) > 0: 
                motgaaende.append( temp )

    if len( motgaaende ) > 0: 
        motgaaendeDf = pd.concat( motgaaende )

        v4ut = v4data[ ~v4data.index.isin(  motgaaendeDf.index )].copy()
        # pdb.set_trace()

    else: 
        v4ut = v4data.copy()


    return v4ut 



def fjernKonnektering( v4data, v1): 
    """
    Fjerner lengden av konnekteringslenker fra  V4-datasettet 

    Konnekteringslenker hentes fra V1 - datasettet. Der det er overlapp mellom en (eller flere) konnekteringslenker og V4-segmenter
    så trekkes lengden av konnektering fra angjeldende V4-segment. 

    Vær obs på forskjellen mellom 'Frameter', 'Tilmeter' og 'Frameter ', 'Tilmeter ' i kolonnenavnene
    Frameter, Tilmneter inklusive mellomrom bakerst = meterverdier på sideanlegg og kryssdeler 
    Uten mellomrom bakerst = meterverdier på vanlig veg. 
    """

    v1 = deepcopy(v1 )
    v1['typeVeg'] = v1['typeVeg'].fillna( value='')

    konnektering = v1[  v1['typeVeg'].str.contains('Konnektering')  ]
    konnektering_vanlig = konnektering[   konnektering['KryssSystem/SideAnlegg Nummer'].isnull( ) ]
    konnektering_side   = konnektering[  ~konnektering['KryssSystem/SideAnlegg Nummer'].isnull( ) ]

    v4data = deepcopy( v4data )
    v4data['orginalLengde'] = v4data['Lengde vegnett']

    for ii, row in v4data.iterrows(): 
        
        if np.isnan(  row['KryssSystem/SideAnlegg Nummer']  ): 
            temp = konnektering_vanlig[     (konnektering_vanlig['Vegkategori']           == row['Vegkategori']) & 
                                            (konnektering_vanlig['Fase']                  == row['Fase']) & 
                                            (konnektering_vanlig['vegnummer']             == row['vegnummer']) & 
                                            (konnektering_vanlig['Strekningsnummer']      == row['Strekningsnummer']) & 
                                            (konnektering_vanlig['Delstrekningsnummer']   == row['Delstrekningsnummer']) & 
                                            (konnektering_vanlig['Frameter']              <  row['Tilmeter']) & 
                                            (konnektering_vanlig['Tilmeter']              >  row['Frameter']) 
                                        ].copy()   

        else: 
            temp = konnektering_side[       (konnektering_side['Vegkategori']           == row['Vegkategori']) & 
                                            (konnektering_side['Fase']                  == row['Fase']) & 
                                            (konnektering_side['vegnummer']             == row['vegnummer']) & 
                                            (konnektering_side['Strekningsnummer']      == row['Strekningsnummer']) & 
                                            (konnektering_side['Delstrekningsnummer']   == row['Delstrekningsnummer']) & 
                                            (konnektering_side['Frameter']              <  row['Tilmeter']) & 
                                            (konnektering_side['Tilmeter']              >  row['Frameter']) 
                                        ].copy()   

        if len( temp ) > 0: 

            v4data.loc[ ii, 'Lengde vegnett'] = row['Lengde vegnett'] - temp['Lengde veg (m)'].sum()


        # if row['vegnummer'] == 39 and row['Strekningsnummer'] == 54: 
        #     pdb.set_trace()

    return v4data




def mengdesjekk( mappenavn, objekttyper, nvdbFilter=None,  lespickle=False, hentFunkraV3=False, brukNvdbData=True, debug=False ): 
    """
    Ny metode som sammenligner V3-oppføringer vegnummer for vegnummre
    """

    # Leser regler for de ulike radene
    (regelListe, dakat) = lesregler()
    
    # Leser de ulike regnearkene 
    (v1, v2, v3alt, v4alt, funkraV3 ) = hentdata( mappenavn, lespickle=lespickle, hentFunkraV3=hentFunkraV3 )

   # Forbereder for lesning av V4-data (ett ark per objekttype)
    v4indeks = list( v4alt['Objektoversikt'].iloc[:,0] )
    v4indeks =  {  int( n.split('-')[0] )  : n  for n in v4indeks }

    datarader = []
    differanser = []
         
    if isinstance( objekttyper, int):
        objekttyper = [ objekttyper ]
    for objekttype in objekttyper: 
        v4regneark = v4alt[v4indeks[objekttype]]
        # v4data = lesv4( filnavn['v4rapp'], sheet_name=v4indeks[objekttype])

    
        if nvdbFilter and brukNvdbData: 
            nvdbData = hentNvdbdata( objekttype, nvdbFilter )
            v4dRaadata = nvdbData 
            v4datakilde = 'nvdb'
            (endiff, flereTellinger) = sammenlignV4( nvdbData, v4regneark, nvdbFilter['kontraktsomrade'], objekttype )
            differanser.append( endiff )
            datarader.extend( flereTellinger )

            # Fant ett objekt uten vegsystemreferanse, fjerner det
            # https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/27/960941773/1.json?inkluder=alle 
            if len( v4dRaadata[ v4dRaadata['vegnummer'].isnull()] ): 
                v4dRaadata = v4dRaadata[ ~v4dRaadata['vegnummer'].isnull() ].copy()
                v4dRaadata['vegnummer'] = v4dRaadata['vegnummer'].astype(int)


        else: 
            v4dRaadata = v4regneark.copy()
            v4datakilde = 'V4'
            # Må døpe om døpe om "Trafikantgruppe" => "trafikantgruppe" pga navnekollisjon med 482 Trafikkregistreringsstasjon
            # Her kan vi heldigvis basere oss på rekkefølgen, hvor den første "Trafikantgruppe" - kolonnen i regnearket er den vi vil ha
            v4dRaadata.rename( columns={'Trafikantgruppe' : 'trafikantgruppe'}, inplace=True )
            if 'Trafikantgruppe.1' in v4dRaadata.columns: 
                v4dRaadata.rename( columns={'Trafikantgruppe.1' : 'Trafikantgruppe'}, inplace=True )

            
        regler = [ x for x in regelListe if x['objtype'] == objekttype ]
        if len( regler ) == 0: 
            print( 'Fant ingen regler for objekttype', objekttype)

        for regl in regler: 
            v4data = v4dRaadata.copy( )
            # v4Backup = v4dRaadata.copy()

            v4data = egenskapfilter( v4data, regl, dakat[str(objekttype)] )

            # Sjekk for "Adskilte løp" for 'withFeatureLabel' - regel 
            if 'withFeatureLabel' in regl: 
                print( f"\n\nFjerner konnekteringslenker og envg mot fra {regl['objtype']} {regl['Beskrivelse']} ")
                print( f"Lengde før korreksjon {v4data['Lengde vegnett'].sum()} ")
                if brukNvdbData: 
                    v4data = v4data[ v4data[ 'adskilte_lop'] != 'Mot'  ].copy()
                else: 
                    v4data = v4filterEnvegMot( v4data, v1 )
                    v4data = fjernKonnektering( v4data, v1)                    # Korrigerer for konnekteringslenker 
                print( f"Lengde etter korreksjon {v4data['Lengde vegnett'].sum()}\n\n")
 

            # Etterprøver V2-regnearket
            (tellinger, differ) = tellV4somV2(   v2, v4data, funkraV3, regl, dakat, v4datakilde=v4datakilde, debug=debug) 
            datarader.extend( tellinger )
            differanser.extend( differ )

            # Etterprøver V3-regnearket 
            (tellinger, differ) = tellV4somV3( v3alt, v4data, funkraV3, regl, dakat, v4datakilde=v4datakilde, debug=debug) 
            datarader.extend( tellinger )
            differanser.extend( differ )

            # spesialbehanding av et par objekt som ikke plukkes opp fordi feilen gjør at de ikke finnes i listene 
            datarader.extend(    feilObjektDefinisjon(regl) )
            differanser.extend(  feilObjektDefinisjon(regl) )
            

    # pdb.set_trace( )
    return (datarader, differanser)
    
if __name__ == "__main__":


    # mappenavn = './nedlasting_ATM_2021-01-279305_Sunnfjord_2021-2026/'
    # filnavn = finnrapportfilnavn( mappenavn ) 
    # v4oversikt = pd.read_excel( filnavn['v4rapp'] )  
    # v4indeks = list( v4oversikt['Unnamed: 0'])[5:] 
    # objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  
    # (tellinger, differanser) = mengdesjekk( mappenavn, objektliste, lespickle=False, hentFunkraV3=False )  


    mapper = ['nedlasting_2021-02-021102_Høgsfjord_2015-2020', 'nedlasting_2021-02-021105_Indre_Ryfylke_2015-2021' ]
    mapper.append( 'nedlasting_UTV_2021-02-02_1206_Voss_2014-2019' ) 
    mapper.append( 'nedlasting_UTV_2021-02-02_9108_Østerdalen_2021-2025' ) 
    flere_komrader = []
    flere_differ = []
    for mappe in mapper: 

        # mappe = 'nedlasting_UTV_2021-02-029305_Sunnfjord_2021-2026'
        mappenavn = './' + mappe + '/'
        # mappenavn = './test_nedlasting28des2020_9305_Sunnfjord/'
        # with open( 'v4picle.pickle', 'rb' ) as f: 
        #     v4alt = pickle.load(f ) 
        # v4indeks = list( v4alt['Objektoversikt']['79 tabeller:'] )
        # objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  

        filnavn = finnrapportfilnavn( mappenavn ) 
        v4oversikt = pd.read_excel( filnavn['v4rapp'] )  
        v4indeks = list( v4oversikt['Unnamed: 0'])[5:] 
        objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  

        # Navn på mapper og kontraktsområder
        svarmapper1 = mappe.split('_')
        svarmapper = [ x for x in svarmapper1 if x.lower() not in ['nedlasting', 'utv', 'test' ] ]
        komrade = ' '.join( svarmapper )
        flere_komrader.append( komrade )

        # (tellinger, differanser) = mengdesjekk( mappenavn, 540, lespickle=False, hentFunkraV3=False )  
        (tellinger, differanser) = mengdesjekk( mappenavn, objektliste, lespickle=False, hentFunkraV3=False )  
        differanser = [ dict( x, **{ 'omrade' : komrade }) for x in differanser ] # https://stackoverflow.com/a/34757497
        flere_differ.extend( differanser )

        diff = pd.DataFrame( differanser )
        tell = pd.DataFrame( tellinger )

        svar = lagHtmlOppsummering( diff, omraade=komrade )

        with open( 'test_' + mappe + '.html', 'w') as f:
            f.write( svar )

    if len( flere_komrader ) > 1: 
        komrade = ', '.join( flere_komrader )
        diff = pd.DataFrame( flere_differ )
        svar = lagHtmlOppsummering( diff, omraade=komrade )
        with open( 'testsammendrag_flererapporter.html', 'w') as f: 
            f.write( svar )

