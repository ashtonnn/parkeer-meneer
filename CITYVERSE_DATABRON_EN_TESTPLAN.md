# Cityverse – verwerking schooldatabron en testplan

## Wat is gebouwd
Parkeer Meneer gebruikt de **BGT / PDOK**-bron uit de vier besproken schooldatabronnen voor geografische informatie, naast de bestaande **synthetische IoT-parkeerbezetting**. De oorspronkelijke parkeerweergave is de standaard. De experimentele 3D-viewer is uit de hoofdroute verwijderd; de aparte technische bestanden blijven voorlopig alleen voor eventueel vervolgonderzoek bestaan.

### Werkelijke dataset
- Dataset: **Basisregistratie Grootschalige Topografie (BGT)**, collectie **wegdeel**, via PDOK OGC API Features.
- Officiële collectiebeschrijving: https://api.pdok.nl/kadaster/bgt/ogc/v1/collections/wegdeel
- Werkelijk bevragingsadres: https://api.pdok.nl/kadaster/bgt/ogc/v1/collections/wegdeel/items
- App-endpoint: `GET /api/school/bgt?lat=51.9228&lon=4.4852` (voorbeeld Meent, Rotterdam).
- Een kleine bounding box rond de gekozen straat wordt gebruikt, met maximaal 150 opgehaalde features en maximaal 65 polygonen voor weergave.
- De app telt ontvangen wegdelen en objecten waarvan een functieveld 'parkeer' bevat. Een geografisch **parkeervlak is niet gelijk aan één gemeten parkeerplek**.
- Op de Rotterdamkaart zijn deze wegdelen als paarse contouren te tonen. Geografie is **echt**; vrij/bezet-status, tijdmachine en parkeeraanbeveling zijn **simulaties**.
- De BGT-koppeling is *geen* bewijs van live IoT-parkeersensoren of van gegarandeerde parkeerbeschikbaarheid.

### Technische foutafhandeling
Als de PDOK-dienst tijdelijk niet bereikbaar is, geeft het server-endpoint `status: unavailable`. De app laat de bronstatus zien en houdt de synthetische parkeersimulatie bruikbaar. Het gehoste endpoint moet op Render worden getest; een codecommit is geen bevestiging dat de verbinding in productie werkt.

## Functionele acceptatiechecks
1. Deploy de nieuwste commit van de `main`-branch naar Render.
2. Open de Parkeer Meneer-site, log in en kies **Meent**. De bestaande parkeersimulatie moet zichtbaar zijn; geen geforceerde 3D-viewer.
3. Scroll naar **Geografische data uit Rotterdam**. Bij de BGT-sectie verschijnen na een geslaagde aanvraag echte aantallen bij *Wegdelen* en *functie parkeervlak*; bij verbindingsfouten verschijnt een eerlijke melding.
4. Open `/api/school/bgt?lat=51.9228&lon=4.4852`. Controleer `status`, `source_url`, `sample_count`, `features` en `occupancy`. Alleen bij `status: connected` én een niet-lege `features.features` kan worden aangetoond dat echte geografische features zijn verwerkt.
5. Ga terug naar de Rotterdamkaart. Het vinkje **Toon BGT-wegdelen** moet echte geografische contouren aan/uit zetten.
6. Gebruik de tijdslider en de knop *Speel af*. Controleer of vrij/bezet-aantallen en de grafiek logisch veranderen (deze uitkomsten zijn synthetisch).
7. Klik een groen vak aan en test de waarschuwing dat een echte parkeerplek niet gegarandeerd is. Controleer dat er géén 3D-knop meer in de hoofdroute staat.
8. Test de fallback als de BGT-dienst geen data geeft; de app mag niet vastlopen.\n9. Controleer de 60-minuten-voorspelling, backtest tegen nulmeting en de CSV-export met 2304 fictieve registraties (24 vakken × 96 kwartieren).\n10. Voer `node parkeer_meneer_app/tests/simulation.test.cjs` uit in de repo-root. Dit is een offline regressiecontrole; test ook handmatig op Render.

## Bewijs voor school
Documenteer per test: gekozen straat, datum/tijd, screenshot van de app, API-status, aantal werkelijk ontvangen BGT-objecten, screenshot van de simulatie, een bevinding en eventueel een verbeteractie.

Het Plan van Aanpak van groep 1B noemt een werkend proof-of-concept/dashboard, inzicht in vrij en bezet, vastgelegde databronnen, minimaal één parkeeranalyse, testresultaten, beperkingen en een advies als beoogde opleveringen. De bezettingspercentages per tijdstip zijn *beschrijvende analyse van synthetische gegevens*. Daarnaast is een uitlegbaar **60-minuten-scenariovoorspelmodel** en een terugtest toegevoegd. Er is **geen getraind voorspellend AI-model**. Het model combineert 50% huidige gesimuleerde bezetting met 50% vooraf ingesteld drukteprofiel; de backtest gebruikt 89 fictieve tijdstippen.

## Bronnen en transparantie
- School: *DDAIS PvA voor Cityverse* (groep 1B).
- School: *IoT en API data Brian 20260921*, met de OUP-catalogusreferenties (`hub.clearly.app`).
- Databron voor deze uitbreiding: **PDOK / Kadaster BGT OGC API Features**, collectie wegdeel.
- Aanvullend: Rotterdamse WFS *Parkeervoorzieningen* is als best-effort bron afzonderlijk beschikbaar, geen sensormeting.

**Nog niet bewezen zonder een Render-test:** of de nieuwste serverversie de PDOK-objecten onder de netwerkcondities van Render kan laden en of alle browserbediening correct werkt.


## Afronding
Zie `CITYVERSE_OPLEVERPLAN.md` voor PvA-mapping, nog openstaande browser-/opdrachtgevertests en conclusies. GitHub-code is geen bevestiging dat de externe BGT-service op Render werkt.
