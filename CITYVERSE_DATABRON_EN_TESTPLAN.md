# Cityverse – verwerking schooldatabron en testplan

## Wat is gebouwd
Parkeer Meneer gebruikt de **BGT / PDOK**-bron uit de vier besproken schooldatabronnen voor geografische informatie, naast de bestaande **synthetische IoT-parkeerbezetting**. De 3D-viewer blijft optioneel. De oorspronkelijke parkeerweergave is de standaard.

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
7. Klik een groen vak aan en test de waarschuwing dat een echte parkeerplek niet gegarandeerd is. Test de optionele 3D-knop apart.
8. Test de fallback als de BGT-dienst geen data geeft; de app mag niet vastlopen.

## Bewijs voor school
Documenteer per test: gekozen straat, datum/tijd, screenshot van de app, API-status, aantal werkelijk ontvangen BGT-objecten, screenshot van de simulatie, een bevinding en eventueel een verbeteractie.

Het Plan van Aanpak van groep 1B noemt een werkend proof-of-concept/dashboard, inzicht in vrij en bezet, vastgelegde databronnen, minimaal één parkeeranalyse, testresultaten, beperkingen en een advies als beoogde opleveringen. De bestaande bezettingspercentages per tijdstip zijn *beschrijvende analyse van synthetische gegevens*; er is **geen getraind voorspellend AI-model**.

## Bronnen en transparantie
- School: *DDAIS PvA voor Cityverse* (groep 1B).
- School: *IoT en API data Brian 20260921*, met de OUP-catalogusreferenties (`hub.clearly.app`).
- Databron voor deze uitbreiding: **PDOK / Kadaster BGT OGC API Features**, collectie wegdeel.
- Aanvullend: Rotterdamse WFS *Parkeervoorzieningen* is als best-effort bron afzonderlijk beschikbaar, geen sensormeting.

**Nog niet bewezen zonder een Render-test:** of de nieuwste serverversie de PDOK-objecten onder de netwerkcondities van Render kan laden en of alle browserbediening correct werkt.
