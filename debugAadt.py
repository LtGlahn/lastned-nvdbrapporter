from datetime import datetime

from copy import deepcopy 
import json 

import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER 
import driftqa
import lastned
import nvdbapiv3



def fiksfeltoversikt( feltoversikt ):

    if isinstance( feltoversikt, float ):
        feltoversikt =  ''
    else: 
        feltoversikt = '#'.join( feltoversikt )

    return feltoversikt 




# Laster ned vegnett for Sunnfjord 

# mittfilter = {  'kontraktsomrade' :  '9305 Sunnfjord 2021-2026' }


# sok = nvdbapiv3.nvdbVegnett()
# sok.filter( mittfilter )
# mindf = pd.DataFrame( sok.to_records( ))
# mindf['feltoversikt'] = mindf['feltoversikt'].apply( lambda x : fiksfeltoversikt( x ))
# mindf['geometry'] = mindf['geometri'].apply( wkt.loads )
# mindf.drop( columns=[ 'geometri', 'href', 'kortform', 'veglenkenummer', 'segmentnummer', 'startnode', 'sluttnode', 'referanse', 'målemetode', 'måledato' ], inplace=True  )
# minGdf = gpd.GeoDataFrame( mindf, geometry='geometry', crs=5973 ) 

# minGdf.to_file( 'debugDrift.gpkg', layer='vegnett9305', driver='GPKG')


# sok = nvdbapiv3.nvdbFagdata(810 )
# sok.filter( mittfilter )
# mindf = pd.DataFrame( sok.to_records( ))
# mindf['geometry'] = mindf['geometri'].apply( wkt.loads )
# vinterGdf = gpd.GeoDataFrame( mindf, geometry='geometry', crs=5973 ) 
# vinterGdf.to_file( 'debugDrift.gpkg', layer='vinterdrift9305', driver='GPKG')

mappe = '../drift_tester/nedlasting_ATM_2021-02-10__9305_Sunnfjord_2021-2026/' 

# objektliste = [301, 540, 810]
objektliste = [810]

(tellinger, differanser) = driftqa.mengdesjekk( mappe, objektliste, nvdbFilter= { 'kontraktsomrade' :  '9305 Sunnfjord 2021-2026' }, brukNvdbData=False )  
diff = pd.DataFrame( differanser )
svar  = driftqa.lagHtmlOppsummering( diff, omraade='9305 Sunnfjord 2021-2026' )
    # with open( '../drift_tester/testsammendrag' + miljo + '_flererapporter.html', 'w') as f: 
    #     f.write( svar )
