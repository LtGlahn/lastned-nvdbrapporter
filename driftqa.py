"""
Ny og forhåpentligvis bedre rutiner for å kvalitetssikre driftskontrakt-rapporter

Bruker de gode funksjonene fra driftskontraktsjekk.py for å 
laste inn og - i noen grad - manipulere data. Men den overordnede logikken er 
skrevet på ny, forhåpentligvis enklere og bedre. 

Her returnerer vi to dataframes: En med alle tallene som er henta, og en med differanser  

"""

import pdb 

import pandas as pd
import pickle
import numpy as np

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

    antallfarge = oppsummerDiff_htmlfarge( mindict['antall'] )
    lengdeFarge = oppsummerDiff_htmlfarge( mindict['lengde'] )
    arealFarge = oppsummerDiff_htmlfarge( mindict['areal'] )
    
    tableRow = (    f"<tr>"
                    f"<td> {mindict['objtype'] } </td>" 
                    f"<td> {mindict['Beskrivelse']} </td>" 
                    f"<td {antallfarge}> {mindict['antall']} </td> "
                    f"<td {lengdeFarge}> {mindict['lengde']} </td>"
                    f"<td {arealFarge}>  {mindict['areal']} </td>"
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


    if np.isnan( antall ): 
        antall = '-'
    elif antall == 0 and np.isnan( antallprosent ): 
        antall = 'OK'
    elif antall == 1: 
        antall = 'Noe avvik'
    elif antallprosent < 2: 
        antall = 'Noe avvik'
    elif antallprosent > 2: 
        antall = 'Mye avvik'
    else: 
        antall = 'FEIL i QA'

    if np.isnan( lengde ): 
        lengde = '-'
    elif lengde == 0 and np.isnan( lengdeprosent ): 
        lengde = 'OK'
    elif ~np.isnan( lengdeprosent) and lengdeprosent < 0.5: 
        lengde = 'OK'
    elif ~np.isnan( lengdeprosent) and lengdeprosent < 2: 
        lengde = 'Noe avvik'
    elif ~np.isnan( lengdeprosent) and lengdeprosent > 2: 
        lengde = 'Store avvik'
    else: 
        lengde = 'FEIL i QA'


    if np.isnan( areal ): 
        areal = '-'
    elif areal == 0 and np.isnan( arealprosent ): 
        areal = 'OK'
    elif ~np.isnan( arealprosent) and arealprosent < 0.5: 
        areal = 'OK'
    elif ~np.isnan( arealprosent) and arealprosent < 2: 
        areal = 'Noe avvik'
    elif ~np.isnan( arealprosent) and arealprosent > 2: 
        areal = 'Store avvik'
    else: 
        areal = 'FEIL i QA'


    oppsum = { 
            'type'             :  ', '.join( list( diff['type'].unique()) ),
            'datakilde'        : ', '.join( list( diff['datakilde'].unique()) ), 
            'telletype'        : ', '.join( list( diff['type'].unique()) ), 
            'Beskrivelse'      : ', '.join( list( diff['Beskrivelse'].unique()) ), 
            'objtype'          : set( list( diff['objtype'].unique()) ),  
            'antall'           :  antall,
            'lengde'           :  lengde,
            'areal'            :  areal,
            'avvik'            : ', '.join( list( diff['avvik'].unique()) ),  
            'Kjent problem'    : ', '.join( list( diff['Kjent problem'].unique()) )  
    }

    return oppsum

def lagHtmlOppsummering( diff ): 

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
                f'<p>Denne tabellen er laget ved å bruke data fra V4-tabellen og egenprodusert kode som "etterligner" beregning av V2- og V3-tabellene, for antall, lengde og areal per vegstrekning.</p>\n\n' 
                f'<h3>Kjente svakheter</h3>\n\n'
                f'men feiler for de mer komplekse tilfellene (f.eks <em>"Grøft unntatt terrenggrøft"</em>). Dette blir forbedret.</p>\n\n' 
                f'<p>Andre <em>"Kjente feil"</em> mener vi er feil i produksjonssystemet vårt. Feilsøking og feilretting pågår.</p>\n'
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
                f"\t {antall:>7} stk {lengde:>10} m {areal:>10} m2 {avvik} {kjent}"   )


def tellV4somV3( v3, v4, funkraV3, regl, dakat): 

    tellinger = []
    differ =  []
    kjent = ''
    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]

    v4temp = v4.copy()
    v4temp['Veg'] = v4temp['Vegkategori'] + 'V' + v4temp['vegnummer'].astype('str')
    for Veg in v4temp['Veg'].unique():
        tellV4 = v4mengdetelling( v4temp[ v4temp['Veg'] == Veg ], 'v4', 'langs-'+Veg, regl, dakat  )
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

            diff  = differanser( tellV3, tellV4, regl)
            loggTelling( diff )
            differ.append( diff )
        else: 
            print( 'Ingen data i V3-rapporten samsvarer med', regl['objtype'], regl['Beskrivelse'])

    return (tellinger, differ) 


def tellV4somV2( v2, v4, funkraV3, regl, dakat): 

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
            v4uttrekk = v4uttrekk[ v4uttrekk['Trafikantgruppe'] == 'K' ]
        elif Veg == 'g/s': 
            v4uttrekk = v4temp[ v4temp['Trafikantgruppe'] == 'G' ]
        else: 
            print( 'IKKE IMPLEMENTERT: Kolonne', Veg, 'i V2-rapporten. FIKS OPP!')

        if isinstance( v4uttrekk, pd.core.frame.DataFrame): 

            tellV4 = v4mengdetelling( v4uttrekk, 'v4', 'langs-'+Veg, regl, dakat  )
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

                diff  = differanser( tellV2, tellV4, regl)
                loggTelling( diff )
                
                differ.append( diff )
            else: 
                print( 'Ingen data i V2-rapporten samsvarer med', regl['objtype'], regl['Beskrivelse'])

    return (tellinger, differ) 


def differanser( tellA, tellB, regl): 

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


def v4mengdetelling( v4, datakilde, telletype, regl, dakat):
    """
    Regner ut antall, lengde og areal for en V4-dataframe. 

    Hvis du skal ha V2- eller V3-oppsummering så må du filtrere det på forhånd 

    RETURNS: 
        tell - dictionary med metadata og antall, lengde, areal
    """
    
    col_id = 'Objekt Id'
    antall = lengde = areal = np.nan 
    colAntall = colLengde = colAreal = colTverrsnitt = None 

    if 'Lengde vegnett' in v4.columns: 
        colVeglengde = 'Lengde vegnett'
    elif 'lengde' in v4.columns:  # vegnnettsdata fra NVDB api / nvdbapiv3.py ? 
        colVeglengde = 'lengde'
    elif 'strekningslengde' in v4.columns:  # fagdata fra NVDB api / nvdbapiv3.py ? 
        colVeglengde = 'strekningslengde'
    else: 
        print( 'ADVARSEL - mangler kolonne for "Lengde vegnett" i dataframe', datakilde, telletype, v4.columns)

    # Teller antall  
    if 'withCount' in regl: 
        antall = len( v4[col_id].unique() )
    elif 'withCountFrom' in regl: 
        colAntall = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withCountFrom'] )]['navn']

        # Finner dem med antall-egenskap, og den inverse
        harAntall  = v4[ ~v4[colAntall].isnull() ].drop_duplicates( subset=col_id)
        ikkeAntall = v4[  v4[colAntall].isnull() ].drop_duplicates( subset=col_id)
        antall     = harAntall[colAntall].sum() + len( ikkeAntall[col_id].unique() )

    # Lengde-regler og variabler 
    # 'withLengthFromRoadnet', 
    # 'withLengthPreferingFromAttribute', 
    # 'withCustomPresetsNumberInRange', 
    if 'withLengthPreferingFromAttribute' in regl: 
        colLengde = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withLengthPreferingFromAttribute'] )]['navn']
    


    # Areal-regler og variabler
    # 'withAreaFromAttribute', 
    # 'withAreaFromAttributeOrCrossSection', 
    # 'withAreaFromCrossSection',
    # 'YearlyGrassCuttingAreaPreset'
    if 'withAreaFromAttribute' in regl: 
        colAreal = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromAttribute'] )]['navn']
    elif 'withAreaFromCrossSection' in regl: 
        colTverrsnitt = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromCrossSection'] )]['navn'] 
    elif 'withAreaFromAttributeOrCrossSection' in regl: 
        colAreal      = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromAttributeOrCrossSection'][0] )]['navn']
        colTverrsnitt = dakat[str(regl['objtype'])]['egenskaper'][str( regl['withAreaFromAttributeOrCrossSection'][1] )]['navn']

    # Lager en v4-kopi spesielt for arealberegning 
    v4areal = v4.copy()
    arealsum_harAreal = arealsum_TxL = 0 
    # Spesialregler for årlig klipp av kantareal, modifiserer V4 
    # med et areal som er multiplisert med faktor 0.25-2
    if 'YearlyGrassCuttingAreaPreset' in regl: 
        v4areal = kantklippspesial( v4areal, regl, dakat[str( regl['objtype'] )])

    if colAreal: 
        # Finner først dem som har  - og ikke har - Areal-egenskap
        harAreal  = v4areal[ ~v4areal[colAreal].isnull() ].drop_duplicates(subset=col_id)
        v4areal   = v4areal[ ~v4areal[colAreal].isnull() ]
        arealsum_harAreal = harAreal[colAreal].sum()

    # Finne dem tversnitt (bredde eller høyde)
    if colTverrsnitt: 
        tverr    = v4areal[ ~v4areal[colTverrsnitt].isnull() ].drop_duplicates(subset=col_id)

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

    areal = arealsum_harAreal + arealsum_TxL

    # Variabler for lengde 
    # 'withLengthFromRoadnet', 
    # 'withLengthPreferingFromAttribute', 
    if colLengde: 
        harLengde = v4[ ~v4[colLengde].isnull() ].drop_duplicates( subset=col_id )
        lengde = harLengde[colLengde].sum() + v4[ v4[colLengde].isnull() ][colVeglengde].sum()

    elif 'withLengthFromRoadnet' in regl: 
        lengde = v4[colVeglengde].sum()

    kjent = ''
    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]


    tell = {    'type'          : 'telling',
                'datakilde'     : datakilde,  
                'telletype'     : telletype, 
                'Beskrivelse'   : regl['Beskrivelse'], 
                'objtype'       : regl['objtype'], 
                'antall' : antall, 'lengde' : lengde, 'areal' : areal, 
                'Kjent problem' : kjent,
                'regl' : regl  }

    loggTelling( tell )
    return tell 

def hentdata( mappenavn, lespickle=False, hentFunkraV3=False  ): 

    filnavn = None 

    # Filer: funkraV3picle.pickle*  v2picle.pickle*  v3picle.pickle*  v4picle.pickle*
    if lespickle: 
        with open( 'v2picle.pickle', 'rb' ) as f:
            v2 = pickle.load( f )
        with open( 'v3picle.pickle', 'rb' ) as f:
            v3alt = pickle.load( f )
        with open( 'v4picle.pickle', 'rb' ) as f: 
            v4alt = pickle.load(f ) 
        # FUNKE ITJ for funkra-rapporten. Feil tegnsett? 
        #     with open( 'funkraV3picle.pickle', 'rb' ) as f:  
        #         funkraV3.pickle.load( f )    

    else: 
        filnavn = finnrapportfilnavn( mappenavn )
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
         

    return (v2, v3alt, v4alt, funkraV3)

def feilObjektDefinisjon(regl): 
    data = []
    kjent = ''

    kjenteFeil = kjenteproblem()
    if regl['Beskrivelse'] in kjenteFeil and kjenteFeil[regl['Beskrivelse']] != '': 
        kjent = kjenteFeil[regl['Beskrivelse']]


    spesial = { 241 : 'Ingen data for 241', 
                810 : 'Summering vinterdriftsklasse feiler'}

    if regl['objtype'] in [241, 810 ]: 
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



def mengdesjekk( mappenavn, objekttyper, lespickle=False, hentFunkraV3=False): 
    """
    Ny metode som sammenligner V3-oppføringer vegnummer for vegnummre
    """

    # Leser regler for de ulike radene
    (regelListe, dakat) = lesregler()
    
    # Leser de ulike regnearkene 
    (v2, v3alt, v4alt, funkraV3 ) = hentdata( mappenavn, lespickle=lespickle, hentFunkraV3=hentFunkraV3 )

   # Forbereder for lesning av V4-data (ett ark per objekttype)
    v4indeks = list( v4alt['Objektoversikt'].iloc[:,0] )
    v4indeks =  {  int( n.split('-')[0] )  : n  for n in v4indeks }

    datarader = []
    differanser = []
         
    if isinstance( objekttyper, int):
        objekttyper = [ objekttyper ]
    for objekttype in objekttyper: 
        v4dRaadata = v4alt[v4indeks[objekttype]]
        # v4data = lesv4( filnavn['v4rapp'], sheet_name=v4indeks[objekttype])

        regler = [ x for x in regelListe if x['objtype'] == objekttype ]
        if len( regler ) == 0: 
            print( 'Fant ingen regler for objekttype', objekttype)

        for regl in regler: 
            v4data = v4dRaadata.copy( )
            # v4Backup = v4dRaadata.copy()

            v4data = egenskapfilter( v4data, regl, dakat[str(objekttype)] )

            # Etterprøver V2-regnearket
            (tellinger, differ) = tellV4somV2(    v2, v4data, funkraV3, regl, dakat) 
            datarader.extend( tellinger )
            differanser.extend( differ )

            # Etterprøver V3-regnearket 
            (tellinger, differ) = tellV4somV3( v3alt, v4data, funkraV3, regl, dakat) 
            datarader.extend( tellinger )
            differanser.extend( differ )

            # spesialbehanding av et par objekt som ikke plukkes opp fordi feilen gjør at de ikke finnes i listene 
            datarader.extend(    feilObjektDefinisjon(regl) )
            differanser.extend(  feilObjektDefinisjon(regl) )
            
    return (datarader, differanser)
    
if __name__ == "__main__":


    # mappenavn = './nedlasting_ATM_2021-01-279305_Sunnfjord_2021-2026/'
    # filnavn = finnrapportfilnavn( mappenavn ) 
    # v4oversikt = pd.read_excel( filnavn['v4rapp'] )  
    # v4indeks = list( v4oversikt['Unnamed: 0'])[5:] 
    # objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  
    # (tellinger, differanser) = mengdesjekk( mappenavn, objektliste, lespickle=False, hentFunkraV3=False )  



    mappenavn = './testmagnus2/'
    mappenavn = './test_nedlasting28des2020_9305_Sunnfjord/'
    # with open( 'v4picle.pickle', 'rb' ) as f: 
    #     v4alt = pickle.load(f ) 
    # v4indeks = list( v4alt['Objektoversikt']['79 tabeller:'] )
    # objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  

    filnavn = finnrapportfilnavn( mappenavn ) 
    v4oversikt = pd.read_excel( filnavn['v4rapp'] )  
    v4indeks = list( v4oversikt['Unnamed: 0'])[5:] 
    objektliste = [ int( x.split('-')[0].strip()  ) for x in v4indeks]  

    # (tellinger, differanser) = mengdesjekk( mappenavn, 80, lespickle=False, hentFunkraV3=False )  
    (tellinger, differanser) = mengdesjekk( mappenavn, objektliste, lespickle=False, hentFunkraV3=True )  

    diff = pd.DataFrame( differanser )
    svar = lagHtmlOppsummering( diff )

    with open( 'testhtml.html', 'w') as f:
        f.write( svar )