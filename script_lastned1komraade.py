"""
Script som laster ned fire rapporttyper fra NVDB rapporter API til angitt mappe

Rapporttyper som lastes ned: 
    V1_Vegnettsrapport.xlsx
    V2_AggregertMengdePerVegkategori.xlsx
    V3_AggregertMengdePerVegnr.xlsx
    V4_Detaljert_mengde.xlsx
    Tilstandsrapport.xlsx

Disse lagres i mappen <mappenavn>_<Navn kontraktsområde>

Dokumentasjon rapporter API 
https://nvdbrapportapi.atlas.vegvesen.no/swagger-ui/#/ 
"""

import json


import lastned 

if __name__ == "__main__":

    kontrakter = [ '9305 Sunnfjord 2021-2026' ]

    # Med mappenavn = 'rapportNedlasting' havner i mappen rapportNedlasting_9305_Sunnfjord_2021-2026/
    lastned.lastnedFlere( driftskontrakter=kontrakter, miljo='PROD', mappenavn='rapportNedlasting')
    
