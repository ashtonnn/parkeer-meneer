from flask import Flask, jsonify, send_from_directory, request, session
from pathlib import Path
import requests, xml.etree.ElementTree as ET
import os, re
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
