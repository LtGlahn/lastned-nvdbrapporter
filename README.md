# lastned-nvdbrapporter

Automatisert nedlasting og sjekk for konsistens av NVDB-rapporter

Testen består i 

1. laste ned fem rapporter per driftskontrakt, fra angitt miljø (UTV, TEST/ATM eller PROD)
2. For hver kontrakt sammenligner vi oppføringer i V2- og V3-rapporten med egne tall laget med basis i V4-rapporten. Hvert vegkategori i V2, og hvert vegstrekning i V3 sjekkes for seg. 
3. Vi lager en html-oppsummering med fargerik tabell per kontraktsområde, [eksempel](http://labs.vegdata.no/nvdbrapporter/driftskontrakter/testrapporter/test2021-02-10/nedlasting_UTV_2021-02-08__9305_Sunnfjord_2021-2026.html), samt en [felles rapport for alle kontraktsområdene](http://labs.vegdata.no/nvdbrapporter/driftskontrakter/testrapporter/test2021-02-10/testsammendrag_2021-02-10_UTV_flererapporter.html) i testen.


# Avhengigheter

Vi trenger python-bibliotekene `pandas` og `geopandas`. Anbefalingen er jo at disse bibliotekene installeres i et såkalt `environment`, for å minimere risiko for versjonskonflikt med andre bibliotek. Jeg har god erfaring med å følge Anaconda-oppskriftene for å håndtere "environments", og da  helst med `conda-forge` som utgangspunkt. Men for dette formålet tror jeg ikke det er så nøye; pip install bør funke greit. 

Og jeg har brukt dette biblioteket for å lese data fra NVDB https://github.com/LtGlahn/nvdbapi-V3 . Scriptet `STARTHER.py` utvider søkestien 
med plasseringen til dette reposet. For så vidt bruker jeg ikke NVDB-data i nåværende versjon (parameterstyrt), men det må i så fall kommenteres ut 
et par steder i koden hvis du vil kjøre uten. 

# Filstruktur, tester og nedlastede rapporter 

Det er muligens en smule uryddig, men jeg foretrakk å lagre testresultater i en annen mappe enn selve reposet (../drift_tester/)

```
.  <------------------------------------------------------ Nivået oppforbi repos
├── drift_tester <---------------------------------------- Mappe for testdata, fylles av script_testkontrakt.py
│   └── testsammendragPROD_flererapporter.html <---------- Felles testrapport, alle driftskontraktene 
│   |
│   ├── ... (filstrukturen nedenfor gjentas for hver av kontraktene angitt i script_testkontrakter.py) .... 
│   |
│   ├── nedlasting_<MILJØ>_<DATO>_<KONTRAKT>.html<= Testrapport per miljø, dato og kontrakt. 
│   └── nedlasting_<MILJØ>_<DATO>_<KONTRAKT>  <==== Testdata, en mappe per miljø, dato og kontrakt
│       ├── Tilstandsrapport.XLSX
│       ├── V1_Vegnettsrapport.XLSX
│       ├── V2_AggregertMengdePerVegkategori.XLSX
│       ├── V3_AggregertMengdePerVegnr.XLSX
│       └── V4_Detaljert_mengde.XLSX
|        
|
└── lastned-nvdbrapporter   <----------------------------- Dette reposet https://github.com/LtGlahn/lastned-nvdbrapporter
    ├── LICENSE
    ├── README.md
    ├── STARTHER.py   <----------------------------------- Angir path for https://github.com/LtGlahn/nvdbapi-V3 
    ├── debugAadt.py
    ├── driftkontraktsjekk.py
    ├── driftqa.py
    ├── lastned.py
    ├── nvdbapi-clientinfo.json
    ├── rapportdefinisjon.json
    ├── script_testkontrakter.py  <---------------------- Testrutine, laster ned og kjører konsistenssjekk
    ├── test_mur.py

```

# Detaljert feilsøking 

Funksjoen `driftqa.py/debugSkrivMeter ` kan aktiveres (debug=True) for å få en detaljert utlisting i konsoll av hvilke objekter og deres stedfesting som telles med i våre beregninger. Potensielt brukbart for feilsøking? 

I så fall er det veldig nyttig å innsnevre feilsøket til kun de relevante objekttypene. I `script_testkontrakter` gjøres dette ved å endre innholdet i listen `objektliste`, f.eks. `objektliste = [ 540, 810]`

# Toodo 

 - Fjerne konnekteringslenker fra regnskapet  (gjelder vel kun 810 og 540, tror jeg)
     - Har en greit gjennomførbar idé her, finner overlapp konnektering (V1-rapport) og objektets stedfesting (V4), og for hver match så trekkes lengden av konnekteringslenken fra lengden av den stedfestingen. 
 - Omstrukturer og finpuss
 - Dokumentasjon, inklusive docstring 

