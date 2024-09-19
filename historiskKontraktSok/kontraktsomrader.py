"""
Finner dagens eller historiske kontraktsområder, og de fagdataene som hører til
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt 
import json
from copy import deepcopy 

import STARTHER
import nvdbapiv3 

def kontrakt2veglenkeposisjoner( kontraktObj:dict):
    """
    Henter ut veglenkeposisjoner fra et kontraktområde-objekt (rått fra NVDB api LES)
    """

    tmp = [ x for x in kontraktObj['egenskaper'] if x['navn'] == 'Liste av lokasjonsattributt']
    assert len( tmp ) == 1, f"Fant ikke stedfestingdata på kontrakt?"
    stedfest = tmp[0]
    minListe = []
    for veg in stedfest['innhold']: 
        minListe.append(  f"{veg['startposisjon']}-{veg['sluttposisjon']}@{veg['veglenkesekvensid']}"  )

    with open( 'veglenkeposisjonerDK9401_per20211230.json', 'w' ) as f:
        json.dump( minListe, f, indent=4)

    return minListe 

def hentFagdata( objektTypeId:int, veglenkeposisjoner:list, sokefilter={} ):
    """
    Finner data på en liste med veglenkeposisjoner. Returnerer dataframe med én rad per objekt og geometri type "best"
    """

    # Deler listen med veglenkeposisjoner opp i mindre biter
    data = []
    inkrement = 10
    count = 0

    # Logger liste med søkefilter til debugging
    sokefilterliste = []

    tidspunkt = None
    if 'tidspunkt' in sokefilter:
        tidspunkt = sokefilter['tidspunkt']

    # Deler opp listen med veglenkeposisjoner i kortere og mer håndterbare biter 
    # 
    nvdbId = []
    nvdbData = []
    while count < len( veglenkeposisjoner ): 
        sokefilter['veglenkesekvens'] = ','.join( veglenkeposisjoner[count : count + inkrement ] )
        sokefilterliste.append( deepcopy( sokefilter ))
        count += inkrement
        # mittsok = nvdbapiv3.nvdbFagdata( objektTypeId, filter=sokefilter )
        # for etObj in mittsok:
        #     nvdbId.append( etObj['id'] )
        #     nvdbData.append( etObj )
        data.extend( nvdbapiv3.nvdbFagdata( objektTypeId, filter=sokefilter).to_records( vegsegmenter=False, tidspunkt=tidspunkt ))


    # with open( 'nvdbdata.json', 'w') as f: 
    #     json.dump( nvdbData, f, indent=4 )

    # with open( 'nvdbId.json', 'w') as f: 
    #     json.dump( nvdbId, f, indent=4 )


    if len( data ) > 0:
        myDf = pd.DataFrame( data )
        # Får en del duplikater fordi noen objekter strekker seg på tvers av vår vilkårlige oppdeling av veglenkesekvens-posisjoner
        myDf = myDf[ ~myDf.duplicated( subset='nvdbId' )].copy()
        myDf.reset_index( inplace=True )
        return myDf 
    else: 
        print( f"Ingen treff på objekttype {objektTypeId} for disse veglenkesekvensene på tidspunkt {tidspunkt} ")
        
    return None 

def finnKontraktNavn( sokefrase:str, tidspunkt=None  ):
    """
    Søker NVDB api LES etter kontraktsområder med navn som matcher søkefrase. Returnerer liste med JSON-objekt fra LES
    """

    mittfilter = {  'egenskap' : f"5174='{sokefrase}'"}
    if tidspunkt: 
        mittfilter['tidspunkt'] = tidspunkt

    sok = nvdbapiv3.nvdbFagdata( 580, filter=mittfilter )
    data = []
    for obj in sok:
        data.append( obj )    

    if len( data ) == 0:
        print( f"Ingen treff på navn 580 Kontraktsområde for søkefrasen {sokefrase} ")
    if len( data ) > 1: 
        print( f"{len(data)} treff på navn 580 Kontraktsområde for søkefrasen {sokefrase}")
        skrivUtSaaMange = 20
        temp = data[0:skrivUtSaaMange]
        for omr in temp: 
            navn = [ x for x in omr['egenskaper'] if x['navn'] == 'Navn']
            print( f"\t{omr['id']}\t '{navn[0]['verdi']}' ")
        if len( data ) > skrivUtSaaMange: 
            print( f"... {len(data)-skrivUtSaaMange} flere objekter")

    return data 
    

if __name__ == '__main__':
    sok1 = '9401 Trondheim 2020-2025 (f.o.m. 01.09.2023)'
    tidspunkt = '2021-12-30'

    # data1 = finnKontraktNavn( sok1 )
    data2 = finnKontraktNavn( sok1, tidspunkt=tidspunkt )

    # fasit_dagens = hentFagdata( 99, kontrakt2veglenkeposisjoner( data1[0] ) )

    fasit_gammal = hentFagdata( 99, kontrakt2veglenkeposisjoner( data2[0] ), sokefilter={'tidspunkt' : tidspunkt } )

    # dagensrapp = pd.read_excel( 'dagens_vegoppmerkingtest.xlsx', sheet_name='99 - Vegoppmerking, langsgående', skiprows=6 )
    # dagensrapp = dagensrapp[ dagensrapp['Første forekomst'] == 1].copy()
    # dagensRappId = set( dagensrapp['Objekt Id'].to_list() )
    # dagensFasit = set( fasit_dagens['nvdbId'].to_list())

    # dagensrapp_per2021 = pd.read_excel( 'dagens_vegoppmerkingUTV_per20211230.xlsx', sheet_name='99 - Vegoppmerking, langsgående', skiprows=6 )
    # dagensrapp_per2021 = pd.read_excel( 'nvdb-rapport-Driftskontrakter_V4_9401_Trondheim_2020-2025_LAGET20231113UTV.xlsx', sheet_name='99 - Vegoppmerking, langsgående', skiprows=6 )
    # dagensrapp_per2021 = pd.read_excel( 'nvdb-rapport-Driftskontrakter_V4_9401_Trondheim_2020-2025_LAGET20231113_ATM.xlsx', sheet_name='99 - Vegoppmerking, langsgående', skiprows=6 )
    dagensrapp_per2021 = pd.read_excel( 'V4_testprod2311.xlsx', sheet_name='99 - Vegoppmerking, langsgående', skiprows=6 )
    # dagensrapp_per2021 = dagensrapp_per2021[ dagensrapp_per2021['Første forekomst'] == 1]

