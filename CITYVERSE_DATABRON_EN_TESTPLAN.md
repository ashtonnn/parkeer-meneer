# Cityverse / Parkeer Meneer — schooleisen, databronnen en toetsbare acceptatie

**Basis:** Plan van Aanpak Cityverse groep 1B (pagina 3–6), cursuswijzer DD&AIS 2026–2027 v1.1 (hoofdstuk 4), docentfeedback: **een werkend prototype, desnoods met dummydata; alleen een klein dashboard is onvoldoende**. Exacte rubric en uploadinstructies staan op Brightspace en zijn nog niet bevestigd.

## Eisen uit het Plan van Aanpak → concrete uitvoering en bewijs

| PvA-eis | Uitvoering in Parkeer Meneer | Status / nog nodig |
| --- | --- | --- |
| IoT-sensorconcept, beoogde gebruiker, vrij/bezet | Gesimuleerde sensoren per voorbeeldstraat, interactieve kaart en tijdregeling | Gebouwd; scenario en gebruikerstest documenteren |
| Beschikbare Cityverse-data inspecteren, herkomst en kwaliteit | Gemeentelijke Rotterdam WFS Parkeervoorzieningen via `/api/parking`; BGT/PDOK via `/api/school/bgt` | API-code aanwezig; aantallen, response en actualiteit op Render nog vastleggen |
| Data verzamelen, combineren en verwerken | Echte locaties als afzonderlijke kaartpunten; synthetische sensorstatus afzonderlijk | Scheiding behouden; niet beweren dat de echte locaties echte bezetting tonen |
| Werkend prototype, niet alleen dashboard | Straatkeuze, kaartinteractie, tijdslider, afspelen, vrij/bezet, CSV-export | Gebouwd; volledige browser-/Render-eindtest nog open |
| Minimaal één relevante data-analyse of AI-component | Bezettingspercentages, 60-minuten-scenariovoorspelling, backtest versus baseline | Aanwezig; **regelgebaseerd, geen getrainde AI**; methodiek en resultaten vastleggen |
| Testen, feedback, conclusies, beperkingen, advies | Regressietest `parkeer_meneer_app/tests/simulation.test.cjs`, CI, documentatie | Automatische test eerder geslaagd; echte eindtest, screenshots, feedback en conclusies nog open |
| Actueel PvA, Scrum-board, teamreview (Definition of Done) | Buiten de publieke app: schoolportfolio / Scrum-board | Apart opleveren; teamlid moet resultaat reviewen |
| Datakwaliteit, privacy, reproduceerbaarheid | Publieke objectlocaties zonder persoonsgegevens; synthetische meetwaarden herkenbaar | Datakwaliteit/API-fallback en testscenario's documenteren |

**Belangrijke scope:** het PvA staat gemarkeerde dummydata toe als echte sensordata ontbreekt. Een geografisch parkeervlak, parkeerautomaat of parkeerterrein is niet gelijk aan een gemeten vrij parkeervak. De kaart mag geen live beschikbaarheid of gegarandeerde plek suggereren.

## Relevantie van aangeleverde datasets

1. **Rotterdam Beheer Openbare Ruimte 2D:** WFS-verwijzing `https://diensten.rotterdam.nl/arcgis/services/SB_Infra/Parkeervoorzieningen/MapServer/WFSServer`; ook Parkeerautomaat. **Meest relevant voor echte locatieobjecten**. De JSON-LD is catalogusmetadata; succesvolle live objectdownload moet afzonderlijk worden bewezen.
2. **BGT/PDOK:** `https://api.pdok.nl/kadaster/bgt/ogc/v1/collections/wegdeel/items`. Bruikbaar als achtergrondgeografie, **niet als live sensordata**. De technische BGT-sectie en kaartschakelaars zijn bewust uit de gebruikersinterface verwijderd; de API blijft bestaan.
3. **Rotterdam 3D publieke ruimte:** optioneel voor vervolgonderzoek; niet nodig voor het parkeerprototype.
4. **Rotterdam 3D schaduwanalyse:** niet relevant voor huidige hoofdvraag; niet kunstmatig toevoegen.

## Actuele acceptatietests (uit te voeren op gedeployde versie)

- [ ] Render toont de laatste GitHub-commit; leg URL, commit-ID en tijdstip vast.
- [ ] Open de site, log in en kies Meent; de kaart en parkeerstatus laden zonder fout.
- [ ] Wissel tussen de vijf voorbeeldstraten en controleer de bijbehorende simulatie.
- [ ] Verplaats de tijdslider en speel de simulatie af; vrij/bezet en grafiek veranderen consistent.
- [ ] Selecteer een vrij voorbeeldvak; de app waarschuwt dat dit geen gegarandeerde echte plek is.
- [ ] Test `/api/parking`: bewaar HTTP-status, `mode`, objectaantal, voorbeeldrecord en bronvermelding. Alleen bij echte ontvangen objecten mag dit als geslaagde live data-integratie worden geclaimd.
- [ ] Test `/api/school/bgt?lat=51.9228&lon=4.4852`: bewaar status, sample_count en ontvangen GeoJSON; deze laag hoeft **niet zichtbaar** te zijn in de gebruikersinterface.
- [ ] Simuleer onbereikbare externe API: de parkeerapp blijft bruikbaar en toont geen verzonnen live-data-status.
- [ ] Controleer CSV-export (24 vakken × 96 kwartieren = 2304 synthetische records per straat) en markering van herkomst.
- [ ] Controleer 60-minutenvoorspelling, terugtest en transparante uitleg dat het model regelgebaseerd is.
- [ ] Voer automatische tests opnieuw uit op de eindcommit en noteer de CI-run.
- [ ] Leg minimaal één review door een teamlid, feedback en een eventuele verbeteractie vast.

**Bewijsformat per test:** test-ID, schooleis, datum/tijd, versie/commit, teststappen, verwacht resultaat, werkelijk resultaat, screenshot of response, geslaagd/mislukt, verantwoordelijke.

## AI Symposium en schooloplevering

- **11 december 2026:** werkend prototype demonstreren in workshop/playground op AI Symposium.
- **13 december 2026:** AI Symposium-bewijs voor portfolio.
- **20 december 2026:** individuele AI Symposium-reflectie.
- Als onderbouwing volgens het PvA: actueel PvA en Scrum-board; IoT-concept en doelgroep; broninventarisatie en dataverwerking; werkende app; analyse/AI-component; testresultaten, conclusies, beperkingen en doorontwikkeladvies.
- **Let op:** de precieze beoordelingsrubric en verplichte uploadbestanden staan volgens de cursuswijzer op Brightspace. Niet doen alsof deze al gecontroleerd zijn.

## Status en open risico's

Deze checklist is documentatie en **geen bewijs van een uitgevoerde Render-test**. De laatst bekende geslaagde GitHub-CI-run bevestigt alleen de automatische checks, niet de browser of externe services. In het bijzonder zijn echte Rotterdamse objectaantallen, servicebeschikbaarheid en screenshots nog niet gevalideerd. Voeg geen verzonnen testresultaten toe.
