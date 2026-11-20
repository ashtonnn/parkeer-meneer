# Cityverse · afrondingsplan en oplevercontrole
**Project:** Slim parkeren in Rotterdam (Parkeer Meneer)  
**Opleiding:** Minor Data Driven & AI Solutions, groep 1B  
**Stand code:** 20 november 2026 — dit document is een werkdocument, geen verklaring dat de opleiding de opdracht heeft goedgekeurd.

## Besluit over scope
We ronden de **werkende, oorspronkelijke parkeerapp** af. Er komt geen GTA-achtige 3D-straat als onderdeel van het MVP. De mislukte 3D-experimenten blijven alleen technisch in het repository en op een back-upbranch staan; de hoofdapp verwijst er niet meer naartoe.

**Waarom:** volgens het Plan van Aanpak moet een afgebakende proof-of-concept/dashboard vrij en bezet inzichtelijk maken, bronnen en beperkingen documenteren en minimaal één relevante parkeeranalyse opleveren. Een fotorealistische digitale tweeling is daar niet vereist. In het PvA staat ook dat **gesimuleerde data is toegestaan** zolang echte sensorgegevens niet beschikbaar zijn.

## Overzicht van het product
1. Automobilist kiest een Rotterdamse voorbeeldstraat (Meent, Coolsingel, Weena, Kruisplein of Kralingse Zoom).
2. Werkelijke straatlocaties worden op de 2D-kaart gezocht; BGT-wegdelen kunnen apart worden opgehaald en getoond als de PDOK-dienst reageert.
3. Een duidelijk gemarkeerd **fictief sensornetwerk** van 24 voorbeeldplekken laat per tijdstip bezetting zien. De app onderscheidt reguliere en illustratief toegankelijke vakken.
4. De gebruiker kan de tijd veranderen, trends zien, een groen voorbeeldvak selecteren en een navigatielink naar de **straat** openen.
5. Het dashboard toont vrije/bezette vakken, druktepercentages en een **60-minuten-scenariovoorspelling**. Het voorspelmodel combineert de huidige gesimuleerde bezetting met een vooraf ingesteld dagprofiel en toont een eerlijk terugtestresultaat.
6. CSV-export maakt de synthetische IoT-voorbeeldwaarden reproduceerbaar voor analyse of demonstratie.

## Eisen uit het Plan van Aanpak — voortgang
| PvA-oplevering | Stand | Nog nodig voor officiële afronding |
| --- | --- | --- |
| 1. Plan van Aanpak en Scrum-board | PvA aangeleverd; Scrum-board status onbekend | Definitieve taakverdeling, sprintbewijs en board actualiseren |
| 2. IoT-concept en doelgroep | Concept omschreven, gebruiker = automobilist/bezoeker | Doelgroepkeuze en pilotstraat door opdrachtgever/docent laten bevestigen |
| 3. Benodigde en beschikbare Cityverse-data | Databronnen en herkomst vastgelegd; openbare BGT-koppeling in code | Werkelijke Render-respons inspecteren; onderscheid met gemeentelijke datasets uitleggen |
| 4. Proof-of-concept | Functionaliteit geïmplementeerd in code, 2D simulatie standaard | Browser-/mobiele validatie en deployment controleren |
| 5. Data-analyse/AI | Beschrijvende analyse + uitlegbaar regelgebaseerd 60-minutenmodel in code | Resultaten en beperkingen beoordelen, bijvoorbeeld in screenshots/CSV |
| 6. Testresultaten, conclusies, beperkingen en advies | Offline checks en testprocedure voorbereid | Echte testuitvoering, waarnemingen, feedback en conclusies toevoegen |

**Belangrijk:** de PvA-tekst noemt data-analyse/AI. Het huidige voorspelmodel is een **analytisch scenariomodel en geen getraind AI-model**. Bevestig met de docent of dit volstaat als een AI-component in de definitieve beoordelingsrubric apart verplicht wordt gesteld.

## Dataprovenance
| Gegeven | Herkomst | Gebruik | Wat het NIET is |
| --- | --- | --- | --- |
| Straatlocatie | OpenStreetMap/Nominatim | Kaart, navigatie naar de straat | Geen geverifieerd individueel parkeervak |
| BGT `wegdeel` | PDOK/Kadaster via OGC API Features, gebaseerd op aangeleverde schoolmetadata | Echte geografische objecten/wegcontouren in de buurt | Geen sensorlocatie en geen vrij/bezet |
| Rotterdam parkeervoorzieningen WFS | Externe gemeentelijke bron (best effort) | Aanvullende geografische objecten indien bereikbaar | Geen betrouwbare actuele bezetting |
| IoT-status van 24 voorbeeldplekken | Eigen deterministisch simulatiemodel | Groen/rood, tijdmachine, grafiek en CSV | Geen echte sensorregistratie |
| Toegankelijke voorbeeldvakken | Illustratief in simulatie | Blauwe uitleg | Geen officiële parkeerrechten of aanduidingen |
| Voorspelling over één uur | Huidige synthetische meting + vooraf vastgesteld dagprofiel | Scenario-analyse | Geen live AI-voorspelling |

Voor de aanvankelijk verstrekte schoolinformatie verwijzen we naar *IoT en API data Brian 20260921* en het aangeleverde BGT JSON-LD-bestand. Die bronnen noemen eindpunten en beschrijvingen, niet een bruikbare tijdreeks met werkelijke straatparkeersensoren.

## Acceptatieproeven — invullen met waarnemingen
| ID | Uitvoering | Verwachte uitkomst | Werkelijke status |
| --- | --- | --- | --- |
| T01 | Open site, registreer of log in, kies **Meent** | 2D parkeerweergave; niet automatisch 3D | Nog live te testen |
| T02 | Klik groen, rood en blauw voorbeeldvak | Groen geeft bevestiging, rood/blauw geen reguliere reservering | Nog live te testen |
| T03 | Schuif tijdmachine en speel dag af | KPI's, 24 vakken, grafiek en voorspelling veranderen | Nog live te testen |
| T04 | Klik **Exporteer synthetische data** | CSV met 2304 rijen plus kopregel; 96 kwartieren, 24 vakken | Nog live te testen |
| T05 | Open `/api/school/bgt?lat=51.9228&lon=4.4852` | Bij werkende PDOK: status connected, GeoJSON, steekproefaantallen | Nog live te testen |
| T06 | Test PDOK onbereikbaar of `status: unavailable` | App toont nette melding; 2D simulatie werkt door | Nog live te testen |
| T07 | Test mobiel (iPhone/Android) op Kralingse Zoom en Coolsingel | Leesbare knoppen, kaart en bezetting | Nog live te testen |
| T08 | Klik navigatielink | Gaat naar gekozen straat, expliciet niet naar individueel vak | Nog live te testen |
| T09 | Voer offline tests uit | JS syntaxis en 480 tijdmomenten over vijf straten geldig | Automatische workflow aangemaakt; status controleren |
| T10 | Laat docent/Cityverse-contactpersoon een demonstratie beoordelen | Concrete feedback vastgelegd en verwerkt | Nog niet bevestigd |

**Bewijs per test:** test-ID, datum, straat, omgeving (Render/lokaal), screenshot of console-uitvoer, testresultaat, bevinding en verbeteractie. Vink nooit een test af zonder werkelijke uitvoering.

## Analyse-uitleg voor de eindpresentatie
- **Beschrijvende analyse:** per kwartier het percentage bezette reguliere voorbeeldplekken. Drukte wordt ingedeeld als rustig/gemiddeld/druk.
- **Model:** een uur vooruit voorspellen door 50% van de huidige gesimuleerde drukte te combineren met 50% van het vooraf ingestelde dagprofiel op het toekomstige tijdstip. Dit is uitdrukkelijk een **scenariomodel**, geen algoritme dat uit echte historische data leerde.
- **Terugtest:** gebruik 89 synthetische tijdstippen, voorspelling versus status 60 minuten later; meet gemiddelde absolute fout in **procentpunten** en vergelijk met de nulmeting die de huidige stand vasthoudt.
- **Interpretatie:** een score op gesimuleerde data zegt niets over de voorspelnauwkeurigheid bij echte parkeersensoren. Bespreek eventuele momenten waarop het model slechter presteert dan de nulmeting.

## Laatste taken voor het team
- [ ] Laat Render dezelfde commit deployen als de laatste `main`-commit.
- [ ] Voer de browser- en API-proeven uit; voeg echt bewijs toe.
- [ ] Scherp het Plan van Aanpak aan op de **definitieve** scope (2D, data en analyse), inclusief verantwoordelijkheid per teamlid.
- [ ] Werk het Scrum-board en de planning bij.
- [ ] Bevestig met opdrachtgever/docent of dit aan de laatste beoordelingscriteria voldoet; noteer ontbrekende eisen als die er zijn.
- [ ] Maak de eindpresentatie: probleem → oplossing → databronnen → demo → analyse → evaluatie → beperkingen → advies.
- [ ] Leg conclusie en advies vast: pilot met echte sensoren, kwaliteitscontrole van locaties, datagovernance, nauwkeurigheidsmeting en eventueel een 3D-digital-twin als **latere uitbreiding**, niet als huidige deliverable.

## Technische links
- Project: https://github.com/ashtonnn/parkeer-meneer
- Back-up (voor deze afrondingsfase): https://github.com/ashtonnn/parkeer-meneer/tree/backup-voor-afronding-2026-11-20
- Live app (Render, pas betrouwbaar na verifieerbare deployment): https://parkeer-meneer.onrender.com/
- BGT bron: https://api.pdok.nl/kadaster/bgt/ogc/v1/collections/wegdeel
- Testplan databron: `CITYVERSE_DATABRON_EN_TESTPLAN.md`
