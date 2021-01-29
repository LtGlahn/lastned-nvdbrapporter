# Oppsummering, kvalitetssjekk av objektdata til driftskontrakter

Denne tabellen er laget ved å bruke data fra V4-tabellen og egenprodusert kode som "etterligner" beregning av V2- og V3-tabellene, for antall, lengde og areal per vegstrekning.

Tabellen her er laget for kontraktsområdet _9305 Sunnfjord 2021-2026_, den 29. januar, basert på data nedlastet 27. januar 2021. 

### Kjente svakheter

Vi mistenker at egenskapsfilteret som brukes i koden vår er litt for primitivt: Det fungerer for enkle tilfeller (f.eks _"Terrenggrøft"_),men feiler for de mer komplekse tilfellene (f.eks "_Grøft unntatt terrenggrøft_"). Dette blir forbedret.

En annen svakhet er også at våre automatiserte tester ikke sammenligner med data fra de gamle Funkra _Standard vedleggsfil" (ennå). Vi har selvsagt gjort manuelle kontroller, men dette bør automatiseres. 


Andre _"Kjente feil"_ mener vi er feil i [produksjonssystemet vårt](https://nvdb-vegnett-og-objektdata.atlas.vegvesen.no/). Feilsøking og feilretting pågår
Andre _"Kjente feil"_ mener vi er feil i produksjonssystemet vårt. Feilsøking og feilretting pågår<table><thead><tr><td>TypeID</td><td>Beskrivelse</td><td>Antall</td><td>Lengde</td><td>Areal</td><td>Kjente feil</td></tr></thead>
<tr><td>{3}</td> <td>Skjerm</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{5}</td> <td>Rekkverk</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{7}</td> <td>Gjerde</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{9}</td> <td>Kantstein</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{14}</td> <td>Rekkverksende, Ettergivende</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{15}</td> <td>Grøntanlegg Grasdekker</td><td >OK</td> <td >OK</td><td >OK</td><td></td></tr>
<tr><td>{20}</td> <td>Kantstolper</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{22}</td> <td>Ferist</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{23}</td> <td>Vegbom</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{24}</td> <td>Skiltportaler</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{25}</td> <td>Leskur</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{27}</td> <td>Avfallsbeholdere</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{28}</td> <td>Utemøbler</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{29}</td> <td>Strøsandkasse</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{37}</td> <td>Kanalisering primærveg</td><td >OK</td> <td >-</td><td >-</td><td>Telling av vegkryss og avledede verdier (primærveg, sekundærveg) feiler</td></tr>
<tr><td>{37}</td> <td>Kanalisering sekundærveg</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Telling av vegkryss og avledede verdier (primærveg, sekundærveg) feiler</td></tr>
<tr><td>{37}</td> <td>Vegkryss</td><td >Mye avvik</td> <td >OK</td><td >-</td><td>Telling av vegkryss og avledede verdier (primærveg, sekundærveg) feiler</td></tr>
<tr><td>{39}</td> <td>Rasteplass</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{42}</td> <td>Kollektivtrafikkterminaler</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{43}</td> <td>Parkeringsområde</td><td >OK</td> <td >OK</td><td >OK</td><td></td></tr>
<tr><td>{44}</td> <td>Kontroll- og veieplasser</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{45}</td> <td>Bomstasjon</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{47}</td> <td>Busslomme</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{47}</td> <td>Trafikklomme u/busslomme</td><td >Mye avvik</td> <td >Store avvik</td><td >Store avvik</td><td></td></tr>
<tr><td>{48}</td> <td>Fortau</td><td >OK</td> <td >OK</td><td >Noe avvik</td><td></td></tr>
<tr><td>{49}</td> <td>Trafikkøyer</td><td >OK</td> <td >OK</td><td >OK</td><td></td></tr>
<tr><td>{60}</td> <td>Alle NVDB-data av typen "Bru" (dvs fra fagsystem Brutus)</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{60}</td> <td>Ferjekai registrert som bru i NVDB</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{62}</td> <td>Mur</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{64}</td> <td>Kaier</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{65}</td> <td>Bygninger</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{66}</td> <td>Skredoverbygg</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{67}</td> <td>Tunneler</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{72}</td> <td>Fjellsikringsutstyr</td><td >OK</td> <td >OK</td><td >OK</td><td></td></tr>
<tr><td>{78}</td> <td>Lukka drenering</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{79}</td> <td>Stikkrenne</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{80}</td> <td>Grøft, terrenggrøft</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{80}</td> <td>Grøft. untatt terrenggrøft</td><td >Mye avvik</td> <td >Store avvik</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{83}</td> <td>Kum, Alle NVDB-data</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{83}</td> <td>Kum, Hjelpesluk</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{83}</td> <td>Kum, ikke tilknyttet lukket dren.</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{83}</td> <td>Kum, tilknyttet lukket drenering</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{85}</td> <td>Pumpestasjon</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{86}</td> <td>Belysningsstrekning</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{95}</td> <td>Skiltportaler (Skiltpkt)</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{96}</td> <td>Informasjonstavle</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{96}</td> <td>Skilt, utvendig belysning</td><td >Noe avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{96}</td> <td>Skilt, innvendig belysning</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{96}</td> <td>Skilt, uten belysning</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{96}</td> <td>Skiltplate, Alle NVDB-data unntatt tunnelmarkering</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{96}</td> <td>Tunnelmarkering</td><td >Mye avvik</td> <td >-</td><td >-</td><td>Skal sjekkes nærmere, mistenker feil i kvalitetskontrollens egenskapfilter</td></tr>
<tr><td>{97}</td> <td>Skilt, variable</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{99}</td> <td>Alle NVDB-data for Vegoppmerking, langsgående</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{99}</td> <td>Vegbanereflektorer</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{107}</td> <td>Værutsatt veg</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{153}</td> <td>Værstasjon</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{162}</td> <td>ATK-punkt</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{167}</td> <td>Tellesløyfer</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{172}</td> <td>Trafikkdelere</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{199}</td> <td>Grøntanlegg Trær</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{208}</td> <td>Oppsamlingsbasseng</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{234}</td> <td>Voll</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{241}</td> <td>Dekke, Betong</td><td >-</td> <td >-</td><td >-</td><td>Utdaterte regler, vi må justere ihht ny datakatalog</td></tr>
<tr><td>{241}</td> <td>Dekke, Grus</td><td >-</td> <td >-</td><td >-</td><td>Utdaterte regler, vi må justere ihht ny datakatalog</td></tr>
<tr><td>{241}</td> <td>Dekke, Stein</td><td >-</td> <td >-</td><td >-</td><td>Utdaterte regler, vi må justere ihht ny datakatalog</td></tr>
<tr><td>{243}</td> <td>Toalettskåler</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{269}</td> <td>Vegskulder/vegkant</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{274}</td> <td>Grøntanlegg Beplantninger</td><td >OK</td> <td >OK</td><td >OK</td><td></td></tr>
<tr><td>{291}</td> <td>Viltrekk</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{301}</td> <td>Kantklippareal</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{301}</td> <td>Kantklippareal, årlig anbefalt areal</td><td >-</td> <td >-</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler og muligens spesialregel for "Anbefalt årlig" feiler</td></tr>
<tr><td>{318}</td> <td>Snø- og isrydding</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
<tr><td>{342}</td> <td>Trafikkspeil</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{482}</td> <td>Tellepunkt</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{511}</td> <td>Grøntanlegg Busker</td><td >OK</td> <td >OK</td><td >OK</td><td></td></tr>
<tr><td>{519}</td> <td>Vegoppmerking, tverrgående</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{540}</td> <td>ÅDT (1), 0 - 500</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{540}</td> <td>ÅDT (2), 500 - 1500</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{540}</td> <td>ÅDT (3), 1500 - 3000</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{540}</td> <td>ÅDT (4), 3000 - 5000</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{540}</td> <td>ÅDT (5), 5000 - 6000</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{540}</td> <td>ÅDT (6), 6000 - 10000</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{540}</td> <td>ÅDT (7), 10000 - 20000</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{542}</td> <td>Støtpute</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse A</td><td >-</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse B,  Høy</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse B,  Middels</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse B, Lav</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse C</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse D</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse E</td><td >-</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse GsA</td><td >-</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse GsB</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{810}</td> <td>Vinterdriftsklasse Sideanlegg</td><td >-</td> <td >-</td><td >-</td><td>Spesialregel for vinterdiftsklasse og ÅDT feiler med for små verdier</td></tr>
<tr><td>{836}</td> <td>Vegoppmerking, forsterket</td><td >OK</td> <td >-</td><td >-</td><td></td></tr>
<tr><td>{838}</td> <td>Vegbredde</td><td >-</td> <td >OK</td><td >OK</td><td>Regeldefinisjon er utdatert ihht datakatalog, må justeres</td></tr>
<tr><td>{845}</td> <td>Fanggjerde</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{859}</td> <td>Taktile Indikatorer</td><td >OK</td> <td >OK</td><td >Store avvik</td><td>Spesialregel areal = Lengde x Bredde feiler</td></tr>
<tr><td>{875}</td> <td>Trapper</td><td >OK</td> <td >OK</td><td >-</td><td></td></tr>
</table>

