# Parkeer Meneer — Cityverse

## Direct testen (mobiel en pc)
Open `index.html` in een moderne browser. De app werkt in demo-modus zonder Python. Voor de kaarttegels is internet nodig; als deze geblokkeerd zijn, verschijnt een schematische achtergrond. De locaties zijn **voorbeeldlocaties**, en de bezetting is **synthetisch**.

## Python-server starten (voor poging tot echte Rotterdam WFS-data)
1. Installeer Python 3.10+.
2. Open een terminal in deze map.
3. Voer uit: `pip install -r requirements.txt`
4. Voer uit: `python app.py`
5. Open `http://localhost:5000` op je pc.
6. Klik op **Probeer Rotterdam-data**.

Voor mobiel: verbind telefoon en pc met hetzelfde wifi-netwerk, zoek het lokale IP-adres van de pc en open `http://PC-IP:5000` op de telefoon. Sta indien nodig lokale toegang toe in de firewall. Voor publieke toegang is hosting met HTTPS nodig.

## Databronnen en beperkingen
De vier door de gebruiker aangeleverde JSON-LD-bestanden staan in `data/`. Dit zijn **catalogusmetadata**, geen actuele parkeerbezetting. De relevante Rotterdamse WFS-verwijzing voor parkeervoorzieningen is afkomstig uit `689f8244faa203e6255bc0dc.jsonld`. De BGT-API is bruikbaar als aanvullende geografische bron, maar niet nodig voor de OpenStreetMap-ondergrond.

De WFS is in deze omgeving niet live bereikbaar geweest. De server vraagt eerst GetCapabilities op, probeert vervolgens GeoJSON-puntobjecten op te halen en toont een duidelijke foutmelding als de bron geen puntobjecten aanbiedt of onbereikbaar is. Polygonen en alternatieve WFS-responsformaten vereisen extra verwerking. **Er worden geen live parkeergegevens of succesvolle API-koppelingen geclaimd.**
