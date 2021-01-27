# Oppsummering av avvik

2021-01-22 10:30:15




# Store avvik



### Arealberegning feiler for en av metodene som brukes

Vi har grove avvik for arealberegning med metoden `withAreaFromAttributeOrCrossSection`. Feilene ligger i området 30-50%. 

Dette gjelder disse oppføringene: 
```
3 Skjerm
47 Busslomme
47 Trafikklomme u/busslomme
```

### Avvik areal 82.46 => 47 Busslomme

```
V2=        3979
V3=        3979
V4=        2181 
```

Regler: {'Beskrivelse': 'Busslomme', 'objtype': 47, 'withFilter': 'ro -> attributeMatches(ro, 1257, 3200)', 'withCount': True, 'withLengthPreferingFromAttribute': 1307, '': [8317, 2239]}



### Avvik areal 115.35 => 47 Trafikklomme u/busslomme

```
V2=        2259
V3=        2259
V4=        1049 
```

Regler: {'Beskrivelse': 'Trafikklomme u/busslomme', 'objtype': 47, 'withFilter': 'ro -> !attributeMatches(ro, 1257, 3200)', 'withCount': True, 'withLengthPreferingFromAttribute': 1307, 'withAreaFromAttributeOrCrossSection': [8317, 2239]}



### Avvik FUNKRA for v2 areal 951.39% => 47 Trafikklomme u/busslomme

```
V2=        2259
V3=        2259
V4=        1049 

Frå Funkra=23751 
```

Regler: {'Beskrivelse': 'Trafikklomme u/busslomme', 'objtype': 47, 'withFilter': 'ro -> !attributeMatches(ro, 1257, 3200)', 'withCount': True, 'withLengthPreferingFromAttribute': 1307, 'withAreaFromAttributeOrCrossSection': [8317, 2239]}



### Avvik areal 149.33% => 3 Skjerm

```
V2=        7259
V3=        7259
V4=        2911 
```

### Avvik areal 2.89 => 7 Gjerde

```
V2=       26046
V3=       26046
V4=       26821 
```


### Avvik areal 20.59 => 15 Grøntanlegg Grasdekker

```
V2=      142926
V3=      142926
V4=      179976 
```

### Avvik FUNKRA for v4 areal 20.59% => 15 Grøntanlegg Grasdekker

```
V2=      142926
V3=      142926
V4=      179976 

Frå Funkra=142926 
```


### Avvik FUNKRA for v2 antall 1.0 stk => 37 Vegkryss

```
V2=         244
V3=         244
V4=         244 

Frå Funkra=243 
```

Regler: {'Beskrivelse': 'Vegkryss', 'objtype': 37, 'withCount': True, 'withLengthFromRoadnet': True}



### Avvik FUNKRA for v3 antall 1.0 stk => 37 Vegkryss

```
V2=         244
V3=         244
V4=         244 

Frå Funkra=243 
```

Regler: {'Beskrivelse': 'Vegkryss', 'objtype': 37, 'withCount': True, 'withLengthFromRoadnet': True}




### Avvik FUNKRA for v2 lengde 1.03% => 48 Fortau

```
V2=        6745
V3=        6745
V4=        6745 

Frå Funkra=6815 
```

Regler: {'Beskrivelse': 'Fortau', 'objtype': 48, 'withCount': True, 'withLengthPreferingFromAttribute': 11268, 'withAreaFromCrossSection': 2241, 'junk_FEILID_withAreaFromAttributeOrCrossSection': [1368, 2241]}


### Multippel stedfesting gir dobbelt opp i tabell => 60 Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)

```
V2=         292 <= Multippel stedfesting 
V3=         280
V4=         280 
Frå Funkra= 280 
```

### Avvik lengde 1.56 => 60 Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)

```
V2=       13367
V3=       13162
V4=       13162 
```

Regler: {'Beskrivelse': 'Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)', 'objtype': 60, 'withCount': True, 'withLengthPreferingFromAttribute': 1313}



### Avvik FUNKRA for v2 lengde 52.53% => 60 Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)

```
V2=       13367
V3=       13162
V4=       13162 

Frå Funkra=6346 
```

Regler: {'Beskrivelse': 'Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)', 'objtype': 60, 'withCount': True, 'withLengthPreferingFromAttribute': 1313}



### Avvik FUNKRA for v3 lengde 51.79% => 60 Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)

```
V2=       13367
V3=       13162
V4=       13162 

Frå Funkra=6346 
```

Regler: {'Beskrivelse': 'Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)', 'objtype': 60, 'withCount': True, 'withLengthPreferingFromAttribute': 1313}



### Avvik FUNKRA for v4 lengde 51.79% => 60 Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)

```
V2=       13367
V3=       13162
V4=       13162 

Frå Funkra=6346 
```

### Avvik FUNKRA for v2 antall 1.0 stk => 62 Mur

```
V2=        1339
V3=        1338
V4=        1338 

Frå Funkra=1338 
```

### Avvik areal 50.18 => 62 Mur

```
V2=      216039
V3=      216039
V4=      143850 
```

### Avvik FUNKRA for v2 areal 30.81% => 62 Mur

```
V2=      216039
V3=      216039
V4=      143850 

Frå Funkra=149472 
```

### Avvik FUNKRA for v3 areal 30.81% => 62 Mur

```
V2=      216039
V3=      216039
V4=      143850 

Frå Funkra=149472 
```

### Avvik FUNKRA for v4 areal 3.91% => 62 Mur

```
V2=      216039
V3=      216039
V4=      143850 

Frå Funkra=149472 
```

### Avvik FUNKRA for v2 antall 1.0 stk => 64 Kaier

```
V2=           4
V3=           4
V4=           4 

Frå Funkra=5 
```

### Avvik FUNKRA for v3 antall 1.0 stk => 64 Kaier

```
V2=           4
V3=           4
V4=           4 

Frå Funkra=5 
```

### Avvik FUNKRA for v4 antall 1.0 stk => 64 Kaier

```
V2=           4
V3=           4
V4=           4 

Frå Funkra=5 
```

### Avvik areal 6.91 => 72 Fjellsikringsutstyr

```
V2=       40445
V3=       40445
V4=       43445 
```

### Feil i testrutine, beregning areal => 72 Fjellsikringsutstyr

```
V2=       40445
V3=       40445
V4=       43445 <= Feil 

Frå Funkra=40445 
```

### Funkra mangler objekt  => 79 Stikkrenne

```
V2=        3437
V3=        3437
V4=        3437 
Frå Funkra=3435 <= 2 for lite 
```

### Avvik FUNKRA for v2 antall 34.0 stk => 96 Skiltplate, Alle NVDB-data unntatt tunnelmarkering

```
V2=        5146
V3=        5146
V4=        5146 

Frå Funkra=5112 
```

Regler: {'Beskrivelse': 'Skiltplate, Alle NVDB-data unntatt tunnelmarkering', 'objtype': 96, 'withFilter': 'ro -> !attributeIn(ro, 5530, 7847, 7848)', 'withCount': True}



### Avvik FUNKRA for v3 antall 34.0 stk => 96 Skiltplate, Alle NVDB-data unntatt tunnelmarkering

```
V2=        5146
V3=        5146
V4=        5146 

Frå Funkra=5112 
```

Regler: {'Beskrivelse': 'Skiltplate, Alle NVDB-data unntatt tunnelmarkering', 'objtype': 96, 'withFilter': 'ro -> !attributeIn(ro, 5530, 7847, 7848)', 'withCount': True}



### Avvik FUNKRA for v4 antall 34.0 stk => 96 Skiltplate, Alle NVDB-data unntatt tunnelmarkering

```
V2=        5146
V3=        5146
V4=        5146 

Frå Funkra=5112 
```

Regler: {'Beskrivelse': 'Skiltplate, Alle NVDB-data unntatt tunnelmarkering', 'objtype': 96, 'withFilter': 'ro -> !attributeIn(ro, 5530, 7847, 7848)', 'withCount': True}


### FUNKRA ett objekt for lite => 97 Skilt, variable

```
V2=          74
V3=          74
V4=          74 
Frå Funkra=  73 
```

# Stort avvik lengde på alle oppføringer for ÅDT og vinterdriftsklasse 

Vi har altfor lav lengdeoppsummering for ÅDT og vinterdriftsklasse. Dette er et kjent problem vi håper å få løst snart. 

# Manglende data i dette kontraktsområdet

```
--- Null data for 21 Permanente Brøytestikk i V2-rapporten for dette kontraktsområdet 
--- Null data for 26 Lekeapparat i V2-rapporten for dette kontraktsområdet 
--- Null data for 40 Snuplass i V2-rapporten for dette kontraktsområdet 
--- Null data for 98 Kilometerstolpe i V2-rapporten for dette kontraktsområdet 
--- Null data for 166 Teledybdemåler i V2-rapporten for dette kontraktsområdet 
--- Null data for 241 Dekke, Betong i V2-rapporten for dette kontraktsområdet 
--- Null data for 241 Dekke, Grus i V2-rapporten for dette kontraktsområdet 
--- Null data for 241 Dekke, Stein i V2-rapporten for dette kontraktsområdet 
--- Null data for 290 Telehiv i V2-rapporten for dette kontraktsområdet 
--- Null data for 319 Kolonnestrekning i V2-rapporten for dette kontraktsområdet 
--- Null data for 451 Sykkelparkering i V2-rapporten for dette kontraktsområdet 
--- Null data for 498 Viltskremmere/varslere i V2-rapporten for dette kontraktsområdet 
--- Null data for 540 ÅDT (8), > 20000 i V2-rapporten for dette kontraktsområdet 
--- Null data for 810 Vinterdriftsklasse A i V2-rapporten for dette kontraktsområdet 
--- Null data for 810 Vinterdriftsklasse E i V2-rapporten for dette kontraktsområdet 
--- Null data for 810 Vinterdriftsklasse GsA i V2-rapporten for dette kontraktsområdet 
--- Null data for 848 Snøskjerm i V2-rapporten for dette kontraktsområdet 
--- Null data for 849 Skredvarslingsanlegg med varsling på veg i V2-rapporten for dette kontraktsområdet 
--- Null data for 876 Overvannsgrøft i V2-rapporten for dette kontraktsområdet 
```

# Feil i testrutine

### Feil i testrutine beregning av areal => 511 Grøntanlegg Busker

```
V2=        7263
V3=        7263
V4=        8559 
Frå Funkra=7263 
```

### Feil i testrutine, oppsummering av V4 tar ikke hensyn til "antall-egenskap: 

Her fant vi en feil i testrutinen - beregning av antall toalettskåler ut fra de 10 objektene med "243 Toalettanlegg" feiler. Det korrekte er 25stk. Dermed blir det store avvik mellom min V4-oppsummering og ny v2,V3. 

Det varierer hvorvidt Funkra teller antall objekter (slik som min V4-telling), eller om den bruker "antall"-egenskap (slik som ny V2,V3). 

Dette gjelder disse objekttypene:
```
243 Toalettskåler
--------------
V2=        25
V3=        25
V4=        10 <= 25 er korrekt 
Frå Funkra=25 


511 Grøntanlegg  
--------------
Ny V2=   1178 <= Ny og riktig, teller antall-egenskapen 
Ny V3=   1178 <= Ny og riktig
Ny V4=     50 <= FEIL i testrutinen, teller kun hvor mange objekt som finnes 
Frå Funkra=50 <= Utdatert definisjon, teller antall objekt.  


20 Kantstolper
--------------
V2=       719
V3=       719
V4=        55 
Frå Funkra=55 

27 Avfallsbeholdere
--------------
V2=        88
V3=        88
V4=        67 
Frå Funkra=88 

28 Utemøbler
--------------
V2=        93
V3=        93
V4=        80 
Frå Funkra=93 

199 Grøntanlegg Trær
---------------
V2=        881
V3=        881
V4=        287 
Frå Funkra=881 

```

# Mindre alvorlige avvik: 

### Avvik areal 3.89 => 845 Fanggjerde

```
V2=        6654
V3=        6654
V4=        6924 
```

### Avvik FUNKRA 1.03% => 318 Snø- og isrydding

```
V2=        40676
V3=        40676
V4=        40676 
Frå Funkra=40258 
```

### Avvik FUNKRA for ny v2,v3  => 5 Rekkverk

Gjelder antall og lengde

```
V2=           1796stk <= 4 objekt for mye pga stedfesting flere trafikantgrupper
V3=           1792stk
V4=           1792stk
Frå Funkra=   1792stk

V2=         236959m^2<= Avvik pga stedfesting flere trafikantgrupper
V3=         236527m^2
V4=      	236527m^2 
Frå Funkra= 228810m^2<= 3% avvik Funkra <=> NVDB rapporter 
```

### Avvik FUNKRA for v2,v3 lengde 3.26% => 5 Rekkverk

```
V2=        236959 <= Multippel stedfesting, inngår i både "G/S" og "E+R"
V3=        236527
V4=        236527 
Frå Funkra=228810 
```

### Funkra mangler ett objekt => 7 Gjerde

```
V2=        288
V3=        288
V4=        288 
Frå Funkra=287 <= Her har Funkra 1 for lite 
```

### Funkra har et vegkryss for lite => 37 Vegkryss

```
V2=         244
V3=         244
V4=         244 
Frå Funkra= 243 <= Funkra har 1 for lite 
```

### Avvik FUNKRA for v3 lengde 1.03% => 318 Snø- og isrydding

```
V2=       40676
V3=       40676
V4=       40676 

Frå Funkra=40258 
```

### Avvik FUNKRA vs ny  v2,v3,v4 lengde 1.02% => 15 Grøntanlegg Grasdekker

```
V2=       32295
V3=       32295
V4=       32295 

Frå Funkra=32626 
```

### Avvik FUNKRA vs ny v2,v3,v4 lengde 1.77% => 172 Trafikkdelere

```
V2=        5958
V3=        5958
V4=        5958 

Frå Funkra=6064 
```

### Avvik FUNKRA for v2, v3, v4 lengde 1.06% => 511 Grøntanlegg Busker

```
V2=        1994
V3=        1994
V4=        1994 

Frå Funkra=2016 
```

### NVDB rapporter tar med alt, men Funkra  tar kun med to objekt => 234 Voll

NVDB rapporter tar med alle objekter av typen 234 Voll (43stk), mens Funkra kun tar med to. Tipper Funkra kun tar med dem som har _Bruksområde=Støyskjerming._

```
V2=          43
V3=          43
V4=          43 
Frå Funkra=   2 <= Bruksområde = Støyskjerming? 
```

### Avvik FUNKRA for v2 lengde 1.03% => 318 Snø- og isrydding

```
V2=        40676
V3=        40676
V4=        40676 
Frå Funkra=40258 
```

### Utdatert definisjon i Funkra => 83 Kum, ikke tilknyttet lukket dren.

Nye NVDB rapporter tar kun med de kummene som svarer "Nei" på om de inngår i drensystem. 

```
V2=           5	<= Ny definisjon 
V3=           5
V4=           5 
Frå Funkra=3932 <= Gammal definisjon
```


### Avvik mellom FUNKRA og ny v2/v3/V4 for lengde 1.27% => 274 Grøntanlegg Beplantninger

```
V2=        273
V3=        273
V4=        273 
Frå Funkra=277 
```


### FUNKRA har utdatert utvalgdsdefinisjon  og mangler derfor 3 stykker => 85 Pumpestasjon 

Dette utvalget har feil navn, objekttype 85=Pumpe, mens objekttype 210=pumpestasjon 


```
V2=        4
V3=        4
V4=        3 <= Feil i testrutine, teller ikke antall-egenskapen, kun antall objekt 
Frå Funkra=1 <= Utdatert utvalgdsdefinisjon
```

### En kantstein for mye i ny V2-rapport => 9 Kantstein

Tipper årsaken er multippel stedfesting, som vanlig 

```
V2=         653 <= 1 for mye, multippel stedfesting? 
V3=         652 
V4=         652 
Frå Funkra= 652 
```
