"""
Debug: Teller toalettanlegg for driftskontakt på ulike tidspunkt
"""
import pandas as pd
import geopandas as gpd
import STARTHER
import nvdbapiv3 

if __name__ == '__main__': 
    kontrakt = '9303 Hardanger og Sogn 2022-2027'
    tider = [ '2023-10-27', '2023-09-30', '2023-06-30', '2023-03-31', '2023-01-31', 
              '2022-12-31', '2022-09-30', '2022-06-30', '2022-03-31', '2022-01-31' ]

    tider = [ '2023-10-27', '2023-09-30' ]


    objType = 243

    for tidspunkt in tider: 
        mittFilter = { 'tidspunkt' : tidspunkt, 'kontraktsomrade' : kontrakt }
        data = pd.DataFrame( nvdbapiv3.nvdbFagdata( objType, filter=mittFilter).to_records())

        if len( data ) > 0: 
            group = data.groupby( 'objekttype').agg( { 'Antall klosett' : 'sum', 'nvdbId' : 'count' } ).reset_index()
            tmp = group.iloc[0]
            print( f"På dato {tidspunkt} har vi {tmp['nvdbId']} objekt med til sammen {tmp['Antall klosett'] } klosett på kontrakt {kontrakt}" )
            for junk, row in data.iterrows():
                print( f"{row['nvdbId']} Antall klosett: {row['Antall klosett']}")

        else: 
            print( f"INGEN toalettanlegg på tidspunkt {tidspunkt} på kontakt {kontrakt} ???")
