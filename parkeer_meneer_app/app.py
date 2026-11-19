from flask import Flask, jsonify, send_from_directory
from pathlib import Path
import requests, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
WFS = "https://diensten.rotterdam.nl/arcgis/services/SB_Infra/Parkeervoorzieningen/MapServer/WFSServer"
HEADERS = {"User-Agent": "ParkeerMeneer/0.3 educational prototype"}
@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")
@app.get("/api/health")
def health():
    return jsonify(status="ok", geographic_source="Rotterdam WFS", occupancy="synthetic")
@app.get("/api/parking")
def parking():
    try:
        r = requests.get(WFS, params={"service":"WFS","request":"GetCapabilities","version":"2.0.0"}, headers=HEADERS, timeout=12)
        r.raise_for_status()
        xml = ET.fromstring(r.content)
        types = [x.text for ft in xml.findall(".//{*}FeatureType") for x in [ft.find("{*}Name")] if x is not None and x.text]
        if not types: raise ValueError("Geen WFS-featuretypes beschikbaar")
        features = []
        for typename in types[:4]:
            q = {"service":"WFS","version":"2.0.0","request":"GetFeature","typeNames":typename,"count":250,"outputFormat":"application/json","srsName":"EPSG:4326"}
            res = requests.get(WFS,params=q,headers=HEADERS,timeout=18)
            if not res.ok or "json" not in res.headers.get("content-type","").lower(): continue
            for f in res.json().get("features",[]):
                g=f.get("geometry") or {}
                typ=g.get("type")
                coords=g.get("coordinates")
                if typ=="Point" and coords and len(coords)>=2: lon,lat=coords[:2]
                elif typ=="MultiPoint" and coords: lon,lat=coords[0][:2]
                else: continue
                if 51.7<float(lat)<52.2 and 3.7<float(lon)<4.9:
                    props=f.get("properties") or {}
                    name=next((str(v) for k,v in props.items() if any(x in k.lower() for x in ("naam","name","straat")) and v), "Parkeervoorziening")
                    features.append({"id":str(f.get("id") or len(features)),"name":name[:80],"lat":float(lat),"lon":float(lon),"source":"Rotterdam WFS"})
        if not features: raise ValueError("Geen bruikbare puntobjecten gevonden; WFS kan andere geometrieën aanbieden")
        return jsonify(mode="live",features=features[:300],types=types,occupancy="not_available")
    except Exception as exc:
        return jsonify(mode="unavailable",features=[],message=str(exc)[:300],occupancy="not_available"),503
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)
