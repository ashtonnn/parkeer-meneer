from flask import Flask, jsonify, send_from_directory
from pathlib import Path
import requests, xml.etree.ElementTree as ET, re
ROOT=Path(__file__).resolve().parent
app=Flask(__name__,static_folder=str(ROOT),static_url_path='')
WFS='https://diensten.rotterdam.nl/arcgis/services/SB_Infra/Parkeervoorzieningen/MapServer/WFSServer'
HEADERS={'User-Agent':'ParkeerMeneer/0.3 educational prototype'}
@app.get('/')
def home():return send_from_directory(ROOT,'index.html')
@app.get('/api/health')
def health():return jsonify(status='ok',source='Rotterdam WFS (metadata supplied by user)',occupancy='simulated')
@app.get('/api/parking')
def parking():
 try:
  r=requests.get(WFS,params={'service':'WFS','request':'GetCapabilities','version':'2.0.0'},headers=HEADERS,timeout=12);r.raise_for_status()
  root=ET.fromstring(r.content)
  types=[]
  for ft in root.findall('.//{*}FeatureType'):
   name=ft.find('{*}Name')
   if name is not None and name.text:types.append(name.text)
  if not types:raise ValueError('Geen WFS feature types gevonden')
  features=[]
  for typename in types[:3]:
   q={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':typename,'count':250,'outputFormat':'application/json','srsName':'EPSG:4326'}
   res=requests.get(WFS,params=q,headers=HEADERS,timeout=18)
   if res.ok and 'json' in res.headers.get('content-type','').lower():
    data=res.json()
    for f in data.get('features',[]):
     g=f.get('geometry') or {};coords=g.get('coordinates');typ=g.get('type')
     if typ=='Point' and isinstance(coords,list) and len(coords)>1:
      lon,lat=coords[:2]
     elif typ=='MultiPoint' and coords:lon,lat=coords[0][:2]
     else:continue
     if 51.7<float(lat)<52.2 and 3.7<float(lon)<4.9:
      props=f.get('properties') or {}
      title=next((str(v) for k,v in props.items() if any(s in k.lower() for s in ('naam','name','straat')) and v), 'Parkeervoorziening')
      features.append({'id':str(f.get('id') or len(features)),'name':title[:80],'lat':float(lat),'lon':float(lon),'properties':props,'source':'Rotterdam WFS'})
  if not features:raise ValueError('WFS bereikbaar, maar geen bruikbare puntlocaties. Mogelijk polygonen of een ander formaat.')
  return jsonify(mode='live',features=features[:300],types=types,occupancy='not available')
 except Exception as exc:
  return jsonify(mode='unavailable',features=[],message=str(exc)[:300],occupancy='not available'),503
if __name__=='__main__':app.run(host='0.0.0.0',port=5000,debug=False)
