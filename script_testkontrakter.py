"""
Script som laster ned NVDB-rapporter for et knippe driftskontrakter og tester om innholdet stemmer av dem. 

Testen består i å sammenstille V4 til V2- og V3-rapporter og sammenligner med de leverte V2- og V3-rapportene. 
""" 

from copy import deepcopy 
import json 
from datetime import datetime

import pandas as pd

import driftqa
import lastned


miljo = 'UTV'
# miljo = 'TEST'
# miljo = 'PROD' # PROD 

nedlasting = None 
t0 = datetime.now() 

kontrakter = [ ]
# kontrakter.append( '9304 Bergen' ) TEST DENNE for å se hva som skjer når du bruker ikke-eksisterende k.navn ... 
kontrakter.append( '9305 Sunnfjord 2021-2026' )
kontrakter.append( '1105 Indre Ryfylke 2015-2021' )
kontrakter.append( '1102 Høgsfjord 2015-2020' )
kontrakter.append( '1206 Voss 2014-2019' )
kontrakter.append( '9108 Østerdalen 2021-2025' )
kontrakter.append( '0104 Ørje 2012-2020' ) 


fname = 'nedlastinger-9apr-' + miljo + '.json'
nedlasting = lastned.lastnedFlere( driftskontrakter=kontrakter, miljo=miljo)
if nedlasting: 
    with open( fname, 'w', encoding='utf-8') as f: 
        json.dump( nedlasting, f, ensure_ascii=False, indent=4 ) 

else: 
    with open( fname ) as f:
        nedlasting = json.load( f )


objektliste = [ 3, 5, 7, 9, 14, 15, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 37, 39, 40, 42, 43, 44, 45, 47, 48, 49,
            60, 62, 64, 65, 66, 67, 72, 78, 79, 80, 83, 85, 86, 95, 96, 97, 98, 99, 107, 153, 162, 166, 167, 172,
            199, 208, 234, 241, 243, 269, 274, 290, 291, 301, 318, 319, 342, 451, 482, 498, 511, 519, 540, 542,
            810, 836, 838, 845, 848, 849, 859, 875, 876]

# objektliste = [540, 810 ]
# objektliste = [ 301]

flere_komrader = []
flere_differ = []
flere_tellinger = []

# Filtrerer ut kun ett kontraktsområde av dem vi har tilgjengelig
# nedlasting = [ x for x in nedlasting if 'Sunnfjord' in x['kontraktsomrade'] ] 

# debug = True 
debug = False 

for komr in nedlasting: 
    mappenavn = komr['mappe'] + '/'
    filnavn = driftqa.finnrapportfilnavn( mappenavn )

    (tellinger, differanser) = driftqa.mengdesjekk( mappenavn, objektliste, nvdbFilter= { 'kontraktsomrade' :  komr['kontraktsomrade'] }, brukNvdbData=False, debug=debug )  
    # føyer til navn på kontraktsområdet til differansene 
    differanser = [ dict( x, **{ 'omrade' : komr['kontraktsomrade'] }) for x in differanser ] # https://stackoverflow.com/a/34757497
    tellinger   = [ dict( x, **{ 'omrade' : komr['kontraktsomrade'] }) for x in tellinger   ] # https://stackoverflow.com/a/34757497

    flere_differ.extend( differanser )
    flere_tellinger.extend( tellinger )

    diff = pd.DataFrame( differanser )
    tell = pd.DataFrame( tellinger )

    svar = driftqa.lagHtmlOppsummering( diff, omraade=komr['kontraktsomrade'] )
    htmlfilnavn = '../drift_tester/' + komr['mappe'].split('/')[-1] + '.html'
    with open(  htmlfilnavn, 'w') as f:
        f.write( svar )

if isinstance( nedlasting, list) and len( nedlasting ) > 1: 
    diff = pd.DataFrame( flere_differ )
    komraader = ', '.join( [ x['kontraktsomrade'] for x in nedlasting ] )
    svar  = driftqa.lagHtmlOppsummering( diff, omraade=komraader )
    with open( '../drift_tester/testsammendrag' + miljo + '_flererapporter.html', 'w') as f: 
        f.write( svar )


t1 = datetime.now()