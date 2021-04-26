"""
Automatisk nedlasting fra "NVDB rapporter", i første omgang data til driftskontrakter. 

https://nvdbrapportapi.atlas.vegvesen.no/swagger-ui/ 


"""
import os
import requests
import json 
from time import sleep
from datetime import datetime 
import pdb 

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
        omradeId =   [ x['id'] for x in data if kontraktNavn.lower() == x['navn'].lower() ]
        if len( omradeId ) == 0: 
            omradeId =   [ x['id'] for x in data if kontraktNavn.lower() in x['navn'].lower() ]

        # navnetreff = [ x       for x in data if kontraktNavn.lower() in x['navn'].lower() ]

        # pdb.set_trace()
        if len( omradeId ) == 1: 
            return omradeId[0]

        elif len(omradeId) == 0: 
            print( 'Null treff på kontraktnavn', kontraktNavn, 'for kontraktstype', kontraktType )
            return None 

        elif len(omradeId) > 1: 
            print( 'Snevre inn søket: Flertydig treff på kontraktnavn', kontraktNavn, 'for kontraktstype', kontraktType )
            return None 

    else: 
        print( 'Henting av k.områdeId', r.url, 'feiler HTTP', r.status_code, r.text  )
        return None 

def lastned( apiurl, endepunkt, parametre, filnavn, formater=['XLSX', 'GPKG', 'DOCX'] ): 
    """
    Generisk nedlastingshåndtering. 
    """

    mappenavn, filnavnrot = os.path.split(  filnavn )

    # Trinn 1: Ber om rapport 
    r = requests.get( apiurl+endepunkt,  params=parametre)
    print( r.url)

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
            if 'nedlastLinkByFiltype' in data['rapport'].keys(): 
                for filtype, nedlastingLink in data['rapport']['nedlastLinkByFiltype'].items():
                    # filnavn = os.path.join( mappenavn, nedlastingLink )
                    if not formater or filtype in formater: 

                        r = requests.get( apiurl + '/rapporter/nedlasting/' + \
                            nedlastingLink, params = { 'filtype' : str(filtype) } )
                        if r.ok: 
                            print( '\t\tLagrer', filnavn, filtype )
                            with open( filnavn + '.' + str(filtype).lower(), 'wb') as f: 
                                f.write( r.content )        

            else: 
                # filnavn = os.path.join( mappenavn, data['rapport']['nedlastLink'] )
                r = requests.get( apiurl + '/rapporter/nedlasting/' + \
                    data['rapport']['nedlastLink'], params= { 'filtype' : data['rapport']['filtype'] }  )

                if r.ok: 
                    with open( filnavn + '.' + data['rapport']['filtype'], 'wb') as f: 
                        f.write( r.content )

        else: 
            print( json.dumps( data, indent=4))

    if not r.ok:  
        print("Feil ved henting av rapport: http", r.status_code, '\n\t', r.text, '\n\t', r.url )




def lastnedFlere(driftskontrakter = False, veglister=False, kostra=False, mappenavn=None, miljo=None  ): 
    """
    Skjellet for det som skal bli en robust nedlasting av alle relevante rapporttyper for en (lang) liste av k.områder / andre områder. Under arbeid

    TODO: Forske fram hvordan er det effektivt å bruke slik nedlastingskode? Parameterrom? ... 
    """

    miljonavn = 'PROD_'
    apiurl = 'https://nvdbrapportapi.atlas.vegvesen.no'
    if miljo and miljo.lower() == 'utv':
        apiurl = 'https://nvdbrapportapi.utv.atlas.vegvesen.no'
        miljonavn = 'UTV_'
    elif miljo and miljo.lower() == 'test':
        apiurl = 'https://nvdbrapportapi.test.atlas.vegvesen.no'
        miljonavn = 'ATM_'

    if not mappenavn: 
        mappenavn = '../drift_tester/nedlasting_' + miljonavn + datetime.now().strftime( '%Y-%m-%d') + '_'

    # Placeholder for statistikk for resultater, mappenavn etc
    resultater = []


    # t_start = datetime.now()
    
    rapportTyper = [{ 'id' :  8000, 'navn' :  "V1_Vegnettsrapport" }, 
                    { 'id' :  9100, 'navn' :  "V2_AggregertMengdePerVegkategori" },
                    { 'id' :  9000, 'navn' :  "V3_AggregertMengdePerVegnr" }, 
                    { 'id' : 12000, 'navn' :  "V4_Detaljert_mengde" },
                    { 'id' : 13000, 'navn' :  "Tilstandsrapport" } ]


    # rapportTyper = [ { 'id' : 13000, 'navn' :  "Tilstandsrapport" } ]

    if driftskontrakter and isinstance(driftskontrakter, str):
        kontrakter = [ driftskontrakter ]
    elif driftskontrakter and isinstance( driftskontrakter, list ): 
        kontrakter = driftskontrakter
    else: 
        kontrakter = [ ]
        # kontrakter.append( '9304 Bergen' )
        kontrakter.append( '9305 Sunnfjord 2021-2026' )
        # kontrakter.append( '1105 Indre Ryfylke 2015-2021' )
        # kontrakter.append( '1102 Høgsfjord 2015-2020' )
        # kontrakter.append( '1206 Voss 2014-2019' )
        # kontrakter.append( '9108 Østerdalen 2021-2025' )
        # kontrakter.append( '0104 Ørje 2012-2020' ) 



    if driftskontrakter: 
        t0 = datetime.now()
        for kontr in kontrakter: 
            t1 = datetime.now()
            resultat  = { 'kontraktsomrade' : kontr }
            kontrId = finnKontraktsID( kontr )
            if kontrId: 
                parametre = { 'kontraktsomradeId' : kontrId, 'vegsystemreferanser' : 'Ev39' }
                mappe = mappenavn + '_' + kontr.replace( ' ', '_')
                mappe = mappe.replace( '(', '-')
                mappe = mappe.replace( ')', '-')

                resultat['mappe'] = mappe 

                for rapportType in rapportTyper: 
                    t2 = datetime.now( )
                    parametre['rapporttype'] = rapportType['id']
                    print( 'Laster ned', mappe, rapportType['navn'])
                    filnavn = os.path.join( mappe, rapportType['navn'] )
                    lastned( apiurl, '/rapporter/driftskontrakt/', parametre, filnavn )
                    print( '\tTid nedlasting', mappe, rapportType['navn'], datetime.now()-t2, '\n' ) 
                    resultat['rapporttype_' + rapportType['navn'] ]  = { 'status' : 'OK', 'filnavn' : filnavn, 'rapportTypeId' : rapportType['id'] } 

            else: 
                errmsg = f'Fant ingen driftskontrakt med navn {kontr}'
                print( errmsg )
                resultat['FEILER'] = errmsg 

            print( 'Tid nedlasting', mappenavn, datetime.now()-t1 )
            resultater.append( resultat )



        print( 'Totalt medgått tid driftskontrakter: Lastet ned', len(rapportTyper), 'for', len( kontrakter ), 'k.områder:', datetime.now()-t0)

    veglisteTyper = [ ]
    # veglisteTyper.append( { 'id' :  889, 'navn' :  "889_Modulvogntog_PROD",  'publisering' : True,   'formater' : ['DOCX', 'XLSX'] }) 
    # veglisteTyper.append({ 'id' :  889, 'navn' :  "889_Modulvogntog_ARB",   'publisering' : False,  'formater' : ['XLSX'] })
    # veglisteTyper.append({ 'id' :  890, 'navn' :  "890_Modulvogntog_Uoff_PROD",  'publisering' : True,   'formater' : ['DOCX', 'XLSX'] })
    # veglisteTyper.append({ 'id' :  890, 'navn' :  "890_Modulvogntog_Uoff_ARB",   'publisering' : False,  'formater' : ['XLSX'] })
    # veglisteTyper.append({ 'id' :  891, 'navn' :  "891_12_65mobilkran_PROD",   'publisering' : True,   'formater' : ['DOCX'] })
    # veglisteTyper.append({ 'id' :  891, 'navn' :  "891_12_65mobilkran_ARB",    'publisering' : False,  'formater' : ['XLSX'] }) 
    # veglisteTyper.append({ 'id' :  892, 'navn' :  "892_12_65mobilkran_Uoff_PROD",  'publisering' : True,   'formater' : ['DOCX'] })
    # veglisteTyper.append({ 'id' :  892, 'navn' :  "892_12_65mobilkran_Uoff_ARB",   'publisering' : False,  'formater' : ['XLSX'] }) 
    # veglisteTyper.append({ 'id' :  893, 'navn' :  "893_12_100-vegnett_PROD",   'publisering' : True,   'formater' : ['DOCX'] })
    # veglisteTyper.append({ 'id' :  893, 'navn' :  "893_12_100-vegnett_ARB",    'publisering' : False,  'formater' : ['XLSX'] }) 
    # veglisteTyper.append({ 'id' :  894, 'navn' :  "894_12_100-vegnett_Uoff_PROD",  'publisering' : True,   'formater' : ['DOCX', 'XLSX'] })
    # veglisteTyper.append({ 'id' :  894, 'navn' :  "894_12_100-vegnett_Uoff_ARB",   'publisering' : False,  'formater' : ['XLSX'] })
    # veglisteTyper.append({ 'id' :  900, 'navn' :  "900_Tømmmer_PROD",   'publisering' : True,   'formater' : ['DOCX'] })
    # veglisteTyper.append({ 'id' :  900, 'navn' :  "900_Tømmer_ARB",    'publisering' : False,  'formater' : ['XLSX'] })
    # veglisteTyper.append({ 'id' :  901, 'navn' :  "901_Tømmer_Uoff_PROD",  'publisering' : True,   'formater' : ['DOCX', 'XLSX'] })
    # veglisteTyper.append({ 'id' :  901, 'navn' :  "901_Tømmer_Uoff_ARB",   'publisering' : False,  'formater' : ['XLSX'] })
    # veglisteTyper.append({ 'id' :  902, 'navn' :  "902_Tømmmer_PROD",   'publisering' : True,   'formater' : ['DOCX'] })
    # veglisteTyper.append({ 'id' :  902, 'navn' :  "902_spesial_ARB",    'publisering' : False,  'formater' : ['XLSX'] }) 
    # veglisteTyper.append({ 'id' :  903, 'navn' :  "903_spesial_Uoff_PROD",  'publisering' : True,   'formater' : ['DOCX', 'XLSX'] })
    # veglisteTyper.append({ 'id' :  903, 'navn' :  "903_spesial_Uoff_ARB",   'publisering' : False,  'formater' : ['XLSX'] })
    # veglisteTyper.append({ 'id' :  904, 'navn' :  "904_Normal_PROD",   'publisering' : True,   'formater' : ['DOCX'] })
    # veglisteTyper.append({ 'id' :  904, 'navn' :  "904_Normal_ARB",    'publisering' : False,  'formater' : ['XLSX'] }) 
    # veglisteTyper.append({ 'id' :  905, 'navn' :  "905_Normal_Uoff_PROD",  'publisering' : True,   'formater' : ['DOCX', 'XLSX'] })
    # veglisteTyper.append({ 'id' :  905, 'navn' :  "905_Normal_Uoff_ARB",   'publisering' : False,  'formater' : ['XLSX'] })
    veglisteTyper.append({ 'id' :  910, 'navn' :  "901_Tømmer_Modulvogntog",   'publisering' : False,  'formater' : ['XLSX'] })
                     

    kommuner = [ 5001 ]
    if veglister: 
        t0 = datetime.now()
        for komm in kommuner: 

            mappe = mappenavn + '/veglister/' + str(komm )
            for rapportType in veglisteTyper: 
                t2 = datetime.now()
                parametre = { 'publisering' : rapportType['publisering'], 'kommune' : komm, 'vegsystemreferanse' : 'Rv706'  }
                print( 'laster ned', mappe, rapportType['id'], rapportType['navn'])
                lastned( apiurl, '/rapporter/veglister/' + str( rapportType['id']), parametre, 
                            os.path.join( mappe, rapportType['navn']), formater=rapportType['formater'] )


    kostraTyper = []
    # kostraTyper.append( { "id": 15001, "navn": "Vegnett - sum hele landet" } )
    # kostraTyper.append( { "id": 15002, "navn": "Fylkesveg med motorveger og motortrafikkveger" } )
    # kostraTyper.append( { "id": 15003,  "navn": "Fylkesveg uten fast dekke" } )
    # kostraTyper.append( { "id": 15004, "navn": "Fylkesveg med 4 felt" } )
    # kostraTyper.append( { "id": 15005,  "navn": "Fylkesveg aksellast mindre enn 10 tonn" } )
    # kostraTyper.append( { "id": 15006, "navn": "Fylkesveg med begrensning på totalvekt mindre enn 50 tonn" } )
    # kostraTyper.append( { "id": 15007, "navn": "Fylkesveg med fartsgrense 50 eller lavere" } )
    # kostraTyper.append( { "id": 15008, "navn": "Fylkesveg med begrensning på kjøretøylengde mindre enn 19,5 meter" } )
    # kostraTyper.append( { "id": 15009, "navn": "Fylkesveg undergang med høyde mindre enn 4 meter" } )
    # kostraTyper.append( { "id": 15011, "navn": "Fylkesveg uten fast dekke over 5000 ÅDT"   } )
    # kostraTyper.append( { "id": 15012, "navn": "Fylkesveg i alt mer enn 5000 ÅDT"  } )
    # kostraTyper.append( { "id": 15013, "navn": "Fylkesveg med lengde tunnel"  } )
    # kostraTyper.append( { "id": 15014, "navn": "Fylkesveg med antall tunnel"  } )
    # kostraTyper.append( { "id": 15015, "navn": "Fylkesveg med tunneler over 500 meter" } )
    # kostraTyper.append( { "id": 15016, "navn": "Fylkesveg_tunneler med høyde lavere enn 4 meter" } )
    # kostraTyper.append( { "id": 15017, "navn": "Fylkesveg_antall bruer" } )
    # kostraTyper.append( { "id": 15018, "navn": "Fylkesveg_bruer under 10 tonn" } )
    # kostraTyper.append( { "id": 15019, "navn": "Fylkesveg_bruer_høyde mindre enn 4 meter"  } )
    # kostraTyper.append( { "id": 15020, "navn": "Fylkesveg_midtrekkverk 2-3 felter"  } )
    # kostraTyper.append( { "id": 15021, "navn": "Gang-og sykkelveger"  } )
    # kostraTyper.append( { "id": 15023, "navn": "Fylkesveg_forsterket vegoppmerking midt" } )
    # kostraTyper.append( { "id": 15024, "navn": "Fylkesveg med støyskjerm og voll" } )
    # kostraTyper.append( { "id": 15025, "navn": "Fylkesveg med kollektivfelt" } )


    fylker = [ [18, 34, 50, 3, 54, 38, 42, 11, 30, 46, 15]]
    # fylker = [ 11, 50, 18 ]
    if kostra: 
        t0 = datetime.now()

        mappe = mappenavn + '/Kostra/'
        for rapportType in kostraTyper: 
            t2 = datetime.now()
            parametre = { 'fylke' : fylker, 'dato' : '2020-12-31'  } 
            print( 'laster ned', mappe, rapportType['id'], rapportType['navn'])
            lastned( apiurl, '/rapporter/kostra/' + str( rapportType['id']), parametre, mappe + rapportType['navn']  )

    if len( resultater) > 0: 
        return resultater
    else: 
        print( 'Nedlasting: Ingen resultater???')


def lastnedveglister():
    """
    Laster ned alle mulige vegliste-varianter for angitt område
    """

    # t0 = datetime.now()
    
    # rapportTyper = [{ 'bkId' :  904, 'navn' :  "Normaltransport, offisiell, arbeid", "publisering" : "false"},  
    #                 { 'bkId' :  905, 'navn' :  "Normaltransport, UOFF, arbeid", "publisering" : "false"}  ]




# def lastnedEnkeltRapport( mappenavn, rapportType, parametre ):
#     """
#     Laster ned angitt rapportType (p.tk. kun driftskontrakt) til angitt mappe. Implementerer polling

#     ARGUMENTS: 
#         mappenavn - navn på katalog der vi skal lagre fila 

#         rapportType - heltall, ID til rapporttype. Per oktober 2020 er disse typene støttet: 
#                         "id":  8000 "V1"     "Vegnettsrapport"   
#                         "id":  9100 "V2"     "Aggregert mengdeoversikt (sum pr. vegkategori)"
#                         "id":  9000 "V3"     "Aggregert mengdeoversikt (sum pr. veg)"
#                         "id": 12000 "V4" "Detaljert mengdeoversikt" (dvs alle obj.typer som er definert for V2, V3 og V4)
#                         "id": 10000 "V4"  "Detaljert mengdeoversikt, enkeltobjekt"
#                         "id": 13000 "Tilstandsrapport" "Tilstandsrapport"

#         parametre - dictionary med område-,  vegfiltre og evt gyldighetsdato, samt andre parametre som måtte være støttet. 
#                Se dokumentasjon for hva som er støttet i ​/rapporter​/driftskontrakt - endepunktet. 
#                https://nvdbrapportapi.atlas.vegvesen.no/swagger-ui/#/Driftskontrakter/get_rapporter_driftskontrakt 
#                Minimum er en av fylke, komune eller kontraktsomradeId. 
#     """
#     apiurl = 'https://nvdbrapportapi.atlas.vegvesen.no'
#     apiurl = 'https://nvdbrapportapi.utv.atlas.vegvesen.no'

    # Trinn 1: Ber om rapport

    # parametre.update( { 'rapporttype' : rapportType  }) # Tilrettelagt for å kunne iterere over flere rapporttyper. 
    # r = requests.get( apiurl + '/rapporter/driftskontrakt', params=parametre )
    # print( r.url )

    # Trinn 2 - polling
    # if r.ok: 
    #     data = r.json()
 
    #     while data['status'] == 'PENDING' and r.ok: 
    #         sleep( 15 )
    #         r = requests.get( apiurl + '/rapporter/poll/' + data['id'] )
    #         data = r.json( )
            
    #         prefix = '\t'
    #         if data['status'] == 'PENDING': 
    #             prefix = '\t\t'

    #         print( prefix, data['status'], data['id'], data['durationMsString'] )
            
    #     if r.ok and data['status'] == 'SUCCESS': 
    #         os.makedirs( mappenavn, exist_ok=True) 
    #         filnavn = os.path.join( mappenavn, data['rapport']['nedlastLink'] )
    #         r = requests.get( apiurl + '/rapporter/nedlasting/' + data['rapport']['nedlastLink'], params= { 'filtype' : data['rapport']['filtype'] }  )

    #         if r.ok: 
    #             with open( filnavn, 'wb') as f: 
    #                 f.write( r.content )

    #     else: 
    #         print( json.dumps( data, indent=4))

    # if not r.ok:  
    #     print("Feil ved henting av rapport: http", r.status_code, '\n\t', r.text, '\n\t', r.url )


