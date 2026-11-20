# Parkeer Meneer · Cityverse Smart Parking Rotterdam

**Onderwijsprototype** voor de minor Data Driven & AI Solutions. Gebruik van echte geografische data (waar bereikbaar) en **gesimuleerde IoT-sensordata**. Dit is geen live parkeerapp.

## Start
```bash
cd parkeer_meneer_app
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000. Je moet je registreren; het wachtwoord moet minimaal 12 tekens hebben. Op Render is voor accounts een persistente schijf/database-instelling nodig om verlies bij een herdeploy te voorkomen.

## Wat werkt in de code
- Vijf voorgeselecteerde Rotterdamse straten: Kralingse Zoom, Weena, Coolsingel, Meent en Kruisplein, plus zoeken via Nominatim.
- Per straat 24 illustratieve vakken; twee daarvan zijn illustratief toegankelijk. Groen betekent **synthetisch vrij**, rood **synthetisch bezet**, blauw **illustratief toegankelijk**, niet officieel vastgesteld.
- Tijdslider met kwartierstappen, grafiek, KPI's, keuze van vak en navigatie naar **straatlocatie**.
- Exporteer de bij de geselecteerde straat horende fictieve IoT-gegevens naar **CSV** (96 tijdmomenten × 24 vakken = 2304 rijen).
- Bescheiden voorspelmodel dat een uur vooruit 50% huidige gesimuleerde bezetting en 50% het vooraf ingestelde drukteprofiel gebruikt. Een terugtest op fictieve gegevens toont de gemiddelde absolute afwijking en vergelijkt die met de nulmeting (huidige stand vasthouden). **Dit is data-analyse, geen getrainde AI en geen voorspelling van echte parkeerbeschikbaarheid.**
- Echte BGT-wegdelen via de openbare **PDOK OGC API Features** (`GET /api/school/bgt?lat=51.9228&lon=4.4852`). BGT-wegdelen zijn geografische vlakken, geen gemeten parkeerplekken; bij storing geeft de app een fallback.
- Aanvullend een best-effort Rotterdamse WFS-koppeling. De technische 3D-experimenten zijn uit de hoofdroute verwijderd en staan los van dit MVP.

## Databronnen
- **Schoolmateriaal**: aangeleverd BGT OGC API Features JSON-LD en *IoT en API data Brian 20260921*. Deze documenten geven toegangspunten/metadata, geen live parkeersensorwaarden.
- **Werkelijk geraadpleegd**: PDOK/Kadaster BGT `wegdeel`, OpenStreetMap/Nominatim en indien bereikbaar Rotterdam WFS.
- **Zelf gegenereerd**: parkeerstatus, toegankelijke voorbeelden, tijdprofiel, voorspellingen en CSV.

## Validatie
```bash
node parkeer_meneer_app/tests/simulation.test.cjs
python -m py_compile parkeer_meneer_app/app.py
```
Voer de commando's uit in de **root van het repository**. Ze controleren broncodesyntaxis en gesimuleerde scenario's, niet de echte Render-browserervaring of externe API-bereikbaarheid. Op GitHub draait hiervoor (indien Actions is ingeschakeld) de workflow `Cityverse MVP - offline controles`.

Lees ook `../CITYVERSE_DATABRON_EN_TESTPLAN.md` en `../CITYVERSE_OPLEVERPLAN.md`.

## Voor oplevering op Render
1. Deploy de nieuwste `main` commit; controleer of Render dezelfde SHA gebruikt.
2. Check `/api/health` en `/api/school/bgt?lat=51.9228&lon=4.4852`.
3. Log in, kies Meent, controleer bezettingskleuren, tijdslider, voorspelling, CSV-export, BGT-status en terugnavigeren.
4. Test Kralingse Zoom en een onbereikbare databron: de simulatie moet blijven werken.
5. Bewaar screenshots en leg de terugkoppeling van team/docent/opdrachtgever vast.

**Let op:** er is geen bewijs van live IoT, geverifieerde individuele parkeerlocaties of een volledig fotorealistische straatweergave. Een groene demo-plek garandeert niets in de echte wereld.
