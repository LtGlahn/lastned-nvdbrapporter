"""
Sjekk for den bug'en knyttet til uthenting av segmentert vegnett på veglenkesekvens 
som har cutoff på 1000 rader. Dvs at med spørringen historisk=true så får vi for få 
vegsegmenter, og da mister vi noen av de 222 leskurene som vi har på 9204 Agder 2026-2029
"""


import lastned 

if __name__ == '__main__': 
    apiurl = 'https://nvdbrapportapi.utv.atlas.vegvesen.no'
    kontrId = lastned.finnKontraktsID( '9204 Agder 2026-2029')
    parametre = { 'kontraktsomradeId' : kontrId  }

    # def lastned( apiurl, endepunkt, parametre, filnavn, formater=['XLSX', 'GPKG', 'DOCX'] ): 
    lastned.lastned( apiurl, '/rapporter/driftskontrakt/' , parametre, 'v4_9204_dagens'  )
    
    parametre['tidspunkt'] = '2024-02-14'
    lastned.lastned( apiurl, '/rapporter/driftskontrakt/' , parametre, 'v4_9204_2024_02_14'  )
