from flask import Flask, jsonify, send_from_directory, request, session
from pathlib import Path
import requests, xml.etree.ElementTree as ET
import os, re, time, threading
from datetime import timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(32), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER")), SESSION_COOKIE_SAMESITE="Lax", PERMANENT_SESSION_LIFETIME=timedelta(days=7))
DB_PATH = Path(os.environ.get("SQLITE_PATH", str(ROOT / "parkeer_meneer.sqlite3")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
def db():
    connection=sqlite3.connect(DB_PATH,timeout=15)
    connection.row_factory=sqlite3.Row
    return connection
with db() as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    if "name" not in [row["name"] for row in conn.execute("PRAGMA table_info(users)")]:
        conn.execute("ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT ''")

@app.post("/api/auth/register")
def register():
    data=request.get_json(silent=True) or {}
    email=str(data.get("email","")).strip().lower()
    password=str(data.get("password",""))
    name=str(data.get("name","")).strip()[:80]
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email) or len(email)>255 or not 12<=len(password)<=128:
        return jsonify(error="Gebruik een geldig e-mailadres en een wachtwoord van 12–128 tekens"),400
    try:
        with db() as conn:
            result=conn.execute("INSERT INTO users (email,password_hash,name) VALUES (?,?,?)",(email,generate_password_hash(password),name))
            uid=result.lastrowid
    except sqlite3.IntegrityError:
        return jsonify(error="Registreren mislukt; e-mailadres mogelijk al in gebruik"),409
    session.clear();session.permanent=True;session["uid"]=uid
    return jsonify(email=email),201

@app.post("/api/auth/login")
def login():
    data=request.get_json(silent=True) or {}
    email=str(data.get("email","")).strip().lower()
    with db() as conn:
        user=conn.execute("SELECT id,email,password_hash FROM users WHERE email=?",(email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"],str(data.get("password",""))):
        return jsonify(error="E-mailadres of wachtwoord onjuist"),401
    session.clear();session.permanent=True;session["uid"]=user["id"]
    return jsonify(email=user["email"])

@app.post("/api/auth/logout")
def logout():
    session.clear();return jsonify(ok=True)

@app.get("/api/auth/me")
def me():
    uid=session.get("uid")
    if not uid:return jsonify(configured=True,email=None)
    with db() as conn:
        user=conn.execute("SELECT email,name FROM users WHERE id=?",(uid,)).fetchone()
    return jsonify(configured=True,email=user["email"] if user else None,name=user["name"] if user else None,admin=bool(user and os.environ.get("ADMIN_EMAIL") and user["email"]==os.environ["ADMIN_EMAIL"].strip().lower()))

@app.post("/api/auth/profile")
def profile():
    uid=session.get("uid")
    if not uid:return jsonify(error="Niet ingelogd"),401
    data=request.get_json(silent=True) or {}
    email=str(data.get("email","")).strip().lower()
    name=str(data.get("name","")).strip()
    password=str(data.get("current_password",""))
    new=str(data.get("new_password",""))
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email) or len(email)>255 or len(name)>80 or (new and not 12<=len(new)<=128):
        return jsonify(error="Controleer e-mail, naam en wachtwoord (minimaal 12 tekens)"),400
    with db() as conn:
        user=conn.execute("SELECT password_hash FROM users WHERE id=?",(uid,)).fetchone()
        if not user or not check_password_hash(user["password_hash"],password):
            return jsonify(error="Huidig wachtwoord onjuist"),403
        try:
            if new:
                conn.execute("UPDATE users SET email=?,name=?,password_hash=? WHERE id=?",(email,name,generate_password_hash(new),uid))
            else:
                conn.execute("UPDATE users SET email=?,name=? WHERE id=?",(email,name,uid))
        except sqlite3.IntegrityError:
            return jsonify(error="E-mailadres al in gebruik"),409
    return jsonify(email=email,name=name)

@app.get("/admin")
def admin_page():
    uid=session.get("uid")
    if not uid:return "Geen toegang",403
    with db() as conn:
        user=conn.execute("SELECT email FROM users WHERE id=?",(uid,)).fetchone()
    if not user or not os.environ.get("ADMIN_EMAIL") or user["email"]!=os.environ["ADMIN_EMAIL"].strip().lower():
        return "Geen toegang",403
    return send_from_directory(ROOT,"admin.html")

def is_admin():
    uid=session.get("uid")
    admin_email=os.environ.get("ADMIN_EMAIL","").strip().lower()
    if not uid or not admin_email:return False
    with db() as conn:
        user=conn.execute("SELECT email FROM users WHERE id=?",(uid,)).fetchone()
    return bool(user and user["email"]==admin_email)

@app.patch("/api/admin/users/<int:user_id>")
def admin_update_user(user_id):
    if not is_admin():return jsonify(error="Geen toegang"),403
    data=request.get_json(silent=True) or {}
    name=str(data.get("name","")).strip()
    email=str(data.get("email","")).strip().lower()
    if len(name)>80 or len(email)>255 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email):
        return jsonify(error="Ongeldige naam of e-mailadres"),400
    admin_email=os.environ.get("ADMIN_EMAIL","").strip().lower()
    with db() as conn:
        user=conn.execute("SELECT email FROM users WHERE id=?",(user_id,)).fetchone()
        if not user:return jsonify(error="Gebruiker niet gevonden"),404
        if user["email"]==admin_email and email!=admin_email:
            return jsonify(error="Beheerderadres kan niet via deze pagina worden gewijzigd"),400
        if user["email"]!=admin_email and email==admin_email:
            return jsonify(error="Beheerderadres is gereserveerd"),400
        try:
            conn.execute("UPDATE users SET name=?,email=? WHERE id=?",(name,email,user_id))
        except sqlite3.IntegrityError:
            return jsonify(error="E-mailadres is al in gebruik"),409
    return jsonify(ok=True)

@app.delete("/api/admin/users/<int:user_id>")
def admin_delete_user(user_id):
    if not is_admin():return jsonify(error="Geen toegang"),403
    if user_id==session.get("uid"):
        return jsonify(error="Je kunt je eigen beheerdersaccount hier niet verwijderen"),400
    with db() as conn:
        user=conn.execute("SELECT email FROM users WHERE id=?",(user_id,)).fetchone()
        if not user:return jsonify(error="Gebruiker niet gevonden"),404
        if user["email"]==os.environ.get("ADMIN_EMAIL","").strip().lower():
            return jsonify(error="Beheerdersaccount kan niet worden verwijderd"),400
        conn.execute("DELETE FROM users WHERE id=?",(user_id,))
    return jsonify(ok=True)

@app.get("/api/admin/users")
def admin_users():
    admin_email=os.environ.get("ADMIN_EMAIL","").strip().lower()
    if not admin_email or not session.get("uid"):
        return jsonify(error="Geen toegang"),403
    with db() as conn:
        admin=conn.execute("SELECT email FROM users WHERE id=?",(session["uid"],)).fetchone()
        if not admin or admin["email"]!=admin_email:
            return jsonify(error="Geen toegang"),403
        users=[dict(row) for row in conn.execute("SELECT id,email,name,created_at FROM users ORDER BY id DESC LIMIT 500")]
    for user in users:
        user["is_admin"]=user["email"]==admin_email
    return jsonify(users=users,count=len(users))

WFS = os.environ.get("ROTTERDAM_PARKING_WFS", "https://diensten.rotterdam.nl/arcgis/services/SB_Infra/Parkeervoorzieningen/MapServer/WFSServer")
HEADERS = {"User-Agent": "ParkeerMeneer/0.4 educational prototype"}
_parking_cache = {"expires": 0, "payload": None}
_parking_lock = threading.Lock()

def _parking_position(geometry):
    """Get representative lon/lat for Point, MultiPoint, LineString or Polygon GeoJSON."""
    if not isinstance(geometry, dict): return None
    kind, coords = geometry.get("type"), geometry.get("coordinates")
    if kind == "Point" and isinstance(coords, list) and len(coords) >= 2: return coords[:2]
    if kind == "MultiPoint" and coords: return coords[0][:2]
    if kind == "LineString" and coords: return coords[len(coords)//2][:2]
    if kind == "MultiLineString" and coords and coords[0]: return coords[0][len(coords[0])//2][:2]
    if kind == "Polygon" and coords and coords[0]:
        ring=coords[0];return [sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring)]
    if kind == "MultiPolygon" and coords and coords[0] and coords[0][0]:
        ring=coords[0][0];return [sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring)]
    return None

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/api/health")
def health():
    return jsonify(status="ok", geographic_source="Rotterdam parking WFS (best effort)", occupancy="synthetic")

# School-provided Cityverse/Open Urban Platform API references (IoT en API data Brian).
# This endpoint retrieves catalog metadata, not live parking occupancy or 3D geometry.
_cityverse_cache={"expires":0.0,"payload":None}
_cityverse_lock=threading.Lock()

@app.get("/api/cityverse/catalog")
def cityverse_catalog():
    now=time.monotonic()
    with _cityverse_lock:
        if _cityverse_cache["payload"] is not None and now < _cityverse_cache["expires"]:
            return jsonify(_cityverse_cache["payload"])
    endpoints={
        "hubs":"https://hub.clearly.app/api/hubs",
        "datasets":"https://hub.clearly.app/api/datasets",
    }
    results={}
    for kind,url in endpoints.items():
        try:
            response=requests.get(url,headers={"Accept":"application/json"},timeout=6)
            response.raise_for_status()
            data=response.json()
            if isinstance(data,list):
                items=data
            elif isinstance(data,dict):
                items=next((data[k] for k in ("items","results","data") if isinstance(data.get(k),list)),[])
            else:
                items=[]
            # Bounded, metadata-only sample; do not expose arbitrary source fields.
            sample=[]
            for item in items[:30]:
                if not isinstance(item,dict):continue
                sample.append({"id":str(item.get("id",""))[:100],"name":str(item.get("name") or item.get("title") or "")[:160]})
            results[kind]={"status":"connected","count_returned":len(items),"sample":sample,"url":url}
        except (requests.RequestException,ValueError,TypeError) as exc:
            results[kind]={"status":"unavailable","error":str(exc)[:160],"url":url}
    payload={"source_document":"IoT en API data Brian (school)","type":"catalog_metadata","occupancy":"synthetic_not_from_cityverse","three_d_geometry":"not_integrated","sources":results}
    with _cityverse_lock:
        _cityverse_cache.update(expires=time.monotonic()+300,payload=payload)
    return jsonify(payload)

@app.get("/api/cityverse/rotterdam-3d")
def cityverse_rotterdam_3d():
    """Inspect school-supplied OUP catalog for Rotterdam 3D resources; no geometry claims."""
    endpoint="https://hub.clearly.app/api/datasets"
    try:
        response=requests.get(endpoint,params={"search":"3D Rotterdam"},headers={"Accept":"application/json"},timeout=12)
        response.raise_for_status()
        data=response.json()
        if isinstance(data,list):
            items=data
        elif isinstance(data,dict):
            items=next((data[k] for k in ("items","results","data") if isinstance(data.get(k),list)),[])
        else:
            items=[]
        matches=[]
        for item in items[:1000]:
            if not isinstance(item,dict):continue
            name=str(item.get("name") or item.get("title") or "")
            if "rotterdam" not in name.lower() or "3d" not in name.lower():continue
            # Return catalog references only, never claim URLs are validated 3D tiles.
            references=[]
            def scan(obj,depth=0):
                if depth>3 or len(references)>=25:return
                if isinstance(obj,dict):
                    for k,v in obj.items():
                        if isinstance(v,str) and v.startswith(("https://","http://")) and any(t in k.lower() for t in ("url","uri","href","endpoint","download")):
                            references.append({"field":str(k)[:60],"url":v[:600]})
                        elif isinstance(v,(dict,list)):scan(v,depth+1)
                elif isinstance(obj,list):
                    for v in obj[:30]:scan(v,depth+1)
            scan(item)
            matches.append({"name":name[:180],"id":str(item.get("id") or item.get("_id") or "")[:120],"references":references})
            if len(matches)>=20:break
        return jsonify(status="connected",source="School OUP / Clearly.Hub",query="3D Rotterdam",count_returned=len(items),matches=matches,geometry_loaded=False,notes="Catalog references only; 3D tile URLs still need validation")
    except (requests.RequestException,ValueError,TypeError) as exc:
        return jsonify(status="unavailable",source="School OUP / Clearly.Hub",error=str(exc)[:180],geometry_loaded=False),503

@app.get("/api/parking")
def parking():
    now=time.monotonic()
    with _parking_lock:
        if _parking_cache["payload"] is not None and now < _parking_cache["expires"]:
            return jsonify(_parking_cache["payload"])
    try:
        response=requests.get(WFS,params={"service":"WFS","request":"GetCapabilities","version":"2.0.0"},headers=HEADERS,timeout=8)
        response.raise_for_status()
        root=ET.fromstring(response.content)
        types=[el.text for ft in root.findall(".//{*}FeatureType") for el in [ft.find("{*}Name")] if el is not None and el.text]
        if not types: raise ValueError("Geen WFS-featuretypes gevonden")
        features=[]; seen=set()
        for typename in types[:6]:
            if len(features)>=300:break
            params={"service":"WFS","version":"2.0.0","request":"GetFeature","typeNames":typename,"count":250,"outputFormat":"application/json","srsName":"EPSG:4326"}
            try:
                res=requests.get(WFS,params=params,headers=HEADERS,timeout=9)
                if not res.ok or "json" not in res.headers.get("content-type","").lower():continue
                data=res.json()
            except (requests.RequestException,ValueError):continue
            for feature in data.get("features",[]):
                position=_parking_position(feature.get("geometry"))
                if position is None:continue
                try:lon,lat=map(float,position)
                except (ValueError,TypeError):continue
                if not (51.7<lat<52.2 and 3.7<lon<4.9):continue
                props=feature.get("properties") or {}
                name=next((str(v) for k,v in props.items() if any(t in k.lower() for t in ("naam","name","straat","type")) and v is not None),"Parkeervoorziening")
                key=(round(lat,6),round(lon,6),typename)
                if key in seen:continue
                seen.add(key)
                features.append({"id":str(feature.get("id") or len(features))[:100],"name":name[:80],"lat":lat,"lon":lon,"source":"Rotterdam WFS","layer":typename[:100]})
                if len(features)>=300:break
        if not features:raise ValueError("Geen bruikbare geografische objecten ontvangen")
        payload={"mode":"live","features":features,"types":types,"occupancy":"not_available","source":"Rotterdam parking WFS","sample_limited":True}
        ttl=900
    except (requests.RequestException,ValueError,ET.ParseError) as exc:
        payload={"mode":"unavailable","features":[],"message":str(exc)[:180],"occupancy":"not_available","source":"Rotterdam parking WFS"}
        ttl=120
    with _parking_lock:
        _parking_cache.update(expires=time.monotonic()+ttl,payload=payload)
    return jsonify(payload)

@app.get("/api/nearby-garages")
def nearby_garages():
    try:
        lat=float(request.args.get("lat",""))
        lon=float(request.args.get("lon",""))
        if not (51.7<lat<52.2 and 3.7<lon<4.9):
            return jsonify(error="Locatie buiten Rotterdam"),400
    except (ValueError,TypeError):
        return jsonify(error="Ongeldige coördinaten"),400
    query=f'[out:json][timeout:8];(nwr["amenity"="parking"]["parking"="multi-storey"](around:4500,{lat},{lon});nwr["amenity"="parking"]["parking"="underground"](around:4500,{lat},{lon}););out center 50;'
    for url in ("https://overpass.kumi.systems/api/interpreter","https://overpass.private.coffee/api/interpreter","https://overpass-api.de/api/interpreter"):
        try:
            res=requests.post(url,data={"data":query},timeout=7)
            res.raise_for_status()
            return jsonify(elements=res.json().get("elements",[]))
        except (requests.RequestException,ValueError):
            continue
    return jsonify(error="Kaartdienst tijdelijk niet bereikbaar",elements=[]),503

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)
