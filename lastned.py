"""
Automatisk nedlasting fra "NVDB rapporter", i første omgang data til driftskontrakter. 

https://nvdbrapportapi.atlas.vegvesen.no/swagger-ui/ 


"""
import os
import requests
import json 
from time import sleep
from datetime import datetime 

def finnKontraktsID( kontraktNavn,  kontraktType = 11750  ):
    """
    Finner ID til den kontrakten som matcher angitt navn, av angitt kontraktType, ved 
    oppslag på https://nvdbrapportapi.atlas.vegvesen.no/rapporter/kontraktsomraader 

    ARGUMENTS
        kontraktNavn: Tekststreng, (deler av) navnet på driftskontrakten

    KEYWORDS
        kontraktType: heltall, ID til kontraktnstype. Per oktober 2020 er lovlige verdier 
            11750 Driftskontrakt (default)
            11753 Elektrokontrakt
            11756 Utprøving
            11755 Tunnelkontrakt
            11751 OPS-kontrakt
            18158 Grøntkontrakt
            11754 Veglyskontrakt
            18159 Andrepartskontrakt
            11752 Refusjonsavtale

            Liste med til enhver tid gjeldende lovlige verdier kan hentes fra 
            https://nvdbrapportapi.atlas.vegvesen.no/rapporter/kontraktsomraadetyper 

    RETURNS 
        ID til kontraktsområdet der angitt navn har eksakt 1 match (helt eller delvis) i navnet på k.området
        Returnerer None hvis det er null treff eller flere treff. 

    """

    r = requests.get('https://nvdbrapportapi.atlas.vegvesen.no/rapporter/kontraktsomraader', params={ 'type' : kontraktType } )
    if r.ok: 
        data = r.json()
        omradeId = [ x['id'] for x in data if kontraktNavn.lower() in x['navn'].lower() ]
        if len( omradeId ) == 1: 
            return omradeId[0]

        elif len(omradeId) == 0: 
            print( 'Null treff på kontraktnavn', kontraktNavn, 'for kontraktstype', kontraktType )
            return None 

        elif len(omradeId) > 1: 
            print( 'Snevre inn søket: Flertydig treff på kontraktnavn', kontraktNavn, 'for kontraktstype', kontraktType )
            print( json.dumps( data, indent=4 ))
            return None 

    else: 
        print( 'Henting av k.områdeId', r.url, 'feiler HTTP', r.status_code, r.text  )
        return None 


def lastnedEnkeltRapport( mappenavn, rapportType, parametre ):
    """
    Laster ned angitt rapportType (p.tk. kun driftskontrakt) til angitt mappe. Implementerer polling

    ARGUMENTS: 
        mappenavn - navn på katalog der vi skal lagre fila 

        rapportType - heltall, ID til rapporttype. Per oktober 2020 er disse typene støttet: 
                        "id":  8000 "V1"     "Vegnettsrapport"   
                        "id":  9100 "V2"     "Aggregert mengdeoversikt (sum pr. vegkategori)"
                        "id":  9000 "V3"     "Aggregert mengdeoversikt (sum pr. veg)"
                        "id": 12000 "V4" "Detaljert mengdeoversikt" (dvs alle obj.typer som er definert for V2, V3 og V4)
                        "id": 10000 "V4"  "Detaljert mengdeoversikt, enkeltobjekt"
                        "id": 13000 "Tilstandsrapport" "Tilstandsrapport"

        parametre - dictionary med område-,  vegfiltre og evt gyldighetsdato, samt andre parametre som måtte være støttet. 
               Se dokumentasjon for hva som er støttet i ​/rapporter​/driftskontrakt - endepunktet. 
               https://nvdbrapportapi.atlas.vegvesen.no/swagger-ui/#/Driftskontrakter/get_rapporter_driftskontrakt 
               Minimum er en av fylke, komune eller kontraktsomradeId. 
    """
    apiurl = 'https://nvdbrapportapi.atlas.vegvesen.no'

    # Trinn 1: Ber om rapport

    parametre.update( { 'rapporttype' : rapportType  }) # Tilrettelagt for å kunne iterere over flere rapporttyper. 
    r = requests.get( apiurl + '/rapporter/driftskontrakt', params=parametre )

    # Trinn 2 - polling
    if r.ok: 
        data = r.json()
 
        while data['status'] == 'PENDING' and r.ok: 
            sleep( 15 )
            r = requests.get( apiurl + '/rapporter/poll/' + data['id'] )
            data = r.json( )
            
            prefix = '\t'
            if data['status'] == 'PENDING': 
                prefix = '\t\t'

            print( prefix, data['status'], data['id'], data['durationMsString'] )
            
        if r.ok and data['status'] == 'SUCCESS': 
            os.makedirs( mappenavn, exist_ok=True) 
            filnavn = os.path.join( mappenavn, data['rapport']['nedlastLink'] )
            r = requests.get( apiurl + '/rapporter/nedlasting/' + data['rapport']['nedlastLink'], params= { 'filtype' : data['rapport']['filtype'] }  )

            if r.ok: 
                with open( filnavn, 'wb') as f: 
                    f.write( r.content )

        else: 
            print( json.dumps( data ), indent=4)

    if not r.ok:  
        print("Feil ved henting av rapport: http", r.status_code, '\n\t', r.text, '\n\t', r.url )

def lastnedFlere(): 
    """
    Skjellet for det som skal bli en robust nedlasting av alle relevante rapporttyper for en (lang) liste av k.områder / andre områder. Under arbeid

    TODO: Forske fram hvordan er det effektivt å bruke slik nedlastingskode? Parameterrom? ... 
    """


    t0 = datetime.now()
    
    rapportTyper = [{ 'id' :  8000, 'navn' :  "V1 - Vegnettsrapport" }, 
                    { 'id' :  9100, 'navn' :  "V2 - Aggregert mengdeoversikt (sum pr. vegkategori)" },
                    { 'id' :  9000, 'navn' :  "V3 - Aggregert mengdeoversikt (sum pr. veg)" }, 
                    { 'id' : 12000, 'navn' :  "V4 - Detaljert mengdeoversikt" },
                    { 'id' : 13000, 'navn' :  "Tilstandsrapport" } ]


    kontrakter = [ '9304 Bergen', '9305 Sunnfjord']
    kontrakter.append( '0104 Ørje 2012-2020' ) 
    for kontr in kontrakter: 
        t1 = datetime.now()
        kontrId = finnKontraktsID( kontr )
        if kontrId: 
            parametre = { 'kontraktsomradeId' : kontrId, 'vegsystemreferanse' : 'Rv13'  }
            mappe = 'test2_nedlasting/' + kontr.replace( ' ', '_')

            for rapportType in rapportTyper: 
                t2 = datetime.now( )
                print( 'Laster ned', mappe, rapportType['navn'])

                lastnedEnkeltRapport( mappe, rapportType['id'], parametre)
                print( '\tTid nedlasting', mappe, rapportType['navn'], datetime.now()-t2 ) 

        print( 'Tid nedlasting', mappe, datetime.now()-t1 )


    print( 'Totalt medgått tid', len( kontrakter ), 'områder:', datetime.now()-t0)