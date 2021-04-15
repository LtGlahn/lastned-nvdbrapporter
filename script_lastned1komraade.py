"""
Script som laster ned fire rapporttyper fra NVDB rapporter API til angitt mappe

Rapporttyper som lastes ned: 
    V1_Vegnettsrapport
    V2_AggregertMengdePerVegkategori
    V3_AggregertMengdePerVegnr
    V4_Detaljert_mengde
    Tilstandsrapport

Dokumentasjon rapporter API 
https://nvdbrapportapi.atlas.vegvesen.no/swagger-ui/#/ 
"""

import json


import lastned 

if __name__ == "__main__":

    kontrakter = [ '9305 Sunnfjord 2021-2026' ]

    lastned.lastnedFlere( driftskontrakter=kontrakter, miljo='PROD', mappenavn='rapportNedlasting')
    
