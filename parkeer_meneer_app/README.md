# Parkeer Meneer – Concept 3

## Start
`pip install -r requirements.txt`
`python app.py`
Open http://localhost:5000

## Werking
- Startpagina: Rotterdamkaart, zoeken naar straat.
- Mascotte: knipoog, tekstballon 'Let's park!', zoomtransitie.
- Straatpagina: 24 **illustratieve** vakken; synthetische IoT-bezetting met reproduceerbare uurpatronen en herberekende KPI's.
- Tik op een groen vak: korte autoanimatie en daarna aparte links voor Google Maps, Waze en Apple Kaarten.
- WFS-koppeling probeert echte Rotterdamse **geografische puntobjecten** op te halen. Het resultaat wordt alleen als geladen weergegeven wanneer de externe service bruikbare records retourneert.

## Belangrijk
De meegeleverde JSON-LD beschrijft de databron; de WFS bevat mogelijk objecten maar geen live parkeersensoren. De straatvakken zijn illustratief, niet aan officiële locaties gekoppeld. Een route gaat naar het midden van de gekozen straat, niet naar een individueel vak. De tijdlijn en spitsprofielen zijn **synthetisch**, geen echte metingen. Geen claim van gegarandeerde beschikbaarheid.

## Deploy
Vervang de bestaande bestanden in `parkeer_meneer_app/` en deploy via de bestaande Render-configuratie. Controleer daarna `/api/health` en `/api/parking`.
