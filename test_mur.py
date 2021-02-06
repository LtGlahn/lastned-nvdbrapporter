"""
Håndarbeid-opptelling av 62 Støttekonstruksjon (Mur i driftskontrakt-rapportene) for 
kontraktsområdet 9305 Sunnfjord 2021-2026

Bruker mitt bibliotek nvdbapi-V3 https://github.com/LtGlahn/nvdbapi-V3 
Fila STARTHER.py (https://github.com/LtGlahn/workinprogress) er kun for å føye nvdbapi-V3 til python path (fordi jeg er 
for lat til å publisere nvdbapi-V3 som en ordentlig pakke på pipy) 

Output fra scriptet (per 22.1.2021)

%run test_mur.py
../../nvdbapi-V3/nvdbapiv3/nvdbapiv3.py:438: UserWarning:
You should provide the file nvdbapi-clientinfo.json

{ "X-Client" : "YOUR SYSTEM",
 "X-Kontaktperson" : "ola.nordmann@eposten.din" }

  warn( mytext )
Objekt 1000 av 1338
Areal fra 521 objekter med Areal-egenskap: 58773.0
Areal fra 192 objekter der vi bruker lengde- og høydeegenskap 19831
Areal fra 131 vegsegmenter (121 objekt) der vi bruker vegnett X høydeegenskap 14844
Areal totalt: 93447.2735

Dobbeltsjekker lengden langs veg også
Lengde ut fra egenskap: 44214
Lengde ut fra vegnett:  16388
Lengde totalt: 60602

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

import STARTHER 
import nvdbapiv3 

sok = nvdbapiv3.nvdbFagdata(62)
sok.filter( {'kontraktsomrade' : '9305 Sunnfjord 2021-2026' })
mydf = pd.DataFrame( sok.to_records() )


# [{'Beskrivelse': 'Mur',
#   'objtype': 62,
#   'withCount': True,
#   'withLengthPreferingFromAttribute': 1315                1315 => 'Lengde'   
#   'withAreaFromAttributeOrCrossSection': [3950, 1582]}]   3950 => 'Areal 
#                                                           1582 => 'Høyde, synlig, gjennomsnitt' 


# Finner først dem som har  - og ikke har - Areal-egenskap
harAreal  = mydf[ ~mydf['Areal'].isnull() ]
harAreal_utenduplikat = harAreal.drop_duplicates( ['nvdbId'])
arealsum_harAreal = harAreal_utenduplikat['Areal'].sum()
print( f'Areal fra {len(harAreal_utenduplikat)} objekter med Areal-egenskap: {arealsum_harAreal}')

ikkeAreal =  mydf[ mydf['Areal'].isnull() ]

# Finne dem som har egenskapen 'Høyde, synlig, gjennomsnitt' 
harHoyde = ikkeAreal[ ~ikkeAreal['Høyde, synlig, gjennomsnitt'].isnull() ]

# Av dem igjen, finne dem som har egenskapen 'Lengde 
harLengde     = harHoyde[ ~harHoyde['Lengde'].isnull()]
harLengde_utendup = deepcopy( harLengde.drop_duplicates( subset=['nvdbId']) )
harLengde_utendup['Areal'] = harLengde_utendup['Lengde'] * harLengde_utendup['Høyde, synlig, gjennomsnitt']
arealsum_HxL = harLengde_utendup['Areal'].sum()
print( f"Areal fra {len(harLengde_utendup)} objekter der vi bruker lengde- og høydeegenskap {round(arealsum_HxL)} " )

# Finne dem vi må bruke vegnettslengde for å finne arealet for
vegnettLengde = harHoyde[ harHoyde['Lengde'].isnull()].copy()
vegnettLengde['Areal'] = vegnettLengde['segmentlengde'] * vegnettLengde['Høyde, synlig, gjennomsnitt']
arealsum_vegnett = vegnettLengde['Areal'].sum()
print( f"Areal fra {len(vegnettLengde)} vegsegmenter ({len(vegnettLengde.drop_duplicates(subset=['nvdbId']) ) } objekt) der vi bruker vegnett X høydeegenskap {round(arealsum_vegnett)} " )
areal_totalt = arealsum_harAreal + arealsum_HxL + arealsum_vegnett 
print(f"Areal totalt: {areal_totalt}" )

# Siden vi først er i gang så regner vi ut lengden også: 
kunLengde  = mydf[ ~mydf['Lengde'].isnull()]
kunLengde_utendup = kunLengde.drop_duplicates( subset=['nvdbId'])
kunVegnett = mydf[  mydf['Lengde'].isnull()]
lengdeSumEgenskap = kunLengde_utendup['Lengde'].sum()
lengdeSumVeg = kunVegnett['segmentlengde'].sum( )
print( '\nDobbeltsjekker lengden langs veg også')
print(f"Lengde ut fra egenskap: {round(lengdeSumEgenskap) } " )
print(f"Lengde ut fra vegnett:  {round(lengdeSumVeg)} " )
print(f"Lengde totalt: {round(lengdeSumEgenskap + lengdeSumVeg  )} " )
